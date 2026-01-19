using System.Globalization;
using System.Text.RegularExpressions;
using JobIntel.Core.DTOs;
using JobIntel.Core.Entities;
using JobIntel.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace JobIntel.Ingest.Services;

/// <summary>
/// Ingestion pipeline that processes raw job data through normalization, deduplication, and storage
/// Implementation follows Technical Design Document Section 6.2.4
/// </summary>
public class IngestionPipeline : IIngestionPipeline
{
    private readonly IJobRepository _jobRepository;
    private readonly IDeduplicationService _deduplicationService;
    private readonly ILogger<IngestionPipeline> _logger;

    public IngestionPipeline(
        IJobRepository jobRepository,
        IDeduplicationService deduplicationService,
        ILogger<IngestionPipeline> logger)
    {
        _jobRepository = jobRepository;
        _deduplicationService = deduplicationService;
        _logger = logger;
    }

    /// <summary>
    /// Process raw jobs through the pipeline: Normalize → Deduplicate → Store
    /// </summary>
    public async Task<IngestionResult> ProcessAsync(
        List<RawJobData> rawJobs,
        string source,
        CancellationToken cancellationToken = default)
    {
        var result = new IngestionResult
        {
            TotalProcessed = rawJobs.Count
        };

        _logger.LogInformation("Starting ingestion pipeline for {Count} jobs from {Source}", rawJobs.Count, source);

        foreach (var rawJob in rawJobs)
        {
            try
            {
                // Step 1: Normalize raw data to JobPosting entity
                var job = await NormalizeJobDataAsync(rawJob, source);

                // Step 2: Generate fingerprint and content hash
                job.Fingerprint = _deduplicationService.GenerateFingerprint(job);
                job.ContentHash = _deduplicationService.GenerateContentHash(job.Description, null);

                // Step 3: Check for existing job by source + source_id FIRST (primary dedup key)
                // 🔧 FIX: 先检查 source+source_id，避免违反 uq_source_external_id 约束
                var existingJob = await _jobRepository.GetBySourceIdAsync(job.Source, job.SourceId, cancellationToken);

                // If not found by source_id, also check by fingerprint (fallback for content-similar jobs)
                if (existingJob == null)
                {
                    existingJob = await _jobRepository.GetByFingerprintAsync(job.Fingerprint, cancellationToken);
                }

                if (existingJob == null)
                {
                    // New job - insert
                    job.CreatedAt = DateTime.UtcNow;
                    job.UpdatedAt = DateTime.UtcNow;
                    job.ScrapedAt = DateTime.UtcNow;
                    job.LastCheckedAt = DateTime.UtcNow;
                    job.IsActive = true;

                    await _jobRepository.InsertAsync(job, cancellationToken);
                    result.NewCount++;

                    _logger.LogDebug("Inserted new job: {Title} at {Company}", job.Title, job.Company);
                }
                else if (existingJob.ContentHash != job.ContentHash)
                {
                    // Content changed - update existing job
                    existingJob.Description = job.Description;
                    existingJob.ContentHash = job.ContentHash;
                    existingJob.UpdatedAt = DateTime.UtcNow;
                    existingJob.LastCheckedAt = DateTime.UtcNow;
                    existingJob.PayRangeMin = job.PayRangeMin;
                    existingJob.PayRangeMax = job.PayRangeMax;
                    existingJob.EmploymentType = job.EmploymentType;
                    existingJob.IsActive = true;

                    await _jobRepository.UpdateAsync(existingJob, cancellationToken);
                    result.UpdatedCount++;

                    _logger.LogDebug("Updated job: {Title} at {Company}", existingJob.Title, existingJob.Company);
                }
                else
                {
                    // Duplicate - no changes needed
                    existingJob.LastCheckedAt = DateTime.UtcNow;
                    await _jobRepository.UpdateAsync(existingJob, cancellationToken);
                    result.DedupedCount++;

                    _logger.LogDebug("Skipped duplicate job: {Title} at {Company}", existingJob.Title, existingJob.Company);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing job: {Title}", rawJob.Title);
                result.Errors.Add($"Error processing '{rawJob.Title}': {ex.Message}");
            }
        }

        _logger.LogInformation(
            "Ingestion completed: {New} new, {Updated} updated, {Deduped} duplicates, {Errors} errors",
            result.NewCount, result.UpdatedCount, result.DedupedCount, result.Errors.Count);

        return result;
    }

    /// <summary>
    /// Normalize raw job data into a JobPosting entity
    /// Python API already parses most fields, so we just map them directly
    /// </summary>
    private async Task<JobPosting> NormalizeJobDataAsync(RawJobData rawJob, string source)
    {
        var job = new JobPosting
        {
            Source = rawJob.Source,  // Use source from Python API
            SourceId = rawJob.SourceId,
            Title = rawJob.Title.Trim(),
            Company = rawJob.Company.Trim(),
            Description = rawJob.Description ?? string.Empty,
            JobUrl = rawJob.JobUrl,

            // Location - already parsed by Python API
            LocationState = rawJob.LocationState,
            LocationSuburb = rawJob.LocationSuburb,

            // Trade - already extracted by Python API
            Trade = rawJob.Trade,

            // Employment type - already normalized by Python API
            EmploymentType = rawJob.EmploymentType,

            // Salary - already parsed by Python API
            PayRangeMin = rawJob.PayRangeMin,
            PayRangeMax = rawJob.PayRangeMax,

            // Posted date - already parsed by Python API
            PostedAt = rawJob.PostedAt,

            // Tags - use tags from Python API if available
            Tags = rawJob.Tags != null && rawJob.Tags.Any()
                ? System.Text.Json.JsonSerializer.Serialize(rawJob.Tags)
                : null
        };

        return await Task.FromResult(job);
    }

    /// <summary>
    /// Parse location string into state and suburb
    /// Examples: "Adelaide, SA" -> state=SA, suburb=Adelaide
    /// </summary>
    private void ParseLocation(string location, out string? state, out string? suburb)
    {
        state = null;
        suburb = null;

        if (string.IsNullOrWhiteSpace(location))
            return;

        var parts = location.Split(',', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);

        if (parts.Length >= 2)
        {
            suburb = parts[0];
            var stateCandidate = parts[1].ToUpperInvariant();

            // Validate Australian state code
            string[] validStates = { "NSW", "VIC", "QLD", "SA", "WA", "TAS", "NT", "ACT" };
            if (validStates.Contains(stateCandidate))
            {
                state = stateCandidate;
            }
        }
        else if (parts.Length == 1)
        {
            suburb = parts[0];
        }
    }

    /// <summary>
    /// Extract trade category from job title
    /// </summary>
    private string? ExtractTrade(string title)
    {
        var titleLower = title.ToLowerInvariant();

        var trades = new Dictionary<string, string[]>
        {
            { "bricklayer", new[] { "bricklayer", "brick layer", "bricklaying" } },
            { "tiler", new[] { "tiler", "tiling", "wall and floor tiler" } },
            { "plasterer", new[] { "plasterer", "plastering", "solid plasterer" } },
            { "carpenter", new[] { "carpenter", "carpentry", "joiner" } },
            { "electrician", new[] { "electrician", "electrical", "sparky" } },
            { "plumber", new[] { "plumber", "plumbing" } },
            { "painter", new[] { "painter", "painting" } },
            { "labourer", new[] { "labourer", "laborer", "construction worker", "general hand" } }
        };

        foreach (var (trade, keywords) in trades)
        {
            if (keywords.Any(keyword => titleLower.Contains(keyword)))
            {
                return trade;
            }
        }

        return null;
    }

    /// <summary>
    /// Normalize employment type
    /// </summary>
    private string? NormalizeEmploymentType(string? employmentType)
    {
        if (string.IsNullOrWhiteSpace(employmentType))
            return null;

        var normalized = employmentType.ToLowerInvariant().Trim();

        return normalized switch
        {
            var t when t.Contains("full") && t.Contains("time") => "full-time",
            var t when t.Contains("part") && t.Contains("time") => "part-time",
            var t when t.Contains("casual") => "casual",
            var t when t.Contains("contract") => "contract",
            var t when t.Contains("apprentice") => "apprenticeship",
            var t when t.Contains("permanent") => "full-time",
            var t when t.Contains("temporary") => "contract",
            _ => normalized
        };
    }

    /// <summary>
    /// Parse salary range from string (e.g., "$35 - $45 per hour")
    /// </summary>
    private void ParseSalaryRange(string? salary, out decimal? min, out decimal? max)
    {
        min = null;
        max = null;

        if (string.IsNullOrWhiteSpace(salary))
            return;

        // Extract all numbers from salary string
        var matches = Regex.Matches(salary, @"\d+(?:\.\d+)?");

        if (matches.Count >= 2)
        {
            if (decimal.TryParse(matches[0].Value, out var minValue))
                min = minValue;
            if (decimal.TryParse(matches[1].Value, out var maxValue))
                max = maxValue;
        }
        else if (matches.Count == 1)
        {
            if (decimal.TryParse(matches[0].Value, out var value))
                min = value;
        }
    }

    /// <summary>
    /// Parse posted date from various string formats
    /// </summary>
    private DateTime? ParsePostedDate(string? postedAt)
    {
        if (string.IsNullOrWhiteSpace(postedAt))
            return null;

        if (DateTime.TryParse(postedAt, CultureInfo.InvariantCulture, DateTimeStyles.None, out var date))
            return date;

        return null;
    }

    /// <summary>
    /// Extract tags from job description and title
    /// </summary>
    private string? ExtractTags(string description, string title)
    {
        var tags = new List<string>();
        var combined = (description + " " + title).ToLowerInvariant();

        if (combined.Contains("visa sponsor") || combined.Contains("sponsorship"))
            tags.Add("visa_sponsor");

        if (combined.Contains("entry level") || combined.Contains("junior") || combined.Contains("apprentice"))
            tags.Add("entry_level");

        if (combined.Contains("senior") || combined.Contains("experienced") || combined.Contains("lead"))
            tags.Add("experienced");

        if (combined.Contains("remote") || combined.Contains("work from home"))
            tags.Add("remote");

        return tags.Any() ? System.Text.Json.JsonSerializer.Serialize(tags) : null;
    }

    /// <summary>
    /// Clean HTML tags and trim whitespace from description
    /// </summary>
    private string CleanHtmlAndTrim(string description)
    {
        if (string.IsNullOrWhiteSpace(description))
            return string.Empty;

        // Remove HTML tags
        var cleaned = Regex.Replace(description, @"<[^>]+>", string.Empty);

        // Decode HTML entities
        cleaned = System.Net.WebUtility.HtmlDecode(cleaned);

        // Collapse multiple whitespaces
        cleaned = Regex.Replace(cleaned, @"\s+", " ");

        return cleaned.Trim();
    }

    /// <summary>
    /// Extract requirements section from description
    /// </summary>
    private string? ExtractRequirements(string description)
    {
        if (string.IsNullOrWhiteSpace(description))
            return null;

        // Look for common requirements section markers
        var patterns = new[]
        {
            @"(?i)Requirements?:(.+?)(?=\n\n|Skills?:|Responsibilities?:|$)",
            @"(?i)Qualifications?:(.+?)(?=\n\n|Skills?:|Responsibilities?:|$)",
            @"(?i)You will have:(.+?)(?=\n\n|Skills?:|Responsibilities?:|$)"
        };

        foreach (var pattern in patterns)
        {
            var match = Regex.Match(description, pattern, RegexOptions.Singleline);
            if (match.Success && match.Groups.Count > 1)
            {
                return CleanHtmlAndTrim(match.Groups[1].Value);
            }
        }

        return null;
    }
}

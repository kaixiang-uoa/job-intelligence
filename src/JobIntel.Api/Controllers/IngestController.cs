using JobIntel.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json;

namespace JobIntel.Api.Controllers;

/// <summary>
/// Data ingestion API endpoints
/// Triggers scraping from Python API and returns raw data
/// </summary>
public class IngestController : BaseApiController
{
    private readonly IScrapeApiClient _scrapeApiClient;
    private readonly IIngestionPipeline _ingestionPipeline;
    private readonly ILogger<IngestController> _logger;

    public IngestController(
        IScrapeApiClient scrapeApiClient,
        IIngestionPipeline ingestionPipeline,
        ILogger<IngestController> logger)
    {
        _scrapeApiClient = scrapeApiClient;
        _ingestionPipeline = ingestionPipeline;
        _logger = logger;
    }

    /// <summary>
    /// Fetch jobs from specified source platform
    /// </summary>
    /// <param name="source">Platform source (seek or indeed)</param>
    /// <param name="keywords">Search keywords (space-separated)</param>
    /// <param name="location">Location filter (optional)</param>
    /// <param name="maxResults">Maximum results to fetch (default: 50)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of raw job data from Python API</returns>
    /// <response code="200">Returns list of jobs</response>
    /// <response code="400">Invalid parameters</response>
    /// <response code="500">Scraping failed</response>
    [HttpGet("{source}")]
    [ProducesResponseType(typeof(IngestResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IngestResponse>> FetchJobs(
        string source,
        [FromQuery] string keywords,
        [FromQuery] string? location = null,
        [FromQuery] int maxResults = 50,
        [FromQuery] bool saveToFile = false,
        CancellationToken cancellationToken = default)
    {
        // Validate source
        var validSources = new[] { "seek", "indeed" };
        if (!validSources.Contains(source.ToLower()))
        {
            return BadRequest(new { error = $"Invalid source. Must be one of: {string.Join(", ", validSources)}" });
        }

        // Validate keywords
        if (string.IsNullOrWhiteSpace(keywords))
        {
            return BadRequest(new { error = "Keywords are required" });
        }

        try
        {
            _logger.LogInformation(
                "Ingesting jobs from {Source}: keywords='{Keywords}', location='{Location}', maxResults={MaxResults}",
                source, keywords, location ?? "Any", maxResults);

            // Call Python scraper API
            var keywordsArray = keywords.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            var jobs = await _scrapeApiClient.FetchJobsAsync(
                source,
                keywordsArray,
                location,
                maxResults,
                cancellationToken);

            // Save to file if requested (for debugging)
            if (saveToFile)
            {
                await SaveJobsToFileAsync(jobs, source, keywords, location);
            }

            // Process jobs through ingestion pipeline (normalize, deduplicate, save)
            var ingestionResult = await _ingestionPipeline.ProcessAsync(jobs, source, cancellationToken);

            _logger.LogInformation(
                "Successfully ingested {Count} jobs from {Source}: {New} new, {Updated} updated, {Deduped} duplicates",
                jobs.Count, source, ingestionResult.NewCount, ingestionResult.UpdatedCount, ingestionResult.DedupedCount);

            return Ok(new IngestResponse
            {
                Source = source,
                Jobs = jobs,
                Count = jobs.Count,
                ScrapedAt = DateTime.UtcNow,
                IngestionStats = new IngestionStats
                {
                    New = ingestionResult.NewCount,
                    Updated = ingestionResult.UpdatedCount,
                    Duplicates = ingestionResult.DedupedCount,
                    Errors = ingestionResult.Errors.Count
                }
            });
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to call Python scraper API");
            return StatusCode(
                StatusCodes.Status500InternalServerError,
                new { error = "Failed to fetch jobs from scraper API", details = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error during ingestion");
            return StatusCode(
                StatusCodes.Status500InternalServerError,
                new { error = "An unexpected error occurred", details = ex.Message });
        }
    }

    /// <summary>
    /// Fetch jobs from both SEEK and Indeed platforms
    /// </summary>
    /// <param name="keywords">Search keywords</param>
    /// <param name="location">Location filter (optional)</param>
    /// <param name="maxResults">Maximum results per source (default: 50)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Combined list of jobs from both platforms</returns>
    [HttpGet("all")]
    [ProducesResponseType(typeof(IngestResponse), StatusCodes.Status200OK)]
    public async Task<ActionResult<IngestResponse>> FetchAllJobs(
        [FromQuery] string keywords,
        [FromQuery] string? location = null,
        [FromQuery] int maxResults = 50,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(keywords))
        {
            return BadRequest(new { error = "Keywords are required" });
        }

        try
        {
            _logger.LogInformation(
                "Ingesting jobs from ALL sources: keywords='{Keywords}', location='{Location}'",
                keywords, location ?? "Any");

            var keywordsArray = keywords.Split(' ', StringSplitOptions.RemoveEmptyEntries);

            // Fetch from both sources in parallel
            var seekTask = _scrapeApiClient.FetchJobsAsync("seek", keywordsArray, location, maxResults, cancellationToken);
            var indeedTask = _scrapeApiClient.FetchJobsAsync("indeed", keywordsArray, location, maxResults, cancellationToken);

            await Task.WhenAll(seekTask, indeedTask);

            var allJobs = seekTask.Result.Concat(indeedTask.Result).ToList();

            // Process all jobs through ingestion pipeline
            var ingestionResult = await _ingestionPipeline.ProcessAsync(allJobs, "all", cancellationToken);

            _logger.LogInformation(
                "Successfully ingested {TotalCount} jobs (SEEK: {SeekCount}, Indeed: {IndeedCount}): {New} new, {Updated} updated, {Deduped} duplicates",
                allJobs.Count, seekTask.Result.Count, indeedTask.Result.Count,
                ingestionResult.NewCount, ingestionResult.UpdatedCount, ingestionResult.DedupedCount);

            return Ok(new IngestResponse
            {
                Source = "all",
                Jobs = allJobs,
                Count = allJobs.Count,
                ScrapedAt = DateTime.UtcNow,
                IngestionStats = new IngestionStats
                {
                    New = ingestionResult.NewCount,
                    Updated = ingestionResult.UpdatedCount,
                    Duplicates = ingestionResult.DedupedCount,
                    Errors = ingestionResult.Errors.Count
                }
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to fetch jobs from all sources");
            return StatusCode(
                StatusCodes.Status500InternalServerError,
                new { error = "Failed to fetch jobs", details = ex.Message });
        }
    }

    /// <summary>
    /// Save scraped jobs to a temporary JSON file for inspection
    /// </summary>
    private async Task SaveJobsToFileAsync(
        List<JobIntel.Core.DTOs.RawJobData> jobs,
        string source,
        string keywords,
        string? location)
    {
        try
        {
            var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
            var filename = $"scraped_jobs_{source}_{keywords.Replace(" ", "_")}_{timestamp}.json";
            var filepath = Path.Combine("/tmp", filename);

            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            };

            var json = JsonSerializer.Serialize(new
            {
                Source = source,
                Keywords = keywords,
                Location = location,
                ScrapedAt = DateTime.UtcNow,
                Count = jobs.Count,
                Jobs = jobs
            }, options);

            await System.IO.File.WriteAllTextAsync(filepath, json);

            _logger.LogInformation(
                "Saved {Count} jobs to file: {FilePath}",
                jobs.Count, filepath);
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Failed to save jobs to file (non-critical)");
        }
    }
}

/// <summary>
/// Response model for ingest endpoints
/// </summary>
public class IngestResponse
{
    public string Source { get; set; } = string.Empty;
    public List<JobIntel.Core.DTOs.RawJobData> Jobs { get; set; } = new();
    public int Count { get; set; }
    public DateTime ScrapedAt { get; set; }
    public IngestionStats? IngestionStats { get; set; }
}

/// <summary>
/// Statistics from the ingestion pipeline
/// </summary>
public class IngestionStats
{
    public int New { get; set; }
    public int Updated { get; set; }
    public int Duplicates { get; set; }
    public int Errors { get; set; }
}

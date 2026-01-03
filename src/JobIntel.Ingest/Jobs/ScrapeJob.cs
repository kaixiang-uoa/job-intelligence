using JobIntel.Core.Entities;
using JobIntel.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace JobIntel.Ingest.Jobs;

/// <summary>
/// Hangfire background job for scraping job postings
/// Implementation follows Development Guide Section 4.4 and Technical Design Document Section 6.2.3
/// </summary>
public class ScrapeJob
{
    private readonly IScrapeApiClient _scrapeClient;
    private readonly IIngestionPipeline _pipeline;
    private readonly IIngestRunRepository _runRepository;
    private readonly ILogger<ScrapeJob> _logger;

    public ScrapeJob(
        IScrapeApiClient scrapeClient,
        IIngestionPipeline pipeline,
        IIngestRunRepository runRepository,
        ILogger<ScrapeJob> logger)
    {
        _scrapeClient = scrapeClient;
        _pipeline = pipeline;
        _runRepository = runRepository;
        _logger = logger;
    }

    /// <summary>
    /// Execute the scraping job
    /// Workflow: Create IngestRun → Fetch jobs from Scrape API → Process through pipeline → Update IngestRun
    /// </summary>
    /// <param name="source">Source platform (e.g., "seek", "indeed", "workforce_australia")</param>
    /// <param name="keywords">Search keywords</param>
    /// <param name="location">Location filter</param>
    /// <param name="maxResults">Maximum number of results to fetch</param>
    public async Task ExecuteAsync(
        string source,
        string[] keywords,
        string? location = null,
        int maxResults = 100)
    {
        // Step 1: Create IngestRun record
        var run = new IngestRun
        {
            Source = source,
            Keywords = string.Join(", ", keywords),
            Location = location,
            StartedAt = DateTime.UtcNow,
            Status = IngestRunStatus.Running,
            JobsFound = 0,
            JobsNew = 0,
            JobsUpdated = 0,
            JobsDeduped = 0
        };

        var runId = await _runRepository.CreateAsync(run);
        _logger.LogInformation(
            "Starting scrape job {RunId} for source: {Source}, keywords: {Keywords}, location: {Location}",
            runId, source, string.Join(", ", keywords), location ?? "Any");

        try
        {
            // Step 2: Fetch jobs from Python Scrape API
            var rawJobs = await _scrapeClient.FetchJobsAsync(source, keywords, location, maxResults);

            _logger.LogInformation(
                "Scrape job {RunId}: Fetched {Count} jobs from {Source}",
                runId, rawJobs.Count, source);

            run.JobsFound = rawJobs.Count;

            // Step 3: Process through ingestion pipeline
            var ingestionResult = await _pipeline.ProcessAsync(rawJobs, source);

            // Step 4: Update IngestRun with results
            run.CompletedAt = DateTime.UtcNow;
            run.JobsNew = ingestionResult.NewCount;
            run.JobsUpdated = ingestionResult.UpdatedCount;
            run.JobsDeduped = ingestionResult.DedupedCount;

            if (ingestionResult.Errors.Any())
            {
                run.Status = IngestRunStatus.PartialSuccess;
                run.ErrorMessage = $"{ingestionResult.Errors.Count} errors occurred during processing";
                run.Metadata = System.Text.Json.JsonSerializer.Serialize(new
                {
                    errors = ingestionResult.Errors.Take(10).ToList() // Store first 10 errors
                });

                _logger.LogWarning(
                    "Scrape job {RunId} completed with {ErrorCount} errors",
                    runId, ingestionResult.Errors.Count);
            }
            else
            {
                run.Status = IngestRunStatus.Success;

                _logger.LogInformation(
                    "Scrape job {RunId} completed successfully: {New} new, {Updated} updated, {Deduped} duplicates",
                    runId, run.JobsNew, run.JobsUpdated, run.JobsDeduped);
            }

            await _runRepository.UpdateAsync(run);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Scrape job {RunId} failed", runId);

            // Update run status to failed
            run.CompletedAt = DateTime.UtcNow;
            run.Status = IngestRunStatus.Failed;
            run.ErrorMessage = ex.Message;
            run.ErrorStackTrace = ex.StackTrace;

            await _runRepository.UpdateAsync(run);

            // Rethrow to let Hangfire handle retry logic
            throw;
        }
    }
}

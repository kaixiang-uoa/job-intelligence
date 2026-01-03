using JobIntel.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace JobIntel.Ingest.Services;

/// <summary>
/// Implementation of scheduled job ingestion service
/// Fetches jobs from SEEK and Indeed, then saves to database via IngestionPipeline
/// </summary>
public class ScheduledIngestService : IScheduledIngestService
{
    private readonly IScrapeApiClient _scrapeApiClient;
    private readonly IIngestionPipeline _ingestionPipeline;
    private readonly ILogger<ScheduledIngestService> _logger;

    public ScheduledIngestService(
        IScrapeApiClient scrapeApiClient,
        IIngestionPipeline ingestionPipeline,
        ILogger<ScheduledIngestService> logger)
    {
        _scrapeApiClient = scrapeApiClient;
        _ingestionPipeline = ingestionPipeline;
        _logger = logger;
    }

    public async Task FetchAndSaveAsync(
        string trade,
        string location,
        int maxResults,
        CancellationToken cancellationToken = default)
    {
        var jobId = $"{trade}-{location}";

        try
        {
            _logger.LogInformation(
                "Scheduled fetch started: trade={Trade}, location={Location}, maxResults={MaxResults}",
                trade, location, maxResults);

            var startTime = DateTime.UtcNow;

            // 1. Fetch from SEEK and Indeed in parallel
            var seekTask = _scrapeApiClient.FetchJobsAsync(
                "seek",
                new[] { trade },
                location,
                maxResults,
                cancellationToken);

            var indeedTask = _scrapeApiClient.FetchJobsAsync(
                "indeed",
                new[] { trade },
                location,
                maxResults,
                cancellationToken);

            await Task.WhenAll(seekTask, indeedTask);

            var seekJobs = await seekTask;
            var indeedJobs = await indeedTask;
            var allJobs = seekJobs.Concat(indeedJobs).ToList();

            _logger.LogInformation(
                "Fetched {TotalCount} jobs: {SeekCount} from SEEK, {IndeedCount} from Indeed",
                allJobs.Count, seekJobs.Count, indeedJobs.Count);

            // 2. Process and save via IngestionPipeline (deduplication included)
            var result = await _ingestionPipeline.ProcessAsync(
                allJobs,
                "scheduled",
                cancellationToken);

            var duration = DateTime.UtcNow - startTime;

            _logger.LogInformation(
                "Scheduled fetch completed for {JobId}: " +
                "{New} new, {Updated} updated, {Duplicates} duplicates, {Errors} errors " +
                "in {Duration:F2}s",
                jobId,
                result.NewCount,
                result.UpdatedCount,
                result.DedupedCount,
                result.Errors.Count,
                duration.TotalSeconds);

            // Log errors if any
            if (result.Errors.Count > 0)
            {
                _logger.LogWarning(
                    "Encountered {ErrorCount} errors during ingestion for {JobId}",
                    result.Errors.Count, jobId);

                foreach (var error in result.Errors.Take(5))  // Log first 5 errors
                {
                    _logger.LogWarning("Ingestion error: {Error}", error);
                }
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Scheduled fetch failed for {JobId}: {ErrorMessage}",
                jobId, ex.Message);

            // Re-throw to let Hangfire handle retry
            throw;
        }
    }
}

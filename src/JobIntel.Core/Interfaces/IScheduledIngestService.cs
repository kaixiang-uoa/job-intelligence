namespace JobIntel.Core.Interfaces;

/// <summary>
/// Service for scheduled job ingestion tasks
/// Used by Hangfire recurring jobs to fetch and save jobs automatically
/// </summary>
public interface IScheduledIngestService
{
    /// <summary>
    /// Fetch jobs from external sources and save to database
    /// </summary>
    /// <param name="trade">Trade/occupation type (e.g., "plumber")</param>
    /// <param name="location">Location to search (e.g., "Sydney")</param>
    /// <param name="maxResults">Maximum number of results to fetch per source</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Task representing the async operation</returns>
    Task FetchAndSaveAsync(
        string trade,
        string location,
        int maxResults,
        CancellationToken cancellationToken = default);
}

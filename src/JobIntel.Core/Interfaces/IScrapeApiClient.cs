using JobIntel.Core.DTOs;

namespace JobIntel.Core.Interfaces;

/// <summary>
/// Interface for communicating with the Python Scrape API
/// </summary>
public interface IScrapeApiClient
{
    /// <summary>
    /// Fetch jobs from a specific source
    /// </summary>
    /// <param name="source">Source platform (e.g., "seek", "indeed")</param>
    /// <param name="keywords">Search keywords</param>
    /// <param name="location">Location filter</param>
    /// <param name="maxResults">Maximum number of results to fetch</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of raw job data</returns>
    Task<List<RawJobData>> FetchJobsAsync(
        string source,
        string[] keywords,
        string? location = null,
        int maxResults = 100,
        CancellationToken cancellationToken = default);
}

using JobIntel.Core.DTOs;

namespace JobIntel.Core.Interfaces;

/// <summary>
/// Interface for the ingestion pipeline that processes raw job data
/// </summary>
public interface IIngestionPipeline
{
    /// <summary>
    /// Process a batch of raw job data through the pipeline
    /// </summary>
    /// <param name="rawJobs">List of raw job data from scraper</param>
    /// <param name="source">Source platform</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Ingestion result with counts</returns>
    Task<IngestionResult> ProcessAsync(
        List<RawJobData> rawJobs,
        string source,
        CancellationToken cancellationToken = default);
}

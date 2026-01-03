using JobIntel.Core.DTOs;
using JobIntel.Core.Entities;

namespace JobIntel.Core.Interfaces;

/// <summary>
/// Repository interface for JobPosting entities
/// </summary>
public interface IJobRepository
{
    // Basic CRUD operations
    Task<JobPosting?> GetByIdAsync(int id, CancellationToken cancellationToken = default);

    Task<JobPosting?> GetByFingerprintAsync(string fingerprint, CancellationToken cancellationToken = default);

    Task<int> InsertAsync(JobPosting job, CancellationToken cancellationToken = default);

    Task UpdateAsync(JobPosting job, CancellationToken cancellationToken = default);

    Task<int> GetCountAsync(CancellationToken cancellationToken = default);

    // Search and filtering (V1 - Sprint 1.4)
    /// <summary>
    /// Search jobs with filtering, sorting and pagination
    /// </summary>
    Task<PaginatedResult<JobPosting>> SearchAsync(
        JobSearchCriteria criteria,
        int page,
        int pageSize,
        string sortBy,
        CancellationToken cancellationToken = default);

    // Analytics and statistics (V1 - Sprint 1.4)
    /// <summary>
    /// Get job count grouped by trade
    /// </summary>
    Task<Dictionary<string, int>> GetCountByTradeAsync(
        DateTime? since = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get job count grouped by location state
    /// </summary>
    Task<Dictionary<string, int>> GetCountByStateAsync(
        DateTime? since = null,
        CancellationToken cancellationToken = default);

    /// <summary>
    /// Get total number of active jobs
    /// </summary>
    Task<int> GetTotalActiveJobsAsync(CancellationToken cancellationToken = default);

    /// <summary>
    /// Get number of jobs added today
    /// </summary>
    Task<int> GetJobsAddedTodayAsync(CancellationToken cancellationToken = default);
}

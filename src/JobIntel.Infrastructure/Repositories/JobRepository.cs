using JobIntel.Core.DTOs;
using JobIntel.Core.Entities;
using JobIntel.Core.Interfaces;
using JobIntel.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace JobIntel.Infrastructure.Repositories;

/// <summary>
/// Repository implementation for JobPosting entities
/// Follows Technical Design Document Section 4.2
/// </summary>
public class JobRepository : IJobRepository
{
    private readonly JobIntelDbContext _context;
    private readonly ILogger<JobRepository> _logger;

    public JobRepository(JobIntelDbContext context, ILogger<JobRepository> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<JobPosting?> GetByIdAsync(int id, CancellationToken cancellationToken = default)
    {
        return await _context.JobPostings
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == id, cancellationToken);
    }

    public async Task<JobPosting?> GetByFingerprintAsync(string fingerprint, CancellationToken cancellationToken = default)
    {
        return await _context.JobPostings
            .FirstOrDefaultAsync(x => x.Fingerprint == fingerprint, cancellationToken);
    }

    public async Task<int> InsertAsync(JobPosting job, CancellationToken cancellationToken = default)
    {
        try
        {
            _context.JobPostings.Add(job);
            await _context.SaveChangesAsync(cancellationToken);

            _logger.LogDebug("Inserted job posting with ID: {Id}", job.Id);
            return job.Id;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to insert job posting: {Title}", job.Title);
            throw;
        }
    }

    public async Task UpdateAsync(JobPosting job, CancellationToken cancellationToken = default)
    {
        try
        {
            _context.JobPostings.Update(job);
            await _context.SaveChangesAsync(cancellationToken);

            _logger.LogDebug("Updated job posting with ID: {Id}", job.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update job posting: {Id}", job.Id);
            throw;
        }
    }

    public async Task<int> GetCountAsync(CancellationToken cancellationToken = default)
    {
        return await _context.JobPostings.CountAsync(cancellationToken);
    }

    // V1 Sprint 1.4 - Search and filtering
    public async Task<PaginatedResult<JobPosting>> SearchAsync(
        JobSearchCriteria criteria,
        int page,
        int pageSize,
        string sortBy,
        CancellationToken cancellationToken = default)
    {
        var query = _context.JobPostings.AsNoTracking().AsQueryable();

        // Apply filters
        if (!string.IsNullOrWhiteSpace(criteria.Trade))
        {
            query = query.Where(x => x.Trade == criteria.Trade);
        }

        if (!string.IsNullOrWhiteSpace(criteria.State))
        {
            query = query.Where(x => x.LocationState == criteria.State);
        }

        if (!string.IsNullOrWhiteSpace(criteria.Suburb))
        {
            query = query.Where(x => x.LocationSuburb == criteria.Suburb);
        }

        if (criteria.PostedAfter.HasValue)
        {
            query = query.Where(x => x.PostedAt >= criteria.PostedAfter.Value);
        }

        if (criteria.PayMin.HasValue)
        {
            query = query.Where(x => x.PayRangeMax >= criteria.PayMin.Value);
        }

        if (criteria.PayMax.HasValue)
        {
            query = query.Where(x => x.PayRangeMin <= criteria.PayMax.Value);
        }

        if (!string.IsNullOrWhiteSpace(criteria.EmploymentType))
        {
            query = query.Where(x => x.EmploymentType == criteria.EmploymentType);
        }

        // Only show active jobs
        query = query.Where(x => x.IsActive);

        // Apply sorting
        query = sortBy.ToLowerInvariant() switch
        {
            "posted_at_asc" => query.OrderBy(x => x.PostedAt),
            "posted_at_desc" => query.OrderByDescending(x => x.PostedAt),
            "pay_asc" => query.OrderBy(x => x.PayRangeMin),
            "pay_desc" => query.OrderByDescending(x => x.PayRangeMax),
            "title_asc" => query.OrderBy(x => x.Title),
            "title_desc" => query.OrderByDescending(x => x.Title),
            _ => query.OrderByDescending(x => x.PostedAt)  // Default: newest first
        };

        // Get total count
        var totalCount = await query.CountAsync(cancellationToken);

        // Apply pagination
        var items = await query
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync(cancellationToken);

        _logger.LogDebug(
            "Search completed: {Count} results (page {Page}/{TotalPages})",
            totalCount, page, (int)Math.Ceiling((double)totalCount / pageSize));

        return new PaginatedResult<JobPosting>
        {
            Items = items,
            TotalCount = totalCount,
            Page = page,
            PageSize = pageSize
        };
    }

    // V1 Sprint 1.4 - Analytics methods
    public async Task<Dictionary<string, int>> GetCountByTradeAsync(
        DateTime? since = null,
        CancellationToken cancellationToken = default)
    {
        var query = _context.JobPostings
            .AsNoTracking()
            .Where(x => x.IsActive && x.Trade != null);

        if (since.HasValue)
        {
            query = query.Where(x => x.ScrapedAt >= since.Value);
        }

        var result = await query
            .GroupBy(x => x.Trade)
            .Select(g => new { Trade = g.Key!, Count = g.Count() })
            .OrderByDescending(x => x.Count)
            .ToDictionaryAsync(x => x.Trade, x => x.Count, cancellationToken);

        return result;
    }

    public async Task<Dictionary<string, int>> GetCountByStateAsync(
        DateTime? since = null,
        CancellationToken cancellationToken = default)
    {
        var query = _context.JobPostings
            .AsNoTracking()
            .Where(x => x.IsActive && x.LocationState != null);

        if (since.HasValue)
        {
            query = query.Where(x => x.ScrapedAt >= since.Value);
        }

        var result = await query
            .GroupBy(x => x.LocationState)
            .Select(g => new { State = g.Key!, Count = g.Count() })
            .OrderByDescending(x => x.Count)
            .ToDictionaryAsync(x => x.State, x => x.Count, cancellationToken);

        return result;
    }

    public async Task<int> GetTotalActiveJobsAsync(CancellationToken cancellationToken = default)
    {
        return await _context.JobPostings
            .AsNoTracking()
            .CountAsync(x => x.IsActive, cancellationToken);
    }

    public async Task<int> GetJobsAddedTodayAsync(CancellationToken cancellationToken = default)
    {
        var today = DateTime.UtcNow.Date;
        return await _context.JobPostings
            .AsNoTracking()
            .CountAsync(x => x.ScrapedAt >= today, cancellationToken);
    }
}

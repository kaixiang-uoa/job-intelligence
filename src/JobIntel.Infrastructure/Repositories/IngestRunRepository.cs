using JobIntel.Core.Entities;
using JobIntel.Core.Interfaces;
using JobIntel.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;

namespace JobIntel.Infrastructure.Repositories;

/// <summary>
/// Repository implementation for IngestRun entities
/// </summary>
public class IngestRunRepository : IIngestRunRepository
{
    private readonly JobIntelDbContext _context;
    private readonly ILogger<IngestRunRepository> _logger;

    public IngestRunRepository(JobIntelDbContext context, ILogger<IngestRunRepository> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<int> CreateAsync(IngestRun run, CancellationToken cancellationToken = default)
    {
        try
        {
            _context.IngestRuns.Add(run);
            await _context.SaveChangesAsync(cancellationToken);

            _logger.LogDebug("Created ingest run with ID: {Id}", run.Id);
            return run.Id;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to create ingest run for source: {Source}", run.Source);
            throw;
        }
    }

    public async Task UpdateAsync(IngestRun run, CancellationToken cancellationToken = default)
    {
        try
        {
            _context.IngestRuns.Update(run);
            await _context.SaveChangesAsync(cancellationToken);

            _logger.LogDebug("Updated ingest run with ID: {Id}", run.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update ingest run: {Id}", run.Id);
            throw;
        }
    }

    public async Task<IngestRun?> GetByIdAsync(int id, CancellationToken cancellationToken = default)
    {
        return await _context.IngestRuns
            .AsNoTracking()
            .FirstOrDefaultAsync(x => x.Id == id, cancellationToken);
    }

    public async Task<List<IngestRun>> GetRecentAsync(int count, CancellationToken cancellationToken = default)
    {
        return await _context.IngestRuns
            .AsNoTracking()
            .OrderByDescending(x => x.StartedAt)
            .Take(count)
            .ToListAsync(cancellationToken);
    }
}

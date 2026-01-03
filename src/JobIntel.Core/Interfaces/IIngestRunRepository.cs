using JobIntel.Core.Entities;

namespace JobIntel.Core.Interfaces;

/// <summary>
/// Repository interface for IngestRun entities
/// </summary>
public interface IIngestRunRepository
{
    Task<int> CreateAsync(IngestRun run, CancellationToken cancellationToken = default);

    Task UpdateAsync(IngestRun run, CancellationToken cancellationToken = default);

    Task<IngestRun?> GetByIdAsync(int id, CancellationToken cancellationToken = default);

    Task<List<IngestRun>> GetRecentAsync(int count, CancellationToken cancellationToken = default);
}

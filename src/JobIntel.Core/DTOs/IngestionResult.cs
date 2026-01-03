namespace JobIntel.Core.DTOs;

/// <summary>
/// Result of the ingestion pipeline processing
/// </summary>
public class IngestionResult
{
    public int NewCount { get; set; }

    public int UpdatedCount { get; set; }

    public int DedupedCount { get; set; }

    public int TotalProcessed { get; set; }

    public List<string> Errors { get; set; } = new();
}

namespace JobIntel.Core.Entities;

public class IngestRun
{
    public int Id { get; set; }

    public string Source { get; set; } = string.Empty;

    public string? Keywords { get; set; }

    public string? Location { get; set; }

    public DateTime StartedAt { get; set; }

    public DateTime? CompletedAt { get; set; }

    public IngestRunStatus Status { get; set; }

    public int JobsFound { get; set; }

    public int JobsNew { get; set; }

    public int JobsUpdated { get; set; }

    public int JobsDeduped { get; set; }

    public string? ErrorMessage { get; set; }

    public string? ErrorStackTrace { get; set; }

    public string? Metadata { get; set; } // JSON metadata
}

public enum IngestRunStatus
{
    Pending = 0,
    Running = 1,
    Success = 2,
    Failed = 3,
    PartialSuccess = 4
}

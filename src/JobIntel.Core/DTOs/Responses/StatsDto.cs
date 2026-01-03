namespace JobIntel.Core.DTOs.Responses;

/// <summary>
/// Overall statistics data transfer object
/// </summary>
public class StatsDto
{
    /// <summary>
    /// Total number of jobs in database
    /// </summary>
    public int TotalJobs { get; set; }

    /// <summary>
    /// Number of currently active jobs
    /// </summary>
    public int ActiveJobs { get; set; }

    /// <summary>
    /// Number of jobs added today
    /// </summary>
    public int JobsAddedToday { get; set; }

    /// <summary>
    /// Job count breakdown by trade
    /// Key: trade name, Value: count
    /// </summary>
    public Dictionary<string, int> ByTrade { get; set; } = new();

    /// <summary>
    /// Job count breakdown by state
    /// Key: state code, Value: count
    /// </summary>
    public Dictionary<string, int> ByState { get; set; } = new();

    /// <summary>
    /// Average pay rate statistics
    /// </summary>
    public AvgPayRateDto? AvgPayRate { get; set; }
}

/// <summary>
/// Average pay rate statistics
/// </summary>
public class AvgPayRateDto
{
    public decimal? Min { get; set; }

    public decimal? Max { get; set; }

    public decimal? Median { get; set; }
}

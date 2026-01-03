namespace JobIntel.Core.DTOs;

/// <summary>
/// Internal search criteria for repository layer
/// Mapped from JobSearchRequest
/// </summary>
public class JobSearchCriteria
{
    public string? Trade { get; set; }

    public string? State { get; set; }

    public string? Suburb { get; set; }

    public DateTime? PostedAfter { get; set; }

    public decimal? PayMin { get; set; }

    public decimal? PayMax { get; set; }

    public string? EmploymentType { get; set; }
}

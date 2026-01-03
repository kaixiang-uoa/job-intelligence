using System.ComponentModel.DataAnnotations;

namespace JobIntel.Core.DTOs.Requests;

/// <summary>
/// Request model for job search with filtering and pagination
/// API uses camelCase, internal uses PascalCase
/// </summary>
public class JobSearchRequest
{
    /// <summary>
    /// Filter by trade/occupation (e.g., "tiler", "bricklayer")
    /// </summary>
    public string? Trade { get; set; }

    /// <summary>
    /// Filter by location state (e.g., "SA", "VIC")
    /// </summary>
    public string? State { get; set; }

    /// <summary>
    /// Filter by location suburb/city (e.g., "Adelaide", "Melbourne")
    /// </summary>
    public string? Suburb { get; set; }

    /// <summary>
    /// Filter jobs posted after this date
    /// </summary>
    public DateTime? PostedAfter { get; set; }

    /// <summary>
    /// Minimum pay range filter
    /// </summary>
    [Range(0, double.MaxValue, ErrorMessage = "PayMin must be greater than or equal to 0")]
    public decimal? PayMin { get; set; }

    /// <summary>
    /// Maximum pay range filter
    /// </summary>
    [Range(0, double.MaxValue, ErrorMessage = "PayMax must be greater than or equal to 0")]
    public decimal? PayMax { get; set; }

    /// <summary>
    /// Filter by employment type (e.g., "Full-time", "Part-time", "Contract")
    /// </summary>
    public string? EmploymentType { get; set; }

    /// <summary>
    /// Page number (1-based)
    /// </summary>
    [Range(1, int.MaxValue, ErrorMessage = "Page must be greater than 0")]
    public int Page { get; set; } = 1;

    /// <summary>
    /// Number of items per page
    /// </summary>
    [Range(1, 100, ErrorMessage = "PageSize must be between 1 and 100")]
    public int PageSize { get; set; } = 20;

    /// <summary>
    /// Sort order (e.g., "posted_at_desc", "posted_at_asc", "pay_desc")
    /// </summary>
    public string SortBy { get; set; } = "posted_at_desc";
}

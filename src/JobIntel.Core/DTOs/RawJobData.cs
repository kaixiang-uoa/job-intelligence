using System.Text.Json.Serialization;

namespace JobIntel.Core.DTOs;

/// <summary>
/// Raw job data received from the Python Scrape API
/// Maps directly to Python's JobPostingDTO
/// </summary>
public class RawJobData
{
    // Required fields
    [JsonPropertyName("source")]
    public string Source { get; set; } = string.Empty;

    [JsonPropertyName("source_id")]
    public string SourceId { get; set; } = string.Empty;

    [JsonPropertyName("title")]
    public string Title { get; set; } = string.Empty;

    [JsonPropertyName("company")]
    public string Company { get; set; } = string.Empty;

    // Location information
    [JsonPropertyName("location_state")]
    public string? LocationState { get; set; }

    [JsonPropertyName("location_suburb")]
    public string? LocationSuburb { get; set; }

    // Job attributes
    [JsonPropertyName("trade")]
    public string? Trade { get; set; }

    [JsonPropertyName("employment_type")]
    public string? EmploymentType { get; set; }

    // Salary information
    [JsonPropertyName("pay_range_min")]
    public decimal? PayRangeMin { get; set; }

    [JsonPropertyName("pay_range_max")]
    public decimal? PayRangeMax { get; set; }

    // Detailed information
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    [JsonPropertyName("tags")]
    public List<string>? Tags { get; set; }

    // Timestamps
    [JsonPropertyName("posted_at")]
    public DateTime? PostedAt { get; set; }

    [JsonPropertyName("scraped_at")]
    public DateTime ScrapedAt { get; set; }

    // Extended fields
    [JsonPropertyName("job_url")]
    public string? JobUrl { get; set; }

    [JsonPropertyName("is_remote")]
    public bool? IsRemote { get; set; }

    [JsonPropertyName("company_url")]
    public string? CompanyUrl { get; set; }
}

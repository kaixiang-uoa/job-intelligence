namespace JobIntel.Core.DTOs.Responses;

/// <summary>
/// Job listing data transfer object for API responses
/// Includes V2 reserved fields (commented out for V1)
/// </summary>
public class JobDto
{
    public int Id { get; set; }

    public string Title { get; set; } = string.Empty;

    public string Company { get; set; } = string.Empty;

    public LocationDto? Location { get; set; }

    public string? Trade { get; set; }

    public string? EmploymentType { get; set; }

    public PayRangeDto? PayRange { get; set; }

    public string Description { get; set; } = string.Empty;

    public string? JobUrl { get; set; }

    public List<string> Tags { get; set; } = new();

    public DateTime? PostedAt { get; set; }

    public JobSourceDto Source { get; set; } = null!;

    // V2 预留字段（当前不使用）
    // /// <summary>
    // /// V2: 当前用户是否已保存此工作
    // /// </summary>
    // public bool IsSaved { get; set; }

    // /// <summary>
    // /// V2: 当前用户是否设置了提醒
    // /// </summary>
    // public bool HasAlert { get; set; }
}

/// <summary>
/// Location information
/// </summary>
public class LocationDto
{
    public string? State { get; set; }

    public string? Suburb { get; set; }
}

/// <summary>
/// Pay range information
/// </summary>
public class PayRangeDto
{
    public decimal? Min { get; set; }

    public decimal? Max { get; set; }

    public string Currency { get; set; } = "AUD";

    public string Unit { get; set; } = "hour";  // hour, year, day
}

/// <summary>
/// Job source information
/// </summary>
public class JobSourceDto
{
    public string Name { get; set; } = string.Empty;

    public string? Url { get; set; }
}

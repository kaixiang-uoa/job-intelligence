namespace JobIntel.Core.Entities;

public class JobPosting
{
    public int Id { get; set; }

    public string Source { get; set; } = string.Empty;

    public string SourceId { get; set; } = string.Empty;

    public string Title { get; set; } = string.Empty;

    public string Company { get; set; } = string.Empty;

    public string? LocationState { get; set; }

    public string? LocationSuburb { get; set; }

    public string? Trade { get; set; }

    public string? EmploymentType { get; set; }

    public decimal? PayRangeMin { get; set; }

    public decimal? PayRangeMax { get; set; }

    public string Description { get; set; } = string.Empty;

    public string? JobUrl { get; set; }

    public string? Keywords { get; set; } // JSONB - extracted keywords for search/recommendations

    public string? Tags { get; set; } // JSONB - array of tags

    public string Fingerprint { get; set; } = string.Empty;

    public string ContentHash { get; set; } = string.Empty;

    public DateTime? PostedAt { get; set; }

    public DateTime ScrapedAt { get; set; }

    public DateTime? LastCheckedAt { get; set; }

    public bool IsActive { get; set; } = true;

    public DateTime CreatedAt { get; set; }

    public DateTime UpdatedAt { get; set; }

    // V2 预留字段 - 用户交互统计（当前不使用，V2 启用）
    /// <summary>
    /// 被用户保存的次数 - V2 功能
    /// </summary>
    public int SavedCount { get; set; } = 0;

    /// <summary>
    /// 被用户查看的次数 - V2 功能
    /// </summary>
    public int ViewCount { get; set; } = 0;
}

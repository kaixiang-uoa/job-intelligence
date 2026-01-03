namespace JobIntel.Core.DTOs;

/// <summary>
/// Internal paginated result from repository layer
/// </summary>
/// <typeparam name="T">Type of entity</typeparam>
public class PaginatedResult<T>
{
    /// <summary>
    /// List of items for current page
    /// </summary>
    public List<T> Items { get; set; } = new();

    /// <summary>
    /// Total number of items across all pages
    /// </summary>
    public int TotalCount { get; set; }

    /// <summary>
    /// Current page number (1-based)
    /// </summary>
    public int Page { get; set; }

    /// <summary>
    /// Number of items per page
    /// </summary>
    public int PageSize { get; set; }

    /// <summary>
    /// Total number of pages
    /// </summary>
    public int TotalPages => (int)Math.Ceiling((double)TotalCount / PageSize);
}

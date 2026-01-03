namespace JobIntel.Core.DTOs.Responses;

/// <summary>
/// Generic paginated response wrapper
/// </summary>
/// <typeparam name="T">Type of data items</typeparam>
public class PaginatedResponse<T>
{
    /// <summary>
    /// List of data items for current page
    /// </summary>
    public List<T> Data { get; set; } = new();

    /// <summary>
    /// Pagination metadata
    /// </summary>
    public PaginationMeta Pagination { get; set; } = null!;
}

/// <summary>
/// Pagination metadata
/// </summary>
public class PaginationMeta
{
    /// <summary>
    /// Current page number (1-based)
    /// </summary>
    public int Page { get; set; }

    /// <summary>
    /// Number of items per page
    /// </summary>
    public int PageSize { get; set; }

    /// <summary>
    /// Total number of items across all pages
    /// </summary>
    public int TotalItems { get; set; }

    /// <summary>
    /// Total number of pages
    /// </summary>
    public int TotalPages { get; set; }

    /// <summary>
    /// Whether there is a next page
    /// </summary>
    public bool HasNextPage => Page < TotalPages;

    /// <summary>
    /// Whether there is a previous page
    /// </summary>
    public bool HasPreviousPage => Page > 1;
}

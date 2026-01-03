using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using JobIntel.Core.DTOs;
using JobIntel.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace JobIntel.Ingest.Services;

/// <summary>
/// HTTP client for communicating with the Python Scrape API
/// Implementation follows Technical Design Document Section 6.2.3
/// </summary>
public class ScrapeApiClient : IScrapeApiClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ScrapeApiClient> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public ScrapeApiClient(HttpClient httpClient, ILogger<ScrapeApiClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
        };
    }

    /// <summary>
    /// Fetch jobs from the Python Scrape API
    /// </summary>
    public async Task<List<RawJobData>> FetchJobsAsync(
        string source,
        string[] keywords,
        string? location = null,
        int maxResults = 100,
        CancellationToken cancellationToken = default)
    {
        try
        {
            _logger.LogInformation(
                "Fetching jobs from source: {Source}, keywords: {Keywords}, location: {Location}",
                source, string.Join(", ", keywords), location ?? "Any");

            // Build request payload - Python API expects single keywords string, not array
            var request = new ScrapeRequest
            {
                Keywords = string.Join(" ", keywords), // Join keywords into single string
                Location = location ?? (source.ToLower() == "indeed" ? "Australia" : "All Australia"),
                MaxResults = maxResults
            };

            var json = JsonSerializer.Serialize(request, _jsonOptions);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            // Call platform-specific endpoint: /scrape/seek or /scrape/indeed
            var endpoint = $"/scrape/{source.ToLower()}";
            var response = await _httpClient.PostAsync(endpoint, content, cancellationToken);

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync(cancellationToken);
                _logger.LogError(
                    "Scrape API returned error status {StatusCode}: {Error}",
                    response.StatusCode, errorContent);
                throw new HttpRequestException(
                    $"Scrape API failed with status {response.StatusCode}: {errorContent}");
            }

            var responseJson = await response.Content.ReadAsStringAsync(cancellationToken);
            var scrapeResponse = JsonSerializer.Deserialize<ScrapeResponse>(responseJson, _jsonOptions);

            if (scrapeResponse?.Jobs == null)
            {
                _logger.LogWarning("Scrape API returned null or invalid response");
                return new List<RawJobData>();
            }

            _logger.LogInformation(
                "Successfully fetched {Count} jobs from {Source}",
                scrapeResponse.Jobs.Count, source);

            return scrapeResponse.Jobs;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to fetch jobs from source: {Source}", source);
            throw;
        }
    }

    /// <summary>
    /// Request model for the Scrape API
    /// Matches Python's ScrapeRequest model
    /// </summary>
    private class ScrapeRequest
    {
        [JsonPropertyName("keywords")]
        public string Keywords { get; set; } = string.Empty;

        [JsonPropertyName("location")]
        public string? Location { get; set; }

        [JsonPropertyName("max_results")]
        public int MaxResults { get; set; } = 100;
    }

    /// <summary>
    /// Response model from the Scrape API
    /// Matches Python's ScrapeResponse model
    /// </summary>
    private class ScrapeResponse
    {
        [JsonPropertyName("platform")]
        public string Platform { get; set; } = string.Empty;

        [JsonPropertyName("jobs")]
        public List<RawJobData> Jobs { get; set; } = new();

        [JsonPropertyName("count")]
        public int Count { get; set; }

        [JsonPropertyName("scraped_at")]
        public DateTime ScrapedAt { get; set; }
    }
}

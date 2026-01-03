using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using JobIntel.Core.Entities;
using JobIntel.Core.Interfaces;

namespace JobIntel.Ingest.Services;

/// <summary>
/// Service for generating fingerprints and content hashes for job deduplication
/// Implementation follows Technical Design Document Section 5.3
/// </summary>
public class DeduplicationService : IDeduplicationService
{
    /// <summary>
    /// Generate a unique fingerprint for a job posting
    /// Fingerprint = SHA256(source:source_id:normalized_title:normalized_company:state:suburb)
    /// </summary>
    public string GenerateFingerprint(JobPosting job)
    {
        var components = new[]
        {
            job.Source.ToLowerInvariant(),
            job.SourceId,
            NormalizeString(job.Title),
            NormalizeString(job.Company),
            job.LocationState?.ToUpperInvariant() ?? string.Empty,
            job.LocationSuburb?.ToLowerInvariant() ?? string.Empty
        };

        var combined = string.Join(":", components);
        return ComputeSHA256Hash(combined);
    }

    /// <summary>
    /// Generate a content hash to detect changes in job description
    /// Content Hash = SHA256(normalized_description + "|" + normalized_requirements)
    /// </summary>
    public string GenerateContentHash(string description, string? requirements)
    {
        var normalized = NormalizeString(description) + "|" + NormalizeString(requirements ?? string.Empty);
        return ComputeSHA256Hash(normalized);
    }

    /// <summary>
    /// Normalize a string for consistent hashing
    /// - Convert to lowercase
    /// - Remove special characters (keep only alphanumeric and spaces)
    /// - Trim and collapse multiple spaces
    /// </summary>
    public string NormalizeString(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return string.Empty;

        // Convert to lowercase
        var normalized = input.ToLowerInvariant();

        // Remove special characters, keep only alphanumeric and spaces
        normalized = Regex.Replace(normalized, @"[^a-z0-9\s]", string.Empty);

        // Collapse multiple spaces to single space
        normalized = Regex.Replace(normalized, @"\s+", " ");

        // Trim
        return normalized.Trim();
    }

    /// <summary>
    /// Compute SHA256 hash of a string
    /// </summary>
    private static string ComputeSHA256Hash(string input)
    {
        var bytes = Encoding.UTF8.GetBytes(input);
        var hashBytes = SHA256.HashData(bytes);
        return Convert.ToHexString(hashBytes).ToLowerInvariant();
    }
}

using JobIntel.Core.Entities;

namespace JobIntel.Core.Interfaces;

/// <summary>
/// Service for generating fingerprints and content hashes for deduplication
/// </summary>
public interface IDeduplicationService
{
    /// <summary>
    /// Generate a unique fingerprint for a job posting
    /// </summary>
    /// <param name="job">Job posting entity</param>
    /// <returns>SHA256 hash fingerprint</returns>
    string GenerateFingerprint(JobPosting job);

    /// <summary>
    /// Generate a content hash to detect changes in job description
    /// </summary>
    /// <param name="description">Job description</param>
    /// <param name="requirements">Job requirements</param>
    /// <returns>SHA256 content hash</returns>
    string GenerateContentHash(string description, string? requirements);

    /// <summary>
    /// Normalize a string for consistent hashing
    /// </summary>
    /// <param name="input">Input string</param>
    /// <returns>Normalized string</returns>
    string NormalizeString(string input);
}

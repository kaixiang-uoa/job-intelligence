using JobIntel.Core.DTOs.Responses;
using JobIntel.Core.Entities;
using System.Text.Json;

namespace JobIntel.Core.Extensions;

/// <summary>
/// Extension methods for JobPosting entity to DTO mapping
/// </summary>
public static class JobPostingExtensions
{
    /// <summary>
    /// Convert JobPosting entity to JobDto
    /// </summary>
    public static JobDto ToDto(this JobPosting job)
    {
        return new JobDto
        {
            Id = job.Id,
            Title = job.Title,
            Company = job.Company,
            Location = new LocationDto
            {
                State = job.LocationState,
                Suburb = job.LocationSuburb
            },
            Trade = job.Trade,
            EmploymentType = job.EmploymentType,
            PayRange = job.PayRangeMin.HasValue || job.PayRangeMax.HasValue
                ? new PayRangeDto
                {
                    Min = job.PayRangeMin,
                    Max = job.PayRangeMax,
                    Currency = "AUD",
                    Unit = "hour"  // Default, can be enhanced later
                }
                : null,
            Description = job.Description,
            JobUrl = job.JobUrl,
            Tags = ParseTags(job.Tags),
            PostedAt = job.PostedAt,
            Source = new JobSourceDto
            {
                Name = job.Source,
                Url = job.JobUrl
            }
            // V2 fields (commented out for V1):
            // IsSaved = false,  // Would check against current user
            // HasAlert = false  // Would check against current user
        };
    }

    /// <summary>
    /// Parse tags string (stored as JSON array) to List<string>
    /// </summary>
    private static List<string> ParseTags(string? tagsJson)
    {
        if (string.IsNullOrWhiteSpace(tagsJson))
        {
            return new List<string>();
        }

        try
        {
            var tags = JsonSerializer.Deserialize<List<string>>(tagsJson);
            return tags ?? new List<string>();
        }
        catch
        {
            // If JSON parsing fails, treat as comma-separated string
            return tagsJson.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                .ToList();
        }
    }
}

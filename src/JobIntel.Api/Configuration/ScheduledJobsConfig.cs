using Hangfire;
using JobIntel.Core.Interfaces;

namespace JobIntel.Api.Configuration;

/// <summary>
/// Configuration for Hangfire scheduled jobs
/// Sets up recurring jobs for automatic data ingestion
/// </summary>
public static class ScheduledJobsConfig
{
    /// <summary>
    /// Configure all recurring jobs for scheduled data ingestion
    /// </summary>
    public static void ConfigureRecurringJobs()
    {
        // Define trade types to monitor (13 main trades)
        var trades = new[]
        {
            "plumber",
            "electrician",
            "carpenter",
            "bricklayer",
            "tiler",
            "painter",
            "roofer",
            "plasterer",
            "glazier",
            "landscaper",
            "concreter",
            "drainer",
            "gasfitter"
        };

        // Define major Australian cities to monitor
        var cities = new[]
        {
            "Sydney",
            "Melbourne",
            "Brisbane",
            "Adelaide",
            "Perth"
        };

        // Create recurring jobs for each trade × city combination
        foreach (var trade in trades)
        {
            foreach (var city in cities)
            {
                var jobId = $"fetch-{trade}-{city}";

                RecurringJob.AddOrUpdate<IScheduledIngestService>(
                    jobId,
                    service => service.FetchAndSaveAsync(trade, city, 50, CancellationToken.None),
                    "0 */6 * * *",  // Run every 6 hours (at minute 0)
                    new RecurringJobOptions
                    {
                        TimeZone = TimeZoneInfo.FindSystemTimeZoneById("AUS Eastern Standard Time")
                    });
            }
        }

        // Log configuration summary
        var totalJobs = trades.Length * cities.Length;
        Console.WriteLine($"✅ Configured {totalJobs} recurring jobs ({trades.Length} trades × {cities.Length} cities)");
        Console.WriteLine($"   Frequency: Every 6 hours");
        Console.WriteLine($"   Time zone: AUS Eastern Standard Time");
        Console.WriteLine($"   View dashboard at: /hangfire");
    }

    /// <summary>
    /// Remove all scheduled jobs (for cleanup/testing)
    /// </summary>
    public static void RemoveAllRecurringJobs()
    {
        var trades = new[]
        {
            "plumber", "electrician", "carpenter", "bricklayer",
            "tiler", "painter", "roofer", "plasterer",
            "glazier", "landscaper", "concreter", "drainer", "gasfitter"
        };

        var cities = new[] { "Sydney", "Melbourne", "Brisbane", "Adelaide", "Perth" };

        foreach (var trade in trades)
        {
            foreach (var city in cities)
            {
                var jobId = $"fetch-{trade}-{city}";
                RecurringJob.RemoveIfExists(jobId);
            }
        }

        Console.WriteLine("✅ Removed all recurring jobs");
    }
}

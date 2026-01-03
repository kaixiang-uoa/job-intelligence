using JobIntel.Core.DTOs.Responses;
using JobIntel.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace JobIntel.Api.Controllers;

/// <summary>
/// Analytics and statistics API endpoints
/// Provides job market insights and trends
/// </summary>
public class AnalyticsController : BaseApiController
{
    private readonly IJobRepository _jobRepository;
    private readonly ILogger<AnalyticsController> _logger;

    public AnalyticsController(
        IJobRepository jobRepository,
        ILogger<AnalyticsController> logger)
    {
        _jobRepository = jobRepository;
        _logger = logger;
    }

    /// <summary>
    /// Get overall job market statistics
    /// </summary>
    /// <param name="since">Optional: only include jobs scraped since this date</param>
    /// <param name="trade">Optional: filter by specific trade</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Statistics including counts by trade, state, and pay rates</returns>
    /// <response code="200">Returns statistics</response>
    [HttpGet("stats")]
    [ProducesResponseType(typeof(StatsDto), StatusCodes.Status200OK)]
    public async Task<ActionResult<StatsDto>> GetStats(
        [FromQuery] DateTime? since,
        [FromQuery] string? trade,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Getting statistics: Since={Since}, Trade={Trade}", since, trade);

        // Get all statistics in parallel for better performance
        var totalJobsTask = _jobRepository.GetCountAsync(cancellationToken);
        var activeJobsTask = _jobRepository.GetTotalActiveJobsAsync(cancellationToken);
        var jobsAddedTodayTask = _jobRepository.GetJobsAddedTodayAsync(cancellationToken);
        var byTradeTask = _jobRepository.GetCountByTradeAsync(since, cancellationToken);
        var byStateTask = _jobRepository.GetCountByStateAsync(since, cancellationToken);

        await Task.WhenAll(
            totalJobsTask,
            activeJobsTask,
            jobsAddedTodayTask,
            byTradeTask,
            byStateTask);

        var stats = new StatsDto
        {
            TotalJobs = await totalJobsTask,
            ActiveJobs = await activeJobsTask,
            JobsAddedToday = await jobsAddedTodayTask,
            ByTrade = await byTradeTask,
            ByState = await byStateTask,
            AvgPayRate = null  // TODO: Implement in future if needed
        };

        // If trade filter is specified, filter the ByState results
        // This would require a more complex query, leaving for future enhancement

        return Ok(stats);
    }

    /// <summary>
    /// Get job count breakdown by trade
    /// </summary>
    /// <param name="since">Optional: only include jobs scraped since this date</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Dictionary of trade names and counts</returns>
    /// <response code="200">Returns trade statistics</response>
    [HttpGet("by-trade")]
    [ProducesResponseType(typeof(Dictionary<string, int>), StatusCodes.Status200OK)]
    public async Task<ActionResult<Dictionary<string, int>>> GetByTrade(
        [FromQuery] DateTime? since,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Getting job count by trade: Since={Since}", since);

        var result = await _jobRepository.GetCountByTradeAsync(since, cancellationToken);

        return Ok(result);
    }

    /// <summary>
    /// Get job count breakdown by state
    /// </summary>
    /// <param name="since">Optional: only include jobs scraped since this date</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Dictionary of state codes and counts</returns>
    /// <response code="200">Returns state statistics</response>
    [HttpGet("by-state")]
    [ProducesResponseType(typeof(Dictionary<string, int>), StatusCodes.Status200OK)]
    public async Task<ActionResult<Dictionary<string, int>>> GetByState(
        [FromQuery] DateTime? since,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Getting job count by state: Since={Since}", since);

        var result = await _jobRepository.GetCountByStateAsync(since, cancellationToken);

        return Ok(result);
    }
}

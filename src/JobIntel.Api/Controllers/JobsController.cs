using JobIntel.Core.DTOs;
using JobIntel.Core.DTOs.Requests;
using JobIntel.Core.DTOs.Responses;
using JobIntel.Core.Extensions;
using JobIntel.Core.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace JobIntel.Api.Controllers;

/// <summary>
/// Job listings API endpoints
/// Provides search, filtering, and job details
/// </summary>
public class JobsController : BaseApiController
{
    private readonly IJobRepository _jobRepository;
    private readonly ILogger<JobsController> _logger;

    public JobsController(
        IJobRepository jobRepository,
        ILogger<JobsController> logger)
    {
        _jobRepository = jobRepository;
        _logger = logger;
    }

    /// <summary>
    /// Search and filter jobs with pagination
    /// </summary>
    /// <param name="request">Search criteria and pagination parameters</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Paginated list of jobs</returns>
    /// <response code="200">Returns paginated job listings</response>
    /// <response code="400">Invalid request parameters</response>
    [HttpGet]
    [ProducesResponseType(typeof(PaginatedResponse<JobDto>), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<PaginatedResponse<JobDto>>> SearchJobs(
        [FromQuery] JobSearchRequest request,
        CancellationToken cancellationToken)
    {
        // Validate request
        if (!ModelState.IsValid)
        {
            return BadRequest(ModelState);
        }

        // Map request to criteria
        var criteria = new JobSearchCriteria
        {
            Trade = request.Trade,
            State = request.State,
            Suburb = request.Suburb,
            PostedAfter = request.PostedAfter,
            PayMin = request.PayMin,
            PayMax = request.PayMax,
            EmploymentType = request.EmploymentType
        };

        _logger.LogInformation(
            "Searching jobs: Trade={Trade}, State={State}, Page={Page}",
            request.Trade, request.State, request.Page);

        // Execute search
        var result = await _jobRepository.SearchAsync(
            criteria,
            request.Page,
            request.PageSize,
            request.SortBy,
            cancellationToken);

        // Map entities to DTOs
        var jobDtos = result.Items.Select(j => j.ToDto()).ToList();

        // Build response
        var response = new PaginatedResponse<JobDto>
        {
            Data = jobDtos,
            Pagination = new PaginationMeta
            {
                Page = result.Page,
                PageSize = result.PageSize,
                TotalItems = result.TotalCount,
                TotalPages = result.TotalPages
            }
        };

        return Ok(response);
    }

    /// <summary>
    /// Get job details by ID
    /// </summary>
    /// <param name="id">Job ID</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Job details</returns>
    /// <response code="200">Returns job details</response>
    /// <response code="404">Job not found</response>
    [HttpGet("{id}")]
    [ProducesResponseType(typeof(JobDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<JobDto>> GetJobById(
        int id,
        CancellationToken cancellationToken)
    {
        _logger.LogInformation("Getting job by ID: {JobId}", id);

        var job = await _jobRepository.GetByIdAsync(id, cancellationToken);

        if (job == null)
        {
            _logger.LogWarning("Job not found: {JobId}", id);
            return NotFound(new { error = $"Job with ID {id} not found" });
        }

        var jobDto = job.ToDto();

        // V2: Increment view count here
        // await _jobRepository.IncrementViewCountAsync(id, cancellationToken);

        return Ok(jobDto);
    }
}

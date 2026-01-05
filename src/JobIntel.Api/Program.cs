using Hangfire;
using Hangfire.Dashboard;
using Hangfire.PostgreSql;
using JobIntel.Api.Configuration;
using JobIntel.Core.Interfaces;
using JobIntel.Ingest.Jobs;
using JobIntel.Ingest.Services;
using JobIntel.Infrastructure.Data;
using JobIntel.Infrastructure.Repositories;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using System.Reflection;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Job Intelligence API",
        Version = "v1.0",
        Description = "RESTful API for job market intelligence and analytics (V1 - MVP)",
        Contact = new OpenApiContact
        {
            Name = "Job Intelligence Platform",
            Url = new Uri("https://github.com/yourusername/job-intelligence")
        }
    });

    // Include XML comments for better Swagger documentation
    var xmlFile = $"{Assembly.GetExecutingAssembly().GetName().Name}.xml";
    var xmlPath = Path.Combine(AppContext.BaseDirectory, xmlFile);
    c.IncludeXmlComments(xmlPath);

    // Add examples and schemas
    c.EnableAnnotations();
});

// Database Configuration
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Host=localhost;Port=5432;Database=jobintel;Username=admin;Password=dev123";

builder.Services.AddDbContext<JobIntelDbContext>(options =>
    options.UseNpgsql(connectionString));

// Hangfire Configuration
builder.Services.AddHangfire(config =>
    config.UsePostgreSqlStorage(connectionString));

builder.Services.AddHangfireServer(options =>
{
    options.ServerName = "JobIntel-Server";
    options.WorkerCount = 5;
});

// HTTP Client for Scrape API
var scrapeApiBaseUrl = builder.Configuration["ScrapeApi:BaseUrl"] ?? "http://localhost:8000";
builder.Services.AddHttpClient<IScrapeApiClient, ScrapeApiClient>(client =>
{
    client.BaseAddress = new Uri(scrapeApiBaseUrl);
    client.Timeout = TimeSpan.FromMinutes(5);
});

// Repository Services
builder.Services.AddScoped<IJobRepository, JobRepository>();
builder.Services.AddScoped<IIngestRunRepository, IngestRunRepository>();

// Domain Services
builder.Services.AddScoped<IDeduplicationService, DeduplicationService>();
builder.Services.AddScoped<IIngestionPipeline, IngestionPipeline>();
builder.Services.AddScoped<IScheduledIngestService, ScheduledIngestService>();

// Background Jobs
builder.Services.AddScoped<ScrapeJob>();

// Logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();

// CORS (for development)
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Run database migrations on startup
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<JobIntelDbContext>();
    try
    {
        app.Logger.LogInformation("Applying database migrations...");
        await dbContext.Database.MigrateAsync();
        app.Logger.LogInformation("Database migrations applied successfully");
    }
    catch (Exception ex)
    {
        app.Logger.LogError(ex, "An error occurred while migrating the database");
        throw;
    }
}

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Job Intelligence API v1");
        c.RoutePrefix = "swagger";
    });
}

app.UseCors("AllowAll");
app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

// Hangfire Dashboard
app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    DashboardTitle = "Job Intelligence - Background Jobs",
    Authorization = new[] { new HangfireAuthorizationFilter() }
});

// Configure Recurring Jobs
ScheduledJobsConfig.ConfigureRecurringJobs();

// Health Check Endpoint
app.MapGet("/api/health", async (JobIntelDbContext dbContext) =>
{
    try
    {
        await dbContext.Database.CanConnectAsync();
        var jobCount = await dbContext.JobPostings.CountAsync();

        return Results.Ok(new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow,
            database = "connected",
            jobCount
        });
    }
    catch (Exception ex)
    {
        return Results.Problem(
            detail: ex.Message,
            statusCode: 503,
            title: "Health check failed");
    }
})
.WithName("HealthCheck")
.WithOpenApi();

// Sample endpoint to trigger manual scrape
app.MapPost("/api/admin/scrape", async (
    ScrapeRequest request,
    IBackgroundJobClient backgroundJobs) =>
{
    var jobId = backgroundJobs.Enqueue<ScrapeJob>(job =>
        job.ExecuteAsync(
            request.Source,
            request.Keywords,
            request.Location,
            request.MaxResults));

    return Results.Accepted($"/hangfire/jobs/details/{jobId}", new
    {
        jobId,
        status = "queued",
        message = "Scraping job has been queued"
    });
})
.WithName("TriggerScrape")
.WithOpenApi();

app.Run();

// Hangfire Authorization Filter (Allow all in development)
public class HangfireAuthorizationFilter : IDashboardAuthorizationFilter
{
    public bool Authorize(DashboardContext context)
    {
        // In development, allow all access
        // In production, implement proper authentication
        return true;
    }
}

// Request model for manual scrape trigger
public record ScrapeRequest(
    string Source,
    string[] Keywords,
    string? Location = null,
    int MaxResults = 100);

using JobIntel.Core.Entities;
using Microsoft.EntityFrameworkCore;

namespace JobIntel.Infrastructure.Data;

/// <summary>
/// Entity Framework Core DbContext for Job Intelligence Platform
/// </summary>
public class JobIntelDbContext : DbContext
{
    public JobIntelDbContext(DbContextOptions<JobIntelDbContext> options) : base(options)
    {
    }

    public DbSet<JobPosting> JobPostings => Set<JobPosting>();

    public DbSet<IngestRun> IngestRuns => Set<IngestRun>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        modelBuilder.ApplyConfigurationsFromAssembly(typeof(JobIntelDbContext).Assembly);
    }
}

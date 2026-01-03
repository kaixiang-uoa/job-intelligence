using JobIntel.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace JobIntel.Infrastructure.Data.Configurations;

/// <summary>
/// Entity configuration for JobPosting
/// Follows Technical Design Document Section 5.2.1
/// </summary>
public class JobPostingConfiguration : IEntityTypeConfiguration<JobPosting>
{
    public void Configure(EntityTypeBuilder<JobPosting> builder)
    {
        builder.ToTable("job_postings");

        // Primary Key
        builder.HasKey(x => x.Id);
        builder.Property(x => x.Id)
            .HasColumnName("id")
            .ValueGeneratedOnAdd();

        // Required Fields
        builder.Property(x => x.Source)
            .HasColumnName("source")
            .HasMaxLength(50)
            .IsRequired();

        builder.Property(x => x.SourceId)
            .HasColumnName("source_id")
            .HasMaxLength(255)
            .IsRequired();

        builder.Property(x => x.Title)
            .HasColumnName("title")
            .HasMaxLength(500)
            .IsRequired();

        builder.Property(x => x.Company)
            .HasColumnName("company")
            .HasMaxLength(255)
            .IsRequired();

        builder.Property(x => x.Description)
            .HasColumnName("description")
            .HasColumnType("text")
            .IsRequired();

        // Optional Fields
        builder.Property(x => x.LocationState)
            .HasColumnName("location_state")
            .HasMaxLength(50);

        builder.Property(x => x.LocationSuburb)
            .HasColumnName("location_suburb")
            .HasMaxLength(100);

        builder.Property(x => x.Trade)
            .HasColumnName("trade")
            .HasMaxLength(50);

        builder.Property(x => x.EmploymentType)
            .HasColumnName("employment_type")
            .HasMaxLength(50);

        builder.Property(x => x.PayRangeMin)
            .HasColumnName("pay_range_min")
            .HasColumnType("decimal(10,2)");

        builder.Property(x => x.PayRangeMax)
            .HasColumnName("pay_range_max")
            .HasColumnType("decimal(10,2)");

        builder.Property(x => x.JobUrl)
            .HasColumnName("job_url")
            .HasMaxLength(1000);

        builder.Property(x => x.Keywords)
            .HasColumnName("keywords")
            .HasColumnType("jsonb");

        builder.Property(x => x.Tags)
            .HasColumnName("tags")
            .HasColumnType("jsonb");

        // Deduplication Fields
        builder.Property(x => x.Fingerprint)
            .HasColumnName("fingerprint")
            .HasMaxLength(255)
            .IsRequired();

        builder.Property(x => x.ContentHash)
            .HasColumnName("content_hash")
            .HasMaxLength(64)
            .IsRequired();

        // Timestamps
        builder.Property(x => x.PostedAt)
            .HasColumnName("posted_at");

        builder.Property(x => x.ScrapedAt)
            .HasColumnName("scraped_at")
            .IsRequired();

        builder.Property(x => x.LastCheckedAt)
            .HasColumnName("last_checked_at");

        builder.Property(x => x.IsActive)
            .HasColumnName("is_active")
            .IsRequired()
            .HasDefaultValue(true);

        builder.Property(x => x.CreatedAt)
            .HasColumnName("created_at")
            .IsRequired();

        builder.Property(x => x.UpdatedAt)
            .HasColumnName("updated_at")
            .IsRequired();

        // V2 预留字段 - 用户交互统计
        builder.Property(x => x.SavedCount)
            .HasColumnName("saved_count")
            .HasDefaultValue(0)
            .IsRequired();

        builder.Property(x => x.ViewCount)
            .HasColumnName("view_count")
            .HasDefaultValue(0)
            .IsRequired();

        // Indexes (per Technical Design Document Section 5.2.1)
        builder.HasIndex(x => x.Source)
            .HasDatabaseName("idx_job_postings_source");

        builder.HasIndex(x => new { x.Trade, x.LocationState })
            .HasDatabaseName("idx_job_postings_trade_state");

        builder.HasIndex(x => x.PostedAt)
            .HasDatabaseName("idx_job_postings_posted_at");

        builder.HasIndex(x => x.IsActive)
            .HasDatabaseName("idx_job_postings_active")
            .HasFilter("is_active = true");

        builder.HasIndex(x => x.Fingerprint)
            .IsUnique()
            .HasDatabaseName("idx_job_postings_fingerprint");

        builder.HasIndex(x => x.ContentHash)
            .HasDatabaseName("idx_job_postings_content_hash");

        // Unique Constraint
        builder.HasIndex(x => new { x.Source, x.SourceId })
            .IsUnique()
            .HasDatabaseName("uq_source_external_id");

        // JSONB Indexes (GIN indexes for efficient JSONB queries)
        builder.HasIndex(x => x.Tags)
            .HasDatabaseName("idx_job_postings_tags")
            .HasMethod("gin");

        builder.HasIndex(x => x.Keywords)
            .HasDatabaseName("idx_job_postings_keywords")
            .HasMethod("gin");
    }
}

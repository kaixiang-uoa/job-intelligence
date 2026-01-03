using JobIntel.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace JobIntel.Infrastructure.Data.Configurations;

/// <summary>
/// Entity configuration for IngestRun
/// Follows Technical Design Document Section 5.2.2
/// </summary>
public class IngestRunConfiguration : IEntityTypeConfiguration<IngestRun>
{
    public void Configure(EntityTypeBuilder<IngestRun> builder)
    {
        builder.ToTable("ingest_runs");

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

        builder.Property(x => x.Keywords)
            .HasColumnName("keywords")
            .HasColumnType("text");

        builder.Property(x => x.Location)
            .HasColumnName("location")
            .HasMaxLength(100);

        builder.Property(x => x.StartedAt)
            .HasColumnName("started_at")
            .IsRequired();

        builder.Property(x => x.CompletedAt)
            .HasColumnName("completed_at");

        builder.Property(x => x.Status)
            .HasColumnName("status")
            .HasMaxLength(20)
            .HasConversion<string>()
            .IsRequired();

        // Statistics
        builder.Property(x => x.JobsFound)
            .HasColumnName("jobs_found")
            .HasDefaultValue(0);

        builder.Property(x => x.JobsNew)
            .HasColumnName("jobs_new")
            .HasDefaultValue(0);

        builder.Property(x => x.JobsUpdated)
            .HasColumnName("jobs_updated")
            .HasDefaultValue(0);

        builder.Property(x => x.JobsDeduped)
            .HasColumnName("jobs_deduped")
            .HasDefaultValue(0);

        // Error Tracking
        builder.Property(x => x.ErrorMessage)
            .HasColumnName("error_message")
            .HasColumnType("text");

        builder.Property(x => x.ErrorStackTrace)
            .HasColumnName("error_stack_trace")
            .HasColumnType("text");

        builder.Property(x => x.Metadata)
            .HasColumnName("metadata")
            .HasColumnType("text");

        // Indexes
        builder.HasIndex(x => new { x.Source, x.StartedAt })
            .HasDatabaseName("idx_ingest_runs_source_started");

        builder.HasIndex(x => x.Status)
            .HasDatabaseName("idx_ingest_runs_status");
    }
}

using System;
using Microsoft.EntityFrameworkCore.Migrations;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace JobIntel.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddV2ReservedFields : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "ingest_runs",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    source = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    keywords = table.Column<string>(type: "text", nullable: true),
                    location = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: true),
                    started_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    completed_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    status = table.Column<string>(type: "character varying(20)", maxLength: 20, nullable: false),
                    jobs_found = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    jobs_new = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    jobs_updated = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    jobs_deduped = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    error_message = table.Column<string>(type: "text", nullable: true),
                    error_stack_trace = table.Column<string>(type: "text", nullable: true),
                    metadata = table.Column<string>(type: "text", nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_ingest_runs", x => x.id);
                });

            migrationBuilder.CreateTable(
                name: "job_postings",
                columns: table => new
                {
                    id = table.Column<int>(type: "integer", nullable: false)
                        .Annotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn),
                    source = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: false),
                    source_id = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    title = table.Column<string>(type: "character varying(500)", maxLength: 500, nullable: false),
                    company = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    location_state = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: true),
                    location_suburb = table.Column<string>(type: "character varying(100)", maxLength: 100, nullable: true),
                    trade = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: true),
                    employment_type = table.Column<string>(type: "character varying(50)", maxLength: 50, nullable: true),
                    pay_range_min = table.Column<decimal>(type: "numeric(10,2)", nullable: true),
                    pay_range_max = table.Column<decimal>(type: "numeric(10,2)", nullable: true),
                    description = table.Column<string>(type: "text", nullable: false),
                    requirements = table.Column<string>(type: "text", nullable: true),
                    tags = table.Column<string>(type: "text", nullable: true),
                    fingerprint = table.Column<string>(type: "character varying(255)", maxLength: 255, nullable: false),
                    content_hash = table.Column<string>(type: "character varying(64)", maxLength: 64, nullable: false),
                    posted_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    scraped_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    last_checked_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: true),
                    is_active = table.Column<bool>(type: "boolean", nullable: false, defaultValue: true),
                    created_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    updated_at = table.Column<DateTime>(type: "timestamp with time zone", nullable: false),
                    saved_count = table.Column<int>(type: "integer", nullable: false, defaultValue: 0),
                    view_count = table.Column<int>(type: "integer", nullable: false, defaultValue: 0)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_job_postings", x => x.id);
                });

            migrationBuilder.CreateIndex(
                name: "idx_ingest_runs_source_started",
                table: "ingest_runs",
                columns: new[] { "source", "started_at" });

            migrationBuilder.CreateIndex(
                name: "idx_ingest_runs_status",
                table: "ingest_runs",
                column: "status");

            migrationBuilder.CreateIndex(
                name: "idx_job_postings_active",
                table: "job_postings",
                column: "is_active",
                filter: "is_active = true");

            migrationBuilder.CreateIndex(
                name: "idx_job_postings_content_hash",
                table: "job_postings",
                column: "content_hash");

            migrationBuilder.CreateIndex(
                name: "idx_job_postings_fingerprint",
                table: "job_postings",
                column: "fingerprint",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "idx_job_postings_posted_at",
                table: "job_postings",
                column: "posted_at");

            migrationBuilder.CreateIndex(
                name: "idx_job_postings_source",
                table: "job_postings",
                column: "source");

            migrationBuilder.CreateIndex(
                name: "idx_job_postings_trade_state",
                table: "job_postings",
                columns: new[] { "trade", "location_state" });

            migrationBuilder.CreateIndex(
                name: "uq_source_external_id",
                table: "job_postings",
                columns: new[] { "source", "source_id" },
                unique: true);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "ingest_runs");

            migrationBuilder.DropTable(
                name: "job_postings");
        }
    }
}

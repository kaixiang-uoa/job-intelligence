using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace JobIntel.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class OptimizeDatabaseSchema : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "requirements",
                table: "job_postings");

            // Change tags from TEXT to JSONB with explicit USING clause
            migrationBuilder.Sql(@"
                ALTER TABLE job_postings
                ALTER COLUMN tags TYPE jsonb
                USING CASE
                    WHEN tags IS NULL THEN NULL
                    WHEN tags = '' THEN NULL
                    ELSE tags::jsonb
                END;
            ");

            migrationBuilder.AddColumn<string>(
                name: "job_url",
                table: "job_postings",
                type: "character varying(1000)",
                maxLength: 1000,
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "keywords",
                table: "job_postings",
                type: "jsonb",
                nullable: true);

            migrationBuilder.CreateIndex(
                name: "idx_job_postings_keywords",
                table: "job_postings",
                column: "keywords")
                .Annotation("Npgsql:IndexMethod", "gin");

            migrationBuilder.CreateIndex(
                name: "idx_job_postings_tags",
                table: "job_postings",
                column: "tags")
                .Annotation("Npgsql:IndexMethod", "gin");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "idx_job_postings_keywords",
                table: "job_postings");

            migrationBuilder.DropIndex(
                name: "idx_job_postings_tags",
                table: "job_postings");

            migrationBuilder.DropColumn(
                name: "job_url",
                table: "job_postings");

            migrationBuilder.DropColumn(
                name: "keywords",
                table: "job_postings");

            migrationBuilder.AlterColumn<string>(
                name: "tags",
                table: "job_postings",
                type: "text",
                nullable: true,
                oldClrType: typeof(string),
                oldType: "jsonb",
                oldNullable: true);

            migrationBuilder.AddColumn<string>(
                name: "requirements",
                table: "job_postings",
                type: "text",
                nullable: true);
        }
    }
}

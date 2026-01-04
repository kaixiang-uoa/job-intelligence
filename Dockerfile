# Build stage
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

# Copy solution and project files
COPY JobIntel.sln .
COPY src/JobIntel.Api/JobIntel.Api.csproj src/JobIntel.Api/
COPY src/JobIntel.Core/JobIntel.Core.csproj src/JobIntel.Core/
COPY src/JobIntel.Infrastructure/JobIntel.Infrastructure.csproj src/JobIntel.Infrastructure/
COPY src/JobIntel.Ingest/JobIntel.Ingest.csproj src/JobIntel.Ingest/

# Restore dependencies
RUN dotnet restore

# Copy all source code
COPY src/ src/

# Build and publish
WORKDIR /src/src/JobIntel.Api
RUN dotnet publish -c Release -o /app/publish

# Runtime stage
FROM mcr.microsoft.com/dotnet/aspnet:8.0
WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy published files
COPY --from=build /app/publish .

# Expose port
EXPOSE 5000

# Run the application
ENTRYPOINT ["dotnet", "JobIntel.Api.dll"]

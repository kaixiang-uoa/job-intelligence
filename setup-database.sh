#!/bin/bash

# Job Intelligence Platform - Database Setup Script
# This script sets up PostgreSQL and creates the database schema

set -e  # Exit on error

echo "========================================="
echo "Job Intelligence Platform - Database Setup"
echo "========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if .NET SDK is installed
if ! command -v dotnet &> /dev/null; then
    echo "❌ Error: .NET SDK is not installed. Please install .NET 8 SDK."
    exit 1
fi

# Step 1: Start PostgreSQL container
echo "📦 Step 1: Starting PostgreSQL container..."
if docker ps -a --format '{{.Names}}' | grep -q '^jobintel-postgres$'; then
    echo "   Container 'jobintel-postgres' already exists."
    if docker ps --format '{{.Names}}' | grep -q '^jobintel-postgres$'; then
        echo "   ✅ Container is already running."
    else
        echo "   Starting existing container..."
        docker start jobintel-postgres
        echo "   ✅ Container started."
    fi
else
    echo "   Creating new PostgreSQL container..."
    docker run -d \
        --name jobintel-postgres \
        -e POSTGRES_DB=jobintel \
        -e POSTGRES_USER=admin \
        -e POSTGRES_PASSWORD=dev123 \
        -p 5432:5432 \
        postgres:16
    echo "   ✅ Container created and started."
fi

# Wait for PostgreSQL to be ready
echo "   Waiting for PostgreSQL to be ready..."
sleep 5

# Test connection
if docker exec jobintel-postgres pg_isready -U admin > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL is ready!"
else
    echo "   ⏳ Waiting a bit more..."
    sleep 5
    if docker exec jobintel-postgres pg_isready -U admin > /dev/null 2>&1; then
        echo "   ✅ PostgreSQL is ready!"
    else
        echo "   ❌ PostgreSQL is not responding. Please check the container logs."
        exit 1
    fi
fi

echo ""

# Step 2: Install EF Core tools if not already installed
echo "🔧 Step 2: Checking EF Core tools..."
if ! dotnet ef --version &> /dev/null; then
    echo "   Installing EF Core tools globally..."
    dotnet tool install --global dotnet-ef
    echo "   ✅ EF Core tools installed."
else
    echo "   ✅ EF Core tools already installed."
fi

echo ""

# Step 3: Build the solution
echo "🏗️  Step 3: Building the solution..."
dotnet build --configuration Release
if [ $? -eq 0 ]; then
    echo "   ✅ Build successful!"
else
    echo "   ❌ Build failed. Please check the errors above."
    exit 1
fi

echo ""

# Step 4: Create database migration
echo "📝 Step 4: Creating database migration..."
cd src/JobIntel.Infrastructure

# Check if migration already exists
if [ -d "Migrations" ]; then
    echo "   ⚠️  Migrations folder already exists."
    read -p "   Do you want to remove existing migrations and create new ones? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   Removing existing migrations..."
        rm -rf Migrations
        dotnet ef migrations add InitialCreate --startup-project ../JobIntel.Api
        echo "   ✅ New migration created!"
    else
        echo "   ℹ️  Using existing migrations."
    fi
else
    dotnet ef migrations add InitialCreate --startup-project ../JobIntel.Api
    echo "   ✅ Migration created!"
fi

echo ""

# Step 5: Apply migration to database
echo "💾 Step 5: Applying migration to database..."
dotnet ef database update --startup-project ../JobIntel.Api
if [ $? -eq 0 ]; then
    echo "   ✅ Database schema created successfully!"
else
    echo "   ❌ Database migration failed. Please check the errors above."
    exit 1
fi

cd ../..

echo ""

# Step 6: Verify database
echo "🔍 Step 6: Verifying database..."
if docker exec jobintel-postgres psql -U admin -d jobintel -c "\dt" | grep -q "job_postings"; then
    echo "   ✅ Table 'job_postings' exists."
else
    echo "   ❌ Table 'job_postings' not found!"
    exit 1
fi

if docker exec jobintel-postgres psql -U admin -d jobintel -c "\dt" | grep -q "ingest_runs"; then
    echo "   ✅ Table 'ingest_runs' exists."
else
    echo "   ❌ Table 'ingest_runs' not found!"
    exit 1
fi

# Count tables
TABLE_COUNT=$(docker exec jobintel-postgres psql -U admin -d jobintel -c "\dt" | grep -c "table")
echo "   ℹ️  Total tables created: $TABLE_COUNT (including Hangfire tables)"

echo ""
echo "========================================="
echo "✅ Database setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Start the API:"
echo "     cd src/JobIntel.Api"
echo "     dotnet run"
echo ""
echo "  2. Access the application:"
echo "     - Swagger UI:        http://localhost:5000/swagger"
echo "     - Health Check:      http://localhost:5000/api/health"
echo "     - Hangfire Dashboard: http://localhost:5000/hangfire"
echo ""
echo "  3. View database:"
echo "     docker exec -it jobintel-postgres psql -U admin -d jobintel"
echo ""
echo "  4. Stop PostgreSQL:"
echo "     docker stop jobintel-postgres"
echo ""
echo "  5. Remove PostgreSQL:"
echo "     docker rm -f jobintel-postgres"
echo ""

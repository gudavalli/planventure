# SQLite to Microsoft SQL Server Migration

## Overview

This document outlines the process of migrating the PlanVenture Account Service from SQLite to Microsoft SQL Server. 
The migration enhances the service's scalability, reliability, and provides better enterprise-level features.

## Why Migrate from SQLite to SQL Server?

1. **Scalability**: SQL Server handles high transaction loads better than SQLite
2. **Concurrency**: Supports multiple concurrent connections and transactions
3. **Security**: Enhanced security features with role-based access control
4. **Backup and Recovery**: More robust data protection options
5. **Advanced Features**: JSON support, stored procedures, triggers, and more
6. **Management Tools**: Better administrative interfaces and monitoring

## Key Benefits

- **Performance**: Better query optimization and execution plans
- **Reliability**: Transaction logging and crash recovery
- **Scalability**: Support for larger databases and more concurrent users
- **Tools**: SQL Server Management Studio and Azure Data Studio

## Summary of Changes

1. **Database Driver Dependencies**
   - Added `pyodbc` and `pymssql` to requirements.txt

2. **Connection String**
   - Updated connection strings in app.py and conftest.py
   - Changed from: `sqlite:///planventure.db`
   - To: `mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/planventure?driver=ODBC+Driver+17+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes`

3. **Model Changes**
   - Updated data types for better SQL Server compatibility
   - Changed `String` to `Unicode` / `NVARCHAR` for text fields
   - Used SQL Server's JSON type for Trip.itinerary

4. **Database Initialization**
   - Created new init_db.py script to handle:
     - Database creation if it doesn't exist
     - Table creation
     - Schema initialization

5. **Database Migration**
   - Created migrate_to_mssql.py to transfer existing data from SQLite to SQL Server
   - Added test_migration.py to validate the data migration process

6. **Performance Optimization**
   - Added optimize_sql_server.py to analyze and improve database performance
   - Configured SQLAlchemy connection pooling settings for SQL Server
   - Added appropriate indexes for common query patterns

7. **Schema Validation**
   - Created validate_schema.py to verify correct table structures and data types
   - Added checks for Unicode support and proper collation settings

8. **Production Security**
   - Added SQL_SERVER_AUTHENTICATION.md with secure authentication setup instructions
   - Configured TLS/SSL encryption for database connections
   - Added documentation for creating least-privilege database users

9. **CI/CD Integration**
   - Created GitHub Actions workflow to test with SQL Server containers
   - Added Docker infrastructure for development and testing

10. **Documentation**
    - Created MSSQL_SETUP.md guide with:
      - Docker SQL Server setup instructions
      - Driver installation
      - Configuration best practices
     - Configuration guidance
     - Management tools

7. **Configuration Templates**
   - Updated .env.example with SQL Server settings

8. **Health Check**
   - Improved the health check endpoint to properly check SQL Server connectivity

## Step-by-Step Migration Guide

### Prerequisites

1. Install the required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

2. Make sure you have the ODBC Driver 17 for SQL Server installed.

### Setting Up the Environment

1. Create a `.env` file based on the `.env.example` template:
   ```powershell
   cp .env.example .env
   ```

2. Edit the `.env` file to set your SQL Server connection details.

### Start SQL Server (Docker)

1. Start the SQL Server container:
   ```powershell
   docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrong@Passw0rd" -p 1433:1433 --name planventure-mssql -d mcr.microsoft.com/mssql/server:2022-latest
   ```

2. Verify the container is running:
   ```powershell
   docker ps
   ```

### Initialize the SQL Server Database

1. Run the database initialization script:
   ```powershell
   python init_db.py
   ```

   This script will:
   - Create the `planventure` database if it doesn't exist
   - Create the `planventure_test` database for testing
   - Initialize all tables according to the SQLAlchemy models

### Migrate Existing Data (Optional)

If you have existing data in SQLite that you want to migrate:

1. Make sure your SQLite database is in the `instance/planventure.db` path.

2. Run the migration script:
   ```powershell
   python migrate_to_mssql.py
   ```

3. The script will:
   - Connect to both SQLite and SQL Server
   - Transfer users and their associated data
   - Transfer trips and maintain relationships
   - Preserve IDs and timestamps

### Verify the Migration

1. Start the API:
   ```powershell
   python app.py
   ```

2. Access the API endpoints to verify data was migrated correctly.

3. You can also connect to SQL Server using SQL Server Management Studio or Azure Data Studio to examine the data.

## Common Issues

1. ODBC Driver Errors
   - Ensure the ODBC Driver 17 for SQL Server is installed
   - On Linux/macOS, verify the driver path

2. Connection Timeouts
   - Check if the SQL Server container is running
   - Verify the port is accessible (1433)

3. Authentication Errors
   - Double-check username and password
   - Ensure SA account is enabled in SQL Server

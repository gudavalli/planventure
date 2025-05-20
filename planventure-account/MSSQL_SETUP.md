# SQL Server Configuration for PlanVenture Account Service

This guide will help you set up Microsoft SQL Server for the PlanVenture Account Service.

## Prerequisites

- Docker (for running SQL Server in a container)
- Python 3.8 or later
- ODBC Driver 17 for SQL Server

## Setting up SQL Server

You have two main options for setting up SQL Server: running it in a Docker container (recommended for development) or using a dedicated SQL Server installation.

### Using Docker (Recommended for Development)

1. Pull the SQL Server Docker image:
   ```powershell
   docker pull mcr.microsoft.com/mssql/server:2022-latest
   ```

2. Start SQL Server container:
   ```powershell
   docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourStrong@Passw0rd" -p 1433:1433 --name planventure-mssql -d mcr.microsoft.com/mssql/server:2022-latest
   ```

3. Verify the container is running:
   ```powershell
   docker ps
   ```

4. To stop the container when you're done:
   ```powershell
   docker stop planventure-mssql
   ```

5. To start the container again later:
   ```powershell
   docker start planventure-mssql
   ```

### Using Azure SQL Database (Recommended for Production)

1. Create an Azure SQL Database instance through the Azure portal
2. Get the connection string from the Azure portal
3. Update your `.env` file with the Azure SQL connection string

### Using a Local SQL Server Installation

If you prefer to use a local SQL Server installation:

1. Download and install SQL Server Express or Developer Edition
2. During setup, choose "SQL Server and Windows Authentication mode"
3. Create a SQL login for the application
4. Update your `.env` file with the local SQL Server credentials

### Installing ODBC Driver

#### Windows
1. Download ODBC Driver 17 from Microsoft's website
2. Run the installer and follow the prompts

#### Linux (Ubuntu)
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
apt-get install -y msodbcsql17
```

#### macOS
```bash
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
brew install msodbcsql17 mssql-tools
```

## Configuring the Application

1. Update your `.env` file with SQL Server connection details:
   ```
   DATABASE_URL=mssql+pyodbc://sa:YourStrong@Passw0rd@localhost:1433/planventure?driver=ODBC+Driver+17+for+SQL+Server
   ```

2. Initialize the database:
   ```bash
   python init_db.py
   ```

## Connection String Format

The connection string format for SQL Server is:
```
mssql+pyodbc://<username>:<password>@<server>:<port>/<database>?driver=ODBC+Driver+17+for+SQL+Server
```

## Schema Modifications for SQL Server

When migrating from SQLite to SQL Server, some schema adjustments have been made:

1. Changed `String` types to `Unicode` (mapped to `NVARCHAR` in SQL Server) for proper UTF-8 support
2. Modified index and constraints to be compatible with SQL Server

## Migrations

If you need to migrate existing data:

1. Run the migration script:
   ```bash
   python migrate_to_mssql.py
   ```

2. The script will:
   - Connect to your SQLite database
   - Extract all data
   - Insert it into your new SQL Server database

## SQL Server Management

To manage your database:
- Use Azure Data Studio (cross-platform UI for SQL Server)
- Use SQL Server Management Studio (Windows only)
- Connect with credentials:
  - Server: localhost,1433
  - Authentication: SQL Login
  - Username: sa
  - Password: YourStrong@Passw0rd (or the password you configured)

## Troubleshooting

If you encounter connection issues:

1. Verify Docker container is running
2. Check if the port 1433 is accessible
3. Ensure ODBC Driver is properly installed
4. Verify SQL Server credentials

For more information on configuring pyodbc with SQLAlchemy, refer to the [SQLAlchemy documentation](https://docs.sqlalchemy.org/en/14/dialects/mssql.html).

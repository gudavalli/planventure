-- SQL Server Setup Script for PlanVenture API
-- This script performs initial setup for SQL Server

-- Enable advanced options
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;

-- Enable contained databases
EXEC sp_configure 'contained database authentication', 1;
RECONFIGURE;

-- MSSQL Configuration Recommendations for Flask/SQLAlchemy Application

-- Set database collation to case-insensitive, accent-sensitive
-- This matches Python's default string comparison behavior
USE [planventure];
ALTER DATABASE [planventure] COLLATE SQL_Latin1_General_CP1_CI_AS;

-- Optional: Setup Case-Sensitive tables when needed
-- CREATE TABLE example_case_sensitive (
--    id INT PRIMARY KEY,
--    value NVARCHAR(100) COLLATE SQL_Latin1_General_CP1_CS_AS
-- );

-- Optimize tempdb (good practice for any SQL Server installation)
USE [master];
ALTER DATABASE [tempdb] MODIFY FILE (NAME = N'tempdev', SIZE = 128MB, FILEGROWTH = 64MB);

-- Create a login for the application if not using SA account
-- CREATE LOGIN [planventure_app] WITH PASSWORD = N'SecurePassword123!';

-- Create a user for the application
-- USE [planventure];
-- CREATE USER [planventure_app] FOR LOGIN [planventure_app];
-- ALTER ROLE [db_owner] ADD MEMBER [planventure_app];

-- Enable snapshot isolation (useful for read operations without blocking)
USE [planventure];
ALTER DATABASE [planventure] SET ALLOW_SNAPSHOT_ISOLATION ON;
ALTER DATABASE [planventure] SET READ_COMMITTED_SNAPSHOT ON;

-- Enable full-text search if needed
-- EXEC sp_fulltext_database 'enable';

-- Optional: Create a read-only user
-- USE [planventure];
-- CREATE USER [planventure_readonly] FOR LOGIN [planventure_readonly];
-- ALTER ROLE [db_datareader] ADD MEMBER [planventure_readonly];

-- Optional: Database performance settings
-- USE [planventure];
-- ALTER DATABASE [planventure] SET AUTO_CREATE_STATISTICS ON;
-- ALTER DATABASE [planventure] SET AUTO_UPDATE_STATISTICS ON;
-- ALTER DATABASE [planventure] SET AUTO_UPDATE_STATISTICS_ASYNC ON;

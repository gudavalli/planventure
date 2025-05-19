# SQL Server Authentication Setup for Production

This document outlines the secure authentication setup for using SQL Server with PlanVenture API in a production environment.

## Overview

For production deployments, it's critical to use secure authentication methods rather than the default SA credentials used in development. This guide covers:

1. Creating dedicated database users with appropriate permissions
2. Configuring connection pooling
3. Setting up Azure AD authentication (if using Azure SQL Database)
4. Using environment variables securely
5. Security best practices

## Step 1: Creating Dedicated Database Users

### Application User Setup

1. Connect to your SQL Server instance using SQL Server Management Studio (SSMS) or Azure Data Studio as an administrator.

2. Create a dedicated login for the application:

```sql
-- Create a login for the application
CREATE LOGIN planventure_app WITH PASSWORD = 'Strong-Password-Here';

-- Create a user in the specific database
USE planventure;
CREATE USER planventure_app FOR LOGIN planventure_app;

-- Grant minimal required permissions
EXEC sp_addrolemember 'db_datareader', 'planventure_app';
EXEC sp_addrolemember 'db_datawriter', 'planventure_app';
```

3. For operations that require more than simple CRUD, grant specific stored procedure execution permissions:

```sql
-- Example for a specific stored procedure
GRANT EXECUTE ON [dbo].[sp_backup_database] TO planventure_app;
```

### Read-Only User Setup

For reporting or monitoring purposes, create a read-only user:

```sql
-- Create a login for read-only access
CREATE LOGIN planventure_readonly WITH PASSWORD = 'Another-Strong-Password';

-- Create a user in the database
USE planventure;
CREATE USER planventure_readonly FOR LOGIN planventure_readonly;

-- Grant read-only permissions
EXEC sp_addrolemember 'db_datareader', 'planventure_readonly';
```

## Step 2: Connection String Configuration for Production

Update your application's connection configuration to use the new credentials. In your `.env` file or environment variables:

```
DB_SERVER=your-production-server.database.windows.net,1433
DB_USERNAME=planventure_app
DB_PASSWORD=Strong-Password-Here
DB_NAME=planventure
DB_DRIVER=ODBC Driver 17 for SQL Server
```

The resulting connection string in your application will be:

```
mssql+pyodbc://planventure_app:Strong-Password-Here@your-production-server.database.windows.net:1433/planventure?driver=ODBC+Driver+17+for+SQL+Server
```

## Step 3: Azure AD Authentication (for Azure SQL Database)

If using Azure SQL Database, consider using Azure AD authentication for enhanced security:

1. In the Azure portal, grant Azure AD roles to your application's managed identity

2. Update your connection string to use Azure AD authentication:

```python
# For managed identity
conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=your-server.database.windows.net;Database=planventure;Authentication=ActiveDirectoryMsi"

# For service principal
conn_str = "Driver={ODBC Driver 17 for SQL Server};Server=your-server.database.windows.net;Database=planventure;Authentication=ActiveDirectoryServicePrincipal;UID=app-id;PWD=client-secret"
```

## Step 4: Configure Connection Pooling

SQLAlchemy automatically implements connection pooling. Adjust the settings in your application config:

```python
# In app.py
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,  # Maximum number of connections in the pool
    'max_overflow': 20,  # Maximum number of connections that can be created above pool_size
    'pool_timeout': 30,  # Seconds to wait before timing out on getting a connection from the pool
    'pool_recycle': 1800,  # Recycle connections after 30 minutes (prevents stale connections)
}
```

## Step 5: Security Best Practices

1. **Never commit credentials to version control**. Use environment variables or a secure secret manager.

2. **Rotate passwords regularly**. Implement a process to change database passwords periodically.

3. **Use TLS/SSL for database connections**. Always enable encrypted connections:

```python
# Add to your connection string
'Encrypt=yes;TrustServerCertificate=no;'
```

4. **Implement a firewall**. Restrict SQL Server access to only necessary IP addresses.

5. **Audit database access**. Enable SQL Server auditing to track who is accessing what data.

6. **Use Transparent Data Encryption (TDE)**. For sensitive data at rest:

```sql
-- Enable TDE
USE master;
GO
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'Strong-Master-Key-Password';
GO
CREATE CERTIFICATE TDECert WITH SUBJECT = 'TDE Certificate';
GO
USE planventure;
GO
CREATE DATABASE ENCRYPTION KEY
WITH ALGORITHM = AES_256
ENCRYPTION BY SERVER CERTIFICATE TDECert;
GO
ALTER DATABASE planventure
SET ENCRYPTION ON;
GO
```

## Implementation Checklist

- [ ] Create dedicated database users
- [ ] Update application connection strings
- [ ] Test authentication in staging environment
- [ ] Configure connection pooling
- [ ] Implement data encryption (TDE)
- [ ] Set up regular password rotation process
- [ ] Enable auditing and monitoring
- [ ] Document security policies and procedures

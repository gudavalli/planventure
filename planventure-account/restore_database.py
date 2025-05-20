#!/usr/bin/env python
"""Restore SQL Server database from a backup file."""
import os
import sys
import argparse
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def restore_database(backup_file, database_name="planventure"):
    """Restore a SQL Server database from backup.
    
    Args:
        backup_file (str): Path to backup file
        database_name (str): Name of the database to restore
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get database config from environment
    server = os.environ.get('DB_SERVER', 'localhost,1433')
    username = os.environ.get('DB_USERNAME', 'sa')
    password = os.environ.get('DB_PASSWORD', 'YourStrong@Passw0rd')
    driver = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Verify backup file exists
    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found: {backup_file}")
        return False
    
    # Replace backslashes with forward slashes for SQL Server
    backup_file = backup_file.replace('\\', '/')
    
    print(f"Restoring database '{database_name}' from {backup_file}...")
    
    try:
        # Connect to the master database
        conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID={username};PWD={password}"
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # Check if database exists
        print("Checking if database exists...")
        cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{database_name}'")
        db_exists = cursor.fetchone()[0] > 0
        
        # If database exists, set to single user mode to allow restore
        if db_exists:
            print(f"Database '{database_name}' exists. Setting to single user mode...")
            try:
                cursor.execute(f"ALTER DATABASE [{database_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
            except Exception as e:
                print(f"Warning: Could not set single user mode: {str(e)}")
        
        # Data file paths
        data_file_path = os.path.join('C:', 'Program Files', 'Microsoft SQL Server', 'MSSQL16.MSSQLSERVER', 'MSSQL', 'DATA', f"{database_name}.mdf")
        log_file_path = os.path.join('C:', 'Program Files', 'Microsoft SQL Server', 'MSSQL16.MSSQLSERVER', 'MSSQL', 'DATA', f"{database_name}_log.ldf")
        
        # For Docker containers, use this path instead
        if os.environ.get('DOCKER_CONTAINER', 'false').lower() == 'true':
            data_file_path = f'/var/opt/mssql/data/{database_name}.mdf'
            log_file_path = f'/var/opt/mssql/data/{database_name}_log.ldf'
        
        # Convert paths to SQL Server format
        data_file_path = data_file_path.replace('\\', '/')
        log_file_path = log_file_path.replace('\\', '/')
        
        # Execute restore command
        print("Executing database restore...")
        
        # Get logical file names from backup
        print("Getting logical file names from backup...")
        fileinfo_query = f"""
        RESTORE FILELISTONLY FROM DISK = N'{backup_file}'
        """
        fileinfo = cursor.execute(fileinfo_query).fetchall()
        
        data_logical_name = None
        log_logical_name = None
        
        for file in fileinfo:
            if file.Type == 'D':  # Data file
                data_logical_name = file.LogicalName
            elif file.Type == 'L':  # Log file
                log_logical_name = file.LogicalName
        
        if not data_logical_name or not log_logical_name:
            print("Error: Could not determine logical file names from backup")
            return False
            
        print(f"Data file logical name: {data_logical_name}")
        print(f"Log file logical name: {log_logical_name}")
        
        # Perform the restore
        restore_query = f"""
        RESTORE DATABASE [{database_name}] 
        FROM DISK = N'{backup_file}' 
        WITH FILE = 1,
        MOVE N'{data_logical_name}' TO N'{data_file_path}',
        MOVE N'{log_logical_name}' TO N'{log_file_path}',
        NOUNLOAD, REPLACE, RECOVERY, STATS = 10
        """
        
        cursor.execute(restore_query)
        
        while cursor.nextset():
            pass
        
        # Set database back to multi-user mode
        if db_exists:
            print(f"Setting database back to multi-user mode...")
            cursor.execute(f"ALTER DATABASE [{database_name}] SET MULTI_USER")
        
        print(f"Database '{database_name}' restored successfully from {backup_file}")
        conn.close()
        return True
    except Exception as e:
        print(f"Error restoring database: {str(e)}")
        return False

def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(description='Restore SQL Server database from backup')
    parser.add_argument('backup_file', type=str, help='Path to backup file')
    parser.add_argument('--database', type=str, default='planventure', help='Database name')
    parser.add_argument('--docker', action='store_true', help='Running in Docker container')
    
    args = parser.parse_args()
    
    # Set Docker environment variable if specified
    if args.docker:
        os.environ['DOCKER_CONTAINER'] = 'true'
    
    success = restore_database(
        backup_file=args.backup_file,
        database_name=args.database
    )
    
    if success:
        print("Restore operation completed successfully.")
        return 0
    else:
        print("Restore operation failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

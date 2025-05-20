#!/usr/bin/env python
"""Backup SQL Server database to a file."""
import os
import sys
import argparse
import pyodbc
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def backup_database(database_name="planventure", backup_dir=None):
    """Backup a SQL Server database.
    
    Args:
        database_name (str): Name of the database to backup
        backup_dir (str): Directory to store backup files
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Get database config from environment
    server = os.environ.get('DB_SERVER', 'localhost,1433')
    username = os.environ.get('DB_USERNAME', 'sa')
    password = os.environ.get('DB_PASSWORD', 'YourStrong@Passw0rd')
    driver = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Use default backup directory if none specified
    if not backup_dir:
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sql', 'backups')
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create timestamp for backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"{database_name}_{timestamp}.bak"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Replace backslashes with forward slashes for SQL Server
    backup_path = backup_path.replace('\\', '/')
    
    print(f"Backing up database '{database_name}' to {backup_path}...")
    
    try:
        # Connect to the database
        conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database_name};UID={username};PWD={password}"
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        
        # Execute backup command
        backup_query = f"""
        BACKUP DATABASE [{database_name}] 
        TO DISK = N'{backup_path}' 
        WITH DESCRIPTION = N'Full backup of {database_name} database',
        NOFORMAT, NOINIT, 
        NAME = N'{database_name}-Full Database Backup', 
        SKIP, NOREWIND, NOUNLOAD, STATS = 10
        """
        
        print("Executing backup command...")
        cursor.execute(backup_query)
        
        while cursor.nextset():
            pass
        
        print(f"Database backup completed successfully to: {backup_path}")
        
        # Verify backup file exists
        if os.path.exists(backup_path):
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)
            print(f"Backup file size: {size_mb:.2f} MB")
        else:
            print("Warning: Backup file not found in expected location")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error backing up database: {str(e)}")
        return False

def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(description='Backup SQL Server database')
    parser.add_argument('--database', type=str, default='planventure', help='Database name')
    parser.add_argument('--dir', type=str, help='Directory to store backup')
    
    args = parser.parse_args()
    
    success = backup_database(
        database_name=args.database,
        backup_dir=args.dir
    )
    
    if success:
        print("Backup operation completed successfully.")
        return 0
    else:
        print("Backup operation failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

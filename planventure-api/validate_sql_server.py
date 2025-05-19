#!/usr/bin/env python
"""Script to validate SQL Server connection and configuration."""
import os
import sys
import pyodbc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_sql_server():
    """Validate SQL Server connection and configuration."""
    print("SQL Server Connection Validator")
    print("===============================\n")
    
    # Load connection parameters
    server = os.getenv('DB_SERVER', 'localhost,1433')
    username = os.getenv('DB_USERNAME', 'sa')
    password = os.getenv('DB_PASSWORD', 'YourStrong@Passw0rd')
    database = os.getenv('DB_NAME', 'planventure')
    driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    print(f"Connection Parameters:")
    print(f"- Server: {server}")
    print(f"- Database: {database}")
    print(f"- Username: {username}")
    print(f"- Driver: {driver}")
    print()
    
    # Step 1: Check ODBC Driver
    print("Step 1: Checking ODBC Driver...")
    try:
        drivers = pyodbc.drivers()
        driver_exists = any(driver in d for d in drivers)
        
        print(f"Available ODBC Drivers:")
        for d in drivers:
            print(f"  - {d}")
        print()
        
        if not driver_exists:
            print(f"ERROR: Required driver '{driver}' not found!")
            print(f"Please install the appropriate ODBC Driver for SQL Server.")
            print("See MSSQL_SETUP.md for instructions.")
            return False
        else:
            print(f"SUCCESS: Required driver '{driver}' is available.")
    except Exception as e:
        print(f"ERROR: Failed to check ODBC drivers: {str(e)}")
        return False
    
    # Step 2: Connect to master database
    print("\nStep 2: Connecting to SQL Server master database...")
    try:
        master_conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID={username};PWD={password}"
        master_conn = pyodbc.connect(master_conn_str)
        master_cursor = master_conn.cursor()
        print(f"SUCCESS: Connected to master database.")
        
        # Check SQL Server version
        version = master_cursor.execute("SELECT @@version").fetchone()[0]
        print(f"SQL Server Version:")
        print(f"  {version.split(chr(10))[0]}")
        master_conn.close()
    except Exception as e:
        print(f"ERROR: Failed to connect to master database: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Is SQL Server running? Check your Docker container or service.")
        print("2. Is the port accessible? Default is 1433.")
        print("3. Are the credentials correct?")
        print("4. Is there a firewall blocking the connection?")
        return False
    
    # Step 3: Connect to application database
    print("\nStep 3: Connecting to application database...")
    try:
        app_conn_str = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
        app_conn = pyodbc.connect(app_conn_str)
        app_cursor = app_conn.cursor()
        print(f"SUCCESS: Connected to '{database}' database.")
        
        # Check database exists
        db_name = app_cursor.execute("SELECT DB_NAME()").fetchone()[0]
        print(f"Current database: {db_name}")
        
        # Check database collation
        collation = app_cursor.execute("SELECT DATABASEPROPERTYEX(DB_NAME(), 'Collation')").fetchone()[0]
        print(f"Database collation: {collation}")
        
        # Check SQL Server settings
        settings = [
            ("ALLOW_SNAPSHOT_ISOLATION", "Is snapshot isolation enabled"),
            ("READ_COMMITTED_SNAPSHOT", "Is read committed snapshot enabled"),
            ("RECOVERY_MODEL", "Recovery model"),
            ("COMPATIBILITY_LEVEL", "Compatibility level")
        ]
        
        print("\nDatabase Settings:")
        for setting, desc in settings:
            value = app_cursor.execute(f"SELECT DATABASEPROPERTYEX(DB_NAME(), '{setting}')").fetchone()[0]
            print(f"  {desc}: {value}")
        
        app_conn.close()
    except Exception as e:
        print(f"ERROR: Failed to connect to application database: {str(e)}")
        print("Does the database exist? Run init_db.py to create it.")
        return False
    
    print("\nValidation completed successfully!")
    return True

if __name__ == "__main__":
    success = validate_sql_server()
    if not success:
        sys.exit(1)

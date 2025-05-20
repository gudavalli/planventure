"""Database utilities for Microsoft SQL Server."""
import os
import logging
import pyodbc
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('database_utils')

def get_connection_string():
    """Get the database connection string from environment variables."""
    server = os.environ.get('DB_SERVER', 'localhost,1433')
    username = os.environ.get('DB_USERNAME', 'sa')
    password = os.environ.get('DB_PASSWORD', 'YourStrong@Passw0rd')
    database = os.environ.get('DB_NAME', 'planventure')
    driver = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    logger.debug(f"Building connection string for {server}/{database}")
    return f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

def test_connection(db):
    """Test database connection.
    
    Args:
        db: SQLAlchemy database instance
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        result = db.session.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return False

def get_database_info(db):
    """Get information about the connected database.
    
    Args:
        db: SQLAlchemy database instance
        
    Returns:
        dict: Database information
    """
    info = {
        "type": "Unknown",
        "version": "Unknown",
        "name": "Unknown",
        "status": "Unknown"
    }
    
    try:
        # Determine database type
        if 'mssql' in str(db.engine.url):
            info["type"] = "Microsoft SQL Server"
            # Get version
            version = db.session.execute(text("SELECT @@version")).scalar()
            info["version"] = version.split('\n')[0] if version else "Unknown"
            # Get database name
            info["name"] = db.session.execute(text("SELECT DB_NAME()")).scalar()
            # Get status
            info["status"] = "Connected"
        else:
            info["type"] = "Other (non-SQL Server)"
            
        logger.info(f"Connected to {info['type']} database: {info['name']}")
        return info
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        info["status"] = f"Error: {str(e)}"
        return info

def create_database_if_not_exists(database_name="planventure"):
    """Create the database if it doesn't exist.
    
    Args:
        database_name (str): Name of the database to create
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        server = os.environ.get('DB_SERVER', 'localhost,1433')
        username = os.environ.get('DB_USERNAME', 'sa')
        password = os.environ.get('DB_PASSWORD', 'YourStrong@Passw0rd')
        driver = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        
        logger.info(f"Attempting to connect to SQL Server at {server}")
        
        # Connect to master database to create the application database
        connection_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE=master;UID={username};PWD={password}"
        try:
            conn = pyodbc.connect(connection_string, autocommit=True)
            logger.info("Connected to SQL Server master database successfully")
        except pyodbc.Error as e:
            logger.error(f"Failed to connect to SQL Server: {str(e)}")
            # Check if it's a driver-related error
            if "Driver" in str(e):
                logger.error(f"ODBC Driver issue. Make sure '{driver}' is installed")
            return False
            
        cursor = conn.cursor()
        
        # Check if database exists
        try:
            cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{database_name}'")
            db_exists = cursor.fetchone()[0] > 0
            
            if not db_exists:
                logger.info(f"Creating database '{database_name}'...")
                cursor.execute(f"CREATE DATABASE {database_name}")
                logger.info(f"Database '{database_name}' created successfully")
            else:
                logger.info(f"Database '{database_name}' already exists")
                
            # Additional validation - verify the database was created
            cursor.execute(f"SELECT COUNT(*) FROM sys.databases WHERE name = '{database_name}'")
            if cursor.fetchone()[0] == 0:
                logger.error(f"Failed to create database '{database_name}'")
                return False
                
        except pyodbc.Error as e:
            logger.error(f"SQL error: {str(e)}")
            return False
        finally:
            conn.close()
            logger.info("Connection to master database closed")
            
        return True
    except Exception as e:
        logger.error(f"Unexpected error creating database: {str(e)}")
        return False
        
def execute_sql_script(db, script_path):
    """Execute a SQL script file against the database.
    
    Args:
        db: SQLAlchemy database instance
        script_path (str): Path to the SQL script file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not os.path.exists(script_path):
        logger.error(f"SQL script file not found: {script_path}")
        return False
        
    try:
        logger.info(f"Executing SQL script: {script_path}")
        with open(script_path, 'r') as file:
            sql_script = file.read()
            
        # Split the script into individual statements
        statements = sql_script.split(';')
        
        for statement in statements:
            if statement.strip():
                try:
                    db.session.execute(text(statement))
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error executing statement: {str(e)}")
                    db.session.rollback()
                    return False
        
        logger.info("SQL script executed successfully")
        return True
    except Exception as e:
        logger.error(f"Error executing SQL script: {str(e)}")
        return False
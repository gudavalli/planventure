#!/usr/bin/env python
"""Script to optimize SQL Server database for PlanVenture Account Service."""
import os
import sys
import pyodbc
from dotenv import load_dotenv
from app import create_app, db
from models.database import get_connection_string

# Load environment variables
load_dotenv()

def analyze_and_optimize():
    """Analyze and optimize the SQL Server database."""
    print("PlanVenture SQL Server Optimization")
    print("===================================\n")
    
    # Connect to SQL Server
    try:
        conn_str = get_connection_string()
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Connected successfully to SQL Server.")
    except Exception as e:
        print(f"ERROR: Failed to connect to SQL Server: {str(e)}")
        return False
    
    # Step 1: Check and create missing indexes
    print("\nStep 1: Analyzing and creating indexes...")
    
    # Common index patterns for API applications
    indexes_to_check = [
        # Format: (table_name, column_name, index_name)
        ("users", "email", "IX_users_email"),
        ("trips", "user_id", "IX_trips_user_id"),
        ("trips", "start_date", "IX_trips_start_date"),
        ("trips", "destination", "IX_trips_destination")
    ]
    
    for table, column, index_name in indexes_to_check:
        try:
            # Check if index exists
            cursor.execute("""
                SELECT COUNT(*)
                FROM sys.indexes
                WHERE name = ? AND object_id = OBJECT_ID(?)
            """, (index_name, table))
            
            if cursor.fetchone()[0] == 0:
                print(f"Creating index {index_name} on {table}({column})...")
                cursor.execute(f"""
                    CREATE INDEX {index_name}
                    ON {table}({column})
                """)
                conn.commit()
                print(f"SUCCESS: Created index {index_name}.")
            else:
                print(f"INFO: Index {index_name} already exists.")
        except Exception as e:
            print(f"ERROR: Failed to check/create index {index_name}: {str(e)}")
    
    # Step 2: Update statistics
    print("\nStep 2: Updating statistics...")
    
    try:
        cursor.execute("EXEC sp_updatestats")
        conn.commit()
        print("SUCCESS: Statistics updated successfully.")
    except Exception as e:
        print(f"ERROR: Failed to update statistics: {str(e)}")
    
    # Step 3: Configure storage parameters
    print("\nStep 3: Checking database storage parameters...")
    
    try:
        cursor.execute("""
            SELECT name, size/128.0 AS SizeMB, 
                   size/128.0 - CAST(FILEPROPERTY(name, 'SpaceUsed') AS INT)/128.0 AS FreeMB
            FROM sys.database_files
            WHERE type = 0  -- Data files
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            name, size_mb, free_mb = row
            print(f"File: {name}, Size: {size_mb:.2f} MB, Free: {free_mb:.2f} MB")
            
            # Check if auto-growth settings are appropriate
            cursor.execute("""
                SELECT growth, is_percent_growth
                FROM sys.database_files
                WHERE name = ?
            """, (name,))
            
            growth_row = cursor.fetchone()
            if growth_row:
                growth, is_percent = growth_row
                if is_percent:
                    print(f"  Growth setting: {growth}% (percentage-based)")
                    if growth < 10:
                        print("  RECOMMENDATION: Consider setting growth to at least 10%")
                else:
                    growth_mb = growth / 128.0  # Convert from 8KB pages to MB
                    print(f"  Growth setting: {growth_mb:.2f} MB (fixed size)")
                    if growth_mb < 64:
                        print("  RECOMMENDATION: Consider setting growth to at least 64 MB")
    except Exception as e:
        print(f"ERROR: Failed to check storage parameters: {str(e)}")
    
    # Step 4: Check for query performance issues
    print("\nStep 4: Analyzing query performance...")
    
    try:
        # Create Flask app context to use models
        app = create_app()
        
        with app.app_context():
            print("Checking for missing indexes in the most common queries...")
            
            # This runs a query that SQL Server can analyze for missing indexes
            cursor.execute("""
            SELECT 
                dm_mid.database_id,
                dm_migs.avg_user_impact,
                dm_migs.last_user_seek,
                dm_mid.statement AS TableName,
                dm_mid.equality_columns,
                dm_mid.inequality_columns,
                dm_mid.included_columns
            FROM sys.dm_db_missing_index_details dm_mid
            INNER JOIN sys.dm_db_missing_index_groups dm_mig ON dm_mid.index_handle = dm_mig.index_handle
            INNER JOIN sys.dm_db_missing_index_group_stats dm_migs ON dm_mig.index_group_handle = dm_migs.group_handle
            WHERE dm_mid.database_id = DB_ID()
            ORDER BY dm_migs.avg_user_impact DESC
            """)
            
            missing_indexes = cursor.fetchall()
            if missing_indexes:
                print("\nMissing indexes recommended by SQL Server:")
                for idx, row in enumerate(missing_indexes):
                    print(f"\n{idx+1}. Impact: {row.avg_user_impact:.2f}%, Last seek: {row.last_user_seek}")
                    print(f"   Table: {row.TableName}")
                    if row.equality_columns:
                        print(f"   Equality columns: {row.equality_columns}")
                    if row.inequality_columns:
                        print(f"   Inequality columns: {row.inequality_columns}")
                    if row.included_columns:
                        print(f"   Included columns: {row.included_columns}")
            else:
                print("No missing indexes detected.")
    except Exception as e:
        print(f"ERROR: Failed to analyze query performance: {str(e)}")
    
    # Close connection
    conn.close()
    
    print("\nOptimization analysis completed. Review the recommendations above.")
    return True

if __name__ == '__main__':
    analyze_and_optimize()

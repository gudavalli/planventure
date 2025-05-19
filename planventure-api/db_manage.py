#!/usr/bin/env python
"""CLI tool for managing the PlanVenture database."""
import argparse
import os
import sys
from dotenv import load_dotenv

def show_help():
    """Show command help."""
    print("PlanVenture Database Management CLI")
    print("\nCommands:")
    print("  init      Initialize the database")
    print("  migrate   Migrate data from SQLite to SQL Server")
    print("  status    Check database connection status")
    print("  drop      Drop all tables (use with caution!)")
    print("\nExamples:")
    print("  python db_manage.py init")
    print("  python db_manage.py migrate")
    print("  python db_manage.py status")

def init_command(args):
    """Initialize the database."""
    from init_db import init_database
    
    if args.no_test:
        create_test_db = False
    else:
        create_test_db = True
        
    success = init_database(
        database_name=args.db_name,
        create_test_db=create_test_db
    )
    
    if success:
        print("\nDatabase initialization completed successfully.")
    else:
        print("\nDatabase initialization encountered errors.")
        sys.exit(1)

def migrate_command(args):
    """Migrate data from SQLite to SQL Server."""
    from migrate_to_mssql import migrate_from_sqlite
    
    print("Starting migration from SQLite to SQL Server...")
    migrate_from_sqlite()

def status_command(args):
    """Check database connection status."""
    from app import create_app, db
    from models.database import test_connection
    
    app = create_app()
    
    print("Testing database connection...")
    with app.app_context():
        if test_connection(db):
            print("✓ Successfully connected to database")
            
            # Get database info
            try:
                result = db.session.execute("SELECT @@version").scalar()
                print(f"\nSQL Server version: {result}")
                
                # Get number of tables
                table_count = len(db.engine.table_names())
                print(f"Number of tables: {table_count}")
                
                # Get database name
                db_name = db.session.execute("SELECT DB_NAME()").scalar()
                print(f"Current database: {db_name}")
            except Exception as e:
                print(f"Error fetching database info: {str(e)}")
        else:
            print("✗ Failed to connect to database")
            sys.exit(1)

def drop_command(args):
    """Drop all tables (use with caution!)."""
    if not args.confirm:
        print("WARNING: This will delete all data in the database.")
        confirmation = input("Type 'DELETE' to confirm: ")
        if confirmation != "DELETE":
            print("Operation cancelled.")
            return
    
    from app import create_app, db
    
    app = create_app()
    
    print("Dropping all tables...")
    with app.app_context():
        try:
            db.drop_all()
            print("✓ All tables dropped successfully")
        except Exception as e:
            print(f"Error dropping tables: {str(e)}")
            sys.exit(1)

def main():
    """CLI entry point."""
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="PlanVenture Database Management CLI",
        add_help=False
    )
    
    # Add help argument
    parser.add_argument(
        '-h', '--help', action='store_true', help="Show help message and exit"
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # init command
    init_parser = subparsers.add_parser('init', help="Initialize the database")
    init_parser.add_argument('--no-test', action='store_true', help="Skip creating test database")
    init_parser.add_argument('--db-name', type=str, default='planventure', help="Database name")
    
    # migrate command
    migrate_parser = subparsers.add_parser('migrate', help="Migrate data from SQLite to SQL Server")
    
    # status command
    status_parser = subparsers.add_parser('status', help="Check database connection status")
    
    # drop command
    drop_parser = subparsers.add_parser('drop', help="Drop all tables (use with caution!)")
    drop_parser.add_argument('--confirm', action='store_true', help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    if args.help or not args.command:
        show_help()
        return
    
    if args.command == 'init':
        init_command(args)
    elif args.command == 'migrate':
        migrate_command(args)
    elif args.command == 'status':
        status_command(args)
    elif args.command == 'drop':
        drop_command(args)

if __name__ == "__main__":
    main()

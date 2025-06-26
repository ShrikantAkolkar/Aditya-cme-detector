#!/usr/bin/env python3
"""
Script to set up the database for the CME detection system
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import init_database, close_database
from src.config import config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_database():
    """Set up the database tables and initial data"""
    
    try:
        logger.info("Setting up Aditya-L1 CME Detection database...")
        
        # Initialize database
        await init_database()
        logger.info("Database tables created successfully")
        
        # You can add initial data setup here if needed
        # For example, default configuration, admin users, etc.
        
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise
    finally:
        await close_database()

def main():
    """Main function"""
    print("Aditya-L1 CME Detection System - Database Setup")
    print("=" * 50)
    
    # Check configuration
    try:
        db_url = config.database_url
        if not db_url:
            print("Error: DATABASE_URL not configured")
            print("Please set the DATABASE_URL environment variable or update config.yaml")
            sys.exit(1)
        
        print(f"Database URL: {db_url}")
        
        # Run setup
        asyncio.run(setup_database())
        
        print("\nDatabase setup completed successfully!")
        print("You can now start the API server and dashboard.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
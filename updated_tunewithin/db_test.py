from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment or use default
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///tanmaydb.db")

def test_database_connection():
    """Test the database connection with proper SQLAlchemy usage."""
    try:
        # Create an engine
        engine = create_engine(DATABASE_URL)
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Execute a simple query using text()
        result = session.execute(text("SELECT 1"))
        first_result = result.scalar()
        
        # Close the session
        session.close()
        
        print(f"Database connection successful! Result: {first_result}")
        return True
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False

if __name__ == "__main__":
    test_database_connection()

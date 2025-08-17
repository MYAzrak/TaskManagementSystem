from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Define the database connection URL
# Using SQLite database file stored locally in the project directory
DATABASE_URL = "sqlite:///./app.db"

# Create the database engine
# This is the core interface to the database that handles connections and SQL execution
# The connect_args parameter is specific to SQLite and allows multiple threads to access the database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create a session factory
# This factory creates database sessions that manage database transactions
# autocommit=False: Changes are not automatically committed to the database
# autoflush=False: Objects are not automatically flushed to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the declarative base class
# This base class is used to define database models as Python classes
# All model classes will inherit from this Base class
Base = declarative_base()


def get_db():
    """
    Dependency function to get a database session.
    This function is typically used as a dependency in FastAPI endpoints.

    Yields:
        Database session object

    Note:
        The session is automatically closed after use due to the try-finally block
    """
    # Create a new database session
    db = SessionLocal()
    try:
        # Yield the session to the calling function
        # This allows the session to be used in the endpoint
        yield db
    finally:
        # Always close the session when done
        # This ensures proper cleanup and prevents connection leaks
        db.close()

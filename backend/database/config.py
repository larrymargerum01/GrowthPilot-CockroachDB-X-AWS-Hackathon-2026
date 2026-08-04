import os

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class DatabaseConfig:
     """
    Stores database configuration
    loaded from environment variables.
    """

     def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        
    
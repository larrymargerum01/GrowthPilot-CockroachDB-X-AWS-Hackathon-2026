import os

class DatabaseConfig:
     """
    Stores database configuration
    loaded from environment variables.
    """

     def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        
    
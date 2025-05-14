import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

class Database:
    def __init__(self):
        # Get database URL from environment variables
        self.SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL") 
        
        if not self.SQLALCHEMY_DATABASE_URL:            
            raise ValueError("DATABASE_URL not found in environment variables")

        # SSL/TLS configuration
        connect_args = self._get_ssl_config()
        
        # Create engine
        self.engine = create_engine(
            self.SQLALCHEMY_DATABASE_URL,
            pool_size=20,
            max_overflow=30,
            pool_recycle=3600,  # Recycle connections every hour
            echo=False,  
            connect_args=connect_args
        )
        
        # Configure session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def _get_ssl_config(self):
        """Configure SSL settings based on environment variables"""
        connect_args = {}
        
        # Get SSL parameters from environment
        ssl_mode = os.getenv("SSL_MODE")
        ssl_root_cert = os.getenv("SSL_ROOT_CERT")
        ssl_cert = os.getenv("SSL_CERT")
        ssl_key = os.getenv("SSL_KEY")
        env = os.getenv("ENV", "development")

        # Auto-enforce SSL in production if not explicitly configured
        if env == "production" and not ssl_mode:
            ssl_mode = "require"

        # Apply SSL configuration
        if ssl_mode:
            connect_args["sslmode"] = ssl_mode
            if ssl_root_cert:
                connect_args["sslrootcert"] = ssl_root_cert
            if ssl_cert:
                connect_args["sslcert"] = ssl_cert
            if ssl_key:
                connect_args["sslkey"] = ssl_key

        return connect_args

    def get_db(self):
        """Dependency for FastAPI or other frameworks"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

db = Database()

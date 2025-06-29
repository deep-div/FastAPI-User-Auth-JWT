from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace the SQLite connection URL with your PostgreSQL connection URL
DATABASE_URL = "postgresql://postgres:Anshi2002@localhost:5433/dummy"

# Create a PostgreSQL engine instance
engine = create_engine(DATABASE_URL)

# Create declarative base meta instance
Base = declarative_base()  

# Bind engine which will be further used in models to automatically create all the models
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False) 




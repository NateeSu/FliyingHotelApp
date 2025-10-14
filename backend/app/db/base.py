from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Note: Models should be imported in alembic/env.py for migrations
# Do not import models here to avoid circular imports

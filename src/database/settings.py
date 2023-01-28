from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

path = 'sqlite:///db.sqlite3'

# Engine の作成
Engine = create_engine(
  path,
  encoding="utf-8",
  echo=False
)

Base = declarative_base()


from datetime import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# base directory setup
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR, exist_ok=True)

# database path (default SQLite, override with DATABASE_URL)
SQLITE_PATH = os.getenv(
    'DATABASE_URL',
    f"sqlite:///{os.path.join(INSTANCE_DIR, 'rag.db')}"
)

engine = create_engine(
    SQLITE_PATH,
    connect_args={"check_same_thread": False} if 'sqlite' in SQLITE_PATH else {}
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)
Base = declarative_base()


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)

    # relationship to chunks
    chunks = relationship('Chunk', back_populates='document')


class Chunk(Base):
    __tablename__ = 'chunks'

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    content = Column(Text)

    chunk_index = Column(Integer, nullable=False)

    # stored as "metadata" column in DB
    chunk_metadata = Column("metadata", Text)

    # relationship to parent document
    document = relationship('Document', back_populates='chunks')


def init_db():
    Base.metadata.create_all(bind=engine)

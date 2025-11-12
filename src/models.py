from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Table,
    ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# SQLite database (file will be created in the repository root)
DATABASE_URL = "sqlite:///./activities.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Association table for many-to-many relationship between activities and participants
activity_participants = Table(
    "activity_participants",
    Base.metadata,
    Column("activity_id", Integer, ForeignKey("activities.id")),
    Column("participant_id", Integer, ForeignKey("participants.id")),
)


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    schedule = Column(String)
    max_participants = Column(Integer)
    participants = relationship(
        "Participant", secondary=activity_participants, back_populates="activities"
    )


class Participant(Base):
    __tablename__ = "participants"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    activities = relationship(
        "Activity", secondary=activity_participants, back_populates="participants"
    )


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()

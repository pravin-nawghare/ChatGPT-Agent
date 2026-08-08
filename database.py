# Database related setup to store chats after app is closed
from datetime import datetime
from pathlib import Path

from config import settings

from sqlalchemy import create_engine, Integer, String, Text, DateTime, Column
from sqlalchemy.orm import declarative_base, sessionmaker

Path("data").mkdir(exist_ok=True)

database_url = settings.DATABASE_URL

engine = create_engine(
    database_url,
    connect_args = {"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bnd=engine, 
    autoflush=False, 
    autocommit= False
)

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tabename__ = "caht_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True)
    title = Column(String, default="New Chat")
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class LongTremMemomry(Base):
    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True)
    memory = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def create_or_update_conservation(thread_id: str, first_message: str | None = None):
    db = SessionLocal()

    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id ==thread_id)
            .first()
        )

        if not conversation:
            title = "New Chat"

            if first_message:
                title = first_message.strip()[:20]
                if len(first_message.strip()) > 20:
                    title += "...."

            conversation = Conversation(
                thread_id = thread_id,
                title = title,
                created_at = datetime.utcnow(),
                updated_at = datetime.utcnow()
            )

            db.add(conversation)

        else:
            conversation.updated_at = datetime.utcnow()

        db.commit()

    finally:
        db.close()

def list_conversation():
    db = SessionLocal()

    try:
        return (
            db.query(Conversation)
            .order_by(Conversation.updated_at.desc())
            .all()
        )

    finally:
        db.close()

def save_user_chat_message(thread_id: str, role: str, content: str):
    db = SessionLocal()

    try:
        msg = ChatMessage(
            thread_id = thread_id,
            role = role,
            content = content,
            created_at = datetime.utcnow()
        )

        db.add(msg)

        conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id == thread_id)
            .first()
        )

        if conversation:
            conversation.updated_at = datetime.utcnow()

        db.commit()

    finally: 
        db.close()

def get_user_chat_history(thread_id: str, memory: str):
    db = SessionLocal()

    try:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.thread_id == thread_id)
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    finally:
        db.close()

def save_memory(thread_id: str, memory: str):
    db = SessionLocal()

    try:
        item = LongTremMemomry(
            thread_id = thread_id,
            memory = memory,
            created_at = datetime.utcnow()
        )

        db.add(item)
        db.commit()

        return "Memory saved successfully"
    finally:
        db.close()

def search_memory(thread_id: str, query: str):
    db = SessionLocal()

    try:
        memories = (
            db.query(LongTremMemomry)
            .filter(LongTremMemomry.thread_id == thread_id)
            .order_by(LongTremMemomry.created_at.desc())
            .limit(10)
            .all()
        )

        if not memories:
            return "No saved memory found"

        return "\n".join({f"- {m.memory}" for m in memories})

    finally:
        db.close()


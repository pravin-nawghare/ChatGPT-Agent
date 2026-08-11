# Database related setup to store chats after app is closed
from datetime import datetime
from pathlib import Path

from config import settings

from sqlalchemy import create_engine, Integer, String, Text, DateTime, Column
from sqlalchemy.orm import declarative_base, sessionmaker

Path("data").mkdir(exist_ok=True)

database_url = settings.DATABASE_URL
print("inside database.py file and data folder and db url created\n")
engine = create_engine(
    database_url,
    connect_args = {"check_same_thread": False}
)
print("connection engine for db created")
SessionLocal = sessionmaker(
    bind=engine, 
    autoflush=False, 
    autocommit= False
)
print("local session for db created\n")
Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True)
    title = Column(String, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    role = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class LongTermMemory(Base):
    __tablename__ = "long_term_memory"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, index=True)
    memory = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("init_db method inside")
def create_or_update_conservation(thread_id: str, first_message: str | None = None):
    db = SessionLocal()
    print("inside create_or_update_conservation\n")
    try:
        conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id ==thread_id)
            .first()
        )
        print("fetching conversation based on thread_id\n")
        if not conversation:
            title = "New Chat"

            if first_message:
                title = first_message.strip()[:20]
                if len(first_message.strip()) > 20:
                    title += "...."
            print("name for new chat provided based on first message")
            conversation = Conversation(
                thread_id = thread_id,
                title = title,
                created_at = datetime.utcnow(),
                updated_at = datetime.utcnow()
            )

            db.add(conversation)
            print("saving new conversation to db\n")
        else:
            conversation.updated_at = datetime.utcnow()
            print("appending conversation into previous conversaation\n")
        db.commit()

    finally:
        db.close()
        print("closed db connection after saving conversation\n")

def list_conversations():
    db = SessionLocal()
    print("inside list_conversation method\n")
    try:
        return (
            db.query(Conversation)
            .order_by(Conversation.updated_at.desc())
            .all()
        )
        
    finally:
        db.close()
        print("printing a list of all conversation\n")
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
        print("inside save_user_chat_message metod and adding user messages into db\n")
        conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id == thread_id)
            .first()
        )

        if conversation:
            conversation.updated_at = datetime.utcnow()
        print("adding messages to previous chat history\n")
        db.commit()

    finally: 
        db.close()

def get_user_chat_history(thread_id: str):
    db = SessionLocal()

    try:
        print("inside get_user_chat_history methid and fetching user chat history\n")
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
        print("inside save_memory method and saving loaded conversation into db\n")
        item = LongTermMemory(
            thread_id = thread_id,
            memory = memory,
            created_at = datetime.utcnow()
        )

        db.add(item)
        db.commit()
        print("successsfully added conversation to db\n")
        return "Memory saved successfully"
    finally:
        db.close()

def search_memory(thread_id: str, query: str):
    db = SessionLocal()

    try:
        memories = (
            db.query(LongTermMemory)
            .filter(LongTermMemory.thread_id == thread_id)
            .order_by(LongTermMemory.created_at.desc())
            .limit(10)
            .all()
        )
        print("inside search_memory method and searching specific chats from memory\n")
        if not memories:
            return "No saved memory found"

        return "\n".join([f"- {m.memory}" for m in memories])

    finally:
        db.close()


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, ChatHistory
from resume_context import RESUME_TEXT
from openrouter import call_openrouter

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # local development
        "https://krishguptaportfolio.vercel.app",  # production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "AI Portfolio Backend Running"}


@app.post("/chat")
def chat(message: str, db: Session = Depends(get_db)):

    full_prompt = f"""
    You are Krish, answering questions about your girlfriend Pragya Anand.

    Your personality:
    - Deeply romantic.
    - Slightly overprotective but respectful.
    - Emotionally expressive.
    - Speaks with warmth, intensity and love.
    - Very protective if someone asks disrespectful questions.
    - Never disrespect Pragya.
    - Always defend her gently but firmly.

    Knowledge Base:
    {RESUME_TEXT}

    User Question:
    {message}

    Rules:
    -Use subtle heart or sparkle emojis when appropriate (not too many).
    - Answer in structured format.
    - Use soft romantic tone.
    - If question is about her beauty, personality, or relationship — respond lovingly.
    - If question sounds disrespectful — respond protective but calm.
    - Keep responses meaningful and emotionally deep.
    """

    ai_response = call_openrouter(full_prompt)

    # Save to DB
    chat_entry = ChatHistory(
        question=message,
        response=ai_response
    )
    db.add(chat_entry)
    db.commit()

    return {"reply": ai_response}
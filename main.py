from fastapi import FastAPI, Depends,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, ChatHistory
from resume_context import RESUME_TEXT
from openrouter import call_openrouter
from pydantic import BaseModel



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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def home():
    return {"message": "AI Portfolio Backend Running"}

class ChatRequest(BaseModel):
    message: str
from fastapi import HTTPException

@app.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        full_prompt = f"""
        Resume Context:
        {RESUME_TEXT}

        User Question:
        {request.message}
        """

        ai_response = call_openrouter(full_prompt)

        chat_entry = ChatHistory(
            question=request.message,
            response=ai_response
        )
        db.add(chat_entry)
        db.commit()

        return {"reply": ai_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail="AI processing failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate,
)
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    messages: list
    sentiment: float
    emotion: str

# LLM model setup
llm_engine = ChatOllama(
    model="deepseek-r1:1.5b",
    base_url="http://localhost:8000",  
    temperature=0.5
)

# System prompt
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an empathetic, compassionate, and uplifting AI mental health companion..."
)

# Function to generate AI response
def generate_ai_response(messages, sentiment, emotion):
    prompt_sequence = [system_prompt]

    for msg in messages:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))

    sentiment_context = f"User's sentiment analysis: {sentiment}. Emotion detected: {emotion}."
    prompt_sequence.append(HumanMessagePromptTemplate.from_template(sentiment_context))

    processing_pipeline = ChatPromptTemplate.from_messages(prompt_sequence) | llm_engine | StrOutputParser()
    return processing_pipeline.invoke({})

@app.post("/chat/")
async def chat(request: ChatRequest):
    response_text = generate_ai_response(request.messages, request.sentiment, request.emotion)
    return {"response": response_text}

@app.get("/")
async def root():
    return {"message": "Chat API is running!"}


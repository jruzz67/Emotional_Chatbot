from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from functools import lru_cache

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for specific trusted domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["Authorization", "Content-Type"],
)

# Set up rate limiter (10 requests per minute per user)
limiter = Limiter(key_func=get_remote_address)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Define request model
class ChatRequest(BaseModel):
    userMessage: str

# Load emotion classification model once (optimized)
@lru_cache(maxsize=1)
def get_emotion_classifier():
    try:
        return pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base"
        )
    except Exception as e:
        logging.error(f"Error loading emotion model: {e}")
        return None  # Avoid crashes if model fails

# Function to analyze emotions from a given text
def analyze_emotion(text: str) -> str:
    classifier = get_emotion_classifier()
    if not classifier:
        return "unknown"

    try:
        result = classifier(text)
        return result[0]['label']  # Directly return the most relevant emotion
    except Exception as e:
        logging.error(f"Error analyzing emotion: {e}")
        return "error"

# Load Chat Model once (optimized)
@lru_cache(maxsize=1)
def get_chat_model():
    return ChatOllama(
        model="mistral:latest",
        base_url="http://localhost:11434",
        temperature=0.5
    )

llm_engine = get_chat_model()

# System prompt for chatbot
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an empathetic, compassionate, and uplifting AI mental health companion..."
)

# Function to generate AI response
async def generate_ai_response(user_message: str) -> dict:
    try:
        # Step 1: Detect Emotion
        detected_emotion = analyze_emotion(user_message)
        sentiment_context = f"Emotion detected: {detected_emotion}."

        # Step 2: Construct chat prompt
        prompt_sequence = [
            system_prompt,
            HumanMessagePromptTemplate.from_template(user_message),
            HumanMessagePromptTemplate.from_template(sentiment_context)
        ]

        # Step 3: Generate response from AI model
        processing_pipeline = ChatPromptTemplate.from_messages(prompt_sequence) | llm_engine | StrOutputParser()
        response_text = processing_pipeline.invoke({"input": user_message})

        # Step 4: Ensure response is not empty
        if not response_text or response_text.strip() == "":
            logging.warning("AI response was empty.")
            response_text = "I'm here to help, but I didn't understand that. Can you elaborate?"

        return {
            "response": response_text.strip(),
            "emotion": detected_emotion
        }
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        return {
            "response": "I'm currently facing technical issues. Please try again later.",
            "emotion": "error"
        }

# Chat endpoint with rate limiting
@app.post("/chat/")
@limiter.limit("10/minute")
async def chat(request: Request, chat_request: ChatRequest):
    result = await generate_ai_response(chat_request.userMessage)
    return result

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Chat API is running!"}

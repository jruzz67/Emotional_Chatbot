from fastapi import FastAPI, HTTPException
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
from transformers import pipeline
import logging

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for all origins (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Request model
class ChatRequest(BaseModel):
    userMessage: str

# Load emotion classification model with error handling
try:
    emotion_classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        return_all_scores=True
    )
except Exception as e:
    logging.error(f"Error loading emotion model: {e}")
    emotion_classifier = None  # Fallback to prevent crashes

# Initialize Chat Model
llm_engine = ChatOllama(
    model="deepseek-r1:1.5b",  # Change model if needed
    base_url="http://localhost:11434",  # Ensure Ollama server is running
    temperature=0.5
)

# System prompt for the chatbot
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an empathetic, compassionate, and uplifting AI mental health companion..."
)

# Function to analyze emotions from a given text
def analyze_emotion(text: str) -> str:
    if not emotion_classifier:
        return "unknown"  # Default if the model failed to load

    try:
        result = emotion_classifier(text)
        emotions = {emotion["label"]: round(emotion["score"], 4) for emotion in result[0]}
        dominant_emotion = max(emotions, key=emotions.get)
        return dominant_emotion
    except Exception as e:
        logging.error(f"Error analyzing emotion: {e}")
        return "error"

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
        response_text = processing_pipeline.invoke({})

        return {
            "response": response_text,
            "emotion": detected_emotion
        }
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        raise HTTPException(status_code=500, detail="Error processing request")

# Endpoint: Process user message (handles both emotion & AI response)
@app.post("/chat/")
async def chat(request: ChatRequest):
    result = await generate_ai_response(request.userMessage)
    return result

@app.get("/")
async def root():
    return {"message": "Chat API is running!"}

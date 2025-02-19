const express = require("express");
const bodyParser = require("body-parser");
const vader = require("vader-sentiment");
const cors = require("cors");
const axios = require("axios");

const app = express();
const port = 5000;

// Middleware
app.use(bodyParser.json());
app.use(cors({ origin: "http://localhost:3000" }));

// API endpoint to analyze sentiment
app.post("/analyze-sentiment", async (req, res) => {
  const { userMessage } = req.body;

  if (!userMessage || typeof userMessage !== "string") {
    return res.status(400).json({ error: "Invalid input" });
  }

  // Analyze sentiment using VADER
  const sentiment = vader.SentimentIntensityAnalyzer.polarity_scores(userMessage);

  // Classify sentiment into emotion
  let emotion = "Neutral";
  if (sentiment.compound >= 0.05) {
    emotion = "Positive";
  } else if (sentiment.compound <= -0.05) {
    emotion = "Negative";
  }

  res.json({ sentiment, emotion });
});

// Start server
app.listen(port, () => {
  console.log(`Backend is running on http://localhost:${port}`);
});

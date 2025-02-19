import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaRobot } from "react-icons/fa";
import axios from "axios";

export default function ChatbotGreeting() {
  const [userMessage, setUserMessage] = useState("");
  const [chatMessage, setChatMessage] = useState("");
  const [emotion, setEmotion] = useState("");
  const [sentimentScore, setSentimentScore] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChat = async () => {
    if (!userMessage.trim()) return;

    setLoading(true);
    try {
      // Send user message to backend for sentiment analysis
      const sentimentResponse = await axios.post("http://localhost:5000/analyze-sentiment", {
        userMessage,
      });

      const { sentiment, emotion, chatbotMessage } = sentimentResponse.data;

      setSentimentScore(sentiment.compound);
      setEmotion(emotion);

      // Send data to DeepSeek for final chatbot response
      const deepSeekResponse = await axios.post("http://localhost:8000/chat/", {
        messages: [{ role: "user", content: userMessage }],
        sentiment,
        emotion,
      });

      setChatMessage(deepSeekResponse.data.response);
    } catch (error) {
      console.error("Error:", error);
      setChatMessage("I'm sorry, I couldn't process that. Let's try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center space-y-4 p-6">
      {/* Chatbot Greeting */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="flex items-center space-x-3 bg-white/80 backdrop-blur-lg px-5 py-2 rounded-full shadow-lg"
      >
        <motion.div
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
        >
          <FaRobot className="text-blue-500 text-2xl" />
        </motion.div>

        <AnimatePresence mode="wait">
          <motion.span
            key={loading ? "loading" : chatMessage}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.6 }}
            className="text-gray-700 font-medium"
          >
            {loading ? "Thinking..." : chatMessage || "Hello! How can I help you today?"}
          </motion.span>
        </AnimatePresence>
      </motion.div>

      {/* Sentiment Analysis Display */}
      <div className="text-center text-gray-600">
        <p>Sentiment Score: {JSON.stringify(sentimentScore)}</p>
        <p>Detected Emotion: <strong>{emotion}</strong></p>
      </div>

      {/* User Message Input */}
      <div className="flex flex-col items-center space-y-2">
        <label className="text-gray-600 font-medium">
          Tell me more about how you're feeling:
        </label>
        <textarea
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          className="border border-gray-300 rounded px-4 py-2 w-full focus:outline-none"
          rows="4"
        />
      </div>

      {/* Submit and Clear Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={handleChat}
          disabled={loading || !userMessage.trim()}
          className={`${
            loading || !userMessage.trim()
              ? "bg-gray-300"
              : "bg-blue-500 hover:bg-blue-600"
          } text-white font-bold py-2 px-6 rounded-full`}
        >
          {loading ? "Processing..." : "Chat"}
        </button>

        <button
          onClick={() => setUserMessage("")}
          className="bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-6 rounded-full"
        >
          Clear
        </button>
      </div>
    </div>
  );
}

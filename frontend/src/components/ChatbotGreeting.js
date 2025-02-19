import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FaRobot } from "react-icons/fa";
import axios from "axios";

export default function ChatbotGreeting() {
  const [userMessage, setUserMessage] = useState("");
  const [chatMessage, setChatMessage] = useState("");
  const [emotion, setEmotion] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChat = async () => {
    if (!userMessage.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:8000/chat/", {
        userMessage,
      });

      const { response: botMessage, emotion } = response.data;
      setChatMessage(botMessage);
      setEmotion(emotion);
    } catch (error) {
      console.error("Error:", error);
      setChatMessage("I'm sorry, I couldn't process that. Let's try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1 }}
      className="flex items-center justify-center h-screen bg-gradient-to-br from-[#222831] to-[#393E46] text-white relative"
    >
      <motion.h1 className="absolute top-5 left-6 text-2xl font-bold text-[#00ADB5]">
        ChatBot
      </motion.h1>

      <motion.div className="w-[75%] h-[75vh] flex flex-col bg-[#EEEEEE]/10 backdrop-blur-lg p-6 rounded-2xl shadow-lg">
        <motion.h2 className="text-center text-lg text-gray-300 mb-2">
          💬 How can I help you today?
        </motion.h2>

        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="flex items-center space-x-3 bg-white/80 backdrop-blur-lg px-5 py-2 rounded-full shadow-lg self-center"
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

        <div className="text-center text-gray-400 my-4">
          <p>Detected Emotion: <strong>{emotion}</strong></p>
        </div>

        <div className="flex flex-col items-center space-y-3">
          <label className="text-gray-300 font-medium">
            Tell me more about how you're feeling:
          </label>
          <textarea
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            className="border border-gray-600 rounded px-4 py-2 w-full bg-[#222831] text-white focus:outline-none"
            rows="4"
          />
        </div>

        <div className="flex space-x-4 mt-4 justify-center">
          <button
            onClick={handleChat}
            disabled={loading || !userMessage.trim()}
            className={`${
              loading || !userMessage.trim()
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-[#0077FF] hover:bg-[#005BBB]"
            } text-white font-bold py-2 px-6 rounded-full`}
          >
            {loading ? "Processing..." : "Chat"}
          </button>

          <button
            onClick={() => setUserMessage("")}
            className="bg-gray-600 hover:bg-gray-500 text-white font-bold py-2 px-6 rounded-full"
          >
            Clear
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
//chat.jsx
import { askQuestion } from "../services/api";
import { useState } from "react";
import { useUpload } from "../context/UploadContext";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import UploadedDocuments from "../components/UploadedDocuments";

export default function Chat() {
  const { messages, setMessages, typing, setTyping } = useUpload();
  const [conversationId, setConversationId] = useState(null);

  const handleSend = async (text) => {
    if (!text?.trim() || typing) return;
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: text.trim(),
      },
    ]);

    setTyping(true);

    try {
      const response = await askQuestion(text.trim(), conversationId);
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response.answer,
          sources: response.sources || [],
        },
      ]);
    } catch (error) {
      console.error("AI request failed:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, there was an error processing your request. Please try again.",
        },
      ]);
    } finally {
      setTyping(false);
    }
  };

  const handleClearChat = () => {
    if (typing) return;
    setMessages([]);
  };

  return (
    <div className="flex h-full min-h-0 flex-col bg-slate-50">
      {/* Knowledge documents */}
      <UploadedDocuments />
      {/* Chat workspace */}
      <ChatWindow
        messages={messages}
        typing={typing}
        onClearChat={handleClearChat}
      />
      {/* Input */}
      <ChatInput onSend={handleSend} disabled={typing} />
    </div>
  );
}

import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  confidence?: number;
}

interface ChatPanelProps {
  storyId: string;
  apiBaseUrl: string;
}

export const ChatPanel: React.FC<ChatPanelProps> = ({ storyId, apiBaseUrl }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${apiBaseUrl}/chat`, {
        story_id: storyId,
        question: input,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        citations: response.data.citations || [],
        confidence: response.data.confidence,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('Chat error:', error);
      const detail =
        error?.response?.data?.detail || 'Could not get response from agent.';
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `❌ ${detail}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg">
        <h3 className="font-bold">🤖 GEMINI ASSISTANT</h3>
        <p className="text-sm text-blue-100">Ask about this story</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p>💬 No messages yet</p>
            <p className="text-sm">Try asking: "What is the consensus?"</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-4 py-2 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : 'bg-gray-200 text-gray-900 rounded-bl-none'
              }`}
            >
              <p className="text-sm">{msg.content}</p>

              {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                <div className="mt-2 text-xs text-gray-600 border-t pt-2">
                  <p className="font-bold">Sources:</p>
                  <p>{msg.citations.join(', ')}</p>
                </div>
              )}

              {msg.role === 'assistant' && msg.confidence && (
                <div className="mt-1 text-xs text-gray-600">
                  Confidence: {(msg.confidence * 100).toFixed(0)}%
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg rounded-bl-none">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4 bg-gray-50 rounded-b-lg">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
            placeholder="Type your question..."
            disabled={loading}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            Send
          </button>
        </div>

        <div className="mt-2 text-xs text-gray-600">
          <p>💡 Try: "What's the consensus?" or "What don't we know?"</p>
        </div>
      </div>
    </div>
  );
};

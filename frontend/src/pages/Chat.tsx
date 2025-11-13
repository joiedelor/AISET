/**
 * Chat Page
 * DO-178C Traceability: REQ-FRONTEND-012
 * Purpose: AI-powered requirements elicitation chat interface
 */

import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Send } from 'lucide-react'

export default function Chat() {
  const { projectId } = useParams<{ projectId: string }>()
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([])
  const [input, setInput] = useState('')

  const handleSend = () => {
    if (!input.trim()) return

    // Add user message
    setMessages([...messages, { role: 'user', content: input }])
    setInput('')

    // Simulate AI response (will be replaced with actual API call)
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'This is a placeholder AI response. The AI service will be integrated here.'
      }])
    }, 1000)
  }

  return (
    <div className="h-[calc(100vh-2rem)] flex flex-col p-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">AI Chat</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Requirements elicitation powered by AI
        </p>
      </div>

      {/* Messages Container */}
      <div className="flex-1 card overflow-y-auto mb-4">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
            Start a conversation to elicit requirements
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`p-4 rounded-lg ${
                  msg.role === 'user'
                    ? 'bg-blue-100 dark:bg-blue-900/20 ml-auto max-w-2xl'
                    : 'bg-gray-100 dark:bg-gray-700 mr-auto max-w-2xl'
                }`}
              >
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {msg.role === 'user' ? 'You' : 'AI Assistant'}
                </p>
                <p className="text-gray-900 dark:text-white">{msg.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="card p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Describe your system requirements..."
            className="input flex-1"
          />
          <button onClick={handleSend} className="btn-primary flex items-center gap-2">
            <Send className="w-4 h-4" />
            Send
          </button>
        </div>
      </div>
    </div>
  )
}

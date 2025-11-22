/**
 * Project Initialization Wizard
 * DO-178C Traceability: REQ-AI-032, REQ-AI-033, REQ-AI-034, REQ-AI-035, REQ-AI-036, REQ-AI-037
 * Purpose: AI-guided project initialization interview
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, CheckCircle, Loader2, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface InitializationContext {
  stage: 'initial' | 'foundation' | 'planning' | 'execution' | 'complete'
  data: Record<string, any>
  project_id?: number
  conversation_id?: number
}

export default function ProjectInitializationWizard() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Welcome to the AISET Project Initialization Wizard! I'll guide you through setting up your project with the right DO-178C/DO-254 configuration. Let's start: Can you describe the project as precisely as you can?"
    }
  ])
  const [input, setInput] = useState('')
  const [context, setContext] = useState<InitializationContext>({
    stage: 'initial',
    data: {}
  })
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isComplete, setIsComplete] = useState(false)

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage = input
    setInput('')
    setError(null)

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      // Call backend project initialization endpoint (REQ-AI-032)
      const response = await axios.post('/api/v1/projects/initialize', {
        user_input: userMessage,
        project_id: context.project_id || null,
        conversation_id: context.conversation_id || null,
        context: context.stage === 'initial' ? null : context
      })

      const data = response.data

      // Add AI response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.next_question
      }])

      // Update context with project_id and conversation_id from response
      setContext({
        stage: data.stage,
        data: data.context || {},
        project_id: data.project_id,
        conversation_id: data.conversation_id
      })

      // Check if interview is complete
      if (data.complete) {
        setIsComplete(true)
        // Optionally redirect to project after completion
        setTimeout(() => {
          navigate(`/projects/${data.project_id}`)
        }, 2000)
      }

    } catch (err: any) {
      console.error('Initialization error:', err)
      setError(err.response?.data?.detail || 'Failed to process your response. Please try again.')

      // Remove optimistically added user message
      setMessages(prev => prev.slice(0, -1))

      // Restore input
      setInput(userMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Project Initialization Wizard
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            AI-guided setup for DO-178C/DO-254 compliance
          </p>
        </div>

        {/* Progress Stages (REQ-AI-032) */}
        <div className="mb-8 card p-6">
          <div className="flex items-center justify-between">
            {['initial', 'foundation', 'planning', 'execution', 'complete'].map((stage, idx) => {
              const isActive = context.stage === stage
              const isPast = ['initial', 'foundation', 'planning', 'execution', 'complete'].indexOf(context.stage) > idx

              return (
                <div key={stage} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    isPast || isActive
                      ? 'border-blue-600 bg-blue-600 text-white'
                      : 'border-gray-300 text-gray-400'
                  }`}>
                    {isPast ? (
                      <CheckCircle className="w-6 h-6" />
                    ) : (
                      <span className="text-sm font-medium">{idx + 1}</span>
                    )}
                  </div>
                  <div className="ml-2 text-sm">
                    <p className={`font-medium ${isActive ? 'text-blue-600' : 'text-gray-600 dark:text-gray-400'}`}>
                      {stage.charAt(0).toUpperCase() + stage.slice(1)}
                    </p>
                  </div>
                  {idx < 4 && (
                    <div className={`w-12 h-0.5 mx-4 ${
                      isPast ? 'bg-blue-600' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {/* Conversation */}
        <div className="card mb-6 h-96 overflow-y-auto">
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
                  {msg.role === 'user' ? 'You' : 'AI Wizard'}
                </p>
                <p className="text-gray-900 dark:text-white">{msg.content}</p>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">AI is thinking...</span>
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        {!isComplete && (
          <div className="card p-4">
            {error && (
              <div className="mb-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            )}
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
                placeholder="Type your answer..."
                className="input flex-1"
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                className="btn-primary flex items-center gap-2"
                disabled={isLoading || !input.trim()}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Send
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Completion Message */}
        {isComplete && (
          <div className="card p-6 text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Project Initialized!
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              Your project has been configured with the appropriate DO-178C/DO-254 settings.
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-500">
              Redirecting to your project...
            </p>
          </div>
        )}

        {/* Info Panel - Interview Stages (REQ-AI-032 to REQ-AI-037) */}
        <div className="mt-6 card p-6 bg-blue-50 dark:bg-blue-900/10">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Interview Stages
          </h3>
          <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-start gap-2">
              <span className="font-medium min-w-24">Foundation:</span>
              <span>Safety criticality, DAL/SIL level, domain</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-medium min-w-24">Planning:</span>
              <span>Regulatory standards, development process, architecture</span>
            </div>
            <div className="flex items-start gap-2">
              <span className="font-medium min-w-24">Execution:</span>
              <span>Lifecycle phase, verification approach, team setup</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

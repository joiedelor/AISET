/**
 * Chat Page - Dual Interface
 * DO-178C Traceability: REQ-FE-008, REQ-FE-007, REQ-AI-017, REQ-AI-018, REQ-AI-019
 * Purpose: AI-powered requirements elicitation with dual-pane interface
 */

import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Send, FileText, Check, X, AlertTriangle, Loader2 } from 'lucide-react'
import { aiApi } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  validation?: {
    valid: boolean
    question_count: number
    issues: string[]
  }
}

interface ProposedChange {
  type: 'addition' | 'modification' | 'deletion'
  content: string
  section: string
  id: string
}

export default function Chat() {
  const { projectId } = useParams<{ projectId: string }>()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [proposedChanges, setProposedChanges] = useState<ProposedChange[]>([])
  const [documentContent, setDocumentContent] = useState<string>('')
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Initialize conversation on component mount (REQ-FE-007)
  useEffect(() => {
    const initConversation = async () => {
      if (!projectId) return

      try {
        const response = await aiApi.createConversation({
          project_id: parseInt(projectId),
          title: 'Requirements Elicitation Session'
        })
        setConversationId(response.data.conversation_id)
      } catch (err) {
        console.error('Failed to create conversation:', err)
        setError('Failed to initialize AI conversation')
      }
    }

    initConversation()
  }, [projectId])

  const handleSend = async () => {
    if (!input.trim() || !conversationId) return

    const userMessage = input
    setInput('')
    setError(null)

    // Add user message immediately for responsive UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      // Call real backend API (REQ-FE-007)
      const response = await aiApi.sendMessage(conversationId, userMessage)

      const aiResponse: Message = {
        role: 'assistant',
        content: response.data.message,
        validation: response.data.validation
      }

      setMessages(prev => [...prev, aiResponse])

      // TODO: Extract proposed changes from AI response
      // For now, simulate a simple requirement extraction
      if (userMessage.toLowerCase().includes('altitude') || userMessage.toLowerCase().includes('operate')) {
        setProposedChanges(prev => [...prev, {
          id: Date.now().toString(),
          type: 'addition',
          section: '3.1 Functional Requirements',
          content: `REQ-SYS-${String(prev.length + 1).padStart(3, '0')}: The system shall operate at specified altitude ranges as determined by user requirements.`
        }])
      }

    } catch (err: any) {
      console.error('Failed to send message:', err)
      setError(err.response?.data?.detail || 'Failed to get AI response')

      // Remove the optimistically added user message on error
      setMessages(prev => prev.slice(0, -1))

      // Restore input
      setInput(userMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleApproveChange = (changeId: string) => {
    // REQ-AI-017: User review and approval
    const change = proposedChanges.find(c => c.id === changeId)
    if (change) {
      setDocumentContent(prev => prev + '\n' + change.content)
      setProposedChanges(prev => prev.filter(c => c.id !== changeId))
    }
  }

  const handleRejectChange = (changeId: string) => {
    // REQ-AI-017: User can reject changes
    setProposedChanges(prev => prev.filter(c => c.id !== changeId))
  }

  return (
    <div className="h-[calc(100vh-2rem)] flex gap-4 p-8">
      {/* LEFT PANE: Chat Dialogue (REQ-FE-008) */}
      <div className="w-1/2 flex flex-col">
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <Send className="w-6 h-6" />
            Dialogue
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            AI-powered requirements elicitation
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
                <div key={idx}>
                  <div
                    className={`p-4 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-blue-100 dark:bg-blue-900/20 ml-auto max-w-xl'
                        : 'bg-gray-100 dark:bg-gray-700 mr-auto max-w-xl'
                    }`}
                  >
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {msg.role === 'user' ? 'You' : 'AI Assistant'}
                    </p>
                    <p className="text-gray-900 dark:text-white">{msg.content}</p>
                  </div>

                  {/* Validation Warning (REQ-AI-001) */}
                  {msg.role === 'assistant' && msg.validation && !msg.validation.valid && (
                    <div className="mt-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg flex items-start gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-600 dark:text-yellow-400 mt-0.5" />
                      <div className="text-sm">
                        <p className="font-medium text-yellow-800 dark:text-yellow-300">
                          Validation Warning
                        </p>
                        <p className="text-yellow-700 dark:text-yellow-400 text-xs mt-1">
                          {msg.validation.issues.join(', ')}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="card p-4">
          {error && (
            <div className="mb-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            </div>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
              placeholder={conversationId ? "Describe your system requirements..." : "Initializing conversation..."}
              className="input flex-1"
              disabled={isLoading || !conversationId}
            />
            <button
              onClick={handleSend}
              className="btn-primary flex items-center gap-2"
              disabled={isLoading || !conversationId || !input.trim()}
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
      </div>

      {/* RIGHT PANE: Document Proposal (REQ-FE-008) */}
      <div className="w-1/2 flex flex-col">
        <div className="mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            <FileText className="w-6 h-6" />
            Document Proposal
          </h2>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
            AI-generated requirements with change highlighting
          </p>
        </div>

        {/* Proposed Changes Section (REQ-AI-019: Highlighted Changes) */}
        {proposedChanges.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
              Pending Changes (Requires Approval)
            </h3>
            <div className="space-y-2">
              {proposedChanges.map((change) => (
                <div
                  key={change.id}
                  className={`card p-4 border-l-4 ${
                    change.type === 'addition'
                      ? 'border-l-green-500 bg-green-50 dark:bg-green-900/10'
                      : change.type === 'modification'
                      ? 'border-l-yellow-500 bg-yellow-50 dark:bg-yellow-900/10'
                      : 'border-l-red-500 bg-red-50 dark:bg-red-900/10'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                        {change.section}
                      </p>
                      <p className="text-sm text-gray-900 dark:text-white font-mono">
                        {change.content}
                      </p>
                      <span
                        className={`inline-block mt-2 px-2 py-1 text-xs font-medium rounded ${
                          change.type === 'addition'
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                            : change.type === 'modification'
                            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                        }`}
                      >
                        {change.type.toUpperCase()}
                      </span>
                    </div>

                    {/* REQ-AI-017: Explicit user approval required */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleApproveChange(change.id)}
                        className="p-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                        title="Approve change"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleRejectChange(change.id)}
                        className="p-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                        title="Reject change"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Approved Document Content */}
        <div className="flex-1 card overflow-y-auto">
          {documentContent ? (
            <div className="prose dark:prose-invert max-w-none">
              <pre className="whitespace-pre-wrap font-mono text-sm">
                {documentContent}
              </pre>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No approved requirements yet</p>
                <p className="text-xs mt-1">Start chatting to generate requirements</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

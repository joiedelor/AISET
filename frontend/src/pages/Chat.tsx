/**
 * Chat Page - Dual Interface
 * DO-178C Traceability: REQ-FE-008, REQ-FE-007, REQ-AI-017, REQ-AI-018, REQ-AI-019
 * Purpose: AI-powered requirements elicitation with dual-pane interface
 */

import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { Send, FileText, Check, X, AlertTriangle, Loader2, Edit3, RefreshCw } from 'lucide-react'
import { aiApi, approvalApi, Proposal, ApprovalRequest } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  validation?: {
    valid: boolean
    question_count: number
    issues: string[]
  }
}

// Modal for editing proposal before approval
interface EditModalProps {
  proposal: Proposal | null
  isOpen: boolean
  onClose: () => void
  onSave: (modifiedContent: string, rationale: string) => void
}

function EditModal({ proposal, isOpen, onClose, onSave }: EditModalProps) {
  const [content, setContent] = useState('')
  const [rationale, setRationale] = useState('')

  useEffect(() => {
    if (proposal) {
      setContent(proposal.proposed_content)
      setRationale('')
    }
  }, [proposal])

  if (!isOpen || !proposal) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
          Edit Proposal Before Approval
        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Content
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full h-40 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Modification Rationale (Required)
            </label>
            <textarea
              value={rationale}
              onChange={(e) => setRationale(e.target.value)}
              placeholder="Explain why you modified this proposal..."
              className="w-full h-20 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>
        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(content, rationale)}
            disabled={!rationale.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg disabled:opacity-50"
          >
            Save & Approve
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Chat() {
  const { projectId } = useParams<{ projectId: string }>()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [approvedContent, setApprovedContent] = useState<string[]>([])
  const [conversationId, setConversationId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [editingProposal, setEditingProposal] = useState<Proposal | null>(null)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const currentUser = 'user' // TODO: Get from auth context

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

      // After AI responds, automatically extract proposals if conversation has enough content
      // User can also manually click "Extract" button
      if (messages.length >= 2) {
        // Auto-extract proposals after a few exchanges
        setTimeout(() => handleExtractProposals(), 500)
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

  // Load proposals from backend (REQ-AI-017)
  const loadProposals = useCallback(async () => {
    if (!conversationId) return

    try {
      const response = await approvalApi.getConversationProposals(conversationId)
      setProposals(response.data.filter(p => p.status === 'pending'))
    } catch (err) {
      console.error('Failed to load proposals:', err)
    }
  }, [conversationId])

  // Extract proposals from conversation
  const handleExtractProposals = async () => {
    if (!conversationId) return

    setIsExtracting(true)
    try {
      const response = await approvalApi.extractProposals(conversationId)
      if (response.data.extracted_count > 0) {
        await loadProposals()
      }
    } catch (err) {
      console.error('Failed to extract proposals:', err)
      setError('Failed to extract proposals from conversation')
    } finally {
      setIsExtracting(false)
    }
  }

  // REQ-AI-017: User review and approval - APPROVE
  const handleApproveChange = async (proposalId: string) => {
    const proposal = proposals.find(p => p.id === proposalId)
    if (!proposal) return

    try {
      const request: ApprovalRequest = {
        decision: 'approved',
        rationale: 'Approved by user review',
        reviewed_by: currentUser
      }

      const response = await approvalApi.approveProposal(proposalId, request)

      // Add to approved content
      setApprovedContent(prev => [...prev, proposal.proposed_content])

      // Remove from proposals
      setProposals(prev => prev.filter(p => p.id !== proposalId))

    } catch (err: any) {
      console.error('Failed to approve proposal:', err)
      setError(err.response?.data?.detail || 'Failed to approve proposal')
    }
  }

  // REQ-AI-017: User can reject changes
  const handleRejectChange = async (proposalId: string) => {
    try {
      const request: ApprovalRequest = {
        decision: 'rejected',
        rationale: 'Rejected by user review',
        reviewed_by: currentUser
      }

      await approvalApi.approveProposal(proposalId, request)
      setProposals(prev => prev.filter(p => p.id !== proposalId))

    } catch (err: any) {
      console.error('Failed to reject proposal:', err)
      setError(err.response?.data?.detail || 'Failed to reject proposal')
    }
  }

  // REQ-AI-017: User can modify before approval
  const handleEditChange = (proposalId: string) => {
    const proposal = proposals.find(p => p.id === proposalId)
    if (proposal) {
      setEditingProposal(proposal)
      setIsEditModalOpen(true)
    }
  }

  // Handle save from edit modal
  const handleSaveEdit = async (modifiedContent: string, rationale: string) => {
    if (!editingProposal) return

    try {
      const request: ApprovalRequest = {
        decision: 'modified',
        modified_content: modifiedContent,
        rationale,
        reviewed_by: currentUser
      }

      await approvalApi.approveProposal(editingProposal.id, request)

      // Add modified content to approved
      setApprovedContent(prev => [...prev, modifiedContent])

      // Remove from proposals
      setProposals(prev => prev.filter(p => p.id !== editingProposal.id))

      // Close modal
      setIsEditModalOpen(false)
      setEditingProposal(null)

    } catch (err: any) {
      console.error('Failed to save edited proposal:', err)
      setError(err.response?.data?.detail || 'Failed to save edited proposal')
    }
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
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <FileText className="w-6 h-6" />
              Document Proposal
            </h2>
            <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">
              AI-generated requirements with change highlighting
            </p>
          </div>
          {/* Extract proposals button */}
          {conversationId && messages.length > 0 && (
            <button
              onClick={handleExtractProposals}
              disabled={isExtracting}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm disabled:opacity-50"
              title="Extract proposals from conversation"
            >
              {isExtracting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4" />
              )}
              Extract
            </button>
          )}
        </div>

        {/* Proposed Changes Section (REQ-AI-019: Highlighted Changes) */}
        {proposals.length > 0 && (
          <div className="mb-4">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
              Pending Changes ({proposals.length}) - Requires Approval (REQ-AI-017)
            </h3>
            <div className="space-y-2 max-h-[40vh] overflow-y-auto">
              {proposals.map((proposal) => (
                <div
                  key={proposal.id}
                  className={`card p-4 border-l-4 ${
                    proposal.change_type === 'addition'
                      ? 'border-l-green-500 bg-green-50 dark:bg-green-900/10'
                      : proposal.change_type === 'modification'
                      ? 'border-l-yellow-500 bg-yellow-50 dark:bg-yellow-900/10'
                      : 'border-l-red-500 bg-red-50 dark:bg-red-900/10'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-xs font-medium text-gray-600 dark:text-gray-400">
                          {proposal.section}
                        </p>
                        <span className="text-xs text-gray-500">
                          ({Math.round(proposal.confidence_score * 100)}% confidence)
                        </span>
                      </div>
                      <p className="text-sm text-gray-900 dark:text-white font-mono">
                        {proposal.proposed_content}
                      </p>
                      {proposal.rationale && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 italic">
                          Rationale: {proposal.rationale}
                        </p>
                      )}
                      <div className="flex items-center gap-2 mt-2">
                        <span
                          className={`inline-block px-2 py-1 text-xs font-medium rounded ${
                            proposal.change_type === 'addition'
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                              : proposal.change_type === 'modification'
                              ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                              : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                          }`}
                        >
                          {proposal.change_type.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">
                          {proposal.entity_type}
                        </span>
                      </div>
                    </div>

                    {/* REQ-AI-017: Explicit user approval required */}
                    {/* REQ-AI-018: No automatic approval - user must click */}
                    <div className="flex flex-col gap-2">
                      <button
                        onClick={() => handleApproveChange(proposal.id)}
                        className="p-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                        title="Approve change"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleEditChange(proposal.id)}
                        className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                        title="Edit before approving"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleRejectChange(proposal.id)}
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
          {approvedContent.length > 0 ? (
            <div className="prose dark:prose-invert max-w-none">
              <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Approved Requirements ({approvedContent.length})
              </h4>
              <div className="space-y-2">
                {approvedContent.map((content, idx) => (
                  <div key={idx} className="p-3 bg-green-50 dark:bg-green-900/10 border-l-4 border-l-green-500 rounded">
                    <pre className="whitespace-pre-wrap font-mono text-sm text-gray-900 dark:text-white">
                      {content}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No approved requirements yet</p>
                <p className="text-xs mt-1">Chat with AI, then click "Extract" to generate proposals</p>
                <p className="text-xs mt-1 text-yellow-600 dark:text-yellow-400">
                  REQ-AI-018: All changes require explicit user approval
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Edit Modal */}
      <EditModal
        proposal={editingProposal}
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false)
          setEditingProposal(null)
        }}
        onSave={handleSaveEdit}
      />
    </div>
  )
}

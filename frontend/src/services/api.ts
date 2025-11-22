/**
 * API Service
 * DO-178C Traceability: REQ-FRONTEND-006
 * Purpose: Backend API client with type safety
 */

import axios from 'axios'
import type {
  Project,
  Requirement,
  AIMessage,
  TraceabilityMatrix,
  DocumentExport,
  ValidationResult,
} from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Projects API
export const projectsApi = {
  list: () => api.get<Project[]>('/projects'),
  get: (id: number) => api.get<Project>(`/projects/${id}`),
  create: (data: Partial<Project>) => api.post<Project>('/projects', data),
}

// Requirements API
export const requirementsApi = {
  list: (projectId: number, params?: {
    status?: string
    type?: string
    priority?: string
  }) => api.get<Requirement[]>(`/projects/${projectId}/requirements`, { params }),
  get: (id: number) => api.get<Requirement>(`/requirements/${id}`),
  create: (data: Partial<Requirement>) => api.post<Requirement>('/requirements', data),
  approve: (id: number, approved_by: string, rationale?: string) =>
    api.post(`/requirements/${id}/approve`, { approved_by, rationale }),
  validate: (id: number) => api.post<ValidationResult>(`/requirements/${id}/validate`),
}

// AI Conversation API
export const aiApi = {
  createConversation: (data: { project_id: number; title?: string }) =>
    api.post<{ conversation_id: number }>('/conversations', data),
  sendMessage: (conversationId: number, message: string) =>
    api.post<{
      message: string
      conversation_id: number
      validation: {
        valid: boolean
        question_count: number
        issues: string[]
      }
    }>(`/conversations/${conversationId}/messages`, { message }),
  getMessages: (conversationId: number) =>
    api.get<AIMessage[]>(`/conversations/${conversationId}/messages`),
  extractRequirements: (conversationId: number) =>
    api.post(`/conversations/${conversationId}/extract`),
}

// Traceability API
export const traceabilityApi = {
  getMatrix: (projectId: number) =>
    api.get<TraceabilityMatrix>(`/projects/${projectId}/traceability-matrix`),
  createRequirementDesignTrace: (data: {
    requirement_id: number
    design_component_id: number
    rationale?: string
  }) => api.post('/traceability/requirement-design', data),
  createRequirementTestTrace: (data: {
    requirement_id: number
    test_case_id: number
    rationale?: string
  }) => api.post('/traceability/requirement-test', data),
  detectGaps: (projectId: number) =>
    api.post(`/projects/${projectId}/detect-gaps`),
  getCoverage: (requirementId: number) =>
    api.get(`/requirements/${requirementId}/coverage`),
}

// Documents API
export const documentsApi = {
  generateSRS: (projectId: number, generated_by: string = 'user') =>
    api.post<DocumentExport>(`/projects/${projectId}/generate-srs`, { generated_by }),
  generateRTM: (projectId: number, generated_by: string = 'user') =>
    api.post<DocumentExport>(`/projects/${projectId}/generate-rtm`, { generated_by }),
}

// Approval Workflow API (REQ-AI-017, REQ-AI-018, REQ-AI-019)
export interface Proposal {
  id: string
  change_type: 'addition' | 'modification' | 'deletion'
  entity_type: 'requirement' | 'design_component' | 'test_case'
  section: string
  original_content?: string
  proposed_content: string
  confidence_score: number
  rationale: string
  status: 'pending' | 'approved' | 'rejected' | 'modified'
  created_at: string
}

export interface ApprovalRequest {
  decision: 'approved' | 'rejected' | 'modified'
  modified_content?: string
  rationale: string
  reviewed_by: string
}

export interface ApprovalResponse {
  proposal_id: string
  decision: string
  reviewed_by: string
  reviewed_at: string
  created_entity_id?: number
  modified_content?: string
}

export const approvalApi = {
  // Get all pending proposals (REQ-AI-017)
  getPendingProposals: (conversationId?: number) =>
    api.get<Proposal[]>('/approval/proposals', {
      params: conversationId ? { conversation_id: conversationId } : undefined
    }),

  // Get proposal by ID
  getProposal: (proposalId: string) =>
    api.get<Proposal>(`/approval/proposals/${proposalId}`),

  // Get proposal diff for highlighting (REQ-AI-019)
  getProposalDiff: (proposalId: string) =>
    api.get<{
      id: string
      change_type: string
      entity_type: string
      section: string
      original?: string
      proposed: string
      rationale: string
      confidence: number
      highlight_class: string
    }>(`/approval/proposals/${proposalId}/diff`),

  // Approve or reject a proposal (REQ-AI-017, REQ-AI-018)
  approveProposal: (proposalId: string, request: ApprovalRequest) =>
    api.post<ApprovalResponse>(`/approval/proposals/${proposalId}/approve`, request),

  // Bulk approve/reject proposals
  bulkApprove: (proposalIds: string[], decision: string, rationale: string, reviewedBy: string) =>
    api.post<ApprovalResponse[]>('/approval/proposals/bulk-approve', {
      proposal_ids: proposalIds,
      decision,
      rationale,
      reviewed_by: reviewedBy
    }),

  // Get proposals for a conversation
  getConversationProposals: (conversationId: number, includeProcessed: boolean = false) =>
    api.get<Proposal[]>(`/approval/conversations/${conversationId}/proposals`, {
      params: { include_processed: includeProcessed }
    }),

  // Extract proposals from conversation
  extractProposals: (conversationId: number) =>
    api.post<{ extracted_count: number; proposals: Array<{ id: string; type: string; section: string; content: string }> }>(
      `/approval/conversations/${conversationId}/extract-proposals`
    ),
}

// Health API
export const healthApi = {
  check: () => api.get('/health'),
  version: () => api.get('/version'),
}

export default api

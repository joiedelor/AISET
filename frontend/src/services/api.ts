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

// Authentication API (REQ-BE-003, REQ-BE-004)
export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
  full_name?: string
}

export interface AuthToken {
  access_token: string
  token_type: string
  expires_in: number
}

export interface UserInfo {
  id: number
  username: string
  email: string
  full_name?: string
  role: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
}

export const authApi = {
  // Login with username and password
  login: (data: LoginRequest) =>
    api.post<AuthToken>('/auth/login', data),

  // Register new user
  register: (data: RegisterRequest) =>
    api.post<UserInfo>('/auth/register', data),

  // Get current user info
  me: () =>
    api.get<UserInfo>('/auth/me'),

  // Refresh access token
  refresh: () =>
    api.post<AuthToken>('/auth/refresh'),

  // Logout (client-side)
  logout: () =>
    api.post('/auth/logout'),

  // Verify token validity
  verify: () =>
    api.get<{ valid: boolean; user_id?: number; username?: string; role?: string }>('/auth/verify'),
}

// Add auth token to requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}

// Configuration Items API (REQ-AI-038, REQ-AI-039, REQ-AI-040)
export interface ConfigurationItemCreate {
  ci_identifier: string
  name: string
  ci_type?: string
  parent_id?: number | null
  description?: string
  part_number?: string
  revision?: string
  version?: string
  lifecycle_phase?: string
  control_level?: string
  status?: string
  criticality?: string
  supplier?: string
  notes?: string
}

export const configurationItemsApi = {
  // Get all CIs for a project
  list: (projectId: number, params?: { ci_type?: string; root_only?: boolean }) =>
    api.get(`/projects/${projectId}/configuration-items`, { params }),

  // Get product structure tree
  getProductStructure: (projectId: number) =>
    api.get(`/projects/${projectId}/product-structure`),

  // Get CI statistics
  getStatistics: (projectId: number) =>
    api.get(`/projects/${projectId}/ci-statistics`),

  // Create CI
  create: (projectId: number, data: ConfigurationItemCreate) =>
    api.post(`/projects/${projectId}/configuration-items`, data),

  // Get single CI
  get: (ciId: number) =>
    api.get(`/configuration-items/${ciId}`),

  // Update CI
  update: (ciId: number, data: Partial<ConfigurationItemCreate>) =>
    api.put(`/configuration-items/${ciId}`, data),

  // Delete CI
  delete: (ciId: number) =>
    api.delete(`/configuration-items/${ciId}`),

  // Get CI children
  getChildren: (ciId: number) =>
    api.get(`/configuration-items/${ciId}/children`),

  // Classify CI
  classify: (ciId: number) =>
    api.get(`/configuration-items/${ciId}/classify`),

  // BOM operations
  getBOM: (ciId: number, bomType?: string) =>
    api.get(`/configuration-items/${ciId}/bom`, { params: bomType ? { bom_type: bomType } : undefined }),

  addBOMEntry: (ciId: number, data: {
    parent_ci_id: number
    child_ci_id: number
    quantity?: number
    bom_type?: string
    unit_of_measure?: string
    position_reference?: string
    find_number?: string
    is_alternate?: boolean
    notes?: string
  }) =>
    api.post(`/configuration-items/${ciId}/bom`, data),

  getWhereUsed: (ciId: number) =>
    api.get(`/configuration-items/${ciId}/where-used`),

  deleteBOMEntry: (bomId: number) =>
    api.delete(`/bom/${bomId}`),
}

export default api

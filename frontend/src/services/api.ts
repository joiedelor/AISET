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
    api.post<{ message: string }>(`/conversations/${conversationId}/messages`, { message }),
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

// Health API
export const healthApi = {
  check: () => api.get('/health'),
  version: () => api.get('/version'),
}

export default api

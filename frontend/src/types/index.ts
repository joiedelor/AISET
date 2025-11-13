/**
 * TypeScript Type Definitions
 * DO-178C Traceability: REQ-FRONTEND-005
 * Purpose: Type-safe data structures for frontend
 */

export enum RequirementType {
  FUNCTIONAL = 'functional',
  PERFORMANCE = 'performance',
  INTERFACE = 'interface',
  SAFETY = 'safety',
  SECURITY = 'security',
  OPERATIONAL = 'operational',
  DESIGN_CONSTRAINT = 'design_constraint',
  DATA = 'data',
}

export enum RequirementPriority {
  CRITICAL = 'critical',
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum RequirementStatus {
  DRAFT = 'draft',
  PENDING_REVIEW = 'pending_review',
  APPROVED = 'approved',
  IMPLEMENTED = 'implemented',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  OBSOLETE = 'obsolete',
}

export enum TestType {
  UNIT = 'unit',
  INTEGRATION = 'integration',
  SYSTEM = 'system',
  ACCEPTANCE = 'acceptance',
  REGRESSION = 'regression',
  PERFORMANCE = 'performance',
  SECURITY = 'security',
}

export enum TestStatus {
  NOT_RUN = 'not_run',
  PASSED = 'passed',
  FAILED = 'failed',
  BLOCKED = 'blocked',
  SKIPPED = 'skipped',
}

export enum MessageRole {
  USER = 'user',
  ASSISTANT = 'assistant',
  SYSTEM = 'system',
}

export interface Project {
  id: number
  name: string
  description?: string
  project_code: string
  certification_level: string
  industry?: string
  status: string
  created_by: string
  created_at: string
  updated_at?: string
}

export interface Requirement {
  id: number
  requirement_id: string
  title: string
  description: string
  type: RequirementType
  priority: RequirementPriority
  status: RequirementStatus
  parent_id?: number
  confidence_score: number
  rationale?: string
  acceptance_criteria?: string
  created_at: string
  created_by: string
  approved_by?: string
  approved_at?: string
}

export interface DesignComponent {
  id: number
  component_id: string
  name: string
  description: string
  type: string
  status: string
  parent_id?: number
  implementation_notes?: string
  file_path?: string
  created_at: string
}

export interface TestCase {
  id: number
  test_id: string
  title: string
  description: string
  type: TestType
  status: TestStatus
  preconditions?: string
  test_steps?: string
  expected_result?: string
  actual_result?: string
  is_automated: boolean
  created_at: string
}

export interface AIMessage {
  id: number
  role: MessageRole
  content: string
  created_at: string
}

export interface AIConversation {
  id: number
  project_id: number
  title: string
  purpose: string
  status: string
  ai_service: string
  model_name: string
  started_at: string
  completed_at?: string
}

export interface TraceabilityMatrix {
  matrix: TraceabilityRow[]
  statistics: TraceabilityStatistics
}

export interface TraceabilityRow {
  requirement_id: string
  title: string
  type: string
  priority: string
  status: string
  design_components: Array<{
    id: string
    name: string
    trace_type: string
  }>
  test_cases: Array<{
    id: string
    title: string
    status: string
    trace_type: string
  }>
  design_coverage: boolean
  test_coverage: boolean
  fully_traced: boolean
}

export interface TraceabilityStatistics {
  total_requirements: number
  fully_traced: number
  with_design_coverage: number
  with_test_coverage: number
  coverage_percentage: number
  design_coverage_percentage: number
  test_coverage_percentage: number
}

export interface DocumentExport {
  document_id: number
  file_path: string
  file_hash: string
  generated_at: string
}

export interface ValidationResult {
  is_valid: boolean
  issues: string[]
  warnings: string[]
  quality_score: number
}

export interface TraceabilityGap {
  type: string
  severity: string
  description: string
}

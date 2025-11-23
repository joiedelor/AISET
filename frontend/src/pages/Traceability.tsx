/**
 * Traceability Page
 * DO-178C Traceability: REQ-FE-012, REQ-FRONTEND-013
 * Purpose: Interactive traceability matrix with gap detection visualization
 */

import { useState, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { traceabilityApi } from '../services/api'
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Filter,
  RefreshCw,
  ChevronDown,
  ChevronRight,
  Search,
  Download,
  AlertCircle,
  Link2,
  FileCode,
  TestTube,
  BarChart3,
} from 'lucide-react'

// Gap type from backend
interface Gap {
  type: string
  severity: string
  description: string
}

interface GapsResponse {
  project_id: number
  gaps_found: number
  gaps: Gap[]
}

// Filter options
type StatusFilter = 'all' | 'fully_traced' | 'partial' | 'not_traced'
type TypeFilter = 'all' | 'functional' | 'non_functional' | 'interface' | 'constraint'

export default function Traceability() {
  const { projectId } = useParams<{ projectId: string }>()
  const queryClient = useQueryClient()

  // State
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())
  const [showGaps, setShowGaps] = useState(false)
  const [activeTab, setActiveTab] = useState<'matrix' | 'gaps' | 'statistics'>('matrix')

  // Fetch traceability matrix
  const { data: matrix, isLoading, refetch } = useQuery({
    queryKey: ['traceability', projectId],
    queryFn: async () => {
      const response = await traceabilityApi.getMatrix(Number(projectId))
      return response.data
    },
    enabled: !!projectId,
  })

  // Fetch gaps
  const { data: gapsData, isLoading: gapsLoading } = useQuery({
    queryKey: ['traceability-gaps', projectId],
    queryFn: async () => {
      const response = await traceabilityApi.detectGaps(Number(projectId))
      return response.data as GapsResponse
    },
    enabled: !!projectId && showGaps,
  })

  // Detect gaps mutation
  const detectGapsMutation = useMutation({
    mutationFn: () => traceabilityApi.detectGaps(Number(projectId)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['traceability-gaps', projectId] })
      setShowGaps(true)
      setActiveTab('gaps')
    },
  })

  // Filter and search the matrix
  const filteredMatrix = useMemo(() => {
    if (!matrix?.matrix) return []

    return matrix.matrix.filter((row) => {
      // Status filter
      if (statusFilter === 'fully_traced' && !row.fully_traced) return false
      if (statusFilter === 'partial' && (row.fully_traced || (!row.design_coverage && !row.test_coverage))) return false
      if (statusFilter === 'not_traced' && (row.design_coverage || row.test_coverage)) return false

      // Type filter
      if (typeFilter !== 'all' && row.type !== typeFilter) return false

      // Search filter
      if (searchTerm) {
        const term = searchTerm.toLowerCase()
        return (
          row.requirement_id.toLowerCase().includes(term) ||
          row.title.toLowerCase().includes(term)
        )
      }

      return true
    })
  }, [matrix, statusFilter, typeFilter, searchTerm])

  // Toggle row expansion
  const toggleRow = (reqId: string) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(reqId)) {
      newExpanded.delete(reqId)
    } else {
      newExpanded.add(reqId)
    }
    setExpandedRows(newExpanded)
  }

  // Export matrix as CSV
  const exportCSV = () => {
    if (!matrix?.matrix) return

    const headers = ['Requirement ID', 'Title', 'Type', 'Priority', 'Design Components', 'Test Cases', 'Status']
    const rows = matrix.matrix.map(row => [
      row.requirement_id,
      `"${row.title.replace(/"/g, '""')}"`,
      row.type,
      row.priority,
      row.design_components.map(d => d.id).join('; '),
      row.test_cases.map(t => t.id).join('; '),
      row.fully_traced ? 'Fully Traced' : row.design_coverage || row.test_coverage ? 'Partial' : 'Not Traced'
    ])

    const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `traceability-matrix-${projectId}.csv`
    a.click()
  }

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50 dark:bg-red-900/20'
      case 'high': return 'text-orange-600 bg-orange-50 dark:bg-orange-900/20'
      case 'medium': return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20'
      case 'low': return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20'
      default: return 'text-gray-600 bg-gray-50 dark:bg-gray-900/20'
    }
  }

  // Get gap type icon
  const getGapIcon = (type: string) => {
    switch (type) {
      case 'missing_design': return <FileCode className="w-4 h-4" />
      case 'missing_test': return <TestTube className="w-4 h-4" />
      case 'orphan_design': return <Link2 className="w-4 h-4" />
      case 'orphan_test': return <Link2 className="w-4 h-4" />
      default: return <AlertCircle className="w-4 h-4" />
    }
  }

  const stats = matrix?.statistics

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mr-2" />
        <span>Loading traceability matrix...</span>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Traceability Matrix</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            DO-178C compliant requirements traceability with gap detection
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => detectGapsMutation.mutate()}
            disabled={detectGapsMutation.isPending}
            className="btn btn-secondary flex items-center gap-2"
          >
            {detectGapsMutation.isPending ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <AlertTriangle className="w-4 h-4" />
            )}
            Detect Gaps
          </button>
          <button onClick={exportCSV} className="btn btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export CSV
          </button>
          <button onClick={() => refetch()} className="btn btn-primary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
        <nav className="flex gap-4">
          <button
            onClick={() => setActiveTab('matrix')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'matrix'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <Link2 className="w-4 h-4 inline mr-2" />
            Matrix View
          </button>
          <button
            onClick={() => setActiveTab('gaps')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'gaps'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <AlertTriangle className="w-4 h-4 inline mr-2" />
            Gap Analysis
            {gapsData && gapsData.gaps_found > 0 && (
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-600">
                {gapsData.gaps_found}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('statistics')}
            className={`pb-3 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'statistics'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            <BarChart3 className="w-4 h-4 inline mr-2" />
            Statistics
          </button>
        </nav>
      </div>

      {/* Statistics Cards - Always visible */}
      {stats && activeTab === 'statistics' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Requirements</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-white mt-1">
              {stats.total_requirements}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400">Fully Traced</p>
            <p className="text-3xl font-bold text-green-600 mt-1">{stats.fully_traced}</p>
            <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all"
                style={{ width: `${stats.coverage_percentage}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">{stats.coverage_percentage.toFixed(1)}%</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400">Design Coverage</p>
            <p className="text-3xl font-bold text-blue-600 mt-1">{stats.with_design_coverage}</p>
            <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${stats.design_coverage_percentage}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">{stats.design_coverage_percentage.toFixed(1)}%</p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400">Test Coverage</p>
            <p className="text-3xl font-bold text-purple-600 mt-1">{stats.with_test_coverage}</p>
            <div className="mt-2 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-purple-600 h-2 rounded-full transition-all"
                style={{ width: `${stats.test_coverage_percentage}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">{stats.test_coverage_percentage.toFixed(1)}%</p>
          </div>
        </div>
      )}

      {/* Gap Analysis Tab */}
      {activeTab === 'gaps' && (
        <div className="card">
          {gapsLoading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mr-2" />
              <span>Analyzing gaps...</span>
            </div>
          ) : gapsData && gapsData.gaps.length > 0 ? (
            <div>
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {gapsData.gaps_found} Traceability Gaps Detected
                </h3>
                <div className="flex gap-2 text-sm">
                  <span className="px-2 py-1 rounded bg-red-100 text-red-600">
                    Critical: {gapsData.gaps.filter(g => g.severity === 'critical').length}
                  </span>
                  <span className="px-2 py-1 rounded bg-orange-100 text-orange-600">
                    High: {gapsData.gaps.filter(g => g.severity === 'high').length}
                  </span>
                  <span className="px-2 py-1 rounded bg-yellow-100 text-yellow-600">
                    Medium: {gapsData.gaps.filter(g => g.severity === 'medium').length}
                  </span>
                  <span className="px-2 py-1 rounded bg-blue-100 text-blue-600">
                    Low: {gapsData.gaps.filter(g => g.severity === 'low').length}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                {gapsData.gaps.map((gap, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg flex items-start gap-3 ${getSeverityColor(gap.severity)}`}
                  >
                    <div className="flex-shrink-0 mt-0.5">{getGapIcon(gap.type)}</div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium capitalize">
                          {gap.type.replace(/_/g, ' ')}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getSeverityColor(gap.severity)}`}>
                          {gap.severity}
                        </span>
                      </div>
                      <p className="text-sm mt-1">{gap.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No Gaps Detected
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                All requirements have complete traceability coverage.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Matrix Tab */}
      {activeTab === 'matrix' && (
        <>
          {/* Filters */}
          <div className="card mb-6">
            <div className="flex flex-wrap gap-4 items-center">
              <div className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filters:</span>
              </div>

              {/* Search */}
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search requirements..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-sm"
                />
              </div>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-sm"
              >
                <option value="all">All Status</option>
                <option value="fully_traced">Fully Traced</option>
                <option value="partial">Partial Coverage</option>
                <option value="not_traced">Not Traced</option>
              </select>

              {/* Type Filter */}
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value as TypeFilter)}
                className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-sm"
              >
                <option value="all">All Types</option>
                <option value="functional">Functional</option>
                <option value="non_functional">Non-Functional</option>
                <option value="interface">Interface</option>
                <option value="constraint">Constraint</option>
              </select>

              {/* Results count */}
              <span className="text-sm text-gray-500">
                Showing {filteredMatrix.length} of {matrix?.matrix.length || 0}
              </span>
            </div>
          </div>

          {/* Matrix Table */}
          {filteredMatrix.length > 0 ? (
            <div className="card">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300 w-8"></th>
                      <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Req ID</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Title</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Type</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Priority</th>
                      <th className="text-center py-3 px-4 font-medium text-gray-700 dark:text-gray-300">
                        <FileCode className="w-4 h-4 inline mr-1" />
                        Design
                      </th>
                      <th className="text-center py-3 px-4 font-medium text-gray-700 dark:text-gray-300">
                        <TestTube className="w-4 h-4 inline mr-1" />
                        Tests
                      </th>
                      <th className="text-center py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredMatrix.map((row) => (
                      <>
                        <tr
                          key={row.requirement_id}
                          className={`border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer ${
                            !row.fully_traced && !row.design_coverage && !row.test_coverage
                              ? 'bg-red-50/50 dark:bg-red-900/10'
                              : ''
                          }`}
                          onClick={() => toggleRow(row.requirement_id)}
                        >
                          <td className="py-3 px-4">
                            {(row.design_components.length > 0 || row.test_cases.length > 0) && (
                              expandedRows.has(row.requirement_id) ? (
                                <ChevronDown className="w-4 h-4 text-gray-500" />
                              ) : (
                                <ChevronRight className="w-4 h-4 text-gray-500" />
                              )
                            )}
                          </td>
                          <td className="py-3 px-4 font-mono text-sm text-gray-900 dark:text-white">
                            {row.requirement_id}
                          </td>
                          <td className="py-3 px-4 text-gray-900 dark:text-white max-w-xs truncate">
                            {row.title}
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              row.type === 'functional' ? 'bg-blue-100 text-blue-700' :
                              row.type === 'non_functional' ? 'bg-purple-100 text-purple-700' :
                              row.type === 'interface' ? 'bg-green-100 text-green-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {row.type}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-center">
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              row.priority === 'critical' ? 'bg-red-100 text-red-700' :
                              row.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                              row.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-gray-100 text-gray-700'
                            }`}>
                              {row.priority}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-center">
                            {row.design_coverage ? (
                              <span className="inline-flex items-center gap-1 text-green-600">
                                <CheckCircle className="w-4 h-4" />
                                <span className="text-sm">{row.design_components.length}</span>
                              </span>
                            ) : (
                              <XCircle className="w-4 h-4 text-red-500 mx-auto" />
                            )}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {row.test_coverage ? (
                              <span className="inline-flex items-center gap-1 text-green-600">
                                <CheckCircle className="w-4 h-4" />
                                <span className="text-sm">{row.test_cases.length}</span>
                              </span>
                            ) : (
                              <XCircle className="w-4 h-4 text-red-500 mx-auto" />
                            )}
                          </td>
                          <td className="py-3 px-4 text-center">
                            {row.fully_traced ? (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs">
                                <CheckCircle className="w-3 h-3" />
                                Complete
                              </span>
                            ) : row.design_coverage || row.test_coverage ? (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-yellow-100 text-yellow-700 text-xs">
                                <AlertTriangle className="w-3 h-3" />
                                Partial
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-red-100 text-red-700 text-xs">
                                <XCircle className="w-3 h-3" />
                                Missing
                              </span>
                            )}
                          </td>
                        </tr>
                        {/* Expanded row details */}
                        {expandedRows.has(row.requirement_id) && (
                          <tr className="bg-gray-50 dark:bg-gray-800/50">
                            <td colSpan={8} className="px-8 py-4">
                              <div className="grid grid-cols-2 gap-6">
                                {/* Design Components */}
                                <div>
                                  <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                                    <FileCode className="w-4 h-4" />
                                    Design Components ({row.design_components.length})
                                  </h4>
                                  {row.design_components.length > 0 ? (
                                    <ul className="space-y-1">
                                      {row.design_components.map((dc, idx) => (
                                        <li key={idx} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                                          <span className="font-mono bg-blue-100 dark:bg-blue-900/30 px-2 py-0.5 rounded">
                                            {dc.id}
                                          </span>
                                          <span>{dc.name}</span>
                                          <span className="text-xs text-gray-400">({dc.trace_type})</span>
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <p className="text-sm text-red-500 italic">No design components linked</p>
                                  )}
                                </div>
                                {/* Test Cases */}
                                <div>
                                  <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                                    <TestTube className="w-4 h-4" />
                                    Test Cases ({row.test_cases.length})
                                  </h4>
                                  {row.test_cases.length > 0 ? (
                                    <ul className="space-y-1">
                                      {row.test_cases.map((tc, idx) => (
                                        <li key={idx} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                                          <span className="font-mono bg-purple-100 dark:bg-purple-900/30 px-2 py-0.5 rounded">
                                            {tc.id}
                                          </span>
                                          <span>{tc.title}</span>
                                          <span className={`text-xs px-1.5 py-0.5 rounded ${
                                            tc.status === 'passed' ? 'bg-green-100 text-green-700' :
                                            tc.status === 'failed' ? 'bg-red-100 text-red-700' :
                                            'bg-gray-100 text-gray-700'
                                          }`}>
                                            {tc.status}
                                          </span>
                                        </li>
                                      ))}
                                    </ul>
                                  ) : (
                                    <p className="text-sm text-red-500 italic">No test cases linked</p>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        )}
                      </>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="card text-center py-12">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                {matrix?.matrix.length === 0 ? 'No traceability data yet' : 'No matching requirements'}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {matrix?.matrix.length === 0
                  ? 'Create requirements and link them to design and tests'
                  : 'Try adjusting your filters'}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}

/**
 * Requirements Page
 * DO-178C Traceability: REQ-FRONTEND-011
 * Purpose: Requirements listing and management
 */

import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { requirementsApi } from '../services/api'
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react'

export default function Requirements() {
  const { projectId } = useParams<{ projectId: string }>()

  const { data: requirements, isLoading } = useQuery({
    queryKey: ['requirements', projectId],
    queryFn: async () => {
      const response = await requirementsApi.list(Number(projectId))
      return response.data
    },
    enabled: !!projectId,
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'approved':
      case 'verified':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'draft':
      case 'pending_review':
        return <Clock className="w-4 h-4 text-yellow-600" />
      case 'rejected':
        return <AlertTriangle className="w-4 h-4 text-red-600" />
      default:
        return null
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (isLoading) {
    return <div className="p-8">Loading requirements...</div>
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Requirements</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            System requirements with DO-178C compliance
          </p>
        </div>
        <button className="btn-primary">New Requirement</button>
      </div>

      {requirements && requirements.length > 0 ? (
        <div className="card">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">ID</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Title</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Type</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Priority</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {requirements.map((req) => (
                  <tr
                    key={req.id}
                    className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <td className="py-3 px-4 font-mono text-sm text-gray-900 dark:text-white">
                      {req.requirement_id}
                    </td>
                    <td className="py-3 px-4 text-gray-900 dark:text-white">
                      {req.title}
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {req.type}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(req.priority)}`}>
                        {req.priority}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(req.status)}
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {req.status.replace('_', ' ')}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {(req.confidence_score * 100).toFixed(0)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="card text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No requirements yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Start a conversation with AI or create requirements manually
          </p>
          <button className="btn-primary">Create Requirement</button>
        </div>
      )}
    </div>
  )
}

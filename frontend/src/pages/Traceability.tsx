/**
 * Traceability Page
 * DO-178C Traceability: REQ-FRONTEND-013
 * Purpose: Traceability matrix and coverage visualization
 */

import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { traceabilityApi } from '../services/api'
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react'

export default function Traceability() {
  const { projectId } = useParams<{ projectId: string }>()

  const { data: matrix, isLoading } = useQuery({
    queryKey: ['traceability', projectId],
    queryFn: async () => {
      const response = await traceabilityApi.getMatrix(Number(projectId))
      return response.data
    },
    enabled: !!projectId,
  })

  if (isLoading) {
    return <div className="p-8">Loading traceability matrix...</div>
  }

  const stats = matrix?.statistics

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Traceability Matrix</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          DO-178C compliant requirements traceability
        </p>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Requirements</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              {stats.total_requirements}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400">Fully Traced</p>
            <p className="text-2xl font-bold text-green-600 mt-1">
              {stats.fully_traced}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {stats.coverage_percentage.toFixed(1)}%
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400">Design Coverage</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">
              {stats.with_design_coverage}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {stats.design_coverage_percentage.toFixed(1)}%
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 dark:text-gray-400">Test Coverage</p>
            <p className="text-2xl font-bold text-purple-600 mt-1">
              {stats.with_test_coverage}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {stats.test_coverage_percentage.toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      {/* Matrix Table */}
      {matrix && matrix.matrix.length > 0 ? (
        <div className="card">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Req ID</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Title</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Design</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Tests</th>
                  <th className="text-center py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Status</th>
                </tr>
              </thead>
              <tbody>
                {matrix.matrix.map((row) => (
                  <tr
                    key={row.requirement_id}
                    className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <td className="py-3 px-4 font-mono text-sm text-gray-900 dark:text-white">
                      {row.requirement_id}
                    </td>
                    <td className="py-3 px-4 text-gray-900 dark:text-white">
                      {row.title.slice(0, 50)}...
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {row.design_components.length > 0
                          ? row.design_components.map(d => d.id).join(', ')
                          : '-'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {row.test_cases.length > 0
                          ? row.test_cases.map(t => t.id).join(', ')
                          : '-'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      {row.fully_traced ? (
                        <CheckCircle className="w-5 h-5 text-green-600 mx-auto" />
                      ) : row.design_coverage || row.test_coverage ? (
                        <AlertTriangle className="w-5 h-5 text-yellow-600 mx-auto" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600 mx-auto" />
                      )}
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
            No traceability data yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            Create requirements and link them to design and tests
          </p>
        </div>
      )}
    </div>
  )
}

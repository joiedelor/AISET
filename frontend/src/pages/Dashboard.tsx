/**
 * Dashboard Page
 * DO-178C Traceability: REQ-FRONTEND-008
 * Purpose: Main dashboard with project overview
 */

import { useQuery } from '@tanstack/react-query'
import { projectsApi, healthApi } from '../services/api'
import { FolderOpen, CheckCircle, AlertTriangle, Activity } from 'lucide-react'

export default function Dashboard() {
  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectsApi.list()
      return response.data
    },
  })

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await healthApi.check()
      return response.data
    },
  })

  const stats = [
    {
      name: 'Total Projects',
      value: projects?.length || 0,
      icon: FolderOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'Active Projects',
      value: projects?.filter(p => p.status === 'active').length || 0,
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'System Status',
      value: health?.status === 'operational' ? 'Healthy' : 'Issue',
      icon: health?.status === 'operational' ? CheckCircle : AlertTriangle,
      color: health?.status === 'operational' ? 'text-green-600' : 'text-red-600',
      bgColor: health?.status === 'operational' ? 'bg-green-100' : 'bg-red-100',
    },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          AI-powered systems engineering with DO-178C compliance
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                    {stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* DO-178C Compliance Status */}
      {health && (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            DO-178C Compliance Configuration
          </h2>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Audit Trail</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                health.do178c_compliance.audit_trail
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {health.do178c_compliance.audit_trail ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Approval Workflow</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                health.do178c_compliance.approval_workflow
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {health.do178c_compliance.approval_workflow ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">Traceability Strict Mode</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${
                health.do178c_compliance.traceability_strict
                  ? 'bg-green-100 text-green-800'
                  : 'bg-red-100 text-red-800'
              }`}>
                {health.do178c_compliance.traceability_strict ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Recent Projects */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Recent Projects
        </h2>
        {projects && projects.length > 0 ? (
          <div className="space-y-2">
            {projects.slice(0, 5).map((project) => (
              <div
                key={project.id}
                className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-md transition-colors"
              >
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{project.name}</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{project.project_code}</p>
                </div>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                  Level {project.certification_level}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 dark:text-gray-400">No projects yet. Create your first project to get started.</p>
        )}
      </div>
    </div>
  )
}

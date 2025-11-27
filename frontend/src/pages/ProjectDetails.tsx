/**
 * Project Details Page
 * DO-178C Traceability: REQ-FRONTEND-010
 * Purpose: Detailed project view with navigation to sub-sections
 */

import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { projectsApi } from '../services/api'
import { FileText, GitBranch, MessageSquare, FileCheck, Network, Workflow } from 'lucide-react'

export default function ProjectDetails() {
  const { projectId } = useParams<{ projectId: string }>()

  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: async () => {
      const response = await projectsApi.get(Number(projectId))
      return response.data
    },
    enabled: !!projectId,
  })

  if (isLoading) {
    return <div className="p-8">Loading project...</div>
  }

  if (!project) {
    return <div className="p-8">Project not found</div>
  }

  const sections = [
    {
      name: 'Requirements',
      description: 'Manage system requirements',
      href: `/projects/${projectId}/requirements`,
      icon: FileText,
      color: 'bg-blue-100 text-blue-600',
    },
    {
      name: 'AI Chat',
      description: 'Requirements elicitation with AI',
      href: `/projects/${projectId}/chat`,
      icon: MessageSquare,
      color: 'bg-purple-100 text-purple-600',
    },
    {
      name: 'Product Structure',
      description: 'Product structure & BOM management',
      href: `/projects/${projectId}/product-structure`,
      icon: Network,
      color: 'bg-cyan-100 text-cyan-600',
    },
    {
      name: 'Process Management',
      description: 'Development process state machines',
      href: `/projects/${projectId}/process-management`,
      icon: Workflow,
      color: 'bg-indigo-100 text-indigo-600',
    },
    {
      name: 'Traceability',
      description: 'Traceability matrix and coverage',
      href: `/projects/${projectId}/traceability`,
      icon: GitBranch,
      color: 'bg-green-100 text-green-600',
    },
    {
      name: 'Documents',
      description: 'Generate certification artifacts',
      href: `/projects/${projectId}/documents`,
      icon: FileCheck,
      color: 'bg-orange-100 text-orange-600',
    },
  ]

  return (
    <div className="p-8">
      {/* Project Header */}
      <div className="card mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {project.name}
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          {project.description || 'No description'}
        </p>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-gray-600 dark:text-gray-400">
            <strong>Code:</strong> {project.project_code}
          </span>
          <span className="text-gray-600 dark:text-gray-400">
            <strong>Certification:</strong> DO-178C Level {project.certification_level}
          </span>
          <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
            {project.status}
          </span>
        </div>
      </div>

      {/* Section Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {sections.map((section) => {
          const Icon = section.icon
          return (
            <Link
              key={section.name}
              to={section.href}
              className="card hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${section.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                    {section.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {section.description}
                  </p>
                </div>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}

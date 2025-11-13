/**
 * Projects Page
 * DO-178C Traceability: REQ-FRONTEND-009
 * Purpose: Projects listing and management
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { projectsApi } from '../services/api'
import { Plus, FolderOpen } from 'lucide-react'

export default function Projects() {
  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectsApi.list()
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="text-center">Loading projects...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your systems engineering projects
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Project
        </button>
      </div>

      {projects && projects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="card hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                  <FolderOpen className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                  {project.status}
                </span>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {project.name}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                {project.description || 'No description'}
              </p>

              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>{project.project_code}</span>
                <span>Level {project.certification_level}</span>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <FolderOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No projects yet
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Get started by creating your first project
          </p>
          <button className="btn-primary">
            Create Project
          </button>
        </div>
      )}
    </div>
  )
}

/**
 * Documents Page
 * DO-178C Traceability: REQ-FRONTEND-014
 * Purpose: Generate and manage certification documents
 */

import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { documentsApi } from '../services/api'
import { FileText, Download, CheckCircle } from 'lucide-react'

export default function Documents() {
  const { projectId } = useParams<{ projectId: string }>()
  const [generating, setGenerating] = useState<string | null>(null)

  const generateSRS = useMutation({
    mutationFn: () => documentsApi.generateSRS(Number(projectId)),
    onSuccess: () => {
      setGenerating(null)
      alert('SRS generated successfully!')
    },
  })

  const generateRTM = useMutation({
    mutationFn: () => documentsApi.generateRTM(Number(projectId)),
    onSuccess: () => {
      setGenerating(null)
      alert('RTM generated successfully!')
    },
  })

  const documents = [
    {
      id: 'srs',
      name: 'Software Requirements Specification (SRS)',
      description: 'Complete requirements documentation per DO-178C',
      icon: FileText,
      generate: () => {
        setGenerating('srs')
        generateSRS.mutate()
      },
    },
    {
      id: 'rtm',
      name: 'Requirements Traceability Matrix (RTM)',
      description: 'Bidirectional traceability report',
      icon: FileText,
      generate: () => {
        setGenerating('rtm')
        generateRTM.mutate()
      },
    },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Documents</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Generate DO-178C certification artifacts
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {documents.map((doc) => {
          const Icon = doc.icon
          const isGenerating = generating === doc.id

          return (
            <div key={doc.id} className="card">
              <div className="flex items-start gap-4 mb-4">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
                  <Icon className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                    {doc.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {doc.description}
                  </p>
                </div>
              </div>

              <button
                onClick={doc.generate}
                disabled={isGenerating}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {isGenerating ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4" />
                    Generate Document
                  </>
                )}
              </button>
            </div>
          )
        })}
      </div>

      {/* Document History */}
      <div className="card mt-8">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Generated Documents
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Document history will appear here after generation
        </p>
      </div>
    </div>
  )
}

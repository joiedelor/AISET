/**
 * Product Structure Page
 * DO-178C Traceability: REQ-FE-010, REQ-AI-038, REQ-AI-039, REQ-AI-040
 * Purpose: Hierarchical product structure tree view and BOM management
 */

import { useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ChevronRight,
  ChevronDown,
  Plus,
  Trash2,
  Package,
  Cpu,
  FileCode,
  HardDrive,
  FileText,
  Link2,
  RefreshCw,
  Search,
  FolderTree,
  List,
} from 'lucide-react'
import { configurationItemsApi } from '../services/api'

// Types
interface ConfigurationItem {
  id: number
  guid: string
  ci_identifier: string
  project_id: number
  parent_id: number | null
  level: number
  path: string
  name: string
  description: string | null
  ci_type: string | null
  part_number: string | null
  status: string | null
  lifecycle_phase: string | null
  control_level: string | null
  criticality: string | null
  created_at: string | null
  children_count: number
  children?: ConfigurationItem[]
}

interface CIStatistics {
  total_cis: number
  by_type: Record<string, number>
  by_status: Record<string, number>
  by_lifecycle_phase: Record<string, number>
  bom_relationships: number
  root_items: number
  max_depth: number
}

// CI Type icons
const getTypeIcon = (ciType: string | null) => {
  switch (ciType) {
    case 'system': return <Package className="w-4 h-4 text-blue-600" />
    case 'subsystem': return <FolderTree className="w-4 h-4 text-indigo-600" />
    case 'component': return <Cpu className="w-4 h-4 text-green-600" />
    case 'software': return <FileCode className="w-4 h-4 text-purple-600" />
    case 'hardware': return <HardDrive className="w-4 h-4 text-orange-600" />
    case 'document': return <FileText className="w-4 h-4 text-gray-600" />
    case 'interface': return <Link2 className="w-4 h-4 text-cyan-600" />
    default: return <Package className="w-4 h-4 text-gray-400" />
  }
}

// Status badge
const getStatusBadge = (status: string | null) => {
  const colors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-700',
    proposed: 'bg-blue-100 text-blue-700',
    approved: 'bg-green-100 text-green-700',
    released: 'bg-purple-100 text-purple-700',
    obsolete: 'bg-red-100 text-red-700',
  }
  return colors[status || 'draft'] || 'bg-gray-100 text-gray-700'
}

// Tree Node Component
function TreeNode({
  item,
  level = 0,
  expandedNodes,
  onToggle,
  onSelect,
  selectedId,
}: {
  item: ConfigurationItem
  level?: number
  expandedNodes: Set<number>
  onToggle: (id: number) => void
  onSelect: (item: ConfigurationItem) => void
  selectedId: number | null
}) {
  const isExpanded = expandedNodes.has(item.id)
  const hasChildren = item.children && item.children.length > 0

  return (
    <div>
      <div
        className={`flex items-center py-2 px-2 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer rounded ${
          selectedId === item.id ? 'bg-blue-50 dark:bg-blue-900/30' : ''
        }`}
        style={{ paddingLeft: `${level * 20 + 8}px` }}
        onClick={() => onSelect(item)}
      >
        {/* Expand/Collapse */}
        <button
          onClick={(e) => {
            e.stopPropagation()
            onToggle(item.id)
          }}
          className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded mr-1"
        >
          {hasChildren ? (
            isExpanded ? (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronRight className="w-4 h-4 text-gray-500" />
            )
          ) : (
            <span className="w-4 h-4" />
          )}
        </button>

        {/* Type Icon */}
        {getTypeIcon(item.ci_type)}

        {/* Identifier and Name */}
        <span className="ml-2 font-mono text-sm text-gray-500 dark:text-gray-400">
          {item.ci_identifier}
        </span>
        <span className="ml-2 text-gray-900 dark:text-white truncate">
          {item.name}
        </span>

        {/* Status Badge */}
        {item.status && (
          <span className={`ml-auto text-xs px-2 py-0.5 rounded-full ${getStatusBadge(item.status)}`}>
            {item.status}
          </span>
        )}
      </div>

      {/* Children */}
      {isExpanded && hasChildren && (
        <div>
          {item.children!.map((child) => (
            <TreeNode
              key={child.id}
              item={child}
              level={level + 1}
              expandedNodes={expandedNodes}
              onToggle={onToggle}
              onSelect={onSelect}
              selectedId={selectedId}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// Main Component
export default function ProductStructure() {
  const { projectId } = useParams<{ projectId: string }>()
  const queryClient = useQueryClient()

  // State
  const [expandedNodes, setExpandedNodes] = useState<Set<number>>(new Set())
  const [selectedItem, setSelectedItem] = useState<ConfigurationItem | null>(null)
  const [viewMode, setViewMode] = useState<'tree' | 'list'>('tree')
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newCIData, setNewCIData] = useState({
    ci_identifier: '',
    name: '',
    ci_type: 'component',
    description: '',
    part_number: '',
    parent_id: null as number | null,
  })

  // Fetch product structure tree
  const { data: treeData, isLoading: treeLoading, refetch } = useQuery({
    queryKey: ['product-structure', projectId],
    queryFn: async () => {
      const response = await configurationItemsApi.getProductStructure(Number(projectId))
      return response.data
    },
    enabled: !!projectId,
  })

  // Fetch statistics
  const { data: statsData } = useQuery({
    queryKey: ['ci-statistics', projectId],
    queryFn: async () => {
      const response = await configurationItemsApi.getStatistics(Number(projectId))
      return response.data as CIStatistics
    },
    enabled: !!projectId,
  })

  // Create CI mutation
  const createMutation = useMutation({
    mutationFn: (data: typeof newCIData) =>
      configurationItemsApi.create(Number(projectId), data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product-structure', projectId] })
      queryClient.invalidateQueries({ queryKey: ['ci-statistics', projectId] })
      setShowCreateModal(false)
      setNewCIData({
        ci_identifier: '',
        name: '',
        ci_type: 'component',
        description: '',
        part_number: '',
        parent_id: null,
      })
    },
  })

  // Delete CI mutation
  const deleteMutation = useMutation({
    mutationFn: (ciId: number) => configurationItemsApi.delete(ciId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['product-structure', projectId] })
      queryClient.invalidateQueries({ queryKey: ['ci-statistics', projectId] })
      setSelectedItem(null)
    },
  })

  // Toggle node expansion
  const toggleNode = useCallback((id: number) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  // Expand all
  const expandAll = useCallback(() => {
    if (!treeData?.tree) return
    const allIds = new Set<number>()
    const collectIds = (items: ConfigurationItem[]) => {
      items.forEach((item) => {
        allIds.add(item.id)
        if (item.children) collectIds(item.children)
      })
    }
    collectIds(treeData.tree)
    setExpandedNodes(allIds)
  }, [treeData])

  // Collapse all
  const collapseAll = useCallback(() => {
    setExpandedNodes(new Set())
  }, [])

  // Filter tree by search
  const filterTree = (items: ConfigurationItem[], term: string): ConfigurationItem[] => {
    if (!term) return items
    const lower = term.toLowerCase()
    return items
      .map((item) => {
        const matchesSearch =
          item.ci_identifier.toLowerCase().includes(lower) ||
          item.name.toLowerCase().includes(lower)
        const filteredChildren = item.children ? filterTree(item.children, term) : []

        if (matchesSearch || filteredChildren.length > 0) {
          return { ...item, children: filteredChildren }
        }
        return null
      })
      .filter(Boolean) as ConfigurationItem[]
  }

  const filteredTree = treeData?.tree ? filterTree(treeData.tree, searchTerm) : []

  if (treeLoading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mr-2" />
        <span>Loading product structure...</span>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-6 flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Product Structure</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Configuration Items and Bill of Materials management
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => {
              setNewCIData({ ...newCIData, parent_id: selectedItem?.id || null })
              setShowCreateModal(true)
            }}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add CI
          </button>
          <button onClick={() => refetch()} className="btn btn-secondary flex items-center gap-2">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      {statsData && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
          <div className="card p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">Total CIs</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{statsData.total_cis}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">Root Items</p>
            <p className="text-2xl font-bold text-blue-600">{statsData.root_items}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">Max Depth</p>
            <p className="text-2xl font-bold text-purple-600">{statsData.max_depth}</p>
          </div>
          <div className="card p-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">BOM Links</p>
            <p className="text-2xl font-bold text-green-600">{statsData.bom_relationships}</p>
          </div>
          {Object.entries(statsData.by_type).slice(0, 2).map(([type, count]) => (
            <div key={type} className="card p-4">
              <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">{type}</p>
              <p className="text-2xl font-bold text-gray-700">{count}</p>
            </div>
          ))}
        </div>
      )}

      {/* Toolbar */}
      <div className="card mb-6">
        <div className="flex flex-wrap gap-4 items-center">
          {/* Search */}
          <div className="relative flex-1 min-w-[200px]">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search CIs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800"
            />
          </div>

          {/* View Mode Toggle */}
          <div className="flex border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">
            <button
              onClick={() => setViewMode('tree')}
              className={`px-3 py-2 flex items-center gap-1 ${
                viewMode === 'tree' ? 'bg-blue-100 text-blue-700' : 'bg-white dark:bg-gray-800'
              }`}
            >
              <FolderTree className="w-4 h-4" />
              Tree
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 flex items-center gap-1 ${
                viewMode === 'list' ? 'bg-blue-100 text-blue-700' : 'bg-white dark:bg-gray-800'
              }`}
            >
              <List className="w-4 h-4" />
              List
            </button>
          </div>

          {/* Expand/Collapse */}
          <button onClick={expandAll} className="btn btn-secondary text-sm">
            Expand All
          </button>
          <button onClick={collapseAll} className="btn btn-secondary text-sm">
            Collapse All
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tree View */}
        <div className="lg:col-span-2 card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <FolderTree className="w-5 h-5" />
            Structure Tree
          </h3>
          {filteredTree.length > 0 ? (
            <div className="max-h-[600px] overflow-y-auto">
              {filteredTree.map((item) => (
                <TreeNode
                  key={item.id}
                  item={item}
                  expandedNodes={expandedNodes}
                  onToggle={toggleNode}
                  onSelect={setSelectedItem}
                  selectedId={selectedItem?.id || null}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              {searchTerm ? 'No matching CIs found' : 'No Configuration Items yet. Click "Add CI" to create one.'}
            </div>
          )}
        </div>

        {/* Details Panel */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            {selectedItem ? 'CI Details' : 'Select a CI'}
          </h3>
          {selectedItem ? (
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-500">Identifier</label>
                <p className="font-mono text-gray-900 dark:text-white">{selectedItem.ci_identifier}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Name</label>
                <p className="text-gray-900 dark:text-white">{selectedItem.name}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Type</label>
                <p className="flex items-center gap-2">
                  {getTypeIcon(selectedItem.ci_type)}
                  <span className="capitalize">{selectedItem.ci_type || 'Unknown'}</span>
                </p>
              </div>
              {selectedItem.description && (
                <div>
                  <label className="text-sm text-gray-500">Description</label>
                  <p className="text-gray-900 dark:text-white">{selectedItem.description}</p>
                </div>
              )}
              {selectedItem.part_number && (
                <div>
                  <label className="text-sm text-gray-500">Part Number</label>
                  <p className="font-mono">{selectedItem.part_number}</p>
                </div>
              )}
              <div>
                <label className="text-sm text-gray-500">Status</label>
                <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(selectedItem.status)}`}>
                  {selectedItem.status || 'draft'}
                </span>
              </div>
              <div>
                <label className="text-sm text-gray-500">Lifecycle Phase</label>
                <p className="capitalize">{selectedItem.lifecycle_phase || 'development'}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Level</label>
                <p>{selectedItem.level}</p>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <button
                  onClick={() => {
                    setNewCIData({ ...newCIData, parent_id: selectedItem.id })
                    setShowCreateModal(true)
                  }}
                  className="btn btn-secondary flex items-center gap-1 text-sm"
                >
                  <Plus className="w-4 h-4" />
                  Add Child
                </button>
                <button
                  onClick={() => {
                    if (confirm('Delete this CI and all children?')) {
                      deleteMutation.mutate(selectedItem.id)
                    }
                  }}
                  className="btn btn-secondary text-red-600 flex items-center gap-1 text-sm"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Click on a CI in the tree to view details
            </p>
          )}
        </div>
      </div>

      {/* Create CI Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Create Configuration Item</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">CI Identifier *</label>
                <input
                  type="text"
                  value={newCIData.ci_identifier}
                  onChange={(e) => setNewCIData({ ...newCIData, ci_identifier: e.target.value })}
                  placeholder="e.g., SYS-001"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Name *</label>
                <input
                  type="text"
                  value={newCIData.name}
                  onChange={(e) => setNewCIData({ ...newCIData, name: e.target.value })}
                  placeholder="e.g., Flight Control System"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Type</label>
                <select
                  value={newCIData.ci_type}
                  onChange={(e) => setNewCIData({ ...newCIData, ci_type: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="system">System</option>
                  <option value="subsystem">Subsystem</option>
                  <option value="component">Component</option>
                  <option value="software">Software</option>
                  <option value="hardware">Hardware</option>
                  <option value="document">Document</option>
                  <option value="interface">Interface</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={newCIData.description}
                  onChange={(e) => setNewCIData({ ...newCIData, description: e.target.value })}
                  rows={3}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Part Number</label>
                <input
                  type="text"
                  value={newCIData.part_number}
                  onChange={(e) => setNewCIData({ ...newCIData, part_number: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              {newCIData.parent_id && (
                <p className="text-sm text-gray-500">
                  Parent: CI #{newCIData.parent_id}
                </p>
              )}
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => createMutation.mutate(newCIData)}
                disabled={!newCIData.ci_identifier || !newCIData.name || createMutation.isPending}
                className="btn btn-primary"
              >
                {createMutation.isPending ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

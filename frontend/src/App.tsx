/**
 * Main Application Component
 * DO-178C Traceability: REQ-FRONTEND-003
 * Purpose: Root application component with routing
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectInitializationWizard from './pages/ProjectInitializationWizard'
import ProjectDetails from './pages/ProjectDetails'
import Requirements from './pages/Requirements'
import Chat from './pages/Chat'
import Traceability from './pages/Traceability'
import Documents from './pages/Documents'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="projects" element={<Projects />} />
          <Route path="projects/new" element={<ProjectInitializationWizard />} />
          <Route path="projects/:projectId" element={<ProjectDetails />} />
          <Route path="projects/:projectId/requirements" element={<Requirements />} />
          <Route path="projects/:projectId/chat" element={<Chat />} />
          <Route path="projects/:projectId/traceability" element={<Traceability />} />
          <Route path="projects/:projectId/documents" element={<Documents />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

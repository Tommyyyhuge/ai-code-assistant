import { Routes, Route } from 'react-router-dom'
import ErrorBoundary from './components/ErrorBoundary'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProblemListPage from './pages/ProblemListPage'
import ProblemDetailPage from './pages/ProblemDetailPage'
import KnowledgeTreePage from './pages/KnowledgeTreePage'
import KnowledgeGraphPage from './pages/KnowledgeGraphPage'
import LearningPathListPage from './pages/LearningPathListPage'
import LearningPathDetailPage from './pages/LearningPathDetailPage'
import AIChatPage from './pages/AIChatPage'
import AISettingsPage from './pages/AISettingsPage'

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/problems" element={<ProblemListPage />} />
          <Route path="/problems/:id" element={<ProblemDetailPage />} />
          <Route path="/knowledge/*" element={<KnowledgeTreePage />} />
          <Route path="/knowledge-graph" element={<KnowledgeGraphPage />} />
          <Route path="/paths" element={<LearningPathListPage />} />
          <Route path="/paths/:slug" element={<LearningPathDetailPage />} />
          <Route path="/chat" element={<AIChatPage />} />
          <Route path="/settings/ai" element={<AISettingsPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  )
}

export default App
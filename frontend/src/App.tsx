import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProblemListPage from './pages/ProblemListPage'
import ProblemDetailPage from './pages/ProblemDetailPage'
import KnowledgeTreePage from './pages/KnowledgeTreePage'
import KnowledgeGraphPage from './pages/KnowledgeGraphPage'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/problems" element={<ProblemListPage />} />
        <Route path="/problems/:id" element={<ProblemDetailPage />} />
        <Route path="/knowledge/*" element={<KnowledgeTreePage />} />
        <Route path="/knowledge-graph" element={<KnowledgeGraphPage />} />
      </Route>
    </Routes>
  )
}

export default App
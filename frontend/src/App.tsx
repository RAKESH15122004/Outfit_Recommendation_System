import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Wardrobe from './pages/Wardrobe'
import Recommendations from './pages/Recommendations'
import SavedOutfits from './pages/SavedOutfits'
import Profile from './pages/Profile'
import Subscriptions from './pages/Subscriptions'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-2 border-copper-500 border-t-transparent rounded-full" />
      </div>
    )
  }
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-2 border-copper-500 border-t-transparent rounded-full" />
      </div>
    )
  }
  if (user) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="wardrobe" element={<Wardrobe />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="saved-outfits" element={<SavedOutfits />} />
        <Route path="profile" element={<Profile />} />
        <Route path="subscriptions" element={<Subscriptions />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

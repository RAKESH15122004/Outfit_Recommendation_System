import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register({ email, password, full_name: fullName || undefined })
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <Link to="/" className="font-display text-3xl font-bold text-ink-900">
            Outfit
          </Link>
          <h2 className="mt-4 text-2xl font-semibold text-ink-800">Create your account</h2>
          <p className="mt-2 text-ink-500">Start styling with AI recommendations</p>
        </div>

        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 rounded-lg bg-red-50 text-red-700 text-sm">{error}</div>
            )}
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Full name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-field"
                placeholder="Alex Smith"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                placeholder="••••••••"
                required
                minLength={6}
              />
              <p className="mt-1 text-xs text-ink-500">At least 6 characters</p>
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
                  Creating account...
                </span>
              ) : (
                'Create account'
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-ink-500 text-sm">
            Already have an account?{' '}
            <Link to="/login" className="text-copper-600 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}

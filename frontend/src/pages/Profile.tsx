import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { User, Mail, Save } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'
import { useToast } from '../context/ToastContext'

const BODY_TYPES = ['', 'Slim', 'Athletic', 'Average', 'Plus', 'Pear', 'Apple', 'Hourglass']
const SKIN_TONES = ['', 'Fair', 'Light', 'Medium', 'Olive', 'Tan', 'Brown', 'Dark']
const COMFORT_LEVELS = ['', 'Minimal', 'Casual', 'Comfortable', 'Smart', 'Formal']

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const { success, error: showError } = useToast()
  const [fullName, setFullName] = useState('')
  const [bodyType, setBodyType] = useState('')
  const [skinTone, setSkinTone] = useState('')
  const [preferredColors, setPreferredColors] = useState('')
  const [comfortLevel, setComfortLevel] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    setFullName(user?.full_name || '')
    setBodyType(user?.body_type || '')
    setSkinTone(user?.skin_tone || '')
    setPreferredColors(Array.isArray(user?.preferred_colors) ? user.preferred_colors.join(', ') : '')
    setComfortLevel(user?.comfort_level || '')
  }, [user])

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    try {
      await api.put('/users/me', {
        full_name: fullName || undefined,
        body_type: bodyType || undefined,
        skin_tone: skinTone || undefined,
        preferred_colors: preferredColors
          ? preferredColors.split(/[,\s]+/).map((c) => c.trim()).filter(Boolean)
          : undefined,
        comfort_level: comfortLevel || undefined,
      })
      await refreshUser()
      success('Profile updated')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div>
        <h1 className="font-display text-3xl font-bold text-ink-900">Profile</h1>
        <p className="mt-2 text-ink-600">Manage your account and style preferences</p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mt-10 max-w-xl"
      >
        <div className="card p-8">
          <div className="flex items-center gap-6 mb-8">
            <div className="w-20 h-20 rounded-full bg-copper-100 flex items-center justify-center">
              <User size={40} className="text-copper-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-ink-900">{user?.full_name || 'User'}</h2>
              <p className="text-ink-500 flex items-center gap-2">
                <Mail size={16} />
                {user?.email}
              </p>
            </div>
          </div>

          <form onSubmit={handleSave} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Full name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-field"
                placeholder="Your name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Email</label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="input-field bg-ink-50 cursor-not-allowed"
              />
              <p className="text-xs text-ink-500 mt-1">Email cannot be changed</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Body type (optional)</label>
              <select
                value={bodyType}
                onChange={(e) => setBodyType(e.target.value)}
                className="input-field"
              >
                <option value="">Select</option>
                {BODY_TYPES.filter(Boolean).map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Skin tone (optional)</label>
              <select
                value={skinTone}
                onChange={(e) => setSkinTone(e.target.value)}
                className="input-field"
              >
                <option value="">Select</option>
                {SKIN_TONES.filter(Boolean).map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">
                Preferred colors (optional, comma-separated)
              </label>
              <input
                type="text"
                value={preferredColors}
                onChange={(e) => setPreferredColors(e.target.value)}
                placeholder="e.g. Blue, Black, White"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Comfort level (optional)</label>
              <select
                value={comfortLevel}
                onChange={(e) => setComfortLevel(e.target.value)}
                className="input-field"
              >
                <option value="">Select</option>
                {COMFORT_LEVELS.filter(Boolean).map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <button type="submit" className="btn-primary flex items-center gap-2" disabled={saving}>
              <Save size={18} />
              {saving ? 'Saving...' : 'Save changes'}
            </button>
          </form>
        </div>
      </motion.div>
    </div>
  )
}

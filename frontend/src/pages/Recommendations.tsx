import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Check, X, MapPin, Thermometer } from 'lucide-react'
import { api } from '../lib/api'
import { useToast } from '../context/ToastContext'

interface Recommendation {
  id: number
  occasion?: string
  location?: string
  weather_temperature?: number
  weather_condition?: string
  confidence_score: number
  outfit?: {
    id: number
    items: { item_name?: string; item_color?: string; item_image_url?: string; item_type: string }[]
  }
  created_at: string
}

// Backend OccasionType values
const OCCASIONS = [
  { value: 'daily', label: 'Daily' },
  { value: 'street_style', label: 'Street Style' },
  { value: 'smart_casual', label: 'Smart Casual' },
  { value: 'office', label: 'Office' },
  { value: 'business_meeting', label: 'Business Meeting' },
  { value: 'corporate_event', label: 'Corporate Event' },
  { value: 'wedding', label: 'Wedding' },
  { value: 'party', label: 'Party' },
  { value: 'festival', label: 'Festival' },
  { value: 'special_event', label: 'Special Event' },
]

const DRESS_CODES = [
  { value: '', label: 'Any' },
  { value: 'casual', label: 'Casual' },
  { value: 'formal', label: 'Formal' },
  { value: 'business', label: 'Business' },
  { value: 'smart_casual', label: 'Smart Casual' },
]

export default function Recommendations() {
  const { success, error: showError } = useToast()
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [occasion, setOccasion] = useState('daily')
  const [dressCode, setDressCode] = useState('')
  const [location, setLocation] = useState('')
  const [colorPrefs, setColorPrefs] = useState('')

  const fetchRecommendations = async () => {
    setLoading(true)
    try {
      const data = await api.get<Recommendation[]>('/recommendations/')
      setRecommendations(data)
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to load recommendations')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const generateRecommendation = async () => {
    setGenerating(true)
    try {
      await api.post('/recommendations/generate', {
        occasion,
        dress_code: dressCode || undefined,
        location: location || undefined,
        color_preferences: colorPrefs
          ? colorPrefs.split(/[,\s]+/).map((c) => c.trim()).filter(Boolean)
          : undefined,
      })
      await fetchRecommendations()
      success('New recommendation generated!')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to generate recommendation')
    } finally {
      setGenerating(false)
    }
  }

  const handleAccept = async (id: number) => {
    try {
      await api.post(`/recommendations/${id}/accept`)
      await fetchRecommendations()
      success('Outfit saved to favorites')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to save outfit')
    }
  }

  const handleReject = async (id: number) => {
    try {
      await api.post(`/recommendations/${id}/reject`)
      await fetchRecommendations()
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to reject')
    }
  }

  const getImageUrl = (url?: string) => {
    if (!url) return ''
    return url.startsWith('http') ? url : `${url.startsWith('/') ? '' : '/'}${url}`
  }

  return (
    <div>
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
        <div>
          <h1 className="font-display text-3xl font-bold text-ink-900">Recommendations</h1>
          <p className="mt-2 text-ink-600">AI-powered outfit suggestions from your wardrobe</p>
        </div>

        <div className="card p-6 flex-1 lg:flex-none lg:max-w-xl">
          <h3 className="font-semibold text-ink-800 mb-4">Generate new recommendation</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Occasion</label>
              <select
                value={occasion}
                onChange={(e) => setOccasion(e.target.value)}
                className="input-field"
              >
                {OCCASIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">Dress code (optional)</label>
              <select
                value={dressCode}
                onChange={(e) => setDressCode(e.target.value)}
                className="input-field"
              >
                {DRESS_CODES.map((d) => (
                  <option key={d.value} value={d.value}>{d.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">
                City (optional, for weather)
              </label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. London, New York"
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-ink-700 mb-1">
                Color preferences (optional, comma-separated)
              </label>
              <input
                type="text"
                value={colorPrefs}
                onChange={(e) => setColorPrefs(e.target.value)}
                placeholder="e.g. Blue, Black, White"
                className="input-field"
              />
            </div>
            <button
              onClick={generateRecommendation}
              disabled={generating}
              className="btn-accent w-full flex items-center justify-center gap-2"
            >
              {generating ? (
                <>
                  <span className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles size={20} />
                  Generate outfit
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="mt-12 space-y-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card h-48 animate-pulse bg-ink-100" />
          ))}
        </div>
      ) : recommendations.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-16 text-center py-16 card"
        >
          <div className="inline-flex p-4 rounded-2xl bg-copper-100 text-copper-600 mb-4">
            <Sparkles size={48} />
          </div>
          <h3 className="text-xl font-semibold text-ink-800">No recommendations yet</h3>
          <p className="mt-2 text-ink-500 max-w-md mx-auto">
            Add items to your wardrobe, then generate your first AI-powered outfit suggestion above.
          </p>
          <button
            onClick={generateRecommendation}
            disabled={generating}
            className="btn-accent mt-6"
          >
            Generate first recommendation
          </button>
        </motion.div>
      ) : (
        <div className="mt-10 space-y-6">
          {recommendations.map((rec, i) => (
            <motion.div
              key={rec.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="card overflow-hidden"
            >
              <div className="p-6 flex flex-col md:flex-row md:items-start gap-6">
                <div className="flex-1">
                  <div className="flex flex-wrap items-center gap-3 text-sm text-ink-500">
                    {rec.occasion && (
                      <span className="px-3 py-1 rounded-full bg-ink-100 capitalize">
                        {rec.occasion.replace(/_/g, ' ')}
                      </span>
                    )}
                    {rec.weather_temperature != null && (
                      <span className="flex items-center gap-1">
                        <Thermometer size={14} />
                        {Math.round(rec.weather_temperature)}°C
                      </span>
                    )}
                    {rec.location && (
                      <span className="flex items-center gap-1">
                        <MapPin size={14} />
                        {rec.location}
                      </span>
                    )}
                    <span className="text-ink-400">
                      {Math.round(rec.confidence_score * 100)}% match
                    </span>
                  </div>
                  {rec.outfit?.items && rec.outfit.items.length > 0 && (
                    <div className="mt-4 flex flex-wrap gap-4">
                      {rec.outfit.items.map((item, idx) => (
                        <div
                          key={idx}
                          className="w-20 h-20 rounded-lg overflow-hidden bg-ink-100 shrink-0"
                        >
                          {item.item_image_url ? (
                            <img
                              src={getImageUrl(item.item_image_url)}
                              alt={item.item_name || 'Item'}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-ink-400 text-xs text-center p-1">
                              {item.item_name || item.item_type}
                            </div>
                          )}
                          <div className="bg-ink-900/70 text-white text-xs px-2 py-0.5 truncate">
                            {item.item_name || item.item_type}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="flex gap-2 shrink-0">
                  <button
                    onClick={() => handleAccept(rec.id)}
                    className="p-2 rounded-lg bg-green-100 text-green-700 hover:bg-green-200 transition-colors"
                    title="Save outfit"
                  >
                    <Check size={20} />
                  </button>
                  <button
                    onClick={() => handleReject(rec.id)}
                    className="p-2 rounded-lg bg-red-100 text-red-700 hover:bg-red-200 transition-colors"
                    title="Reject"
                  >
                    <X size={20} />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

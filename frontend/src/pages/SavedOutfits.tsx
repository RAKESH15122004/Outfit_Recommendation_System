import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Heart, Trash2 } from 'lucide-react'
import { api } from '../lib/api'
import { useToast } from '../context/ToastContext'

interface OutfitItem {
  item_name?: string
  item_color?: string
  item_image_url?: string
  item_type: string
}

interface SavedOutfit {
  id: number
  outfit_id: number
  custom_name?: string
  notes?: string
  created_at: string
  outfit?: {
    id: number
    occasion?: string
    category?: string
    items: OutfitItem[]
    confidence_score: number
  }
}

export default function SavedOutfits() {
  const { success, error: showError } = useToast()
  const [saved, setSaved] = useState<SavedOutfit[]>([])
  const [loading, setLoading] = useState(true)

  const fetchSaved = async () => {
    setLoading(true)
    try {
      const data = await api.get<SavedOutfit[]>('/outfits/saved/list')
      setSaved(data)
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to load saved outfits')
      setSaved([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSaved()
  }, [])

  const removeSaved = async (savedId: number) => {
    if (!confirm('Remove from saved outfits?')) return
    try {
      await api.delete(`/outfits/saved/${savedId}`)
      setSaved((prev) => prev.filter((s) => s.id !== savedId))
      success('Removed from saved outfits')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to remove')
    }
  }

  const getImageUrl = (url?: string) => {
    if (!url) return ''
    return url.startsWith('http') ? url : `${url.startsWith('/') ? '' : '/'}${url}`
  }

  return (
    <div>
      <div>
        <h1 className="font-display text-3xl font-bold text-ink-900">Saved outfits</h1>
        <p className="mt-2 text-ink-600">Your favorite looks</p>
      </div>

      {loading ? (
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card h-64 animate-pulse bg-ink-100" />
          ))}
        </div>
      ) : saved.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-16 text-center py-16 card"
        >
          <div className="inline-flex p-4 rounded-2xl bg-ink-100 text-ink-400 mb-4">
            <Heart size={48} />
          </div>
          <h3 className="text-xl font-semibold text-ink-800">No saved outfits</h3>
          <p className="mt-2 text-ink-500 max-w-md mx-auto">
            Accept recommendations to save them here, or save outfits you love from your history.
          </p>
        </motion.div>
      ) : (
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {saved.map((s, i) => (
            <motion.div
              key={s.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="card overflow-hidden group"
            >
              <div className="p-4 flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-ink-900">
                    {s.custom_name || (s.outfit?.occasion ? s.outfit.occasion.replace(/_/g, ' ') : 'Saved outfit')}
                  </h3>
                  {s.outfit && (
                    <p className="text-sm text-ink-500 mt-1">
                      {Math.round((s.outfit.confidence_score || 0) * 100)}% match
                    </p>
                  )}
                </div>
                <button
                  onClick={() => removeSaved(s.id)}
                  className="p-2 rounded-lg text-ink-400 hover:text-red-600 hover:bg-red-50 transition-all"
                  title="Remove from saved"
                >
                  <Trash2 size={18} />
                </button>
              </div>
              {s.outfit?.items && s.outfit.items.length > 0 && (
                <div className="flex gap-2 p-4 pt-0 overflow-x-auto">
                  {s.outfit.items.map((item, idx) => (
                    <div
                      key={idx}
                      className="w-16 h-16 rounded-lg overflow-hidden bg-ink-100 shrink-0 flex-shrink-0"
                    >
                      {item.item_image_url ? (
                        <img
                          src={getImageUrl(item.item_image_url)}
                          alt={item.item_name || 'Item'}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-ink-400 text-xs p-1 text-center">
                          {item.item_name || item.item_type}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

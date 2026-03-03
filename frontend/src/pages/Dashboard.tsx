import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shirt, Sparkles, Heart, ChevronRight } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'

interface Stats {
  wardrobeCount: number
  outfitCount: number
  savedCount: number
}

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState<Stats>({ wardrobeCount: 0, outfitCount: 0, savedCount: 0 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchStats() {
      try {
        const [items, recs, saved] = await Promise.all([
          api.get<unknown[]>('/wardrobe/items').catch(() => []),
          api.get<unknown[]>('/recommendations/').catch(() => []),
          api.get<unknown[]>('/outfits/saved/list').catch(() => []),
        ])
        setStats({
          wardrobeCount: Array.isArray(items) ? items.length : 0,
          outfitCount: Array.isArray(recs) ? recs.length : 0,
          savedCount: Array.isArray(saved) ? saved.length : 0,
        })
      } catch {
        // Stats are non-critical; silently use defaults
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  const cards = [
    {
      title: 'Wardrobe',
      value: stats.wardrobeCount,
      desc: 'Items in your closet',
      icon: Shirt,
      href: '/wardrobe',
      color: 'copper',
    },
    {
      title: 'Recommendations',
      value: stats.outfitCount,
      desc: 'AI-generated outfits',
      icon: Sparkles,
      href: '/recommendations',
      color: 'sage',
    },
    {
      title: 'Saved outfits',
      value: stats.savedCount,
      desc: 'Favorites',
      icon: Heart,
      href: '/saved-outfits',
      color: 'ink',
    },
  ]

  return (
    <div>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h1 className="font-display text-3xl font-bold text-ink-900">
          Hello{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}
        </h1>
        <p className="mt-2 text-ink-600">Your style dashboard</p>
      </motion.div>

      <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map(({ title, value, desc, icon: Icon, href, color }, i) => (
          <motion.div
            key={title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i, duration: 0.4 }}
          >
            <Link to={href} className="block">
              <div className="card p-6 group hover:shadow-card-hover transition-all duration-300">
                <div className="flex items-start justify-between">
                  <div
                    className={`p-3 rounded-xl ${
                      color === 'copper'
                        ? 'bg-copper-100 text-copper-600'
                        : color === 'sage'
                        ? 'bg-sage-500/15 text-sage-600'
                        : 'bg-ink-100 text-ink-600'
                    }`}
                  >
                    <Icon size={28} />
                  </div>
                  <ChevronRight
                    size={20}
                    className="text-ink-400 group-hover:text-copper-600 group-hover:translate-x-1 transition-all"
                  />
                </div>
                {loading ? (
                  <div className="mt-4 h-8 w-16 bg-ink-200 rounded animate-pulse" />
                ) : (
                  <p className="mt-4 text-3xl font-bold text-ink-900">{value}</p>
                )}
                <p className="mt-1 font-medium text-ink-800">{title}</p>
                <p className="text-sm text-ink-500">{desc}</p>
              </div>
            </Link>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.4 }}
        className="mt-12"
      >
        <Link to="/recommendations" className="block">
          <div className="card p-8 bg-gradient-to-br from-ink-900 to-ink-800 text-white">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
              <div>
                <h2 className="font-display text-2xl font-bold">Get a new outfit idea</h2>
                <p className="mt-2 text-ink-200">
                  Generate AI-powered recommendations based on your wardrobe, occasion, and weather.
                </p>
              </div>
              <div className="flex items-center gap-2 text-copper-400 font-medium">
                <Sparkles size={20} />
                Generate outfit
                <ChevronRight size={20} />
              </div>
            </div>
          </div>
        </Link>
      </motion.div>
    </div>
  )
}

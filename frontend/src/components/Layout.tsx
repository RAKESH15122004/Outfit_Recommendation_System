import { Outlet } from 'react-router-dom'
import { Link, useLocation } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Shirt,
  Sparkles,
  Heart,
  User,
  CreditCard,
  LogOut,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/wardrobe', icon: Shirt, label: 'Wardrobe' },
  { path: '/recommendations', icon: Sparkles, label: 'Recommendations' },
  { path: '/saved-outfits', icon: Heart, label: 'Saved Outfits' },
  { path: '/profile', icon: User, label: 'Profile' },
  { path: '/subscriptions', icon: CreditCard, label: 'Subscriptions' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-ink-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/dashboard" className="flex items-center gap-2">
              <span className="font-display text-2xl font-bold text-ink-900">Outfit</span>
            </Link>
            <div className="flex items-center gap-4">
              <span className="text-sm text-ink-600 hidden sm:block">
                {user?.full_name || user?.email}
              </span>
              <button
                onClick={logout}
                className="p-2 rounded-lg text-ink-500 hover:text-ink-800 hover:bg-ink-100 transition-colors"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
        <nav className="border-t border-ink-100 overflow-x-auto">
          <div className="max-w-7xl mx-auto px-4 flex gap-1 py-2">
            {navItems.map(({ path, icon: Icon, label }) => {
              const active = location.pathname === path
              return (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap font-medium transition-all ${
                    active
                      ? 'bg-ink-900 text-white'
                      : 'text-ink-600 hover:bg-ink-100 hover:text-ink-900'
                  }`}
                >
                  <Icon size={18} />
                  {label}
                </Link>
              )
            })}
          </div>
        </nav>
      </header>

      <main className="flex-1">
        <motion.div
          key={location.pathname}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  )
}

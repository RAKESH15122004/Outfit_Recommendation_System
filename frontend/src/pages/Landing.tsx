import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Sparkles, Shirt, Palette, Cloud } from 'lucide-react'

export default function Landing() {
  return (
    <div className="min-h-screen overflow-hidden">
      <header className="absolute top-0 left-0 right-0 z-10 px-6 py-6 flex items-center justify-between">
        <span className="font-display text-2xl font-bold text-ink-900">Outfit</span>
        <div className="flex gap-4">
          <Link to="/login" className="text-ink-600 hover:text-ink-900 font-medium">
            Sign in
          </Link>
          <Link
            to="/register"
            className="btn-primary"
          >
            Get started
          </Link>
        </div>
      </header>

      <section className="relative min-h-screen flex flex-col items-center justify-center px-6 pt-24">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-copper-200/30 via-transparent to-transparent" />
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="relative text-center max-w-4xl mx-auto"
        >
          <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-bold text-ink-900 tracking-tight">
            AI-powered outfit
            <br />
            <span className="text-copper-600 italic">recommendations</span>
          </h1>
          <p className="mt-8 text-xl text-ink-600 max-w-2xl mx-auto">
            Let our smart stylist curate perfect looks from your wardrobe—tailored to occasion,
            weather, and your personal style.
          </p>
          <div className="mt-12 flex flex-wrap justify-center gap-4">
            <Link to="/register" className="btn-accent text-lg px-8 py-4">
              Start styling
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-4">
              I have an account
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="relative mt-24 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl"
        >
          {[
            { icon: Sparkles, label: 'AI suggestions', desc: 'Smart outfit pairing' },
            { icon: Shirt, label: 'Wardrobe', desc: 'Organize your closet' },
            { icon: Palette, label: 'Style matching', desc: 'Colors & occasions' },
            { icon: Cloud, label: 'Weather-ready', desc: 'Dress for the day' },
          ].map(({ icon: Icon, label, desc }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + i * 0.1, duration: 0.5 }}
              className="card p-6 text-center"
            >
              <div className="inline-flex p-3 rounded-xl bg-copper-100 text-copper-600 mb-3">
                <Icon size={24} />
              </div>
              <h3 className="font-semibold text-ink-900">{label}</h3>
              <p className="text-sm text-ink-500 mt-1">{desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>
    </div>
  )
}

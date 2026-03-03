import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Upload, X, Star, Trash2, Pencil } from 'lucide-react'
import { api } from '../lib/api'
import { useToast } from '../context/ToastContext'

interface WardrobeItem {
  id: number
  name: string
  category: string
  color: string
  image_url: string
  thumbnail_url?: string
  is_favorite: boolean
  brand?: string
  subcategory?: string
  size?: string
  notes?: string
}

const CATEGORIES = [
  { value: '', label: 'All' },
  { value: 'top', label: 'Tops' },
  { value: 'bottom', label: 'Bottoms' },
  { value: 'footwear', label: 'Footwear' },
  { value: 'accessory', label: 'Accessories' },
  { value: 'outerwear', label: 'Outerwear' },
  { value: 'dress', label: 'Dresses' },
]

const UPLOAD_CATEGORIES = [
  { value: 'top', label: 'Top' },
  { value: 'bottom', label: 'Bottom' },
  { value: 'footwear', label: 'Footwear' },
  { value: 'accessory', label: 'Accessory' },
  { value: 'outerwear', label: 'Outerwear' },
  { value: 'dress', label: 'Dress' },
]

const COLORS = [
  'Black', 'White', 'Navy', 'Gray', 'Beige', 'Brown', 'Red', 'Blue',
  'Green', 'Pink', 'Yellow', 'Orange', 'Purple', 'Multi',
]

export default function Wardrobe() {
  const { success, error: showError } = useToast()
  const [items, setItems] = useState<WardrobeItem[]>([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [editingItem, setEditingItem] = useState<WardrobeItem | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadName, setUploadName] = useState('')
  const [uploadCategory, setUploadCategory] = useState('top')
  const [uploadColor, setUploadColor] = useState('Black')
  const [editName, setEditName] = useState('')
  const [editColor, setEditColor] = useState('')
  const [editCategory, setEditCategory] = useState('top')
  const [uploadError, setUploadError] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)

  const fetchItems = async () => {
    setLoading(true)
    try {
      const url = category ? `/wardrobe/items?category=${category}` : '/wardrobe/items'
      const data = await api.get<WardrobeItem[]>(url)
      setItems(data)
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to load wardrobe')
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchItems()
  }, [category])

  const getImageUrl = (url: string) => {
    if (url.startsWith('http')) return url
    return `${url.startsWith('/') ? '' : '/'}${url}`
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadError('')
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('name', uploadName || file.name.replace(/\.[^.]+$/, ''))
      formData.append('category', uploadCategory)
      formData.append('color', uploadColor)
      const token = localStorage.getItem('access_token')
      const res = await fetch('/api/v1/wardrobe/items/upload', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(typeof err.detail === 'string' ? err.detail : err.detail?.message || 'Upload failed')
      }
      await fetchItems()
      setShowUpload(false)
      setUploadName('')
      setUploadCategory('top')
      setUploadColor('Black')
      if (fileInput.current) fileInput.current.value = ''
      success('Item added to wardrobe')
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Remove this item from your wardrobe?')) return
    try {
      await api.delete(`/wardrobe/items/${id}`)
      setItems((prev) => prev.filter((i) => i.id !== id))
      success('Item removed')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to remove item')
    }
  }

  const toggleFavorite = async (item: WardrobeItem) => {
    try {
      await api.put(`/wardrobe/items/${item.id}`, {
        name: item.name,
        category: item.category,
        color: item.color,
        is_favorite: !item.is_favorite,
      })
      setItems((prev) =>
        prev.map((i) => (i.id === item.id ? { ...i, is_favorite: !i.is_favorite } : i))
      )
      success(item.is_favorite ? 'Removed from favorites' : 'Added to favorites')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to update')
    }
  }

  const openEdit = (item: WardrobeItem) => {
    setEditingItem(item)
    setEditName(item.name)
    setEditColor(item.color)
    setEditCategory(item.category)
  }

  const handleSaveEdit = async () => {
    if (!editingItem) return
    try {
      await api.put(`/wardrobe/items/${editingItem.id}`, {
        name: editName,
        color: editColor,
        category: editCategory,
      })
      setItems((prev) =>
        prev.map((i) =>
          i.id === editingItem.id
            ? { ...i, name: editName, color: editColor, category: editCategory }
            : i
        )
      )
      setEditingItem(null)
      success('Item updated')
    } catch (err) {
      showError(err instanceof Error ? err.message : 'Failed to update item')
    }
  }

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold text-ink-900">Wardrobe</h1>
          <p className="mt-2 text-ink-600">Manage your closet</p>
        </div>
        <button onClick={() => setShowUpload(true)} className="btn-primary flex items-center gap-2">
          <Plus size={20} />
          Add item
        </button>
      </div>

      <div className="mt-8 flex flex-wrap gap-2">
        {CATEGORIES.map((c) => (
          <button
            key={c.value}
            onClick={() => setCategory(c.value)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              category === c.value
                ? 'bg-ink-900 text-white'
                : 'bg-white text-ink-600 hover:bg-ink-100'
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="mt-12 grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="card h-72 animate-pulse bg-ink-100" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-16 text-center py-16 card"
        >
          <div className="inline-flex p-4 rounded-2xl bg-ink-100 text-ink-400 mb-4">
            <Upload size={48} />
          </div>
          <h3 className="text-xl font-semibold text-ink-800">No items yet</h3>
          <p className="mt-2 text-ink-500">Add clothes to your wardrobe to get started</p>
          <button onClick={() => setShowUpload(true)} className="btn-primary mt-6">
            Add first item
          </button>
        </motion.div>
      ) : (
        <motion.div
          layout
          className="mt-8 grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
        >
          <AnimatePresence>
            {items.map((item, i) => (
              <motion.div
                key={item.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: i * 0.03 }}
                className="card overflow-hidden group"
              >
                <div className="aspect-[3/4] bg-ink-100 relative overflow-hidden">
                  <img
                    src={getImageUrl(item.thumbnail_url || item.image_url)}
                    alt={item.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src =
                        'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" fill="%23d9d5cc"><rect width="200" height="200"/><text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="%238f8572" font-size="14">No image</text></svg>'
                    }}
                  />
                  <div className="absolute top-2 right-2 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => openEdit(item)}
                      className="p-2 rounded-full bg-white/90 hover:bg-white shadow"
                      title="Edit"
                    >
                      <Pencil size={18} className="text-ink-600" />
                    </button>
                    <button
                      onClick={() => toggleFavorite(item)}
                      className="p-2 rounded-full bg-white/90 hover:bg-white shadow"
                      title={item.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      <Star
                        size={18}
                        fill={item.is_favorite ? 'currentColor' : 'none'}
                        className={item.is_favorite ? 'text-amber-500' : 'text-ink-600'}
                      />
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-2 rounded-full bg-white/90 hover:bg-red-50 text-red-600 shadow"
                      title="Remove"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-ink-900 truncate">{item.name}</h3>
                  <div className="mt-1 flex items-center justify-between gap-2">
                    <p className="text-sm text-ink-500 capitalize">{item.color}</p>
                    <span className="inline-flex px-2 py-0.5 rounded-full bg-ink-100 text-[11px] font-medium text-ink-600 capitalize">
                      {item.category}
                    </span>
                  </div>
                  {item.brand && (
                    <p className="text-xs text-ink-400 mt-1">{item.brand}</p>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}

      <AnimatePresence>
        {showUpload && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink-900/50 backdrop-blur-sm"
            onClick={() => !uploading && setShowUpload(false)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="card p-8 max-w-md w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold">Add wardrobe item</h3>
                <button
                  onClick={() => !uploading && setShowUpload(false)}
                  className="p-2 rounded-lg hover:bg-ink-100"
                >
                  <X size={20} />
                </button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-1">Name</label>
                  <input
                    type="text"
                    value={uploadName}
                    onChange={(e) => setUploadName(e.target.value)}
                    placeholder="e.g. Blue denim jacket"
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-1">Category</label>
                  <select
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value)}
                    className="input-field"
                  >
                    {UPLOAD_CATEGORIES.map((c) => (
                      <option key={c.value} value={c.value}>{c.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-1">Color</label>
                  <select
                    value={uploadColor}
                    onChange={(e) => setUploadColor(e.target.value)}
                    className="input-field"
                  >
                    {COLORS.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-2">Photo</label>
                  <input
                    ref={fileInput}
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleUpload}
                    className="hidden"
                  />
                  <div
                    onClick={() => fileInput.current?.click()}
                    className="border-2 border-dashed border-ink-200 rounded-xl p-8 text-center cursor-pointer hover:border-copper-500 hover:bg-copper-50/30 transition-all"
                  >
                    {uploading ? (
                      <div className="flex flex-col items-center gap-2">
                        <div className="animate-spin w-10 h-10 border-2 border-copper-500 border-t-transparent rounded-full" />
                        <p className="text-sm">Uploading...</p>
                      </div>
                    ) : (
                      <>
                        <Upload size={40} className="mx-auto text-ink-400" />
                        <p className="mt-2 font-medium text-ink-700 text-sm">Click to upload</p>
                        <p className="text-xs text-ink-500">JPG, PNG, WebP</p>
                      </>
                    )}
                  </div>
                </div>
              </div>
              {uploadError && (
                <p className="mt-4 text-sm text-red-600">{uploadError}</p>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {editingItem && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink-900/50 backdrop-blur-sm"
            onClick={() => setEditingItem(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="card p-8 max-w-md w-full"
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold">Edit item</h3>
                <button
                  onClick={() => setEditingItem(null)}
                  className="p-2 rounded-lg hover:bg-ink-100"
                >
                  <X size={20} />
                </button>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-1">Name</label>
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    className="input-field"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-1">Category</label>
                  <select
                    value={editCategory}
                    onChange={(e) => setEditCategory(e.target.value)}
                    className="input-field"
                  >
                    {UPLOAD_CATEGORIES.map((c) => (
                      <option key={c.value} value={c.value}>{c.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-ink-700 mb-1">Color</label>
                  <select
                    value={editColor}
                    onChange={(e) => setEditColor(e.target.value)}
                    className="input-field"
                  >
                    {COLORS.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div className="mt-6 flex gap-3">
                <button onClick={() => setEditingItem(null)} className="btn-secondary flex-1">
                  Cancel
                </button>
                <button onClick={handleSaveEdit} className="btn-primary flex-1">
                  Save changes
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

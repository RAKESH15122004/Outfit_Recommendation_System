import React, { createContext, useContext, useEffect, useState } from 'react'
import { api } from '../lib/api'

export interface User {
  id: number
  email: string
  full_name: string | null
  body_type: string | null
  skin_tone: string | null
  preferred_colors: string[] | null
  brand_affinity: string[] | null
  comfort_level: string | null
  budget_range: Record<string, number> | null
  is_active: boolean
  role: string
  profile_image_url: string | null
  created_at: string
  last_login: string | null
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

export interface RegisterData {
  email: string
  password: string
  full_name?: string
  body_type?: string
  skin_tone?: string
  preferred_colors?: string[]
  brand_affinity?: string[]
  comfort_level?: string
  budget_range?: Record<string, number>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const refreshUser = async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setUser(null)
      setLoading(false)
      return
    }
    try {
      const u = await api.get<User>('/auth/me')
      setUser(u)
    } catch {
      setUser(null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshUser()
  }, [])

  const login = async (email: string, password: string) => {
    const data = await api.post<{ access_token: string; refresh_token: string }>(
      '/auth/login',
      { email, password }
    )
    if (!data?.access_token) throw new Error('Login failed')
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    await refreshUser()
  }

  const register = async (data: RegisterData) => {
    await api.post('/auth/register', data)
    await login(data.email, data.password)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

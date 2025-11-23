/**
 * Authentication Context
 * DO-178C Traceability: REQ-BE-003, REQ-BE-004
 * Purpose: Provide authentication state and actions to the application
 */

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, setAuthToken, UserInfo, LoginRequest, RegisterRequest } from '../services/api'

interface AuthContextType {
  user: UserInfo | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const TOKEN_KEY = 'aiset_auth_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Initialize auth state from stored token
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(TOKEN_KEY)

      if (token) {
        setAuthToken(token)
        try {
          const response = await authApi.me()
          setUser(response.data)
        } catch (error) {
          // Token invalid, clear it
          localStorage.removeItem(TOKEN_KEY)
          setAuthToken(null)
        }
      }

      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (data: LoginRequest) => {
    const response = await authApi.login(data)
    const { access_token } = response.data

    // Store token
    localStorage.setItem(TOKEN_KEY, access_token)
    setAuthToken(access_token)

    // Fetch user info
    const userResponse = await authApi.me()
    setUser(userResponse.data)
  }

  const register = async (data: RegisterRequest) => {
    // Register user
    await authApi.register(data)

    // Auto-login after registration
    await login({ username: data.username, password: data.password })
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY)
    setAuthToken(null)
    setUser(null)
  }

  const refreshUser = async () => {
    try {
      const response = await authApi.me()
      setUser(response.data)
    } catch (error) {
      logout()
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

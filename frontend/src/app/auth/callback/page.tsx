'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export default function Callback() {
  const router = useRouter()
  const { session } = useAuth()

  useEffect(() => {
    if (session) {
      router.push('/dashboard')
    }
  }, [session, router])

  return (
    <main className="min-h-screen bg-[url('/nba-court-bg.png')] bg-cover bg-center flex items-center justify-center px-4">
      <div className="text-center">
        <div className="w-12 h-12 mx-auto mb-4 border-4 border-white border-t-transparent rounded-full animate-spin" />
        <p className="text-white text-lg font-medium">Redirecting...</p>
      </div>
    </main>
  )
}

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export default function Dashboard() {
  const router = useRouter()
  const { session, user, supabase } = useAuth()
  const [isActive, setisActive] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!session) {
      router.push('/')
      return
    }

    const checkActive = async () => {
      const userId = user?.user_metadata?.provider_id
      if (!userId) return

      const { data: channel } = await supabase
        .from('channels')
        .select('*')
        .eq('broadcaster_user_id', userId)
        .single()

      setisActive(!!channel)
      setLoading(false)
    }

    checkActive()
  }, [session, user, supabase, router])

  const handleJoin = async () => {
    const userId = user?.user_metadata?.provider_id
    if (!userId) return

    await supabase.from('channels').upsert({ broadcaster_user_id: userId })
    setisActive(true)
  }

  const handleLeave = async () => {
    const userId = user?.user_metadata?.provider_id
    if (!userId) return
    
    await supabase.from('channels').delete().eq('broadcaster_user_id', userId)
    setisActive(false) 
  }

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/')
  }

  if (loading || !session) return (
    <main>
      <p>Loading...</p>
    </main>
  )

  return (
    <main>
      <h1>Hello, {user?.user_metadata?.full_name}</h1>
      {isActive ? (
        <button onClick={handleLeave}>Leave Channel</button>
      ) : (
        <button onClick={handleJoin}>Join Channel</button>
      )}
      <br />
      <button onClick={handleLogout} className="mt-4">Logout</button>
    </main>
  )
}

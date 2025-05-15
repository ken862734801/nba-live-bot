'use client'

import Head from 'next/head'
import Image from 'next/image'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export default function Dashboard() {
  const router = useRouter()
  const { session, user, supabase } = useAuth()
  const [isActive, setIsActive] = useState(false)
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
        .select('is_active')
        .eq('broadcaster_user_id', userId)
        .single()

      setIsActive(!!channel?.is_active)
      setLoading(false)
    }

    checkActive()
  }, [session, user, supabase, router])

  const handleJoin = async () => {
    const md = user?.user_metadata
    if (!md) return

    await supabase
      .from('channels')
      .upsert({
        broadcaster_user_id: md.provider_id,
        user_name: md.full_name,
        is_active: true,
        updated_at: new Date().toISOString(),
      })
    setIsActive(true)
  }

  const handleLeave = async () => {
    const md = user?.user_metadata
    if (!md) return

    await supabase
      .from('channels')
      .update({ is_active: false, updated_at: new Date().toISOString() })
      .eq('broadcaster_user_id', md.provider_id)
    setIsActive(false)
  }

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/')
  }

  const avatarUrl =
    user?.user_metadata?.avatar_url || '/twitch-icon.svg'

  if (loading || !session) {
    return (
      <main className="flex items-center justify-center min-h-screen bg-[url('/nba-court-bg.png')] bg-cover bg-center px-4">
        <p className="text-white text-lg">Loading...</p>
      </main>
    )
  }

  return (
    <>
      <Head>
        <title>Dashboard • NBALiveBot</title>
      </Head>

      <main className="min-h-screen bg-[url('/nba-court-bg.png')] bg-cover bg-center flex items-center justify-center px-4">
        <div className="bg-black/70 backdrop-blur-md rounded-3xl shadow-2xl p-10 max-w-md w-full text-center">
          <div className="mx-auto w-24 h-24 mb-4 relative">
            <Image
              src={avatarUrl}
              alt="User avatar"
              className="rounded-full object-cover"
              fill
            />
          </div>

          <h2 className="text-lg text-white font-medium mb-6 capitalize">
            Hello, {user?.user_metadata?.full_name}!
          </h2>

          <button
            onClick={isActive ? handleLeave : handleJoin}
            className="w-full bg-[#9146FF] hover:bg-[#772ce8] text-white font-semibold py-2.5 px-4 mb-4 rounded-xl transition cursor-pointer"
          >
            {isActive ? 'Leave Channel' : 'Join Channel'}
          </button>

          <button
            onClick={handleLogout}
            className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-2.5 px-4 rounded-xl transition cursor-pointer"
          >
            Logout
          </button>
        </div>
      </main>
    </>
  )
}

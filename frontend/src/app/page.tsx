'use client'

import Head from 'next/head'
import Image from 'next/image'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'

export default function Home() {
  const router = useRouter()
  const { session, supabase } = useAuth()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (session) router.push('/dashboard')
  }, [session, router])

  const handleLogin = async () => {
    setLoading(true)
    await supabase.auth.signInWithOAuth({
      provider: 'twitch',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      },
    })
  }

  return (
    <>
      <Head>
        <title>Login • NBALiveBot</title>
        <link rel="icon" href="/twitch-icon.svg" />
      </Head>

      <main className="min-h-screen bg-[url('/nba-court-bg.png')] bg-cover bg-center flex items-center justify-center px-4">
        <div className="bg-black/70 backdrop-blur-md rounded-3xl shadow-2xl p-10 max-w-md w-full text-center">
          {/* <Image
            src="/logo.png"
            alt="NBALiveBot Logo"
            width={120}
            height={120}
            className="mx-auto mb-5"
            priority
          /> */}
          <h1 className="text-4xl font-extrabold text-white mb-2">NBALiveBot</h1>
          <p className="text-gray-300 text-sm mb-6">
            Get real-time NBA stats right in your Twitch chat.
          </p>
          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-[#9146FF] hover:bg-[#772ce8] text-white font-semibold py-2.5 px-4 rounded-xl transition cursor-pointer"
          >
            {loading ? 'Connecting...' : 'Login with Twitch'}
          </button>
          <p className="text-xs text-gray-400 mt-4">
            Login required to connect your Twitch channel.
          </p>
        </div>
      </main>
    </>
  )
}

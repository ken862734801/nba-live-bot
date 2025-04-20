"use client"

import { createClient } from "@supabase/supabase-js"
import type { Session, User } from "@supabase/supabase-js"
import { createContext, useContext, useEffect, useState } from "react"

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_KEY!);

type AuthContextType = {
    session: Session | null
    user: User | null
    supabase: typeof supabase
}
const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({children}: {children: React.ReactNode}) {
    const [session, setSession] = useState<Session | null>(null)
    const [user, setUser] = useState<User | null>(null)
    
    useEffect(() => {
        const init = async () => {
            const {data} = await supabase.auth.getSession()
            setSession(data.session)
            setUser(data.session?.user ?? null)
        }
        
        const {
            data: { subscription},
            } = supabase.auth.onAuthStateChange((_, session) => {
                setSession(session)
                setUser(session?.user ?? null)
        })

        init()

        return () => {
            subscription.unsubscribe()
        }
    }, [])

    return (
        <AuthContext.Provider value={{session, user, supabase}}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth(){
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider")
    }
    return context
}
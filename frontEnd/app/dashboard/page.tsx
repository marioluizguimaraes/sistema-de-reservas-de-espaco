"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [stats, setStats] = useState({ minhasSalas: 0, minhasReservas: 0 })

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }

    // Fetch user data and stats
    fetchData(token)
  }, [router])

  const fetchData = async (token: string) => {
    try {
      // Get current user info from localStorage or API
      const userInfo = localStorage.getItem("user")
      if (userInfo) {
        setUser(JSON.parse(userInfo))
      }

      // Fetch minhas salas and reservas for stats
      const [salasRes, reservasRes] = await Promise.all([
        fetch("http://localhost:3001/salas?minhas=true", {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch("http://localhost:3001/reservas", {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ])

      const salasData = await salasRes.json()
      const reservasData = await reservasRes.json()

      setStats({
        minhasSalas: salasData.results?.length || 0,
        minhasReservas: reservasData.results?.length || 0,
      })
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-primary">
            SpaceHub
          </Link>
          <button
            onClick={() => {
              localStorage.removeItem("access_token")
              router.push("/")
            }}
            className="text-sm font-medium text-muted-foreground hover:text-foreground"
          >
            Sair
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="p-6 bg-card border border-border rounded-lg">
            <p className="text-muted-foreground text-sm mb-2">Minhas Salas</p>
            <p className="text-4xl font-bold text-primary mb-4">{stats.minhasSalas}</p>
            <Link href="/minhas-salas">
              <Button variant="outline" size="sm" className="w-full bg-transparent">
                Ver Salas
              </Button>
            </Link>
          </div>

          <div className="p-6 bg-card border border-border rounded-lg">
            <p className="text-muted-foreground text-sm mb-2">Minhas Reservas</p>
            <p className="text-4xl font-bold text-primary mb-4">{stats.minhasReservas}</p>
            <Link href="/minhas-reservas">
              <Button variant="outline" size="sm" className="w-full bg-transparent">
                Ver Reservas
              </Button>
            </Link>
          </div>

          <div className="p-6 bg-card border border-border rounded-lg">
            <p className="text-muted-foreground text-sm mb-2">Ações Rápidas</p>
            <div className="space-y-2">
              <Link href="/salas" className="block">
                <Button variant="outline" size="sm" className="w-full bg-transparent">
                  Explorar Salas
                </Button>
              </Link>
              <Link href="/minhas-salas/nova" className="block">
                <Button variant="outline" size="sm" className="w-full bg-transparent">
                  Criar Sala
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Quick Navigation */}
        <div className="bg-secondary/30 p-6 rounded-lg border border-border">
          <h2 className="text-lg font-bold mb-4">Navegação Rápida</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <Link href="/salas" className="block">
              <Button variant="outline" className="w-full justify-start bg-transparent">
                🔍 Explorar Salas Disponíveis
              </Button>
            </Link>
            <Link href="/minhas-salas" className="block">
              <Button variant="outline" className="w-full justify-start bg-transparent">
                🏢 Gerenciar Minhas Salas
              </Button>
            </Link>
            <Link href="/minhas-reservas" className="block">
              <Button variant="outline" className="w-full justify-start bg-transparent">
                📅 Minhas Reservas
              </Button>
            </Link>
            <Link href="/relatorios" className="block">
              <Button variant="outline" className="w-full justify-start bg-transparent">
                📊 Relatórios
              </Button>
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}

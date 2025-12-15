"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import SalaCard from "@/components/salas/sala-card"
import { useRouter } from "next/navigation"

interface Sala {
  id: number
  nome: string
  descricao: string
  capacidade: number
  preco_por_hora: string
  cidade: string
  rua: string
  numero: string
  dono?: { username: string }
}

export default function SalasPage() {
  const router = useRouter()
  const [salas, setSalas] = useState<Sala[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [filtro, setFiltro] = useState("")
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    setIsAuthenticated(!!token)

    if (!token) {
      router.push("/login")
      return
    }

    fetchSalas(token)
  }, [router])

  const fetchSalas = async (token: string) => {
    try {
      const url = filtro ? `http://localhost:3001/salas?cidade=${filtro}` : "http://localhost:3001/salas"

      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!res.ok) throw new Error("Erro ao buscar salas")

      const data = await res.json()
      setSalas(data.results || data)
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
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
          <div className="flex gap-4">
            <Link href="/minhas-salas">
              <Button variant="outline" size="sm">
                Minhas Salas
              </Button>
            </Link>
            <Link href="/minhas-reservas">
              <Button variant="outline" size="sm">
                Minhas Reservas
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" size="sm">
                Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-6">Explorar Salas</h1>
          <div className="flex gap-4">
            <Input
              placeholder="Filtrar por cidade..."
              value={filtro}
              onChange={(e) => setFiltro(e.target.value)}
              className="max-w-sm"
            />
            <Button onClick={() => fetchSalas(localStorage.getItem("access_token") || "")}>Buscar</Button>
          </div>
        </div>

        {/* Salas Grid */}
        {isLoading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
          </div>
        ) : salas.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            <p className="mb-4">Nenhuma sala encontrada</p>
            <Link href="/minhas-salas">
              <Button>Criar Sala</Button>
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {salas.map((sala) => (
              <SalaCard key={sala.id} sala={sala} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

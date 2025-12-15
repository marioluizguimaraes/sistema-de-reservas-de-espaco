"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import SalaCard from "@/components/salas/sala-card"

interface Sala {
  id: number
  nome: string
  descricao: string
  capacidade: number
  preco_por_hora: string
  cidade: string
  rua: string
  numero: string
}

export default function MinhasSalasPage() {
  const router = useRouter()
  const [salas, setSalas] = useState<Sala[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }

    fetchSalas(token)
  }, [router])

  const fetchSalas = async (token: string) => {
    try {
      const res = await fetch("http://localhost:3001/salas?minhas=true", {
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

  const handleDelete = async (id: number) => {
    if (!confirm("Tem certeza que deseja deletar esta sala?")) return

    try {
      const token = localStorage.getItem("access_token")
      const res = await fetch(`http://localhost:3001/salas/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!res.ok) throw new Error("Erro ao deletar sala")

      setSalas(salas.filter((s) => s.id !== id))
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
          <Link href="/dashboard">
            <Button variant="outline" size="sm">
              Voltar
            </Button>
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Minhas Salas</h1>
          <Link href="/minhas-salas/nova">
            <Button>+ Criar Sala</Button>
          </Link>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
          </div>
        ) : salas.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground mb-4">Você ainda não tem nenhuma sala</p>
            <Link href="/minhas-salas/nova">
              <Button>Criar Primeira Sala</Button>
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {salas.map((sala) => (
              <div key={sala.id} className="relative">
                <SalaCard sala={sala} />
                <div className="absolute top-4 right-4 flex gap-2">
                  <Link href={`/minhas-salas/${sala.id}/editar`}>
                    <Button variant="outline" size="sm">
                      Editar
                    </Button>
                  </Link>
                  <button
                    onClick={() => handleDelete(sala.id)}
                    className="px-3 py-1 text-sm font-medium bg-destructive/10 text-destructive hover:bg-destructive/20 rounded transition"
                  >
                    Deletar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

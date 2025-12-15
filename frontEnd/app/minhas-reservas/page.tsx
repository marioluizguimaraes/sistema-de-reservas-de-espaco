"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import ReservaCard from "@/components/reservas/reserva-card"

interface Reserva {
  id: number
  sala: number
  data_inicio: string
  data_fim: string
  status: string
  forma_pagamento: string
  valor_total?: number
}

export default function MinhasReservasPage() {
  const router = useRouter()
  const [reservas, setReservas] = useState<Reserva[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }

    fetchReservas(token)
  }, [router])

  const fetchReservas = async (token: string) => {
    try {
      const res = await fetch("http://localhost:3001/reservas", {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!res.ok) throw new Error("Erro ao buscar reservas")

      const data = await res.json()
      setReservas(data.results || data)
    } catch (err) {
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleResponder = async (id: number, acao: "APROVAR" | "REJEITAR") => {
    try {
      const token = localStorage.getItem("access_token")
      const res = await fetch(`http://localhost:3001/reservas/${id}/responder`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ acao }),
      })

      if (!res.ok) throw new Error("Erro ao responder reserva")

      fetchReservas(token || "")
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
        <h1 className="text-3xl font-bold mb-8">Minhas Reservas</h1>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
          </div>
        ) : reservas.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-muted-foreground mb-4">Você não tem nenhuma reserva</p>
            <Link href="/salas">
              <Button>Explorar Salas</Button>
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {reservas.map((reserva) => (
              <ReservaCard key={reserva.id} reserva={reserva} onResponder={handleResponder} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}

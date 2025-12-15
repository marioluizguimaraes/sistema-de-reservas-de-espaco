"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter, useParams } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface Sala {
  id: number
  nome: string
  descricao: string
  capacidade: number
  preco_por_hora: string
  cidade: string
  rua: string
  numero: string
  bairro: string
  estado: string
  cep: string
  dono?: { username: string }
}

export default function SalaDetailPage() {
  const router = useRouter()
  const params = useParams()
  const salaId = params.id
  const [sala, setSala] = useState<Sala | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isReserving, setIsReserving] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    data_inicio: "",
    data_fim: "",
    forma_pagamento: "PIX",
  })

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (!token) {
      router.push("/login")
      return
    }

    fetchSala(token)
  }, [salaId, router])

  const fetchSala = async (token: string) => {
    try {
      const res = await fetch(`http://localhost:3001/salas/${salaId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })

      if (!res.ok) throw new Error("Sala não encontrada")

      const data = await res.json()
      setSala(data)
    } catch (err) {
      console.error(err)
      router.push("/salas")
    } finally {
      setIsLoading(false)
    }
  }

  const handleReserve = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsReserving(true)

    try {
      const token = localStorage.getItem("access_token")
      if (!token) throw new Error("Não autenticado")

      const res = await fetch("http://localhost:3001/reservas", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          sala: salaId,
          data_inicio: new Date(formData.data_inicio).toISOString(),
          data_fim: new Date(formData.data_fim).toISOString(),
          forma_pagamento: formData.forma_pagamento,
        }),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || "Erro ao reservar")
      }

      alert("Reserva criada com sucesso!")
      router.push("/minhas-reservas")
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao reservar")
    } finally {
      setIsReserving(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
      </div>
    )
  }

  if (!sala) {
    return <div>Sala não encontrada</div>
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-primary">
            SpaceHub
          </Link>
          <Link href="/salas">
            <Button variant="outline" size="sm">
              Voltar
            </Button>
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Imagem */}
        <div className="w-full h-64 bg-muted rounded-lg mb-8 flex items-center justify-center">
          <span className="text-8xl">🏢</span>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Info */}
          <div className="md:col-span-2">
            <h1 className="text-4xl font-bold mb-2">{sala.nome}</h1>
            <p className="text-lg text-muted-foreground mb-6">{sala.descricao}</p>

            <div className="space-y-6">
              <div>
                <h3 className="font-bold text-lg mb-4">Detalhes</h3>
                <div className="grid gap-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Capacidade:</span>
                    <span className="font-medium">{sala.capacidade} pessoas</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Preço por hora:</span>
                    <span className="font-medium">R$ {sala.preco_por_hora}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Localização:</span>
                    <span className="font-medium">
                      {sala.rua}, {sala.numero}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Cidade/Estado:</span>
                    <span className="font-medium">
                      {sala.cidade}, {sala.estado}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">CEP:</span>
                    <span className="font-medium">{sala.cep}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Reservar */}
          <div className="bg-card border border-border rounded-lg p-6 h-fit">
            <h3 className="font-bold text-lg mb-4">Reservar Sala</h3>

            {!showForm ? (
              <Button onClick={() => setShowForm(true)} className="w-full rounded-full">
                Fazer Reserva
              </Button>
            ) : (
              <form onSubmit={handleReserve} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Data/Hora Início *</label>
                  <Input
                    type="datetime-local"
                    value={formData.data_inicio}
                    onChange={(e) => setFormData({ ...formData, data_inicio: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Data/Hora Fim *</label>
                  <Input
                    type="datetime-local"
                    value={formData.data_fim}
                    onChange={(e) => setFormData({ ...formData, data_fim: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Forma de Pagamento *</label>
                  <select
                    value={formData.forma_pagamento}
                    onChange={(e) => setFormData({ ...formData, forma_pagamento: e.target.value })}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                  >
                    <option value="PIX">PIX</option>
                    <option value="CARTAO">Cartão</option>
                    <option value="BOLETO">Boleto</option>
                  </select>
                </div>

                <Button type="submit" disabled={isReserving} className="w-full">
                  {isReserving ? "Reservando..." : "Confirmar Reserva"}
                </Button>

                <Button type="button" variant="outline" onClick={() => setShowForm(false)} className="w-full">
                  Cancelar
                </Button>
              </form>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

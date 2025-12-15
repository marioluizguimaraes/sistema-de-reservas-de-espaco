"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function NovaSalaPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [formData, setFormData] = useState({
    nome: "",
    descricao: "",
    capacidade: "",
    preco_por_hora: "",
    rua: "",
    numero: "",
    bairro: "",
    cidade: "",
    estado: "",
    cep: "",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    try {
      const token = localStorage.getItem("access_token")
      if (!token) throw new Error("Não autenticado")

      const res = await fetch("http://localhost:3001/salas", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          ...formData,
          capacidade: Number.parseInt(formData.capacidade),
          preco_por_hora: Number.parseFloat(formData.preco_por_hora),
        }),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || "Erro ao criar sala")
      }

      router.push("/minhas-salas")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar sala")
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
          <Link href="/minhas-salas">
            <Button variant="outline" size="sm">
              Voltar
            </Button>
          </Link>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Criar Nova Sala</h1>

        <form onSubmit={handleSubmit} className="space-y-6 bg-card p-8 rounded-lg border border-border">
          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/30 rounded text-destructive text-sm">
              {error}
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Nome da Sala *</label>
              <Input name="nome" value={formData.nome} onChange={handleChange} required />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Capacidade *</label>
              <Input name="capacidade" type="number" value={formData.capacidade} onChange={handleChange} required />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Descrição</label>
            <textarea
              name="descricao"
              value={formData.descricao}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
              rows={4}
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Preço por Hora *</label>
              <Input
                name="preco_por_hora"
                type="number"
                step="0.01"
                value={formData.preco_por_hora}
                onChange={handleChange}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Cidade *</label>
              <Input name="cidade" value={formData.cidade} onChange={handleChange} required />
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Rua *</label>
              <Input name="rua" value={formData.rua} onChange={handleChange} required />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Número *</label>
              <Input name="numero" value={formData.numero} onChange={handleChange} required />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Bairro</label>
              <Input name="bairro" value={formData.bairro} onChange={handleChange} />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Estado *</label>
              <Input name="estado" value={formData.estado} onChange={handleChange} required />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">CEP *</label>
              <Input name="cep" value={formData.cep} onChange={handleChange} required />
            </div>
          </div>

          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? "Criando..." : "Criar Sala"}
          </Button>
        </form>
      </main>
    </div>
  )
}

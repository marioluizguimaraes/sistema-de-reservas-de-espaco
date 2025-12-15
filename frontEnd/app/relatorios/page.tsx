"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface Sala {
  id: number
  nome: string
}

export default function RelatoriosPage() {
  const router = useRouter()
  const [salas, setSalas] = useState<Sala[]>([])
  const [salaId, setSalaId] = useState("")
  const [limite, setLimite] = useState("10")
  const [ordenacao, setOrdenacao] = useState("RECENTES")
  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [relatorio, setRelatorio] = useState("")

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

  const handleGerarRelatorio = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!salaId) return

    setIsGenerating(true)
    try {
      const url = `http://localhost:3001/relatorios/sala/${salaId}?limite=${limite}&ordenacao=${ordenacao}`
      const res = await fetch(url)

      if (!res.ok) throw new Error("Erro ao gerar relatório")

      const xml = await res.text()
      setRelatorio(xml)
    } catch (err) {
      console.error(err)
      setRelatorio("Erro ao gerar relatório")
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadRelatorio = () => {
    const element = document.createElement("a")
    element.setAttribute("href", "data:text/xml;charset=utf-8," + encodeURIComponent(relatorio))
    element.setAttribute("download", `relatorio-sala-${salaId}.xml`)
    element.style.display = "none"
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
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

      <main className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Relatórios de Salas</h1>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Formulário */}
            <form onSubmit={handleGerarRelatorio} className="bg-card p-6 rounded-lg border border-border space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Selecionar Sala *</label>
                <select
                  value={salaId}
                  onChange={(e) => setSalaId(e.target.value)}
                  className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                  required
                >
                  <option value="">-- Selecione uma sala --</option>
                  {salas.map((sala) => (
                    <option key={sala.id} value={sala.id}>
                      {sala.nome}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Limite de Registros</label>
                  <Input type="number" value={limite} onChange={(e) => setLimite(e.target.value)} min="1" />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Ordenação</label>
                  <select
                    value={ordenacao}
                    onChange={(e) => setOrdenacao(e.target.value)}
                    className="w-full px-3 py-2 border border-border rounded-lg bg-background text-foreground"
                  >
                    <option value="RECENTES">Mais Recentes</option>
                    <option value="ANTIGAS">Mais Antigas</option>
                    <option value="MAIOR_DURACAO">Maior Duração</option>
                  </select>
                </div>
              </div>

              <Button type="submit" disabled={isGenerating} className="w-full">
                {isGenerating ? "Gerando..." : "Gerar Relatório SOAP"}
              </Button>
            </form>

            {/* Resultado */}
            {relatorio && (
              <div className="bg-card p-6 rounded-lg border border-border space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold">Relatório (XML)</h2>
                  <Button onClick={downloadRelatorio} variant="outline" size="sm">
                    📥 Download
                  </Button>
                </div>

                <pre className="bg-muted p-4 rounded text-xs overflow-auto max-h-96 text-foreground">{relatorio}</pre>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}

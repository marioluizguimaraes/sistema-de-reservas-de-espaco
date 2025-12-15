"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { LogIn } from "lucide-react"

export default function Home() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    setIsAuthenticated(!!token)
    setIsLoading(false)
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent"></div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <nav className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="text-2xl font-bold text-primary">SpaceHub</div>
          <div className="flex gap-4">
            {isAuthenticated ? (
              <>
                <Link href="/dashboard">
                  <Button variant="outline">Dashboard</Button>
                </Link>
                <Link href="/salas">
                  <Button variant="outline">Explorar</Button>
                </Link>
                <button
                  onClick={() => {
                    localStorage.removeItem("access_token")
                    router.push("/")
                  }}
                  className="px-4 py-2 text-sm font-medium text-foreground hover:bg-muted rounded-lg transition"
                >
                  Sair
                </button>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="outline">
                    <LogIn />
                    Entrar</Button>
                </Link>
                <Link href="/register">
                  <Button>Criar Conta</Button>
                </Link>
              </>
            )}
          </div>
        </nav>
      </header>

      <section className="px-4 py-20 text-center">
        <h1 className="text-5xl font-bold mb-6 text-foreground">Encontre a Sala Perfeita</h1>
        <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
          Alugue salas de reunião, espaços de trabalho e outros ambientes com facilidade
        </p>
        <div className="flex gap-4 justify-center">
          {isAuthenticated ? (
            <Link href="/salas">
              <Button size="lg" className="rounded-full px-8">
                Explorar Salas
              </Button>
            </Link>
          ) : (
            <>
              <Link href="/register">
                <Button size="lg" className="rounded-full px-8">
                  Começar Agora
                </Button>
              </Link>
              <Link href="/salas">
                <Button variant="outline" size="lg" className="rounded-full px-8 bg-transparent">
                  Ver Salas
                </Button>
              </Link>
            </>
          )}
        </div>
      </section>
    </main>
  )
}

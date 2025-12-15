"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function RegisterPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    cpf: "",
    celular: "",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
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
      const res = await fetch("http://localhost:3001/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.error || "Erro ao registrar")
      }

      router.push("/login?registered=true")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao registrar")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">SpaceHub</h1>
          <p className="text-muted-foreground">Criar nova conta</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 bg-card p-8 rounded-lg border border-border">
          {error && (
            <div className="p-4 bg-destructive/10 border border-destructive/30 rounded text-destructive text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">Usuário</label>
            <Input
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="seu_usuario"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Email</label>
            <Input
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="seu@email.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Senha</label>
            <Input
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">CPF</label>
            <Input name="cpf" value={formData.cpf} onChange={handleChange} placeholder="000.000.000-00" required />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Celular</label>
            <Input name="celular" value={formData.celular} onChange={handleChange} placeholder="11999999999" required />
          </div>

          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? "Registrando..." : "Criar Conta"}
          </Button>
        </form>

        <p className="text-center mt-6 text-muted-foreground">
          Já tem conta?{" "}
          <Link href="/login" className="text-primary font-medium hover:underline">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  )
}

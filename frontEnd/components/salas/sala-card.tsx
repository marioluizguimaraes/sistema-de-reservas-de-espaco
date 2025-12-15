"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Images } from "lucide-react"

interface Sala {
  id: number
  nome: string
  descricao?: string
  capacidade: number
  preco_por_hora: string
  cidade: string
  rua: string
  numero: string
  dono?: { username: string }
}

export default function SalaCard({ sala }: { sala: Sala }) {
  return (
    <Link href={`/salas/${sala.id}`}>
      <div className="bg-card border border-border rounded-lg p-6 hover:shadow-lg transition cursor-pointer h-full flex flex-col">
        {/* Imagem Placeholder */}
        <div className="w-full h-40 bg-muted rounded-lg mb-4 flex items-center justify-center">
          <span><Images className="text-gray-300" size={64}/></span>
        </div>

        {/* Conteúdo */}
        <h3 className="font-bold text-lg mb-2 line-clamp-2">{sala.nome}</h3>

        {sala.descricao && <p className="text-sm text-muted-foreground mb-3 line-clamp-2">{sala.descricao}</p>}

        {/* Detalhes */}
        <div className="space-y-2 mb-4 flex-1">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Capacidade:</span>
            <span className="font-medium">{sala.capacidade} pessoas</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Preço:</span>
            <span className="font-medium">R$ {sala.preco_por_hora}/h</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Localização:</span>
            <span className="font-medium">{sala.cidade}</span>
          </div>
        </div>

        <Button className="w-full rounded-full">Ver Detalhes</Button>
      </div>
    </Link>
  )
}

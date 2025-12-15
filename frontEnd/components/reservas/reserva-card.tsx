"use client"

import { Button } from "@/components/ui/button"
import { useState } from "react"

interface Reserva {
  id: number
  sala: number
  data_inicio: string
  data_fim: string
  status: string
  forma_pagamento: string
  valor_total?: number
}

interface ReservaCardProps {
  reserva: Reserva
  onResponder?: (id: number, acao: "APROVAR" | "REJEITAR") => void
}

export default function ReservaCard({ reserva, onResponder }: ReservaCardProps) {
  const [isResponding, setIsResponding] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "APROVADA":
        return "bg-green-100 text-green-800 border-green-300"
      case "REJEITADA":
        return "bg-red-100 text-red-800 border-red-300"
      case "PENDENTE_APROVACAO":
        return "bg-yellow-100 text-yellow-800 border-yellow-300"
      case "CANCELADA":
        return "bg-gray-100 text-gray-800 border-gray-300"
      case "CONCLUIDA":
        return "bg-blue-100 text-blue-800 border-blue-300"
      default:
        return "bg-muted text-foreground"
    }
  }

  const inicio = new Date(reserva.data_inicio).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })

  const fim = new Date(reserva.data_fim).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })

  return (
    <div className="bg-card border border-border rounded-lg p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-bold text-lg">Sala #{reserva.sala}</h3>
          <p className="text-sm text-muted-foreground">Reserva #{reserva.id}</p>
        </div>
        <span className={`px-3 py-1 text-sm font-medium rounded border ${getStatusColor(reserva.status)}`}>
          {reserva.status}
        </span>
      </div>

      <div className="grid md:grid-cols-2 gap-4 mb-6 text-sm">
        <div>
          <p className="text-muted-foreground mb-1">Início</p>
          <p className="font-medium">{inicio}</p>
        </div>
        <div>
          <p className="text-muted-foreground mb-1">Fim</p>
          <p className="font-medium">{fim}</p>
        </div>
        <div>
          <p className="text-muted-foreground mb-1">Forma de Pagamento</p>
          <p className="font-medium">{reserva.forma_pagamento}</p>
        </div>
        {reserva.valor_total && (
          <div>
            <p className="text-muted-foreground mb-1">Valor Total</p>
            <p className="font-medium">R$ {reserva.valor_total}</p>
          </div>
        )}
      </div>

      {reserva.status === "PENDENTE_APROVACAO" && onResponder && (
        <div className="flex gap-4">
          <Button
            onClick={() => {
              setIsResponding(true)
              onResponder(reserva.id, "APROVAR")
            }}
            disabled={isResponding}
            className="flex-1"
          >
            ✓ Aprovar
          </Button>
          <Button
            onClick={() => {
              setIsResponding(true)
              onResponder(reserva.id, "REJEITAR")
            }}
            disabled={isResponding}
            variant="outline"
            className="flex-1"
          >
            ✗ Rejeitar
          </Button>
        </div>
      )}
    </div>
  )
}

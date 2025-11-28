from django.db import models
from django.conf import settings
from .sala import Sala

class Reserva(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE_APROVACAO', 'Aguardando Aprovação do Dono'),
        ('APROVADA', 'Aprovada'),
        ('REJEITADA', 'Rejeitada'),
        ('CANCELADA', 'Cancelada pelo Solicitante'),
        ('CONCLUIDA', 'Concluída'),
    ]

    PAGAMENTO_CHOICES = [
        ('PIX', 'Pix'),
        ('CARTAO_CREDITO', 'Cartão de Crédito'),
        ('CARTAO_DEBITO', 'Cartão de Débito'),
        ('BOLETO', 'Boleto'),
        ('DINHEIRO', 'Dinheiro no Local'),
    ]

    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='minhas_reservas')
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, related_name='reservas_recebidas')
    
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    forma_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE_APROVACAO')
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criado_em']
        db_table = "reservas"
        
    def __str__(self):
        return f"Reserva {self.id} - {self.sala.nome} ({self.status})"
    
    def calcular_valor_total(self):
        if self.data_inicio and self.data_fim and self.sala.preco_por_hora:
            diff = self.data_fim - self.data_inicio
            horas = diff.total_seconds() / 3600
            self.valor_total = round(float(self.sala.preco_por_hora) * horas, 2)
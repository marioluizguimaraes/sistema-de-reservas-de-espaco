from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from api.models import Reserva
from api.serializers import ReservaSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Reserva.objects.filter(
            models.Q(solicitante=user) | models.Q(sala__dono=user)
        ).distinct()

    def perform_create(self, serializer):
        reserva = serializer.save(solicitante=self.request.user)
        reserva.calcular_valor_total()
        reserva.save()

    @decorators.action(detail=True, methods=['post'])
    def responder(self, request, pk=None):
        """
        Endpoint para o DONO da sala ACEITAR ou REJEITAR a reserva.
        Body: { "acao": "APROVAR" } ou { "acao": "REJEITAR" }
        """
        reserva = self.get_object()
        
        if request.user != reserva.sala.dono:
            return Response(
                {"erro": "Apenas o dono da sala pode aprovar/rejeitar reservas."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        acao = request.data.get('acao', '').upper()
        
        if acao == 'APROVAR':
            reserva.status = 'APROVADA'
        elif acao == 'REJEITAR':
            reserva.status = 'REJEITADA'
        else:
            return Response({"erro": "Ação inválida. Use APROVAR ou REJEITAR."}, status=400)
            
        reserva.save()
        return Response({"status": f"Reserva {reserva.status.lower()} com sucesso."})

    @decorators.action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Endpoint para o SOLICITANTE cancelar sua própria reserva.
        """
        reserva = self.get_object()
        
        if request.user != reserva.solicitante:
            return Response({"erro": "Apenas o solicitante pode cancelar."}, status=403)
            
        if reserva.status in ['REJEITADA', 'CANCELADA', 'CONCLUIDA']:
             return Response({"erro": "Não é possível cancelar esta reserva."}, status=400)

        reserva.status = 'CANCELADA'
        reserva.save()
        return Response({"status": "Reserva cancelada."})
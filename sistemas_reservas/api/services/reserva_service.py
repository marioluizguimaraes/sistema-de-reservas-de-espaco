from django.db.models import Q
from api.models import Reserva

class ReservaService:
    @staticmethod
    def verificar_disponibilidade(sala, data_inicio, data_fim, reserva_id_ignorar=None):
        """
        Verifica se a sala está livre. 
        Reservas REJEITADAS ou CANCELADAS não ocupam espaço.
        """
        conflitos = Reserva.objects.filter(
            sala=sala,
            status__in=['PENDENTE_APROVACAO', 'APROVADA']
        ).filter(
            Q(data_inicio__lt=data_fim) & Q(data_fim__gt=data_inicio)
        )

        if reserva_id_ignorar:
            conflitos = conflitos.exclude(id=reserva_id_ignorar)

        return not conflitos.exists()
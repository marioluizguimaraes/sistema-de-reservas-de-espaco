from rest_framework import serializers
from api.models import Reserva
from api.services import ReservaService

class ReservaSerializer(serializers.ModelSerializer):
    sala_nome = serializers.CharField(source='sala.nome', read_only=True)
    solicitante_nome = serializers.CharField(source='solicitante.username', read_only=True)

    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ('solicitante', 'status', 'valor_total', 'criado_em', 'atualizada_em')

    def validate(self, data):
        if data['data_inicio'] >= data['data_fim']:
            raise serializers.ValidationError("Data de início deve ser anterior ao fim.")
            
        sala = data.get('sala') or self.instance.sala
        reserva_id = self.instance.id if self.instance else None

        if not ReservaService.verificar_disponibilidade(sala, data['data_inicio'], data['data_fim'], reserva_id):
            raise serializers.ValidationError("Sala indisponível para este horário.")

        return data
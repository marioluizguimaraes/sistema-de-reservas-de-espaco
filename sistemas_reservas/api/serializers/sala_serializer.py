from rest_framework import serializers
from api.models import Sala

class SalaSerializer(serializers.ModelSerializer):
    dono_nome = serializers.CharField(source='dono.username', read_only=True)

    class Meta:
        model = Sala
        fields = '__all__'
        read_only_fields = ('dono', 'criado_em', 'atualizado_em')
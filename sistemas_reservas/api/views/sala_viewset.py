from rest_framework import viewsets, permissions
from api.models import Sala
from api.serializers import SalaSerializer

class SalaViewSet(viewsets.ModelViewSet):
    serializer_class = SalaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Qualquer um vê, só logado cria

    def get_queryset(self):
        queryset = Sala.objects.all()
        minhas = self.request.query_params.get('minhas')
        
        if minhas == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(dono=self.request.user)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(dono=self.request.user)
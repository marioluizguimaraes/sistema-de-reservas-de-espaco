from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Sala, Reserva
from api.soap_service import RelatorioSoapService
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class SetupTestCase(TestCase):
    """Configuração base para os testes"""
    def setUp(self):
        self.client = APIClient()
        
        # Criar Usuários
        self.dono = User.objects.create_user(
            username='dono', password='password123', email='dono@teste.com',
            cpf='111.111.111-11', celular='11999999999'
        )
        self.solicitante = User.objects.create_user(
            username='solicitante', password='password123', email='solicitante@teste.com',
            cpf='222.222.222-22', celular='22999999999'
        )
        
        # Tokens JWT (Autenticação Manual para os testes)
        response_dono = self.client.post(reverse('login'), {'username': 'dono', 'password': 'password123'})
        self.token_dono = response_dono.data['access']
        
        response_solicitante = self.client.post(reverse('login'), {'username': 'solicitante', 'password': 'password123'})
        self.token_solicitante = response_solicitante.data['access']

        # Criar uma Sala (pertence ao dono)
        self.sala = Sala.objects.create(
            dono=self.dono, nome="Sala Teste", capacidade=10, 
            preco_por_hora=50.00, rua="Rua A", numero="1", 
            bairro="Centro", cidade="São Paulo", estado="SP", cep="00000-000"
        )

class UserTests(TestCase):
    def test_registro_usuario(self):
        """Deve permitir cadastrar um novo usuário"""
        client = APIClient()
        data = {
            "username": "novo_user", "password": "password123", "email": "novo@teste.com",
            "cpf": "333.333.333-33", "celular": "33999999999"
        }
        response = client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

class SalaTests(SetupTestCase):
    def test_criar_sala_autenticado(self):
        """Usuário logado deve conseguir criar sala"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_dono)
        data = {
            "nome": "Sala Nova", "capacidade": 5, "preco_por_hora": "100.00",
            "rua": "Rua B", "numero": "2", "bairro": "Bairro B",
            "cidade": "Rio", "estado": "RJ", "cep": "22222-222", "descricao": "Teste"
        }
        response = self.client.post(reverse('sala-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verifica se o dono foi atribuído automaticamente
        self.assertEqual(Sala.objects.last().dono, self.dono)

    def test_criar_sala_nao_autenticado(self):
        """Anônimo não pode criar sala"""
        self.client.credentials() # Remove token
        response = self.client.post(reverse('sala-list'), {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ReservaTests(SetupTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse('reserva-list')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_solicitante)
        
        # Datas para teste (amanhã)
        self.inicio = timezone.now() + timedelta(days=1)
        self.fim = self.inicio + timedelta(hours=2)

    def test_criar_reserva_sucesso(self):
        """Deve criar reserva e status inicial deve ser PENDENTE_APROVACAO"""
        data = {
            "sala": self.sala.id,
            "data_inicio": self.inicio,
            "data_fim": self.fim,
            "forma_pagamento": "PIX"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reserva = Reserva.objects.get(id=response.data['id'])
        self.assertEqual(reserva.status, 'PENDENTE_APROVACAO')
        self.assertEqual(reserva.solicitante, self.solicitante)
        # Verifica cálculo automático do valor (2 horas * 50.00)
        self.assertEqual(float(reserva.valor_total), 100.00)

    def test_impedir_reserva_datas_invalidas(self):
        """Data fim não pode ser antes do início"""
        data = {
            "sala": self.sala.id,
            "data_inicio": self.fim, # Invertido
            "data_fim": self.inicio,
            "forma_pagamento": "PIX"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_impedir_conflito_horario(self):
        """Não deve permitir reserva no mesmo horário de outra APROVADA ou PENDENTE"""
        # Cria primeira reserva
        Reserva.objects.create(
            sala=self.sala, solicitante=self.solicitante,
            data_inicio=self.inicio, data_fim=self.fim,
            status='APROVADA', forma_pagamento='PIX'
        )
        
        # Tenta criar outra sobreposta
        data = {
            "sala": self.sala.id,
            "data_inicio": self.inicio + timedelta(minutes=30), # Começa no meio da outra
            "data_fim": self.fim + timedelta(minutes=30),
            "forma_pagamento": "BOLETO"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Sala indisponível", str(response.data))

class AcoesReservaTests(SetupTestCase):
    def setUp(self):
        super().setUp()
        self.reserva = Reserva.objects.create(
            sala=self.sala, solicitante=self.solicitante,
            data_inicio=timezone.now() + timedelta(days=2),
            data_fim=timezone.now() + timedelta(days=2, hours=1),
            status='PENDENTE_APROVACAO', forma_pagamento='PIX'
        )

    def test_dono_aprovar_reserva(self):
        """O dono da sala deve conseguir aprovar"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_dono)
        url = reverse('reserva-responder', kwargs={'pk': self.reserva.id})
        
        response = self.client.post(url, {'acao': 'APROVAR'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, 'APROVADA')

    def test_solicitante_nao_pode_aprovar(self):
        """O solicitante NÃO pode aprovar a própria reserva"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_solicitante)
        url = reverse('reserva-responder', kwargs={'pk': self.reserva.id})
        
        response = self.client.post(url, {'acao': 'APROVAR'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_solicitante_cancelar_reserva(self):
        """Solicitante pode cancelar sua reserva"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_solicitante)
        url = reverse('reserva-cancelar', kwargs={'pk': self.reserva.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.status, 'CANCELADA')

class SOAPServiceTests(SetupTestCase):
    def test_logica_relatorio_soap(self):
        """Testa diretamente a lógica do serviço SOAP sem precisar de XML"""
        # Criar algumas reservas
        agora = timezone.now()
        Reserva.objects.create(sala=self.sala, solicitante=self.solicitante, data_inicio=agora, data_fim=agora+timedelta(hours=1), status='CONCLUIDA', forma_pagamento='PIX', valor_total=50)
        Reserva.objects.create(sala=self.sala, solicitante=self.solicitante, data_inicio=agora-timedelta(days=1), data_fim=agora-timedelta(days=1, hours=2), status='CANCELADA', forma_pagamento='PIX', valor_total=100)

        # Chamar o método do serviço
        ctx = None # Contexto fake
        resultado = RelatorioSoapService.gerar_relatorio_reservas(ctx, self.sala.id, 10, 'RECENTES')
        
        self.assertEqual(len(resultado), 2)
        # Verifica se o primeiro da lista é o mais recente (ordenação RECENTES)
        self.assertEqual(resultado[0].status, 'CONCLUIDA') 
        
        # Verifica campos customizados
        self.assertEqual(resultado[0].duracao_horas, "1.0h")
        self.assertEqual(resultado[0].solicitante_cpf, "222.222.222-22")
"""
Testes automatizados de API para o Sistema de Reservas de Espaço:

- CDU-001: Realizar cadastro
- CDU-002: Realizar login
- CDU-003: Cadastrar sala
- CDU-004: Listar e buscar salas
- CDU-005: Solicitar reserva
- CDU-006: Responder reserva (aprovar/rejeitar)
- CDU-007: Cancelar reserva
- CDU-008: Gerenciar sala (editar/excluir)

Endpoints exercitados:
- POST   /api/auth/register/
- POST   /api/auth/login/
- POST   /api/auth/refresh/
- GET    /api/salas/
- POST   /api/salas/
- GET    /api/salas/{id}/
- PATCH  /api/salas/{id}/
- DELETE /api/salas/{id}/
- POST   /api/reservas/
- GET    /api/reservas/{id}/
- POST   /api/reservas/{id}/responder/
- POST   /api/reservas/{id}/cancelar/
"""

from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from api.models import Reserva, Sala

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers de construção de cenário
# ---------------------------------------------------------------------------

def make_user(username="usuario_teste", email="teste@example.com",
              cpf="000.000.000-00", password="Senha@Valida123"):
    return User.objects.create_user(
        username=username,
        email=email,
        password=password,
        cpf=cpf,
        celular="84900000000",
    )


def make_sala(dono, nome="Sala de Teste", cidade="Natal",
              estado="RN", disponivel=True, preco_por_hora="100.00"):
    return Sala.objects.create(
        dono=dono,
        nome=nome,
        descricao="Descrição padrão para testes.",
        capacidade=10,
        rua="Rua Teste",
        numero="1",
        bairro="Centro",
        cidade=cidade,
        estado=estado,
        cep="59000-000",
        preco_por_hora=preco_por_hora,
        disponivel=disponivel,
    )


def make_reserva(solicitante, sala, status_reserva="PENDENTE_APROVACAO",
                 data_inicio=None, data_fim=None):
    if data_inicio is None:
        data_inicio = datetime(2030, 8, 1, 10, 0, 0, tzinfo=timezone.utc)
    if data_fim is None:
        data_fim = datetime(2030, 8, 1, 12, 0, 0, tzinfo=timezone.utc)
    reserva = Reserva.objects.create(
        solicitante=solicitante,
        sala=sala,
        data_inicio=data_inicio,
        data_fim=data_fim,
        forma_pagamento="PIX",
        status=status_reserva,
    )
    reserva.calcular_valor_total()
    reserva.save()
    return reserva


# ---------------------------------------------------------------------------
# CDU-001: Realizar cadastro
# ---------------------------------------------------------------------------

class CDU001FluxoPrincipalTests(TestCase):
    """FP - Cadastro com dados válidos."""

    def setUp(self):
        self.client = APIClient()

    def test_fp_cadastro_retorna_201(self):
        response = self.client.post("/api/auth/register/", {
            "username": "novo_usuario",
            "email": "novo@example.com",
            "password": "Senha@Valida123",
            "cpf": "111.222.333-44",
            "celular": "84911110000",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fp_senha_nao_retornada_na_resposta(self):
        response = self.client.post("/api/auth/register/", {
            "username": "user_seguro",
            "email": "seguro@example.com",
            "password": "SenhaSecreta@99",
            "cpf": "222.333.444-55",
            "celular": "84922220000",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
        self.assertNotIn("SenhaSecreta@99", str(response.content))

    def test_fp_usuario_criado_no_banco(self):
        self.client.post("/api/auth/register/", {
            "username": "user_banco",
            "email": "banco@example.com",
            "password": "Senha@Valida123",
            "cpf": "333.444.555-66",
            "celular": "84933330000",
        }, format="json")
        self.assertTrue(User.objects.filter(username="user_banco").exists())


class CDU001FluxosAlternativosTests(TestCase):
    """FA - Dados duplicados ou incompletos."""

    def setUp(self):
        self.client = APIClient()
        make_user(username="existente", email="existente@example.com", cpf="999.888.777-66")

    def test_fa_username_duplicado_retorna_400(self):
        response = self.client.post("/api/auth/register/", {
            "username": "existente",
            "email": "outro@example.com",
            "password": "Senha@Valida123",
            "cpf": "444.555.666-77",
            "celular": "84944440000",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_fa_email_duplicado_retorna_400(self):
        response = self.client.post("/api/auth/register/", {
            "username": "outro_usuario",
            "email": "existente@example.com",
            "password": "Senha@Valida123",
            "cpf": "555.666.777-88",
            "celular": "84955550000",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_fa_cpf_ausente_retorna_400(self):
        response = self.client.post("/api/auth/register/", {
            "username": "sem_cpf",
            "email": "semcpf@example.com",
            "password": "Senha@Valida123",
            "celular": "84966660000",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cpf", response.data)


# ---------------------------------------------------------------------------
# CDU-002: Realizar login
# ---------------------------------------------------------------------------

class CDU002FluxoPrincipalTests(TestCase):
    """FP - Login com credenciais válidas."""

    def setUp(self):
        self.client = APIClient()
        make_user(username="login_user", email="login@example.com", cpf="100.100.100-10")

    def test_fp_login_retorna_200_com_tokens(self):
        response = self.client.post("/api/auth/login/", {
            "username": "login_user",
            "password": "Senha@Valida123",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_fp_senha_nao_aparece_na_resposta(self):
        response = self.client.post("/api/auth/login/", {
            "username": "login_user",
            "password": "Senha@Valida123",
        }, format="json")
        self.assertNotIn("Senha@Valida123", str(response.content))

    def test_fp_refresh_retorna_novo_access_token(self):
        login = self.client.post("/api/auth/login/", {
            "username": "login_user",
            "password": "Senha@Valida123",
        }, format="json")
        response = self.client.post("/api/auth/refresh/", {
            "refresh": login.data["refresh"],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class CDU002FluxosAlternativosTests(TestCase):
    """FA - Credenciais inválidas ou usuário inexistente."""

    def setUp(self):
        self.client = APIClient()
        make_user(username="login_user2", email="login2@example.com", cpf="200.200.200-20")

    def test_fa_senha_incorreta_retorna_401(self):
        response = self.client.post("/api/auth/login/", {
            "username": "login_user2",
            "password": "senhaErrada",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_fa_usuario_inexistente_retorna_401(self):
        response = self.client.post("/api/auth/login/", {
            "username": "nao_existe_xyz",
            "password": "Senha@Valida123",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)


# ---------------------------------------------------------------------------
# CDU-003: Cadastrar sala
# ---------------------------------------------------------------------------

SALA_VALIDA = {
    "nome": "Sala de Reunião A",
    "descricao": "Sala com projetor e ar-condicionado.",
    "capacidade": 10,
    "rua": "Rua das Flores",
    "numero": "123",
    "bairro": "Centro",
    "cidade": "Natal",
    "estado": "RN",
    "cep": "59000-000",
    "preco_por_hora": "50.00",
    "disponivel": True,
}


class CDU003FluxoPrincipalTests(TestCase):
    """FP - Cadastro de sala com dados válidos por usuário autenticado."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_sala", email="dono@example.com", cpf="300.300.300-30")
        self.client.force_authenticate(user=self.dono)

    def test_fp_criar_sala_retorna_201(self):
        response = self.client.post("/api/salas/", SALA_VALIDA, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fp_dono_atribuido_automaticamente(self):
        response = self.client.post("/api/salas/", SALA_VALIDA, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        sala = Sala.objects.get(id=response.data["id"])
        self.assertEqual(sala.dono, self.dono)

    def test_fp_sala_criada_como_disponivel(self):
        response = self.client.post("/api/salas/", SALA_VALIDA, format="json")
        self.assertTrue(response.data["disponivel"])

    def test_fp_sala_visivel_na_listagem(self):
        self.client.post("/api/salas/", SALA_VALIDA, format="json")
        response = self.client.get("/api/salas/")
        resultados = response.data if isinstance(response.data, list) else response.data.get("results", [])
        self.assertGreaterEqual(len(resultados), 1)


class CDU003FluxosAlternativosTests(TestCase):
    """FA - Cadastro sem autenticação ou com dados inválidos."""

    def setUp(self):
        self.client = APIClient()

    def test_fa_sem_autenticacao_retorna_401(self):
        response = self.client.post("/api/salas/", SALA_VALIDA, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fa_nome_ausente_retorna_400(self):
        dono = make_user(username="dono_sem_nome", email="dsn@example.com", cpf="301.301.301-31")
        self.client.force_authenticate(user=dono)
        dados = {k: v for k, v in SALA_VALIDA.items() if k != "nome"}
        response = self.client.post("/api/salas/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nome", response.data)

    def test_fa_preco_invalido_retorna_400(self):
        dono = make_user(username="dono_preco", email="dp@example.com", cpf="302.302.302-32")
        self.client.force_authenticate(user=dono)
        dados = {**SALA_VALIDA, "preco_por_hora": "preco_invalido"}
        response = self.client.post("/api/salas/", dados, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# CDU-004: Listar e buscar salas
# ---------------------------------------------------------------------------

class CDU004FluxoPrincipalTests(TestCase):
    """FP - Listagem pública de salas disponíveis."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_lista", email="dlista@example.com", cpf="400.400.400-40")
        make_sala(self.dono, nome="Sala Natal Disp", cidade="Natal", disponivel=True)

    def test_fp_listagem_publica_retorna_200(self):
        response = self.client.get("/api/salas/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fp_listagem_contem_sala_cadastrada(self):
        response = self.client.get("/api/salas/")
        resultados = response.data if isinstance(response.data, list) else response.data.get("results", [])
        self.assertGreaterEqual(len(resultados), 1)


class CDU004FiltrosTests(TestCase):
    """FA - Filtros por cidade, disponibilidade e dono."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_filtros", email="dfilt@example.com", cpf="401.401.401-41")
        make_sala(self.dono, nome="Sala Natal", cidade="Natal", disponivel=True)
        make_sala(self.dono, nome="Sala Recife", cidade="Recife", disponivel=False)

    def test_fa_filtro_por_cidade_retorna_apenas_sala_da_cidade(self):
        response = self.client.get("/api/salas/?cidade=Natal")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resultados = response.data if isinstance(response.data, list) else response.data.get("results", [])
        for sala in resultados:
            self.assertEqual(sala["cidade"], "Natal")

    def test_fa_filtro_disponivel_true_omite_salas_indisponiveis(self):
        response = self.client.get("/api/salas/?disponivel=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resultados = response.data if isinstance(response.data, list) else response.data.get("results", [])
        for sala in resultados:
            self.assertTrue(sala["disponivel"])

    def test_fa_minhas_salas_retorna_somente_salas_do_usuario(self):
        self.client.force_authenticate(user=self.dono)
        response = self.client.get("/api/salas/?minhas=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        resultados = response.data if isinstance(response.data, list) else response.data.get("results", [])
        self.assertGreaterEqual(len(resultados), 1)

    def test_fa_id_inexistente_retorna_404(self):
        response = self.client.get("/api/salas/999999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# CDU-005: Solicitar reserva
# ---------------------------------------------------------------------------

class CDU005FluxoPrincipalTests(TestCase):
    """FP - Solicitação de reserva com dados válidos."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_res", email="dres@example.com", cpf="500.500.500-50")
        self.solicitante = make_user(username="solic_res", email="sres@example.com", cpf="501.501.501-51")
        self.sala = make_sala(self.dono, preco_por_hora="100.00")
        self.client.force_authenticate(user=self.solicitante)

    def test_fp_reserva_criada_com_status_pendente(self):
        response = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-08-01T10:00:00Z",
            "data_fim": "2030-08-01T12:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "PENDENTE_APROVACAO")

    def test_fp_valor_total_calculado_automaticamente(self):
        """2 horas × R$100/h = R$200."""
        response = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-09-01T10:00:00Z",
            "data_fim": "2030-09-01T12:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data["valor_total"]), 200.00)

    def test_fp_solicitante_e_o_usuario_autenticado(self):
        response = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-10-01T08:00:00Z",
            "data_fim": "2030-10-01T09:00:00Z",
            "forma_pagamento": "DINHEIRO",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["solicitante"], self.solicitante.id)


class CDU005ValorLimiteTests(TestCase):
    """Análise de valor limite: datas e conflitos."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_res2", email="dres2@example.com", cpf="502.502.502-52")
        self.solicitante = make_user(username="solic_res2", email="sres2@example.com", cpf="503.503.503-53")
        self.sala = make_sala(self.dono, preco_por_hora="100.00")
        self.client.force_authenticate(user=self.solicitante)

    def test_fa_data_inicio_igual_ao_fim_retorna_400(self):
        response = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-08-01T10:00:00Z",
            "data_fim": "2030-08-01T10:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fa_data_inicio_posterior_ao_fim_retorna_400(self):
        response = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-08-01T14:00:00Z",
            "data_fim": "2030-08-01T12:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fa_conflito_de_horario_retorna_400(self):
        self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-11-01T10:00:00Z",
            "data_fim": "2030-11-01T12:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        response = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-11-01T11:00:00Z",
            "data_fim": "2030-11-01T13:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fa_reserva_cancelada_libera_horario(self):
        """Reservas CANCELADAS não bloqueiam o mesmo horário para novas reservas."""
        r1 = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2031-01-01T10:00:00Z",
            "data_fim": "2031-01-01T12:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.client.post(f"/api/reservas/{r1.data['id']}/cancelar/")
        r2 = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2031-01-01T10:00:00Z",
            "data_fim": "2031-01-01T12:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)

    def test_fa_sem_autenticacao_retorna_401(self):
        self.client.force_authenticate(user=None)
        response = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-12-01T10:00:00Z",
            "data_fim": "2030-12-01T12:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# CDU-006: Responder reserva (aprovar / rejeitar)
# ---------------------------------------------------------------------------

class CDU006FluxoPrincipalTests(TestCase):
    """FP - Dono aprova ou rejeita reserva pendente."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_resp", email="dresp@example.com", cpf="600.600.600-60")
        self.solicitante = make_user(username="solic_resp", email="sresp@example.com", cpf="601.601.601-61")
        self.sala = make_sala(self.dono)

    def test_fp_dono_aprova_reserva_e_status_atualiza(self):
        reserva = make_reserva(self.solicitante, self.sala)
        self.client.force_authenticate(user=self.dono)
        response = self.client.post(
            f"/api/reservas/{reserva.id}/responder/", {"acao": "APROVAR"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "APROVADA")

    def test_fp_dono_rejeita_reserva_e_status_atualiza(self):
        reserva = make_reserva(self.solicitante, self.sala)
        self.client.force_authenticate(user=self.dono)
        response = self.client.post(
            f"/api/reservas/{reserva.id}/responder/", {"acao": "REJEITAR"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "REJEITADA")

    def test_fp_reserva_rejeitada_libera_horario_para_nova_reserva(self):
        """Após rejeição, o mesmo horário deve estar disponível para nova reserva."""
        reserva = make_reserva(self.solicitante, self.sala)
        self.client.force_authenticate(user=self.dono)
        self.client.post(
            f"/api/reservas/{reserva.id}/responder/", {"acao": "REJEITAR"}, format="json"
        )
        self.client.force_authenticate(user=self.solicitante)
        r2 = self.client.post("/api/reservas/", {
            "sala": self.sala.id,
            "data_inicio": "2030-08-01T10:00:00Z",
            "data_fim": "2030-08-01T12:00:00Z",
            "forma_pagamento": "PIX",
        }, format="json")
        self.assertEqual(r2.status_code, status.HTTP_201_CREATED)


class CDU006ControleAcessoTests(TestCase):
    """Controle de acesso ao endpoint responder."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_resp2", email="dresp2@example.com", cpf="602.602.602-62")
        self.solicitante = make_user(username="solic_resp2", email="sresp2@example.com", cpf="603.603.603-63")
        self.sala = make_sala(self.dono)
        self.reserva = make_reserva(self.solicitante, self.sala)

    def test_fa_solicitante_nao_pode_aprovar_propria_reserva(self):
        self.client.force_authenticate(user=self.solicitante)
        response = self.client.post(
            f"/api/reservas/{self.reserva.id}/responder/", {"acao": "APROVAR"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fa_acao_invalida_retorna_400(self):
        self.client.force_authenticate(user=self.dono)
        response = self.client.post(
            f"/api/reservas/{self.reserva.id}/responder/", {"acao": "IGNORAR"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fa_sem_autenticacao_retorna_401(self):
        response = self.client.post(
            f"/api/reservas/{self.reserva.id}/responder/", {"acao": "APROVAR"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# CDU-007: Cancelar reserva
# ---------------------------------------------------------------------------

class CDU007FluxoPrincipalTests(TestCase):
    """FP - Solicitante cancela sua própria reserva."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_canc", email="dcanc@example.com", cpf="700.700.700-70")
        self.solicitante = make_user(username="solic_canc", email="scanc@example.com", cpf="701.701.701-71")
        self.sala = make_sala(self.dono)
        self.client.force_authenticate(user=self.solicitante)

    def test_fp_cancelar_reserva_pendente_atualiza_status(self):
        reserva = make_reserva(self.solicitante, self.sala)
        response = self.client.post(f"/api/reservas/{reserva.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "CANCELADA")

    def test_fp_cancelar_reserva_aprovada_atualiza_status(self):
        reserva = make_reserva(self.solicitante, self.sala, status_reserva="APROVADA")
        response = self.client.post(f"/api/reservas/{reserva.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, "CANCELADA")


class CDU007ValorLimiteTests(TestCase):
    """Valor limite: status terminais impedem cancelamento."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_canc2", email="dcanc2@example.com", cpf="702.702.702-72")
        self.solicitante = make_user(username="solic_canc2", email="scanc2@example.com", cpf="703.703.703-73")
        self.sala = make_sala(self.dono)

    def test_fa_cancelar_reserva_ja_cancelada_retorna_400(self):
        reserva = make_reserva(self.solicitante, self.sala, status_reserva="CANCELADA")
        self.client.force_authenticate(user=self.solicitante)
        response = self.client.post(f"/api/reservas/{reserva.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fa_cancelar_reserva_rejeitada_retorna_400(self):
        reserva = make_reserva(self.solicitante, self.sala, status_reserva="REJEITADA")
        self.client.force_authenticate(user=self.solicitante)
        response = self.client.post(f"/api/reservas/{reserva.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fa_cancelar_reserva_concluida_retorna_400(self):
        reserva = make_reserva(self.solicitante, self.sala, status_reserva="CONCLUIDA")
        self.client.force_authenticate(user=self.solicitante)
        response = self.client.post(f"/api/reservas/{reserva.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CDU007ControleAcessoTests(TestCase):
    """Controle de acesso: apenas o solicitante pode cancelar."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_canc3", email="dcanc3@example.com", cpf="704.704.704-74")
        self.solicitante = make_user(username="solic_canc3", email="scanc3@example.com", cpf="705.705.705-75")
        self.sala = make_sala(self.dono)
        self.reserva = make_reserva(self.solicitante, self.sala)

    def test_fa_dono_da_sala_nao_pode_cancelar(self):
        self.client.force_authenticate(user=self.dono)
        response = self.client.post(f"/api/reservas/{self.reserva.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fa_sem_autenticacao_retorna_401(self):
        response = self.client.post(f"/api/reservas/{self.reserva.id}/cancelar/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# CDU-008: Gerenciar sala (editar / excluir)
# ---------------------------------------------------------------------------

class CDU008EditarSalaTests(TestCase):
    """FP - Dono edita propriedades da sala."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_edit", email="dedit@example.com", cpf="800.800.800-80")
        self.sala = make_sala(self.dono)
        self.client.force_authenticate(user=self.dono)

    def test_fp_dono_edita_nome_via_patch(self):
        response = self.client.patch(
            f"/api/salas/{self.sala.id}/", {"nome": "Sala Editada"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nome"], "Sala Editada")

    def test_fp_dono_atualiza_preco(self):
        response = self.client.patch(
            f"/api/salas/{self.sala.id}/", {"preco_por_hora": "150.00"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["preco_por_hora"]), 150.00)

    def test_fp_dono_desativa_disponibilidade(self):
        response = self.client.patch(
            f"/api/salas/{self.sala.id}/", {"disponivel": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["disponivel"])

    def test_fp_dono_reativa_disponibilidade(self):
        self.sala.disponivel = False
        self.sala.save()
        response = self.client.patch(
            f"/api/salas/{self.sala.id}/", {"disponivel": True}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["disponivel"])


class CDU008ExcluirSalaTests(TestCase):
    """FP - Dono exclui a sala."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_del", email="ddel@example.com", cpf="801.801.801-81")
        self.sala = make_sala(self.dono)
        self.client.force_authenticate(user=self.dono)

    def test_fp_dono_exclui_sala_retorna_204(self):
        sala_id = self.sala.id
        response = self.client.delete(f"/api/salas/{sala_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_fp_sala_excluida_nao_existe_no_banco(self):
        sala_id = self.sala.id
        self.client.delete(f"/api/salas/{sala_id}/")
        self.assertFalse(Sala.objects.filter(id=sala_id).exists())

    def test_fp_sala_excluida_retorna_404_no_get(self):
        sala_id = self.sala.id
        self.client.delete(f"/api/salas/{sala_id}/")
        response = self.client.get(f"/api/salas/{sala_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CDU008ControleAcessoTests(TestCase):
    """Controle de acesso: sem autenticação não pode editar ou excluir."""

    def setUp(self):
        self.client = APIClient()
        self.dono = make_user(username="dono_ac", email="dac@example.com", cpf="802.802.802-82")
        self.sala = make_sala(self.dono)

    def test_fa_sem_autenticacao_nao_pode_editar(self):
        response = self.client.patch(
            f"/api/salas/{self.sala.id}/", {"nome": "Sem Token"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_fa_sem_autenticacao_nao_pode_excluir(self):
        response = self.client.delete(f"/api/salas/{self.sala.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

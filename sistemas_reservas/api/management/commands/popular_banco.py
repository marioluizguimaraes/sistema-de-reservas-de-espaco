from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import CustomUser, Sala, Reserva
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Popula o banco com dados realistas de usuários, salas e reservas em Natal/RN.'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌎 Populando dados mais reais em Natal/RN...')

        # LIMPEZA
        Reserva.objects.all().delete()
        Sala.objects.all().delete()
        CustomUser.objects.all().delete()
        self.stdout.write('🧹 Base limpa!')

        # SUPERUSUÁRIO
        admin = CustomUser.objects.create_superuser(
            username='mario',
            email='mario@natal.com',
            password='123',
            cpf='000.000.000-00',
            celular='84999990000'
        )
        self.stdout.write(f'👑 Superusuário criado: {admin.username}')

        # USUÁRIOS
        usuarios_data = [
            {
                'user': 'ana_silva',
                'cpf': '111.111.111-11',
                'bairro_pref': 'Ponta Negra',
                'nome': 'Ana Paula Silva'
            },
            {
                'user': 'bruno_costa',
                'cpf': '222.222.222-22',
                'bairro_pref': 'Tirol',
                'nome': 'Bruno Henrique Costa'
            },
            {
                'user': 'carla_dias',
                'cpf': '333.333.333-33',
                'bairro_pref': 'Petrópolis',
                'nome': 'Carla Beatriz Dias'
            },
            {
                'user': 'daniel_souza',
                'cpf': '444.444.444-44',
                'bairro_pref': 'Lagoa Nova',
                'nome': 'Daniel Souza Andrade'
            },
        ]

        # TIPOS DE SALA REALISTAS
        tipos_sala = [
            ("Auditório Atlântico", 120, 450.00, "Auditório equipado com projetor 4K e acústica aprimorada."),
            ("Sala de Reunião Oceano", 12, 95.00, "Sala moderna com TV 55'' e videoconferência."),
            ("Espaço Coworking Dunas", 25, 160.00, "Ambiente colaborativo ideal para freelancers e pequenas equipes."),
            ("Estúdio Criativo Potiguar", 6, 220.00, "Estúdio ideal para gravações, podcasts e fotografia."),
            ("Salão de Eventos Brisa Norte", 180, 980.00, "Salão amplo para festas, palestras e workshops."),
            ("Sala de Treinamento Horizon", 35, 130.00, "Espaço para capacitações equipado com quadro digital."),
        ]

        # RUAS REALISTAS
        ruas_por_bairro = {
            "Ponta Negra": ["Engenheiro Roberto Freire", "Rua das Conchas", "Av. Praia de Ponta Negra"],
            "Tirol": ["Av. Hermes da Fonseca", "Rua Ceará-Mirim", "Rua Alberto Maranhão"],
            "Petrópolis": ["Av. Afonso Pena", "Rua Trairi", "Av. Hermes da Fonseca"],
            "Lagoa Nova": ["Av. Capitão-Mor Gouveia", "Rua Jaguarari", "Rua São José"],
        }

        usuarios_objs = []

        # CRIAÇÃO DE USUÁRIOS + SALAS
        for i, u_data in enumerate(usuarios_data):

            user = CustomUser.objects.create_user(
                username=u_data['user'],
                email=f"{u_data['user']}@email.com",
                password='123',
                cpf=u_data['cpf'],
                celular=f"8498{random.randint(1000000,9999999)}",
                foto_url=f"https://i.pravatar.cc/150?img={i+10}"
            )
            usuarios_objs.append(user)

            # 6 salas por usuário
            for j in range(6):
                modelo = tipos_sala[j]

                rua_escolhida = random.choice(ruas_por_bairro[u_data['bairro_pref']])
                numero = random.randint(100, 3500)

                Sala.objects.create(
                    dono=user,
                    nome=f"{modelo[0]} - Unidade {j+1}",
                    descricao=f"{modelo[3]} Localizado no bairro {u_data['bairro_pref']}.",
                    capacidade=modelo[1],
                    preco_por_hora=modelo[2],
                    rua=rua_escolhida,
                    numero=str(numero),
                    bairro=u_data['bairro_pref'],
                    cidade="Natal",
                    estado="RN",
                    cep=f"59{random.randint(100,999)}-{random.randint(100,999)}",
                    disponivel=True
                )

            self.stdout.write(f"👤 Usuário {user.username} criado com 6 salas realistas em {u_data['bairro_pref']}.")

        # RESERVAS REALISTAS
        hoje = timezone.now()
        salas = list(Sala.objects.all())

        for _ in range(18):
            sala_alvo = random.choice(salas)
            usuario = random.choice([u for u in usuarios_objs if u != sala_alvo.dono])

            dias = random.randint(-15, 15)
            inicio = hoje + timedelta(days=dias, hours=random.randint(8, 19))
            fim = inicio + timedelta(hours=random.choice([1, 2, 3, 4]))

            status = random.choice(['PENDENTE_APROVACAO', 'APROVADA', 'CONCLUIDA', 'CANCELADA'])

            reserva = Reserva(
                solicitante=usuario,
                sala=sala_alvo,
                data_inicio=inicio,
                data_fim=fim,
                forma_pagamento=random.choice(['PIX', 'CARTAO', 'DINHEIRO']),
                status=status
            )

            reserva.calcular_valor_total()
            reserva.save()

        self.stdout.write(self.style.SUCCESS("✅ Base populada com dados mais reais!"))

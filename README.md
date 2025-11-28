- Tema: **Sistema de Reservas de Salas / Estúdios / Salão de Eventos**
- API REST em Django REST Framework
- Serviço SOAP integrado
- API Gateway em Node.js (com HATEOAS)
- Modelagem dos dados
- Estrutura dos projetos
- Requisitos funcionais e não funcionais
- Explicação da arquitetura
- Fluxos principais
- Autenticação (Cadastro, Login e Logout)


---

# 📘 **DOCUMENTAÇÃO DO SISTEMA DE RESERVA DE SALAS / ESTÚDIOS / SALÃO DE EVENTOS**


# 1. 🎯 **Descrição Geral do Sistema**

O Sistema de Reservas de Salas é uma plataforma que permite que usuários realizem:

* Cadastro e autenticação
* Consulta de salas disponíveis
* Solicitação de reservas
* Visualização das suas reservas
* Geração de relatórios via SOAP
* Utilização do sistema através de um API Gateway em Node.js
* Consumo padronizado via front-end web

O sistema utiliza uma **arquitetura híbrida**, unindo:

* **REST (Django REST Framework) para operações CRUD**
* **SOAP (serviço adicional no backend) para consultas avançadas**
* **Gateway Node.js** para unificação, autenticação centralizada e HATEOAS

# 2. 🏗 **Arquitetura Geral**

```
┌─────────────────────┐        ┌─────────────────────────┐
│    Front-End Web    │ <----> │ API Gateway (Node.js)   │
└─────────────────────┘        └───────────┬─────────────┘
                                           │
                               ┌───────────┴───────────┐
                               │                       │
               ┌───────────────▼────────────┐   ┌──────▼──────────────┐
               │ API REST (Django REST)     │   │ Serviço SOAP        │
               │ CRUD + Auth + Reservas     │   │ Relatórios          │
               └────────────────────────────┘   └─────────────────────┘
```

Funções do Gateway:

* Gerenciar autenticação unificada
* Encaminhar chamadas ao REST
* Intermediar chamadas SOAP
* Injetar **HATEOAS** em todas as respostas
* Realizar validação de tokens

# 4. 🧩 **Modelagem de Dados**

## 4.1 **Modelo: User (accounts_user)**

**Relacionamentos**: nenhum além do padrão

Atributos:

* id (PK)
* nome
* email (único)
* senha (hash)
* criado_em
* atualizado_em

## 4.2 **Modelo: Sala (rooms_room)**

Atributos:

* id (PK)
* nome
* capacidade
* descrição
* localização
* disponível (bool)
* criado_em
* atualizado_em

## 4.3 **Modelo: Reserva (reservations_reservation)**

**Relacionamentos**:

* user  → FK para `User`
* room  → FK para `Sala`

Atributos:

* id (PK)
* user_id (FK)
* room_id (FK)
* data_inicio (datetime)
* data_fim (datetime)
* status (pendente, confirmada, cancelada)
* criada_em
* atualizada_em

# 5. 🔐 **Autenticação e Segurança**

A API REST implementa **JWT**.
Fluxo:

1. **Cadastro**
2. **Login → retorna token JWT**
3. **Todas as operações (exceto login/cadastro) exigem token**
4. **Logout** é feito invalidando o token (no gateway ou blacklist opcional)

O **Gateway Node** valida o token antes de redirecionar qualquer requisição.


# 6. 🧭 **Endpoints da API (REST)**

## 6.1 **Endpoints de autenticação**

| Método | Endpoint              | Descrição           |
| ------ | --------------------- | ------------------- |
| POST   | `/api/auth/register/` | Cadastro            |
| POST   | `/api/auth/login/`    | Login (retorna JWT) |
| POST   | `/api/auth/logout/`   | Invalida token      |

## 6.2 **Endpoints de salas**

| Método | Endpoint           | Descrição     |
| ------ | ------------------ | ------------- |
| GET    | `/api/rooms/`      | Listar salas  |
| POST   | `/api/rooms/`      | Criar sala    |
| GET    | `/api/rooms/{id}/` | Detalhar sala |
| PUT    | `/api/rooms/{id}/` | Atualizar     |
| DELETE | `/api/rooms/{id}/` | Remover       |

## 6.3 **Endpoints de reservas**

| Método | Endpoint                  | Descrição                  |
| ------ | ------------------------- | -------------------------- |
| GET    | `/api/reservations/`      | Listar reservas do usuário |
| POST   | `/api/reservations/`      | Criar reserva              |
| GET    | `/api/reservations/{id}/` | Detalhar                   |
| PUT    | `/api/reservations/{id}/` | Atualizar                  |
| DELETE | `/api/reservations/{id}/` | Cancelar                   |

# 7. 🧼 **Endpoints SOAP**

O serviço SOAP oferece funções não CRUD, orientadas a lógica de negócio avançada.

## 7.1 **Funções SOAP expostas**

### `getNextAvailableRoom(dateTime)`

Retorna:

* id da sala
* nome
* horário disponível mais próximo

### `getDailySchedule(date)`

Retorna:

* lista de reservas do dia
* horários ocupados x livres

### `countReservationsForRoom(roomId)`

Retorna:

* quantidade total de reservas daquela sala

# 8. 🚪 **API Gateway (Node.js)**

O Gateway atua como **porta única do sistema**, expondo endpoints “amigáveis”:

## 8.1 **Gateway - Autenticação**

| Método | Endpoint                 | Encaminha |
| ------ | ------------------------ | --------- |
| POST   | `/gateway/auth/login`    | REST      |
| POST   | `/gateway/auth/register` | REST      |
| POST   | `/gateway/auth/logout`   | REST      |

## 8.2 **Gateway - Salas**

| Método | Endpoint         | Encaminha |
| ------ | ---------------- | --------- |
| GET    | `/gateway/rooms` | REST      |
| POST   | `/gateway/rooms` | REST      |
| …      | etc              |           |

Com **HATEOAS**:

```
{
  "rooms": [...],
  "links": [
    {"rel": "self", "href": "/gateway/rooms"},
    {"rel": "reserve", "href": "/gateway/reservations"}
  ]
}
```

## 8.3 **Gateway - Reservas**

| Método | Endpoint                | Encaminha |
| ------ | ----------------------- | --------- |
| GET    | `/gateway/reservations` | REST      |
| POST   | `/gateway/reservations` | REST      |


## 8.4 **Gateway - SOAP**

| Método | Endpoint                             | Descrição  |
| ------ | ------------------------------------ | ---------- |
| GET    | `/gateway/soap/next-room?dateTime=`  | Chama SOAP |
| GET    | `/gateway/soap/daily-schedule?date=` | Chama SOAP |
| GET    | `/gateway/soap/count?roomId=`        | Chama SOAP |


# 9. 📋 **Requisitos Funcionais**

1. RF001 — O usuário deve poder se cadastrar no sistema.
2. RF002 — O usuário deve poder realizar login e receber um token JWT.
3. RF003 — O usuário deve poder listar salas disponíveis.
4. RF004 — O usuário deve poder criar reservas.
5. RF005 — O usuário deve poder visualizar suas reservas.
6. RF006 — O usuário deve poder editar ou cancelar uma reserva.
7. RF007 — O sistema deve impedir reservas sobrepostas.
8. RF008 — O usuário deve poder solicitar relatório das salas via SOAP.
9. RF009 — O gateway deve unificar todas as requisições.
10. RF010 — As respostas devem incluir HATEOAS no Gateway.
11. RF011 — O usuário deve usar o front-end para consumir o Gateway.

# 10. 🧱 **Requisitos Não Funcionais**

1. RNF001 — A API REST deve seguir padrões RESTful.
2. RNF002 — O sistema deve utilizar JWT para autenticação.
3. RNF003 — A comunicação SOAP deve ser baseada em WSDL válido.
4. RNF004 — O sistema deve ser modular, com camadas bem definidas.
5. RNF005 — O Gateway deve lidar com falhas do REST e do SOAP.
6. RNF006 — O sistema deve ser responsivo e simples para o usuário final.
7. RNF007 — O banco de dados deve garantir integridade referencial.
8. RNF008 — O WSDL deve ser documentado e apresentado.
9. RNF009 — Todas as endpoints devem ser testáveis via Postman/Swagger.
10. RNF010 — O código deve ser hospedado no GitHub.

# 11. 🔄 **Fluxo Geral do Usuário**

1. Usuário acessa o front-end
2. Realiza **cadastro** → Gateway → REST
3. Faz **login** → Gateway → REST
4. Front guarda o token
5. Lista salas via Gateway
6. Escolhe uma sala e um horário
7. Cria reserva via Gateway → REST
8. Caso queira relatório, front chama:
   → Gateway → SOAP → Gateway → Front


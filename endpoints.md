# 📘 Documentação Técnica - Sistema Híbrido de Reservas (REST & SOAP)

## 1\. 🏗️ Arquitetura e Estrutura do Projeto

O sistema utiliza uma arquitetura **MVT (Model-View-Template)** adaptada para **API REST**, onde os *Templates* são substituídos por *Serializers*. O projeto é modularizado para garantir a separação de responsabilidades.

### Estrutura de Diretórios

```text
sistemas_reservas/
└── api/
    ├── models/          # Camada de Dados (ORM)
    │   ├── user.py      # Extensão do Usuário (CustomUser)
    │   ├── sala.py      # Entidade Sala
    │   └── reserva.py   # Entidade Reserva
    ├── serializers/     # Camada de Transformação (Data <-> JSON)
    ├── views/           # Camada de Controle (Lógica HTTP)
    │   ├── auth_views.py
    │   ├── sala_viewset.py
    │   └── reserva_viewset.py
    ├── services/        # Camada de Regra de Negócio Pura
    │   └── reserva_service.py # Lógica de conflito de horários
    ├── soap_service.py  # Servidor SOAP (Spyne)
    ├── urls.py          # Roteador de URLs
    └── tests.py         # Testes Automatizados
```

-----

## 2\. 🗂️ Relacionamentos do Banco de Dados

O sistema utiliza PostgreSQL e implementa os seguintes relacionamentos relacionais:

1.  **Usuário (CustomUser) ↔ Sala (1:N):**

      * Um usuário pode ser "Dono" de várias salas.
      * Uma sala pertence a um único dono.
      * *Implementação:* `ForeignKey` em `Sala` apontando para `settings.AUTH_USER_MODEL`.

2.  **Usuário (CustomUser) ↔ Reserva (1:N):**

      * Um usuário ("Solicitante") pode fazer várias reservas.
      * *Implementação:* `ForeignKey` em `Reserva` apontando para `solicitante`.

3.  **Sala ↔ Reserva (1:N):**

      * Uma sala pode ter várias reservas ao longo do tempo.
      * *Implementação:* `ForeignKey` em `Reserva` apontando para `sala`.

-----

## 3\. 🌐 Documentação dos Endpoints REST

Abaixo estão detalhados os endpoints gerados pelo Swagger. Para todas as requisições (exceto Login/Registro), é necessário enviar o Header:
`Authorization: Bearer <SEU_ACCESS_TOKEN>`

### 🔐 Autenticação (3 Endpoints)

#### 1\. Registrar Usuário

  * **Endpoint:** `POST /api/auth/register/`
  * **Descrição:** Cria um novo usuário com dados estendidos (CPF, Celular).
  * **cURL:**
    ```bash
    curl -X POST 'http://127.0.0.1:8000/api/auth/register/' \
    -H 'Content-Type: application/json' \
    -d '{
        "username": "joao", "password": "123", "email": "joao@teste.com",
        "cpf": "111.222.333-44", "celular": "11999999999"
    }'
    ```

#### 2\. Login (Obter Token)

  * **Endpoint:** `POST /api/auth/login/`
  * **Descrição:** Autentica e retorna tokens JWT (access e refresh).
  * **cURL:**
    ```bash
    curl -X POST 'http://127.0.0.1:8000/api/auth/login/' \
    -H 'Content-Type: application/json' \
    -d '{ "username": "joao", "password": "123" }'
    ```

#### 3\. Refresh Token

  * **Endpoint:** `POST /api/auth/refresh/`
  * **Descrição:** Gera um novo token de acesso usando o token de refresh (para não precisar logar novamente).

-----

### 🏢 Salas (CRUD - 5 Endpoints Principais)

#### 4\. Listar Salas

  * **Endpoint:** `GET /api/salas/`
  * **Filtros:** `?minhas=true`, `?dono={id}`, `?cidade={nome}`.
  * **Descrição:** Retorna lista de salas.
  * **cURL:**
    ```bash
    curl -X GET 'http://127.0.0.1:8000/api/salas/' -H 'Authorization: Bearer <TOKEN>'
    ```

#### 5\. Criar Sala

  * **Endpoint:** `POST /api/salas/`
  * **Descrição:** O usuário logado é automaticamente associado como dono.
  * **cURL:**
    ```bash
    curl -X POST 'http://127.0.0.1:8000/api/salas/' \
    -H 'Authorization: Bearer <TOKEN>' \
    -H 'Content-Type: application/json' \
    -d '{
        "nome": "Sala Vip", "capacidade": 10, "preco_por_hora": "50.00",
        "rua": "Rua X", "numero": "10", "bairro": "Centro",
        "cidade": "SP", "estado": "SP", "cep": "00000-000", "descricao": "Sala Top"
    }'
    ```

#### 6\. Detalhar Sala

  * **Endpoint:** `GET /api/salas/{id}/`
  * **Descrição:** Retorna dados de uma única sala.

#### 7\. Atualizar Sala

  * **Endpoint:** `PUT /api/salas/{id}/` (Completo) ou `PATCH /api/salas/{id}/` (Parcial)
  * **Descrição:** Atualiza dados da sala. Apenas o dono (ou admin) tem permissão.

#### 8\. Deletar Sala

  * **Endpoint:** `DELETE /api/salas/{id}/`
  * **Descrição:** Remove a sala do sistema.

-----

### 📅 Reservas (CRUD + Ações - 8 Endpoints)

#### 9\. Listar Reservas

  * **Endpoint:** `GET /api/reservas/`
  * **Regra de Segurança:** O usuário só vê reservas que ele fez ou reservas feitas nas salas dele.

#### 10\. Criar Reserva

  * **Endpoint:** `POST /api/reservas/`
  * **Descrição:** Solicita uma reserva. O status inicia como `PENDENTE_APROVACAO`. O sistema valida conflito de horário automaticamente.
  * **cURL:**
    ```bash
    curl -X POST 'http://127.0.0.1:8000/api/reservas/' \
    -H 'Authorization: Bearer <TOKEN>' \
    -H 'Content-Type: application/json' \
    -d '{
        "sala": 1,
        "data_inicio": "2025-12-01T14:00:00Z",
        "data_fim": "2025-12-01T16:00:00Z",
        "forma_pagamento": "PIX"
    }'
    ```

#### 11\. Detalhar Reserva

  * **Endpoint:** `GET /api/reservas/{id}/`

#### 12\. Atualizar Reserva

  * **Endpoint:** `PUT` ou `PATCH /api/reservas/{id}/`
  * **Descrição:** Permite editar a reserva (ex: mudar horário). A validação de conflito roda novamente.

#### 13\. Deletar Reserva

  * **Endpoint:** `DELETE /api/reservas/{id}/`

#### 14\. Responder Reserva (Ação Customizada)

  * **Endpoint:** `POST /api/reservas/{id}/responder/`
  * **Descrição:** **Apenas o Dono da Sala** pode usar.
  * **Body:** `{"acao": "APROVAR"}` ou `{"acao": "REJEITAR"}`.
  * **cURL:**
    ```bash
    curl -X POST 'http://127.0.0.1:8000/api/reservas/1/responder/' \
    -H 'Authorization: Bearer <TOKEN_DONO>' \
    -H 'Content-Type: application/json' \
    -d '{ "acao": "APROVAR" }'
    ```

#### 15\. Cancelar Reserva (Ação Customizada)

  * **Endpoint:** `POST /api/reservas/{id}/cancelar/`
  * **Descrição:** **Apenas o Solicitante** pode usar. Cancela a reserva se ela não estiver concluída/rejeitada.

-----

### 🧼 Serviço SOAP (1 Endpoint Complexo)

O SOAP é utilizado para relatórios pesados, retornando XML.

#### 16\. Endpoint SOAP

  * **Endpoint:** `POST /api/soap/`
  * **WSDL (Definição):** `GET /api/soap/?wsdl`
  * **Funcionalidade:** Gera relatório detalhado contendo dados cruzados (Sala + Reserva + Dados Sensíveis do Usuário).
  * **cURL de Exemplo:**
    ```bash
    curl -X POST 'http://127.0.0.1:8000/api/soap/' \
    -H 'Content-Type: text/xml' \
    -d '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tns="sistemas.reservas.soap">
       <soapenv:Header/>
       <soapenv:Body>
          <tns:gerar_relatorio_reservas>
             <tns:sala_id>1</tns:sala_id>
             <tns:limite>10</tns:limite>
             <tns:ordenacao>MAIOR_DURACAO</tns:ordenacao>
          </tns:gerar_relatorio_reservas>
       </soapenv:Body>
    </soapenv:Envelope>'
    ```
  * **Resposta (XML):** Retorna array de `SoapReservaRelatorio` com CPF, Celular, Valor Total e Duração em horas.

-----

## 4\. 🛠️ Solução de Compatibilidade (Python 3.13)

Durante o desenvolvimento, identificou-se uma incompatibilidade crítica entre a biblioteca **Spyne (2.14.0)** e o **Python 3.13**.

### O Problema

O Python 3.13 removeu módulos legados que o Spyne tentava importar internamente (`spyne.util.six.moves`). Isso causava `ModuleNotFoundError`.

### A Solução (Monkey Patch no `manage.py`)

Para não violar a integridade da biblioteca editando seus arquivos fonte, foi aplicado um "patch" no ponto de entrada da aplicação (`manage.py`).

```python
# Em manage.py
try:
    import collections.abc
    import sys
    # Injeta o módulo novo do Python 3 no caminho antigo que o Spyne procura
    sys.modules["spyne.util.six.moves.collections_abc"] = collections.abc
except ImportError:
    pass
```

Isso "engana" o Spyne, fazendo-o acreditar que o módulo antigo existe, quando na verdade ele está usando o módulo nativo moderno do Python. Isso garante que o servidor SOAP funcione perfeitamente.

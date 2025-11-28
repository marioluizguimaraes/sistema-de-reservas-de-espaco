# 📘 Documentação de Consumo da API (Gateway)

**Base URL:** `http://localhost:3000`

## 🔐 1. Autenticação

Estes endpoints são públicos e servem para criar contas ou obter o token de acesso necessário para as outras operações.

### 1.1 Registar Novo Utilizador

Cria uma conta no sistema com dados estendidos (CPF, Celular).

  * **Método:** `POST`
  * **Endpoint:** `/auth/register`
  * **Body (JSON):**
    ```json
    {
      "username": "joao.silva",
      "password": "senha_segura",
      "email": "joao@email.com",
      "cpf": "111.222.333-44",
      "celular": "11999999999"
    }
    ```
  * **Exemplo de Uso:**
    ```bash
    curl -X POST http://localhost:3000/auth/register \
    -H "Content-Type: application/json" \
    -d '{ "username": "joao", "password": "123", "email": "j@test.com", "cpf": "000.000.000-00", "celular": "000000000" }'
    ```

### 1.2 Login (Obter Token)

Autentica as credenciais e devolve o Token JWT (`access`). **Guarde este token**, ele é obrigatório no cabeçalho `Authorization` das outras requisições.

  * **Método:** `POST`
  * **Endpoint:** `/auth/login`
  * **Body (JSON):**
    ```json
    {
      "username": "joao.silva",
      "password": "senha_segura"
    }
    ```
  * **Resposta Sucesso:**
    ```json
    {
      "refresh": "eyJhbGciOiJIUz...",
      "access": "eyJhbGciOiJIUz..." 
    }
    ```

-----

## 🏢 2. Gestão de Salas

Endpoints para visualizar e gerir espaços. As respostas incluem links **HATEOAS** (`_links`) para facilitar a navegação.

### 2.1 Listar Salas

Retorna todas as salas cadastradas. Suporta filtros via URL.

  * **Método:** `GET`
  * **Endpoint:** `/salas`
  * **Parâmetros (Query Params):**
      * `cidade`: Filtrar por cidade (ex: `/salas?cidade=Lisboa`).
      * `minhas`: Se `true`, retorna apenas salas onde é o dono.
  * **Header:** `Authorization: Bearer <SEU_TOKEN>`
  * **Exemplo:**
    ```bash
    curl http://localhost:3000/salas -H "Authorization: Bearer <TOKEN>"
    ```

### 2.2 Criar Sala

Cadastra uma nova sala. O utilizador logado torna-se o dono automaticamente.

  * **Método:** `POST`
  * **Endpoint:** `/salas`
  * **Header:** `Authorization: Bearer <SEU_TOKEN>`
  * **Body (JSON):**
    ```json
    {
      "nome": "Sala de Reunião A",
      "descricao": "Projetor 4K e Ar Condicionado",
      "capacidade": 10,
      "preco_por_hora": "50.00",
      "rua": "Av. Liberdade",
      "numero": "100",
      "bairro": "Centro",
      "cidade": "Lisboa",
      "estado": "LS",
      "cep": "1000-000"
    }
    ```

### 2.3 Detalhar Sala

Vê os dados de uma sala específica.

  * **Método:** `GET`
  * **Endpoint:** `/salas/{id}`
  * **Exemplo:** `GET /salas/1`

### 2.4 Atualizar Sala (Total ou Parcial)

  * **Método:** `PUT` (Total) ou `PATCH` (Parcial)
  * **Endpoint:** `/salas/{id}`
  * **Body:** Campos que deseja alterar (ex: apenas o preço).

### 2.5 Remover Sala

  * **Método:** `DELETE`
  * **Endpoint:** `/salas/{id}`

-----

## 📅 3. Gestão de Reservas

### 3.1 Criar Reserva

Solicita o agendamento de uma sala. O sistema valida automaticamente se há conflitos de horário.

  * **Método:** `POST`
  * **Endpoint:** `/reservas`
  * **Header:** `Authorization: Bearer <SEU_TOKEN>`
  * **Body (JSON):**
    ```json
    {
      "sala": 1,
      "data_inicio": "2025-12-01T14:00:00Z",
      "data_fim": "2025-12-01T16:00:00Z",
      "forma_pagamento": "PIX"
    }
    ```

### 3.2 Listar Minhas Reservas

Mostra reservas que você fez (solicitante) ou que fizeram nas suas salas (dono).

  * **Método:** `GET`
  * **Endpoint:** `/reservas`

### 3.3 Ações Especiais na Reserva

#### A. Aprovar ou Rejeitar (Apenas Dono)

O dono da sala deve responder a pedidos com status `PENDENTE_APROVACAO`.

  * **Método:** `POST`
  * **Endpoint:** `/reservas/{id}/responder`
  * **Body (JSON):**
    ```json
    { "acao": "APROVAR" } 
    // ou 
    { "acao": "REJEITAR" }
    ```

#### B. Cancelar Reserva (Apenas Solicitante)

O cliente pode cancelar o seu pedido se ele ainda não tiver sido concluído.

  * **Método:** `POST`
  * **Endpoint:** `/reservas/{id}/cancelar`
  * **Body:** `{}` (Vazio)

-----

## 🧼 4. Relatórios Avançados (SOAP)

Este endpoint consome o serviço SOAP no backend, mas o Gateway facilita o acesso permitindo uma chamada GET simples.

### 4.1 Gerar Relatório de Sala

Retorna o XML contendo estatísticas, lista de reservas e dados sensíveis dos utilizadores (CPF/Celular) para uma sala específica.

  * **Método:** `GET`
  * **Endpoint:** `/relatorios/sala/{id}`
  * **Parâmetros (Opcionais):**
      * `limite`: Número máximo de registos (ex: `10`).
      * `ordenacao`: Critério de ordem (`RECENTES`, `ANTIGAS`, `MAIOR_DURACAO`).
  * **Exemplo de Uso:**
    ```bash
    # Pede as 5 reservas mais longas da sala 1
    curl "http://localhost:3000/relatorios/sala/1?limite=5&ordenacao=MAIOR_DURACAO"
    ```
  * **Resposta:** Retorna um documento **XML**.
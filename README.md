# 📘 Documentação Técnica de Arquitetura e Engenharia de Software

## 1\. Visão Geral da Solução

O **Sistema de Reservas** é uma aplicação backend desenvolvida em **Python 3.13** utilizando o framework **Django**. A sua principal característica arquitetural é o modelo **Híbrido**, expondo simultaneamente:

1.  Uma **API RESTful** para operações transacionais (CRUD de usuários, salas e reservas).
2.  Um **Serviço SOAP** para operações de relatórios e agregação de dados complexos.

O sistema opera no modelo de negócios "Marketplace de Espaços" (estilo Airbnb), onde usuários podem atuar tanto como locadores (donos de salas) quanto locatários (solicitantes).

-----

## 2\. Stack Tecnológica

  * **Linguagem:** Python 3.13
  * **Core Framework:** Django 5.2.8
  * **REST API:** Django REST Framework (DRF) 3.16 + SimpleJWT (Autenticação)
  * **SOAP API:** Spyne 2.14.0 (com patch de compatibilidade)
  * **Banco de Dados:** PostgreSQL (driver `psycopg2-binary`)
  * **Documentação:** Drf-yasg (Swagger/Redoc)
  * **Parser XML:** Lxml 6.0

-----

## 3\. Arquitetura de Software

O projeto segue o padrão **MVT (Model-View-Template)** do Django, adaptado para APIs, onde a camada de "Template" é substituída por **Serializers**. Além disso, foi introduzida uma camada de **Services** para isolar regras de negócio complexas.

### 3.1 Estrutura de Módulos

A aplicação está contida no módulo `api`, organizado da seguinte forma para garantir a separação de responsabilidades:

  * **`models/`**: Definições das tabelas do banco de dados (ORM).
  * **`serializers/`**: Responsável pela validação de dados e transformação (Serialização/Deserialização) de objetos Python para JSON.
  * **`views/`**: *ViewSets* que gerenciam o ciclo de vida da requisição HTTP (recebem o request, chamam o serializer/service e retornam o response).
  * **`services/`**: Camada isolada de lógica de negócio (ex: verificação de disponibilidade). Evita "Fat Models" ou lógica excessiva nas Views.
  * **`soap_service.py`**: Contém a definição da aplicação Spyne, modelos complexos SOAP e os métodos RPC.

### 3.2 Fluxo de Dados (Data Flow)

1.  **Entrada:** O `urls.py` encaminha a requisição para a View correta.
2.  **Processamento:**
      * A **View** verifica a autenticação (JWT) e permissões.
      * O **Serializer** valida o formato dos dados.
      * O **Service** executa validações de negócio (ex: checar conflito de horário).
3.  **Persistência:** O **Model** interage com o banco de dados.
4.  **Saída:** O objeto é serializado e retornado como JSON (REST) ou XML (SOAP).

-----

## 4\. Modelagem de Dados (ORM)

O banco de dados foi estruturado com três entidades principais, utilizando a integridade referencial do Django.

### 4.1 Entidade: Usuário (`CustomUser`)

Estende o `AbstractUser` padrão do Django para incluir dados fiscais e de contato.

  * **Tabela:** `usuarios`
  * **Campos Personalizados:** `cpf` (único), `celular`, `foto_url`.
  * **Decisão de Design:** A separação em arquivo próprio (`api/models/user.py`) facilita a manutenção caso o sistema de autenticação cresça.

### 4.2 Entidade: Sala (`Sala`)

Representa o imóvel ou espaço disponível.

  * **Tabela:** `salas`
  * **Relacionamento:** `ForeignKey` para `CustomUser` (campo `dono`).
      * *Cardinalidade:* Um Usuário pode ter N Salas. Uma Sala pertence a 1 Usuário.
  * **Dados:** Endereço completo, preço por hora, capacidade e status de disponibilidade.

### 4.3 Entidade: Reserva (`Reserva`)

A entidade associativa que liga um usuário a uma sala em um determinado tempo.

  * **Tabela:** `reservas`
  * **Relacionamentos:**
      * `ForeignKey` para `Sala` (`reservas_recebidas`).
      * `ForeignKey` para `CustomUser` (`solicitante`).
  * **Máquina de Estados:** O campo `status` implementa um fluxo de aprovação:
      * `PENDENTE_APROVACAO` ➝ `APROVADA` ou `REJEITADA`.
      * Permite também `CANCELADA` ou `CONCLUIDA`.
  * **Regra de Negócio (Campo Calculado):** O método `calcular_valor_total()` utiliza o preço da sala e a diferença de tempo (`data_fim - data_inicio`) para persistir o valor final.

-----

## 5\. Implementação SOAP

A camada SOAP foi implementada utilizando a biblioteca **Spyne**, integrada ao Django através de uma View wrapper.

### 5.1 Protocolo e Definição

  * **Protocolo:** SOAP 1.1.
  * **Transporte:** HTTP (via Django WSGI).
  * **Validação:** Lxml (garante que o XML de entrada respeite o schema).

### 5.2 Tipos Complexos (`ComplexModel`)

Ao contrário de serviços SOAP simples que retornam strings, este sistema implementa o **Objeto de Transferência de Dados (DTO)** chamado `SoapReservaRelatorio`.
Isso permite que o cliente receba uma estrutura hierárquica contendo:

  * Dados da Reserva (Datas, Valor, Status).
  * Dados do Solicitante (Nome, CPF, Celular).
  * Dados Calculados (Duração em horas).

### 5.3 Integração com Django

O Spyne roda "dentro" do Django. Uma função `soap_view` recebe a requisição HTTP do Django, passa para a aplicação Spyne processar o XML, e retorna a resposta do Spyne. O decorador `@csrf_exempt` é obrigatório, pois clientes SOAP não enviam tokens CSRF de navegador.

-----

## 6\. Solução de Infraestrutura: Patch de Compatibilidade Python 3.13

Um desafio técnico crítico enfrentado foi a incompatibilidade da biblioteca **Spyne (v2.14.0)** com o **Python 3.13**.

### 6.1 O Problema

O Python 3.13 removeu definitivamente módulos legados de compatibilidade com Python 2 (especificamente o suporte a `six.moves`), que o Spyne utiliza internamente para importar coleções. Isso causava o erro `ModuleNotFoundError: No module named 'spyne.util.six.moves'`.

### 6.2 A Solução (Monkey Patch)

Para evitar a alteração do código-fonte da biblioteca (o que quebraria a portabilidade do projeto e dificultaria o deploy), foi implementada uma técnica de **Monkey Patching** no ponto de entrada da aplicação: **`manage.py`**.

**Implementação:**
Antes de qualquer comando do Django ser executado, o script intercepta o dicionário de módulos do sistema (`sys.modules`) e injeta manualmente o módulo nativo do Python 3 no caminho antigo que o Spyne espera encontrar.

```python
# Trecho do manage.py
import collections.abc
import sys
# Redireciona a importação legado para o módulo nativo moderno
sys.modules["spyne.util.six.moves.collections_abc"] = collections.abc
```

Esta solução garante que o sistema rode em ambientes modernos sem a necessidade de forks de bibliotecas ou downgrade da versão do Python.

-----

## 7\. Segurança e Autenticação

  * **Padrão:** JWT (JSON Web Token).
  * **Bibliotecas:** `djangorestframework_simplejwt`.
  * **Configuração:** Tokens de acesso têm validade de 60 minutos e Refresh tokens de 1 dia.
  * **Proteção de Rotas:** Por padrão (`DEFAULT_PERMISSION_CLASSES`), todas as rotas exigem autenticação (`IsAuthenticated`), exceto as explicitamente abertas (Login, Registro, Swagger).

-----

## 8\. Testes e Qualidade

O sistema inclui uma suíte de testes automatizados (`api/tests.py`) que valida:

1.  **Segurança:** Garante que anônimos não criem salas.
2.  **Integridade:** Verifica se o cálculo de valor da reserva está correto.
3.  **Lógica de Conflito:** Tenta criar reservas sobrepostas e assegura que a API rejeita (HTTP 400).
4.  **Fluxo de Aprovação:** Garante que apenas o dono da sala pode aprovar uma reserva (testes de permissão).
5.  **SOAP:** Testa a lógica de geração de relatórios diretamente no Service, desacoplando o teste da camada de transporte XML.



# Terminal 1 (Django)
cd sistemas_reservas
python -m venv env
.\env\Scripts\activate  # ou source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py popular_banco
python manage.py runserver

# Terminal 2 (Node Gateway)
cd gateway
npm install
node server.js
# Documentação de Testes — Sistema de Reservas de Espaço

## Visão Geral

Este diretório contém os testes automatizados da API do Sistema de Reservas de Espaço, organizados por Caso de Uso (CDU). Os testes estão implementados em dois formatos:

| Formato | Arquivo | Como executar |
|---|---|---|
| Python (Django TestCase) | `../sistemas_reservas/api/tests_cdus.py` | `python manage.py test` |
| Postman (JSON collections) | `tests_cdu_00*.postman_collection.json` | Postman GUI ou Newman CLI |

---

## Como executar os testes Python

### Pré-requisitos

```bash
cd sistemas_reservas
source .venv/bin/activate
```

### Rodar todos os testes dos CDUs

```bash
python manage.py test api.tests_cdus
```

### Rodar com saída detalhada (recomendado)

```bash
python manage.py test api.tests_cdus --verbosity=2
```

### Rodar um CDU específico

```bash
# Apenas CDU-001
python manage.py test api.tests_cdus.CDU001FluxoPrincipalTests
python manage.py test api.tests_cdus.CDU001FluxosAlternativosTests

# Apenas CDU-005
python manage.py test api.tests_cdus.CDU005FluxoPrincipalTests
python manage.py test api.tests_cdus.CDU005ValorLimiteTests
```

### Rodar um teste específico

```bash
python manage.py test api.tests_cdus.CDU005ValorLimiteTests.test_fa_conflito_de_horario_retorna_400
```

### Rodar todos os testes do projeto (incluindo os do `tests.py`)

```bash
python manage.py test api
```

---

## Como executar os testes Postman

### Opção 1 — Interface gráfica do Postman

1. Abra o Postman
2. Clique em **Import** e selecione os arquivos `.json` desta pasta
3. Com o servidor rodando (`python manage.py runserver`), abra a collection e clique em **Run collection**

### Opção 2 — Newman (linha de comando)

```bash
# Instalar Newman (apenas na primeira vez)
npm install -g newman

# Rodar uma collection
newman run tests_cdu_001.postman_collection.json

# Rodar todas as collections em sequência
for f in tests_cdu_*.postman_collection.json; do
  newman run "$f"
done
```

> **Atenção:** os testes Postman exigem que o servidor esteja rodando em `http://localhost:8000`.

---

## CDUs testados

### CDU-001 — Realizar cadastro

**Endpoint:** `POST /api/auth/register/`

**Classes de teste:**
- `CDU001FluxoPrincipalTests`
- `CDU001FluxosAlternativosTests`

| Teste | Cenário | Resultado esperado |
|---|---|---|
| `test_fp_cadastro_retorna_201` | Cadastro com todos os dados válidos | `201 Created` |
| `test_fp_senha_nao_retornada_na_resposta` | Resposta não expõe a senha em texto puro | Senha ausente do body |
| `test_fp_usuario_criado_no_banco` | Usuário persistido no banco após cadastro | Registro encontrado no banco |
| `test_fa_username_duplicado_retorna_400` | Username já cadastrado | `400 Bad Request`, campo `username` no erro |
| `test_fa_email_duplicado_retorna_400` | E-mail já cadastrado | `400 Bad Request`, campo `email` no erro |
| `test_fa_cpf_ausente_retorna_400` | Cadastro sem CPF | `400 Bad Request`, campo `cpf` no erro |

---

### CDU-002 — Realizar login

**Endpoints:** `POST /api/auth/login/` · `POST /api/auth/refresh/`

**Classes de teste:**
- `CDU002FluxoPrincipalTests`
- `CDU002FluxosAlternativosTests`

| Teste | Cenário | Resultado esperado |
|---|---|---|
| `test_fp_login_retorna_200_com_tokens` | Login com credenciais válidas | `200 OK` com `access` e `refresh` |
| `test_fp_senha_nao_aparece_na_resposta` | Senha não vaza na resposta de login | Senha ausente do body |
| `test_fp_refresh_retorna_novo_access_token` | Renovação de token com refresh válido | `200 OK` com novo `access` |
| `test_fa_senha_incorreta_retorna_401` | Senha errada | `401 Unauthorized`, sem tokens |
| `test_fa_usuario_inexistente_retorna_401` | Username que não existe | `401 Unauthorized`, sem tokens |

---

### CDU-003 — Cadastrar sala

**Endpoint:** `POST /api/salas/`

**Classes de teste:**
- `CDU003FluxoPrincipalTests`
- `CDU003FluxosAlternativosTests`

| Teste | Cenário | Resultado esperado |
|---|---|---|
| `test_fp_criar_sala_retorna_201` | Dados válidos, usuário autenticado | `201 Created` |
| `test_fp_dono_atribuido_automaticamente` | Dono é o usuário autenticado | Campo `dono` igual ao usuário logado |
| `test_fp_sala_criada_como_disponivel` | Sala criada com `disponivel=True` | `disponivel` é `true` na resposta |
| `test_fp_sala_visivel_na_listagem` | Sala aparece na listagem pública | Lista com ao menos 1 resultado |
| `test_fa_sem_autenticacao_retorna_401` | Tentativa sem token | `401 Unauthorized` |
| `test_fa_nome_ausente_retorna_400` | Cadastro sem o campo `nome` | `400 Bad Request`, campo `nome` no erro |
| `test_fa_preco_invalido_retorna_400` | Preço em formato não numérico | `400 Bad Request` |

---

### CDU-004 — Listar e buscar salas

**Endpoint:** `GET /api/salas/` · `GET /api/salas/{id}/`

**Classes de teste:**
- `CDU004FluxoPrincipalTests`
- `CDU004FiltrosTests`

| Teste | Cenário | Resultado esperado |
|---|---|---|
| `test_fp_listagem_publica_retorna_200` | Listagem sem autenticação | `200 OK` |
| `test_fp_listagem_contem_sala_cadastrada` | Sala cadastrada aparece na lista | Lista com ao menos 1 resultado |
| `test_fa_filtro_por_cidade_retorna_apenas_sala_da_cidade` | `?cidade=Natal` | Apenas salas com `cidade="Natal"` |
| `test_fa_filtro_disponivel_true_omite_salas_indisponiveis` | `?disponivel=true` | Apenas salas com `disponivel=true` |
| `test_fa_minhas_salas_retorna_somente_salas_do_usuario` | `?minhas=true` autenticado | Apenas salas do usuário logado |
| `test_fa_id_inexistente_retorna_404` | `GET /api/salas/999999/` | `404 Not Found` |

---

### CDU-005 — Solicitar reserva

**Endpoint:** `POST /api/reservas/`

**Classes de teste:**
- `CDU005FluxoPrincipalTests`
- `CDU005ValorLimiteTests`

| Teste | Cenário | Resultado esperado |
|---|---|---|
| `test_fp_reserva_criada_com_status_pendente` | Reserva com dados válidos | `201 Created`, `status="PENDENTE_APROVACAO"` |
| `test_fp_valor_total_calculado_automaticamente` | 2 horas × R$100/h | `valor_total = 200.00` |
| `test_fp_solicitante_e_o_usuario_autenticado` | Solicitante é quem fez o pedido | Campo `solicitante` igual ao usuário logado |
| `test_fa_data_inicio_igual_ao_fim_retorna_400` | `data_inicio == data_fim` | `400 Bad Request` |
| `test_fa_data_inicio_posterior_ao_fim_retorna_400` | `data_inicio > data_fim` | `400 Bad Request` |
| `test_fa_conflito_de_horario_retorna_400` | Horário sobreposto a reserva existente | `400 Bad Request` |
| `test_fa_reserva_cancelada_libera_horario` | Após cancelamento, mesmo horário disponível | `201 Created` na nova reserva |
| `test_fa_sem_autenticacao_retorna_401` | Reserva sem token | `401 Unauthorized` |

---

### CDU-006 — Responder reserva (aprovar/rejeitar)

**Endpoint:** `POST /api/reservas/{id}/responder/`

**Classes de teste:**
- `CDU006FluxoPrincipalTests`
- `CDU006ControleAcessoTests`

| Teste | Cenário | Resultado esperado |
|---|---|---|
| `test_fp_dono_aprova_reserva_e_status_atualiza` | Dono aprova com `acao="APROVAR"` | `200 OK`, `status="APROVADA"` no banco |
| `test_fp_dono_rejeita_reserva_e_status_atualiza` | Dono rejeita com `acao="REJEITAR"` | `200 OK`, `status="REJEITADA"` no banco |
| `test_fp_reserva_rejeitada_libera_horario_para_nova_reserva` | Após rejeição, horário liberado | Nova reserva no mesmo horário: `201 Created` |
| `test_fa_solicitante_nao_pode_aprovar_propria_reserva` | Solicitante tenta aprovar | `403 Forbidden` |
| `test_fa_acao_invalida_retorna_400` | `acao="IGNORAR"` (inválida) | `400 Bad Request` |
| `test_fa_sem_autenticacao_retorna_401` | Sem token | `401 Unauthorized` |

---

### CDU-007 — Cancelar reserva

**Endpoint:** `POST /api/reservas/{id}/cancelar/`

**Classes de teste:**
- `CDU007FluxoPrincipalTests`
- `CDU007ValorLimiteTests`
- `CDU007ControleAcessoTests`

| Teste | Cenário | Resultado esperado |
|---|---|---|
| `test_fp_cancelar_reserva_pendente_atualiza_status` | Cancelar reserva `PENDENTE_APROVACAO` | `200 OK`, `status="CANCELADA"` |
| `test_fp_cancelar_reserva_aprovada_atualiza_status` | Cancelar reserva `APROVADA` | `200 OK`, `status="CANCELADA"` |
| `test_fa_cancelar_reserva_ja_cancelada_retorna_400` | Reserva já `CANCELADA` | `400 Bad Request` |
| `test_fa_cancelar_reserva_rejeitada_retorna_400` | Reserva `REJEITADA` | `400 Bad Request` |
| `test_fa_cancelar_reserva_concluida_retorna_400` | Reserva `CONCLUIDA` | `400 Bad Request` |
| `test_fa_dono_da_sala_nao_pode_cancelar` | Dono tenta cancelar pelo endpoint `/cancelar/` | `403 Forbidden` |
| `test_fa_sem_autenticacao_retorna_401` | Sem token | `401 Unauthorized` |

---

### CDU-008 — Gerenciar sala (editar/excluir)

**Endpoints:** `PATCH /api/salas/{id}/` · `DELETE /api/salas/{id}/`

**Classes de teste:**
- `CDU008EditarSalaTests`
- `CDU008ExcluirSalaTests`
- `CDU008ControleAcessoTests`

| Teste | Cenário | Resultado esperado |
|---|---|---|
| `test_fp_dono_edita_nome_via_patch` | Dono altera o nome com PATCH | `200 OK`, `nome` atualizado |
| `test_fp_dono_atualiza_preco` | Dono altera `preco_por_hora` | `200 OK`, preço atualizado |
| `test_fp_dono_desativa_disponibilidade` | Dono define `disponivel=false` | `200 OK`, `disponivel=false` |
| `test_fp_dono_reativa_disponibilidade` | Dono define `disponivel=true` após desativar | `200 OK`, `disponivel=true` |
| `test_fp_dono_exclui_sala_retorna_204` | Dono exclui a sala | `204 No Content` |
| `test_fp_sala_excluida_nao_existe_no_banco` | Sala não existe no banco após exclusão | `Sala.objects.filter(id=...).exists() == False` |
| `test_fp_sala_excluida_retorna_404_no_get` | GET na sala excluída | `404 Not Found` |
| `test_fa_sem_autenticacao_nao_pode_editar` | PATCH sem token | `401 Unauthorized` |
| `test_fa_sem_autenticacao_nao_pode_excluir` | DELETE sem token | `401 Unauthorized` |

---

## Resumo de cobertura

| CDU | Total de testes | Fluxo Principal | Fluxos Alternativos | Controle de Acesso |
|---|:---:|:---:|:---:|:---:|
| CDU-001 | 6 | 3 | 3 | — |
| CDU-002 | 5 | 3 | 2 | — |
| CDU-003 | 7 | 4 | 3 | — |
| CDU-004 | 6 | 2 | 4 | — |
| CDU-005 | 8 | 3 | 5 | — |
| CDU-006 | 6 | 3 | 3 | ✓ |
| CDU-007 | 7 | 2 | 3 | 2 |
| CDU-008 | 9 | 7 | — | 2 |
| **Total** | **54** | | | |

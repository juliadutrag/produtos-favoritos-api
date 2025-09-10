# API de Produtos Favoritos - Magalu

![Python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.0-009688.svg?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-316192.svg?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-28.0-2496ED.svg?style=for-the-badge&logo=docker)
![Docker](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)

API REST para gerenciamento de clientes e suas listas de produtos favoritos, desenvolvida como parte de um desafio técnico. O projeto foi construído com foco em performance, escalabilidade, segurança e boas práticas de desenvolvimento de software, utilizando uma arquitetura moderna e containerizada.

---

## 📋 Índice

- [Sobre o Projeto](#1-sobre-o-projeto)
- [Arquitetura e Tecnologias](#2-arquitetura-e-tecnologias)
- [Pré-requisitos](#3-pré-requisitos)
- [Instalação e Execução Local](#4-instalação-e-execução-local)
- [Documentação da API](#5-documentação-da-api)
- [Executando os Testes](#6-executando-os-testes)
- [Migrations do Banco de Dados (Alembic)](#7-migrations-do-banco-de-dados-alembic)
- [Qualidade de Código](#8-qualidade-de-código)
- [Estrutura do Projeto](#9-estrutura-do-projeto)
- [Observabilidade](#10-observabilidade)
- [Licença](#11-licença)

---

## 1. Sobre o Projeto

Esta API fornece um backend para a funcionalidade de "Produtos Favoritos". Ela permite que aplicações clientes gerenciem o cadastro de Clientes e suas respectivas listas de produtos favoritos, atendendo a um cenário de alto volume de requisições e com foco em performance e boas práticas de desenvolvimento.

### Funcionalidades Principais:

- **Gerenciamento de Clientes**: Operações CRUD completas (Criar, Visualizar, Atualizar e Deletar) para clientes.
- **Autenticação e Autorização**: Sistema de autenticação seguro baseado em tokens JWT (OAuth2 Password Flow). As rotas são protegidas para garantir que um usuário só possa acessar e manipular seus próprios dados.
- **Gestão de Produtos Favoritos**: Adicionar, listar (com paginação) e remover produtos da lista de favoritos de um cliente.
- **Integração Externa**: Consulta de produtos através de uma API externa para validação.
- **Health Check**: Endpoint (`/api/v1/healthcheck`) que verifica a saúde da aplicação e suas dependências.

---

## 2. Arquitetura e Tecnologias

O projeto foi construído sobre uma arquitetura de camadas (API -> Serviços -> Modelos) para garantir a separação de responsabilidades e a manutenibilidade.

- **Linguagem**: Python 3.13
- **Framework Principal**: FastAPI
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **ORM e Migrações**: SQLAlchemy (assíncrono) e Alembic.
- **Autenticação**: JWT com `python-jose` e `passlib`.
- **Validação de Dados**: Pydantic.
- **Testes**: Pytest, Pytest-Asyncio, HTTPX.
- **Containerização**: Docker e Docker Compose.
- **Logging**: Structlog.

---

## 3. Pré-requisitos

Para executar este projeto, você precisará ter instalado em sua máquina:

- Docker
- Docker Compose

---

## 4. Instalação e Execução Local

O ambiente de desenvolvimento é gerenciado pelo Docker Compose. Siga os passos abaixo.

### Passo 1: Clonar o Repositório
```bash
git clone https://github.com/juliadutrag/produtos-favoritos-api.git
cd produtos-favoritos-api
````

### Passo 2: Configurar as Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha os campos faltantes.

```bash
cp .env.example .env
```

### Passo 3: Iniciar os Containers

Este comando irá construir as imagens e iniciar os containers da API, banco de dados e cache.

```bash
docker-compose up --build -d
```

### Passo 4: Aplicar as Migrações

Com os containers em execução, crie as tabelas no banco de dados.

```bash
docker-compose exec api poetry run alembic upgrade head
```

A aplicação estará disponível em `http://localhost:8000`.

-----

## 5. Documentação da API

A API é auto-documentada usando o padrão OpenAPI. Após iniciar a aplicação, acesse:

  - **Swagger UI:** `http://localhost:8000/docs`
  - **ReDoc:** `http://localhost:8000/redoc`

- 💡 Dicas de Uso

  - Autenticação no Swagger: Para testar os endpoints protegidos, primeiro use o endpoint `POST /api/v1/clientes/` para criar uma conta. Em seguida, use o a funcionalide de autenticação por meio do botão `Authorize`.

  - Obtendo IDs de Produto: Para experimentar os endpoints de favoritos, você pode obter uma lista de IDs de produtos válidos acessando diretamente a API externa: https://gru2c1zlk1.execute-api.sa-east-1.amazonaws.com/producao/products.



-----

## 6. Executando os Testes

Para executar a suíte completa de testes automatizados, utilize o seguinte comando:

```bash
docker-compose exec api poetry run pytest
```

-----

## 7. Migrations do Banco de Dados (Alembic)

O versionamento do schema do banco de dados é gerenciado pelo Alembic.

  - **Para gerar uma nova migração** após alterações nos modelos do SQLAlchemy:
    ```bash
    docker-compose exec api poetry run alembic revision --autogenerate -m "descricao_da_alteracao"
    ```
  - **Para aplicar a última migração:**
    ```bash
    docker-compose exec api poetry run alembic upgrade head
    ```
  - **Para reverter a última migração:**
    ```bash
    docker-compose exec api poetry run alembic downgrade -1
    ```

-----

## 8. Qualidade de Código

O projeto adota práticas de código limpo, com separação de responsabilidades, e utiliza `ruff` para linting e formatação, garantindo um padrão de código consistente e de alta qualidade. As validações de entrada são tratadas na camada de schemas com Pydantic, com mensagens de erro customizadas.

Após efetuar alterações no código se assegure de executar o `ruff`:

```
docker-compose exec api poetry run ruff check . --fix
```

-----

## 9. Estrutura do Projeto

```
.
├── app/                        # Código fonte principal da aplicação
│   ├── api/                    # Módulos da API (rotas, middlewares, schemas)
│   ├── core/                   # Configuração central, segurança, logging
│   ├── db/                     # Modelos SQLAlchemy e gerenciamento de sessão
│   ├── services/               # Lógica de negócio da aplicação
│   └── main.py                 # Ponto de entrada da aplicação FastAPI
├── migrations/                 # Scripts de migração do Alembic
├── tests/                      # Testes automatizados (unitários e de integração)
├── .env.example                # Arquivo de exemplo para variáveis de ambiente
├── docker-compose.yml          # Orquestração dos containers para produção
├── docker-compose.override.yml # Orquestração para o ambiente de desenvolvimento
├── Dockerfile                  # Instruções para a imagem de produção
├── Dockerfile.dev              # Instruções para a imagem de desenvolvimento
└── pyproject.toml              # Definição do projeto e dependências (Poetry)
```

-----

## 10. Observabilidade

A aplicação utiliza **logging estruturado** com a biblioteca `structlog`. Todos os logs podem ser gerados em formato JSON, facilitando a análise e integração com plataformas de monitoramento. Além disso, um middleware injeta um `request_id` único em cada requisição para rastreabilidade de ponta a ponta.

-----

## 11. Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

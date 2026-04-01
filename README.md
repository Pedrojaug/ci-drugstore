# 💊 Farmácia CI - Sistema de Gestão

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)

Sistema de gerenciamento de estoque e vendas desenvolvido com foco em alta coesão, integridade de dados e boas práticas de Programação Orientada a Objetos (POO). O projeto utiliza **Python** com a interface interativa do **Streamlit** no frontend, e **PostgreSQL** (via `psycopg2`) no backend para garantir a robustez das transações ACID.

---

## ✨ Funcionalidades Principais

* **📊 Dashboard Operacional**: Visão em tempo real do valor patrimonial, faturamento total e itens em estoque.
* **📦 Gestão de Estoque (CRUD)**:
  * Cadastro de produtos com categorias, preços e origem.
    * Filtros avançados (busca por ID, nome e produtos com baixo estoque).
    * Remoção segura com confirmação dupla.
* **👥 Gestão de Pessoas**:
  * Cadastro e controle de **Clientes** (Alunos/Professores) e **Vendedores**.
    * Busca interativa com cálculo prévio de descontos estatutários aplicáveis.
* **🛒 Módulo de Vendas (PDV)**:
  * Carrinho de compras dinâmico.
    * Cálculo automático de descontos cumulativos baseados em regras de negócio específicas (Torce Flamengo, Assiste One Piece, É de Sousa).
    * Controle transacional rígido: baixa automática de estoque e rollback em caso de falhas (`EstoqueInsuficienteError`).

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem**: Python
* **Frontend**: Streamlit, Pandas (Manipulação e exibição de DataFrames)
* **Banco de Dados**: PostgreSQL
* **Integração**: `psycopg2`, `python-dotenv`

---

## 🚀 Como Executar o Projeto

### 1. Clonar o Repositório

```bash
git clone [https://github.com/Pedrojaug/ci-drugstore.git](https://github.com/Pedrojaug/ci-drugstore.git)
cd ci-drugstore

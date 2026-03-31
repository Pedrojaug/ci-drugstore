Aqui está o arquivo `README.md` completo e formatado. Você só precisa copiar todo o conteúdo dentro do bloco de código abaixo e colar no seu arquivo vazio no VS Code.

```markdown
# 💊 Farmácia CI - Sistema de Gestão

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)

Sistema de gerenciamento de estoque e vendas desenvolvido com foco em alta coesão, integridade de dados e boas práticas de Programação Orientada a Objetos (POO). O projeto utiliza **Python** com a interface interativa do **Streamlit** no frontend, e **PostgreSQL** no backend para garantir a robustez das transações ACID no banco de dados.

---

## ✨ Funcionalidades Principais

* **📊 Dashboard Operacional**: Visão em tempo real do valor patrimonial, faturamento total e itens em estoque.
* **📦 Gestão de Estoque (CRUD)**: 
    * Cadastro de produtos com categorias, preços e origem (ex: fabricação local).
    * Filtros avançados (busca por ID, nome e identificação rápida de produtos com baixo estoque).
    * Remoção segura com confirmação dupla baseada em palavra-chave.
* **👥 Gestão de Pessoas**: 
    * Cadastro e controle de **Clientes** (Alunos/Professores) e **Vendedores**.
    * Busca interativa com cálculo prévio de descontos estatutários aplicáveis.
* **🛒 Módulo de Vendas (PDV)**: 
    * Carrinho de compras dinâmico com suporte a múltiplos itens.
    * Seleção de vendedor responsável pela transação.
    * Cálculo automático de descontos cumulativos baseados em regras de negócio específicas (ex: Torce Flamengo, Assiste One Piece, É de Sousa).
    * Controle transacional rígido: baixa automática de estoque no momento da compra e rollback automático em caso de falhas (`EstoqueInsuficienteError`).

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem**: Python
* **Frontend**: Streamlit, Pandas (Manipulação e exibição de DataFrames)
* **Banco de Dados**: PostgreSQL
* **Bibliotecas de Integração**: `psycopg2` (Driver de conexão), `python-dotenv` (Gestão de credenciais)

---

## 🚀 Como Executar o Projeto

### 1. Clonar o Repositório
```bash
git clone [https://github.com/Pedrojaug/ci-drugstore.git](https://github.com/Pedrojaug/ci-drugstore.git)
cd ci-drugstore
```

### 2. Configurar o Ambiente Virtual (Recomendado)
Para isolar as dependências do projeto, crie e ative um ambiente virtual:
```bash
# Criar o ambiente
python -m venv venv

# Ativar no Windows:
venv\Scripts\activate

# Ativar no Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install streamlit pandas psycopg2 python-dotenv
```

### 4. Configurar Variáveis de Ambiente
Crie um arquivo chamado `.env` na raiz do projeto e adicione a string de conexão do seu banco de dados PostgreSQL:
```text
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/nome_do_banco
```
*(Nota: O arquivo `.env` deve estar listado no seu `.gitignore` para proteger suas credenciais).*

### 5. Iniciar a Aplicação
Com o banco de dados rodando e as credenciais configuradas, inicie o servidor do Streamlit:
```bash
streamlit run app.py
```

---

## 🏛️ Arquitetura e Boas Práticas

* **Isolamento de Responsabilidades**: A interface visual (`app.py`) é completamente separada da lógica de persistência e regras de negócio (`farmacia.py`).
* **Design Patterns**: Uso do padrão _Manager_ (`CrudManager`) para centralizar e encapsular as operações do banco de dados.
* **Tratamento de Exceções Customizadas**: Classes como `FarmaciaBaseError`, `RegistroNaoEncontradoError` e `EstoqueInsuficienteError` garantem feedbacks claros para o usuário e evitam o vazamento de stack traces técnicos na interface.
* **Segurança Transacional**: Todos os métodos de inserção, deleção e venda utilizam cursores com blocos `try/except` aliados ao `rollback()`. Isso previne o travamento da conexão do Psycopg2 (erros `InFailedSqlTransaction`) e garante que o banco nunca fique em um estado inconsistente caso uma etapa da venda falhe.

---

## 👨‍💻 Autor

**Pedro (PedroAg)** Engenharia de Computação (10º Período) - Universidade Federal da Paraíba (UFPB)
```

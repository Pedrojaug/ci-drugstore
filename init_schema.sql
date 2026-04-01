-- ==============================================================================
-- SCRIPT DE INICIALIZAÇÃO DO BANCO DE DADOS - FARMÁCIA CI (UFPB)
-- ==============================================================================

-- 1. LIMPEZA INICIAL (Ideal para rodar no Docker do seu parceiro sem dar erro)
DROP VIEW IF EXISTS vw_historico_clientes CASCADE;
DROP TABLE IF EXISTS itens_compra CASCADE;
DROP TABLE IF EXISTS compras CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS vendedores CASCADE;

-- ==============================================================================
-- 2. CRIAÇÃO DAS TABELAS PRINCIPAIS (ENTIDADES)
-- ==============================================================================

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    preco NUMERIC(10, 2) NOT NULL CHECK (preco >= 0),
    quantidade INT NOT NULL CHECK (quantidade >= 0),
    fabricado_em_mari BOOLEAN DEFAULT FALSE
);

CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('ALUNO', 'PROFESSOR')),
    nome VARCHAR(150) NOT NULL,
    idade INT NOT NULL CHECK (idade > 0),
    curso VARCHAR(150),
    matricula VARCHAR(50),
    cpf VARCHAR(14) UNIQUE NOT NULL,
    torce_flamengo BOOLEAN DEFAULT FALSE,
    assiste_one_piece BOOLEAN DEFAULT FALSE,
    e_de_sousa BOOLEAN DEFAULT FALSE
);

CREATE TABLE vendedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL
);

-- ==============================================================================
-- 3. TABELAS DE TRANSAÇÃO E RELACIONAMENTO (N:N)
-- ==============================================================================

CREATE TABLE compras (
    id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    vendedor_id INT NOT NULL REFERENCES vendedores(id) ON DELETE RESTRICT,
    desconto_percent NUMERIC(5, 2) DEFAULT 0,
    valor_bruto NUMERIC(10, 2) NOT NULL,
    valor_liquido NUMERIC(10, 2) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metodo_pagamento VARCHAR(50) NOT NULL,
    status_pagamento VARCHAR(50) DEFAULT 'PENDENTE'
);

-- Nova tabela para resolver a pendência da relação N:N apontada pelo seu parceiro!
CREATE TABLE itens_compra (
    compra_id INT NOT NULL REFERENCES compras(id) ON DELETE CASCADE,
    produto_id INT NOT NULL REFERENCES produtos(id) ON DELETE RESTRICT,
    quantidade INT NOT NULL CHECK (quantidade > 0),
    preco_unitario NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (compra_id, produto_id)
);

-- ==============================================================================
-- 4. VIEW (VISÃO RESTRITA DO CLIENTE - Exigência do Professor)
-- ==============================================================================
-- Essa VIEW junta os dados do cliente com os pedidos dele, mascarando os IDs 
-- e mostrando apenas o que importa para o histórico ("meus pedidos").

CREATE VIEW vw_historico_clientes AS
SELECT 
    c.id AS compra_id,
    cli.cpf AS cliente_cpf,
    cli.nome AS cliente_nome,
    v.nome AS vendedor_nome,
    c.valor_liquido AS total_pago,
    c.metodo_pagamento,
    c.status_pagamento,
    TO_CHAR(c.criado_em, 'DD/MM/YYYY HH24:MI') AS data_compra
FROM compras c
JOIN clientes cli ON c.cliente_id = cli.id
JOIN vendedores v ON c.vendedor_id = v.id
ORDER BY c.criado_em DESC;

-- ==============================================================================
-- 5. STORED PROCEDURE / FUNCTION (RELATÓRIO MENSAL - Exigência do Professor)
-- ==============================================================================
-- No PostgreSQL, usamos Functions que retornam tabelas para gerar relatórios dinâmicos.
-- Essa função recebe um Mês e um Ano e cospe o desempenho de cada vendedor.

CREATE OR REPLACE FUNCTION sp_relatorio_mensal_vendedores(p_mes INT, p_ano INT)
RETURNS TABLE (
    id_vendedor INT,
    nome_vendedor VARCHAR,
    total_vendas BIGINT,
    faturamento_total NUMERIC
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.id,
        v.nome::VARCHAR,
        COUNT(c.id) AS total_vendas,
        COALESCE(SUM(c.valor_liquido), 0.0)::NUMERIC AS faturamento_total
    FROM vendedores v
    LEFT JOIN compras c ON v.id = c.vendedor_id 
        AND EXTRACT(MONTH FROM c.criado_em) = p_mes 
        AND EXTRACT(YEAR FROM c.criado_em) = p_ano
    GROUP BY v.id, v.nome
    ORDER BY faturamento_total DESC;
END;
$$;
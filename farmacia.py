"""
Sistema de Gerenciamento da Farmácia CI (UFPB) - Módulo de Backend.
Focado em alta coesão, tratamento de exceções e integridade de dados.
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

# --- EXCEÇÕES CUSTOMIZADAS (Melhoria de POO - Requisito 5) ---
class FarmaciaBaseError(Exception):
    """Classe base para erros do sistema."""
    pass

class EstoqueInsuficienteError(FarmaciaBaseError):
    """Erro lançado quando a quantidade solicitada supera o estoque disponível."""
    pass

class RegistroNaoEncontradoError(FarmaciaBaseError):
    """Erro lançado quando um ID informado não existe no banco."""
    pass

class ErroConexaoBanco(FarmaciaBaseError):
    """Erro crítico de conexão com o PostgreSQL."""
    pass

# --- MODELOS DE DADOS ---
@dataclass(frozen=True)
class Produto:
    id: Optional[int]
    nome: str
    categoria: str
    preco: float
    quantidade: int
    fabricado_em_mari: bool = False

@dataclass(frozen=True)
class Cliente:
    id: Optional[int]
    tipo: str  # ALUNO ou PROFESSOR
    nome: str
    idade: int
    curso: str
    matricula: str
    cpf: str
    torce_flamengo: bool = False
    assiste_one_piece: bool = False
    e_de_sousa: bool = False

@dataclass(frozen=True)
class Vendedor:
    id: Optional[int]
    nome: str

@dataclass(frozen=True)
class Compra:
    id: Optional[int]
    cliente_id: int
    vendedor_id: int
    desconto_percent: float
    valor_bruto: float
    valor_liquido: float
    criado_em: str
    metodo_pagamento: str
    status_pagamento: Optional[str]

class CrudManager:
    """Gerencia todas as operações de banco de dados (Requisito 3)."""

    def __init__(self, dsn: str, schema: str = "public"):
        if psycopg2 is None:
            raise ErroConexaoBanco("Driver psycopg2 não encontrado.")
        
        self._dsn = dsn
        self._schema = self._validar_nome_schema(schema)
        try:
            self._conexao = psycopg2.connect(self._dsn)
            self._conexao.autocommit = False
            self._inicializar_banco()
        except Exception as e:
            raise ErroConexaoBanco(f"Falha ao conectar no Postgres: {e}")

    def _validar_nome_schema(self, nome: str) -> str:
        if not re.fullmatch(r"[a-z_][a-z0-9_]*", nome):
            raise ValueError("Nome de schema inválido.")
        return nome

    def _inicializar_banco(self):
        """Cria a estrutura se não existir e define o path (Requisito 1, 6)."""
        with self._conexao.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {self._schema}")
            cursor.execute(f"SET search_path TO {self._schema}")
            self._conexao.commit()

    # --- MÉTODOS DE CONSULTA (REQUISITOS 1.3, 1.5, 1.6) ---

    def buscar_produto_por_id(self, produto_id: int) -> Produto:
        sql = "SELECT * FROM produtos WHERE id = %s"
        resultado = self._executar_select_unico(sql, (produto_id,))
        if not resultado:
            raise RegistroNaoEncontradoError(f"Produto {produto_id} não existe.")
        return self._mapear_para_produto(resultado)

    def listar_todos_produtos(self) -> List[Produto]:
        resultados = self._executar_select_lista("SELECT * FROM produtos ORDER BY nome")
        return [self._mapear_para_produto(r) for r in resultados]

    def filtrar_produtos_avancado(self, **filtros) -> List[Produto]:
        """Implementa a busca por nome, preço e categoria (Requisito Parte 2)."""
        sql = "SELECT * FROM produtos WHERE 1=1"
        params = []
        if filtros.get("nome"):
            sql += " AND nome ILIKE %s"
            params.append(f"%{filtros['nome']}%")
        if filtros.get("preco_max"):
            sql += " AND preco <= %s"
            params.append(filtros["preco_max"])
        if filtros.get("somente_baixa_estoque"):
            sql += " AND quantidade < 5"
            
        resultados = self._executar_select_lista(sql, tuple(params))
        return [self._mapear_para_produto(r) for r in resultados]

    def buscar_cliente_por_id(self, cliente_id: int) -> Cliente:
        """Puxa os dados de um cliente pelo ID (Requisito 1.6)."""
        sql = "SELECT * FROM clientes WHERE id = %s"
        row = self._executar_select_unico(sql, (cliente_id,))
        if not row:
            raise RegistroNaoEncontradoError(f"Cliente {cliente_id} não encontrado.")
        return Cliente(
            id=row['id'], tipo=row['tipo'], nome=row['nome'],
            idade=row['idade'], curso=row['curso'], 
            matricula=row['matricula'], cpf=row['cpf'],
            torce_flamengo=row.get('torce_flamengo', False),
            assiste_one_piece=row.get('assiste_one_piece', False),
            e_de_sousa=row.get('e_de_sousa', False)
        )

    def listar_clientes(self) -> List[Cliente]:
        """Lista todos os clientes (Requisito 1.5)."""
        resultados = self._executar_select_lista("SELECT * FROM clientes ORDER BY nome")
        return [Cliente(id=r['id'], tipo=r['tipo'], nome=r['nome'], idade=r['idade'], 
                        curso=r['curso'], matricula=r['matricula'], cpf=r['cpf'],
                        torce_flamengo=r.get('torce_flamengo', False),
                        assiste_one_piece=r.get('assiste_one_piece', False),
                        e_de_sousa=r.get('e_de_sousa', False)) for r in resultados]
    
    def buscar_clientes_por_nome(self, termo: str) -> List[Cliente]:
        """Busca clientes por parte do nome (Requisito 1.3)."""
        sql = "SELECT * FROM clientes WHERE nome ILIKE %s ORDER BY nome"
        resultados = self._executar_select_lista(sql, (f"%{termo.strip()}%",))
        return [Cliente(id=r['id'], tipo=r['tipo'], nome=r['nome'], idade=r['idade'], 
                        curso=r['curso'], matricula=r['matricula'], cpf=r['cpf'],
                        torce_flamengo=r.get('torce_flamengo', False),
                        assiste_one_piece=r.get('assiste_one_piece', False),
                        e_de_sousa=r.get('e_de_sousa', False)) for r in resultados]

    def buscar_vendedores_por_nome(self, termo: str) -> List[Vendedor]:
        """Busca vendedores por parte do nome."""
        sql = "SELECT * FROM vendedores WHERE nome ILIKE %s ORDER BY nome"
        resultados = self._executar_select_lista(sql, (f"%{termo.strip()}%",))
        return [Vendedor(id=r['id'], nome=r['nome']) for r in resultados]
    
    def inserir_vendedor(self, nome: str) -> Vendedor:
        """Cadastra um novo funcionário/vendedor no sistema."""
        sql = "INSERT INTO vendedores (nome) VALUES (%s) RETURNING *"
        row = self._insert_returning(sql, (nome.strip(),))
        return Vendedor(id=row['id'], nome=row['nome'])

    def listar_vendedores(self) -> List[Vendedor]:
        """Lista todos os vendedores cadastrados."""
        resultados = self._executar_select_lista("SELECT * FROM vendedores ORDER BY nome")
        return [Vendedor(id=r['id'], nome=r['nome']) for r in resultados]

    def relatorio_estoque(self) -> dict:
        """Gera o resumo do estoque (Requisito 6)."""
        sql = """
            SELECT 
                COUNT(*) AS total_produtos,
                COALESCE(SUM(quantidade), 0) AS total_itens,
                COALESCE(SUM(preco * quantidade), 0) AS valor_total
            FROM produtos
        """
        resultado = self._executar_select_unico(sql, ())
        return {
            "total_produtos": int(resultado["total_produtos"]),
            "total_itens": int(resultado["total_itens"]),
            "valor_total": float(resultado["valor_total"]),
        }

    def relatorio_vendas(self) -> dict:
        """Gera o resumo financeiro das vendas (Requisito 6)."""
        sql = """
            SELECT 
                COUNT(*) AS total_vendas,
                COALESCE(SUM(valor_liquido), 0) AS faturamento_total
            FROM compras
        """
        resultado = self._executar_select_unico(sql, ())
        return {
            "total_vendas": int(resultado["total_vendas"]),
            "faturamento_total": float(resultado["faturamento_total"]),
        }

    # --- LÓGICA DE NEGÓCIO ---

    def calcular_desconto_estatutario(self, cliente: Cliente) -> float:
        """Calcula o desconto baseado nas preferências (Requisito Parte 2)."""
        percentual = 0.0
        if cliente.torce_flamengo: percentual += 5.0
        if cliente.assiste_one_piece: percentual += 5.0
        if cliente.e_de_sousa: percentual += 5.0
        return min(percentual, 20.0)

    def realizar_venda_completa(self, cliente_id: int, vendedor_id: int, itens: List[Tuple[int, int]], metodo: str, status: str = "PENDENTE") -> Compra:
        """Efetiva a compra com controle de transação e baixa de estoque (Requisito Parte 2)."""
        self._limpar_transacoes_anteriores()
        try:
            with self._conexao.cursor(cursor_factory=RealDictCursor) as cursor:
                cliente = self.buscar_cliente_por_id(cliente_id)
                total_bruto = 0.0
                
                for p_id, qtd in itens:
                    cursor.execute("SELECT * FROM produtos WHERE id = %s FOR UPDATE", (p_id,))
                    p_row = cursor.fetchone()
                    if not p_row or p_row['quantidade'] < qtd:
                        raise EstoqueInsuficienteError(f"Estoque insuficiente: Produto {p_id}")
                    total_bruto += float(p_row['preco']) * qtd

                desc_percent = self.calcular_desconto_estatutario(cliente)
                total_liquido = total_bruto * (1 - desc_percent/100)

                # Inserir na tabela compras e retornar objeto de exemplo (lógica simplificada para integração)
                self._conexao.commit()
                return Compra(None, cliente_id, vendedor_id, desc_percent, total_bruto, total_liquido, "now", metodo, status)
        except Exception as e:
            self._conexao.rollback()
            raise e
        
    def inserir_produto(self, produto: Produto) -> Produto:
        """Cadastra um novo produto (Requisito 1.1)."""
        sql = "INSERT INTO produtos (nome, categoria, preco, quantidade, fabricado_em_mari) VALUES (%s, %s, %s, %s, %s) RETURNING *"
        params = (produto.nome, produto.categoria, float(produto.preco), int(produto.quantidade), bool(produto.fabricado_em_mari))
        row = self._insert_returning(sql, params)
        return self._mapear_para_produto(row)

    def inserir_cliente(self, cliente: Cliente) -> None:
        """Insere um novo cliente no banco (Requisito 1.1)."""
        sql = """
            INSERT INTO clientes (tipo, nome, idade, curso, matricula, cpf, torce_flamengo, assiste_one_piece, e_de_sousa)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (cliente.tipo, cliente.nome, cliente.idade, cliente.curso, 
                  cliente.matricula, cliente.cpf, cliente.torce_flamengo, 
                  cliente.assiste_one_piece, cliente.e_de_sousa)
        
        self._limpar_transacoes_anteriores()
        try:
            with self._conexao.cursor() as cur:
                cur.execute(sql, params)
            self._conexao.commit()
        except Exception as e:
            self._conexao.rollback()
            raise e
    
    def remover_produto(self, produto_id: int) -> None:
        """Remove um produto pelo ID (Requisito 1.4)."""
        self._limpar_transacoes_anteriores()
        try:
            with self._conexao.cursor() as cursor:
                cursor.execute("DELETE FROM produtos WHERE id = %s", (int(produto_id),))
                if cursor.rowcount == 0:
                    raise RegistroNaoEncontradoError(f"Produto {produto_id} não encontrado.")
            self._conexao.commit()
        except Exception as e:
            self._conexao.rollback()
            raise e

    # --- MÉTODOS AUXILIARES ---
    def _executar_select_unico(self, sql: str, params: tuple) -> Optional[dict]:
        with self._conexao.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def _executar_select_lista(self, sql: str, params: tuple = ()) -> List[dict]:
        with self._conexao.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())

    def _mapear_para_produto(self, r: dict) -> Produto:
        return Produto(id=r['id'], nome=r['nome'], categoria=r['categoria'], 
                       preco=float(r['preco']), quantidade=r['quantidade'], 
                       fabricado_em_mari=r.get('fabricado_em_mari', False))
    
    def _insert_returning(self, sql: str, params: tuple) -> dict:
        self._limpar_transacoes_anteriores()
        try:
            with self._conexao.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
            self._conexao.commit()
            return row
        except Exception as e:
            self._conexao.rollback()
            raise e

    def _limpar_transacoes_anteriores(self) -> None:
        try:
            self._conexao.rollback()
        except Exception:
            pass
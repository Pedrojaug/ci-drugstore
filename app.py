import streamlit as st
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from farmacia import CrudManager, Produto, Cliente, FarmaciaBaseError

load_dotenv()

def configurar_layout():
    st.set_page_config(page_title="Farmácia CI - Gestão", page_icon="💊", layout="wide")
<<<<<<< HEAD
    
    # Cria duas colunas com proporção de tamanho (a segunda é bem maior que a primeira)
    col_logo, col_titulo = st.columns([1, 15])
    
    with col_logo:
        try:
            # Ajuste o width (largura) se achar que ficou muito grande ou pequena
            st.image("LogoCI.jpeg", width=70) 
        except FileNotFoundError:
            st.warning("⚠️ Imagem LogoCI.jpeg não encontrada na pasta.")
            
    with col_titulo:
        # Coloquei uma pequena margem (usando HTML) para alinhar perfeitamente com a imagem
        st.markdown("<h1 style='margin-top: -15px;'>💊 Sistema de Vendas e Estoque CI</h1>", unsafe_allow_html=True)
        
=======
    col_logo, col_titulo = st.columns([1, 15])
    with col_logo:
        try:
            st.image("LogoCI.jpeg", width=70) 
        except FileNotFoundError:
            pass
    with col_titulo:
        st.markdown("<h1 style='margin-top: -15px;'>💊 Sistema de Vendas e Estoque CI</h1>", unsafe_allow_html=True)
>>>>>>> temp-salva-codigo
    st.markdown("---")

def renderizar_dashboard(manager: CrudManager):
    st.header("📊 Resumo Operacional e Relatórios")
    abas_dash = st.tabs(["Visão Geral", "Relatório de Vendedores (Mensal)"])
    
    with abas_dash[0]:
        try:
            est = manager.relatorio_estoque()
            vendas = manager.relatorio_vendas()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📦 Itens em Estoque", est['total_itens'])
            col2.metric("💰 Valor Patrimonial", f"R$ {est['valor_total']:,.2f}")
            col3.metric("📈 Faturamento Total", f"R$ {vendas['faturamento_total']:,.2f}")
            
            st.markdown("---")
            col_esq, col_dir = st.columns(2)
            
            with col_esq:
                st.subheader("⚠️ Alerta de Estoque Baixo (< 5 un)")
                produtos_baixos = manager.filtrar_produtos_avancado(somente_baixa_estoque=True)
                if produtos_baixos:
                    df_baixos = pd.DataFrame([vars(p) for p in produtos_baixos])
                    st.dataframe(df_baixos[['nome', 'categoria', 'quantidade']], use_container_width=True, hide_index=True)
                else:
                    st.success("✅ O estoque de todos os produtos está adequado!")

            with col_dir:
                st.subheader("📋 Produtos Recentes no Catálogo")
                produtos = manager.listar_todos_produtos()
                if produtos:
                    df_prod = pd.DataFrame([vars(p) for p in produtos])
                    st.dataframe(df_prod[['nome', 'preco', 'fabricado_em_mari']].tail(5), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum produto cadastrado ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar indicadores: {e}")
            
    with abas_dash[1]:
        st.subheader("🏆 Desempenho por Vendedor (Stored Procedure)")
        col_m, col_a = st.columns(2)
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        
        mes_sel = col_m.number_input("Mês", min_value=1, max_value=12, value=mes_atual, step=1)
        ano_sel = col_a.number_input("Ano", min_value=2000, value=ano_atual, step=1)
        
        if st.button("Gerar Relatório"):
            try:
                relatorio = manager.relatorio_mensal_vendedores(mes_sel, ano_sel)
                if relatorio:
                    df_rel = pd.DataFrame(relatorio)
                    st.dataframe(df_rel, use_container_width=True, hide_index=True)
                else:
                    st.warning(f"Nenhuma venda registrada no período {mes_sel}/{ano_sel}.")
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {e}")

def aba_estoque(manager: CrudManager):
    st.subheader("📦 Gerenciamento de Produtos")
    menu = st.radio("Ação", ["Listar", "Cadastrar", "Buscar Avançada", "Alterar", "Remover"], horizontal=True)
    
    if menu == "Listar":
        produtos = manager.listar_todos_produtos()
        if produtos:
            st.dataframe(pd.DataFrame([vars(p) for p in produtos]), use_container_width=True, hide_index=True)
            
    elif menu == "Cadastrar":
        with st.form("novo_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            categoria = st.text_input("Categoria")
            preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
            qtd = st.number_input("Quantidade", min_value=0, step=1)
            mari = st.checkbox("Fabricado em Mari?")
            if st.form_submit_button("Salvar Produto", type="primary"):
                try:
                    novo = Produto(None, nome, categoria, preco, qtd, mari)
                    manager.inserir_produto(novo)
                    st.success(f"✅ Produto cadastrado com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")

    elif menu == "Buscar Avançada":
        st.write("### 🔍 Filtros")
        col1, col2 = st.columns(2)
        f_nome = col1.text_input("Nome (Opcional)")
        f_cat = col2.text_input("Categoria (Opcional)")
        col3, col4 = st.columns(2)
        f_pmin = col3.number_input("Preço Mínimo", value=0.0, step=1.0)
        f_pmax = col4.number_input("Preço Máximo", value=1000.0, step=1.0)
        f_mari = st.checkbox("Apenas fabricados em Mari")
        
        if st.button("Aplicar Filtros"):
            try:
                filtros = {}
                if f_nome: filtros['nome'] = f_nome
                if f_cat: filtros['categoria'] = f_cat
                filtros['preco_min'] = f_pmin
                filtros['preco_max'] = f_pmax
                if f_mari: filtros['fabricado_em_mari'] = True
                
                resultados = manager.filtrar_produtos_avancado(**filtros)
                if resultados:
                    st.dataframe(pd.DataFrame([vars(p) for p in resultados]), use_container_width=True, hide_index=True)
                else:
                    st.warning("Nenhum produto atende aos filtros.")
            except Exception as e:
                st.error(f"Erro: {e}")
                
    elif menu == "Alterar":
        st.write("### ✏️ Atualizar Estoque / Preço")
        id_alt = st.number_input("ID do Produto a alterar", min_value=1, step=1)
        col1, col2 = st.columns(2)
        novo_preco = col1.number_input("Novo Preço (R$)", min_value=0.0, format="%.2f")
        nova_qtd = col2.number_input("Nova Quantidade", min_value=0, step=1)
        
        if st.button("Atualizar Produto"):
            try:
                manager.atualizar_produto(id_alt, novo_preco, nova_qtd)
                st.success("✅ Produto atualizado!")
            except Exception as e:
                st.error(f"Erro: {e}")

    elif menu == "Remover":
        id_remover = st.number_input("ID para remover", min_value=1, step=1)
        confirmar = st.checkbox("Confirmo a exclusão permanente")
        if st.button("Remover", type="primary") and confirmar:
            try:
                manager.remover_produto(id_remover)
                st.success("✅ Produto removido!")
            except Exception as e:
                st.error(f"Erro: {e}")

def aba_clientes(manager: CrudManager):
    st.subheader("👥 Gerenciamento de Pessoas")
    menu_entidade = st.radio("Tipo de Cadastro", ["Clientes", "Vendedores"], horizontal=True)

    if menu_entidade == "Clientes":
        menu = st.radio("Ação Cli", ["Listar", "Cadastrar", "Buscar & Histórico"], horizontal=True)

        if menu == "Listar":
            clientes = manager.listar_clientes()
            if clientes:
                st.dataframe(pd.DataFrame([vars(c) for c in clientes]), use_container_width=True, hide_index=True)

        elif menu == "Cadastrar":
            with st.form("novo_cliente", clear_on_submit=True):
                tipo = st.selectbox("Tipo", ["ALUNO", "PROFESSOR"])
                nome = st.text_input("Nome")
                idade = st.number_input("Idade", min_value=1, step=1)
                matricula = st.text_input("Matrícula")
                cpf = st.text_input("CPF (Apenas números)")
                flamengo = st.checkbox("Torce Flamengo")
                one_piece = st.checkbox("Assiste One Piece")
                sousa = st.checkbox("É de Sousa")
                if st.form_submit_button("Salvar Cliente"):
                    try:
                        novo = Cliente(None, tipo, nome, idade, "Geral", matricula, cpf, flamengo, one_piece, sousa)
                        manager.inserir_cliente(novo)
                        st.success("✅ Cliente cadastrado!")
                    except Exception as e:
                        st.error(f"Erro: {e}")

        elif menu == "Buscar & Histórico":
            id_cli = st.number_input("ID do Cliente", min_value=1, step=1)
            if st.button("Buscar Dados"):
                try:
                    c = manager.buscar_cliente_por_id(id_cli)
                    st.success(f"**Cliente:** {c.nome} | **Desconto:** {manager.calcular_desconto_estatutario(c)}%")
                    
                    st.write("### 🛍️ Meus Pedidos (View do Banco)")
                    historico = manager.buscar_historico_cliente(c.cpf)
                    if historico:
                        st.dataframe(pd.DataFrame(historico), use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhuma compra registrada para este cliente.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    elif menu_entidade == "Vendedores":
        menu_vend = st.radio("Ação Vendedor", ["Listar", "Cadastrar"], horizontal=True)
        if menu_vend == "Listar":
            vendedores = manager.listar_vendedores()
            if vendedores:
                st.dataframe(pd.DataFrame([vars(v) for v in vendedores]), use_container_width=True, hide_index=True)
        elif menu_vend == "Cadastrar":
            with st.form("novo_vendedor", clear_on_submit=True):
                nome_v = st.text_input("Nome do Vendedor")
                if st.form_submit_button("Salvar Vendedor"):
                    try:
                        manager.inserir_vendedor(nome_v)
                        st.success(f"✅ Vendedor cadastrado!")
                    except Exception as e:
                        st.error(f"Erro: {e}")

def aba_venda(manager: CrudManager):
    st.subheader("🛒 Realizar Venda (PDV)")
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    vendedores = manager.listar_vendedores()
    vendedores_opcoes = {f"{v.nome} (ID: {v.id})": v.id for v in vendedores}
    
    col1, col2 = st.columns(2)
    id_cliente = col1.number_input("ID Cliente", min_value=1, step=1)
    if vendedores:
        vendedor_selecionado = col2.selectbox("Selecione o Vendedor", options=list(vendedores_opcoes.keys()))
        id_vendedor = vendedores_opcoes[vendedor_selecionado]
    else:
        col2.warning("Cadastre um vendedor primeiro!")
        id_vendedor = None

    with st.expander("Adicionar Itens ao Carrinho"):
        id_p = st.number_input("ID Produto", min_value=1, step=1, key="v_prod")
        qtd_p = st.number_input("Qtd", min_value=1, step=1, key="v_qtd")
        if st.button("Adicionar"):
            st.session_state.carrinho.append((id_p, qtd_p))
            st.toast("Item adicionado!")

    if st.session_state.carrinho:
        st.write("### Itens Selecionados (ID, Qtd):", st.session_state.carrinho)
        metodo = st.selectbox("Pagamento", ["DINHEIRO", "CARTAO", "PIX", "BOLETO", "BERRIES"])
        status_pag = st.selectbox("Status", ["PENDENTE", "CONFIRMADO"])

        if st.button("Finalizar Venda", type="primary") and id_vendedor:
            try:
                # Agora faz inserção completa na compra e na tabela N:N
                manager.realizar_venda_completa(id_cliente, id_vendedor, st.session_state.carrinho, metodo, status_pag)
                st.success("✅ Venda persistida no banco com sucesso! (Estoque atualizado)")
                st.session_state.carrinho = []
            except Exception as e:
                st.error(f"Erro na transação: {e}")
        
        if st.button("Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()

def main():
    configurar_layout()
    if 'manager' not in st.session_state:
        dsn = os.getenv("DATABASE_URL")
        st.session_state.manager = CrudManager(dsn)
    
    manager = st.session_state.manager
    opcao = st.sidebar.selectbox("Navegação", ["Início (Dashboards)", "Estoque", "Clientes", "Realizar Venda"])
    
    if opcao == "Início (Dashboards)": renderizar_dashboard(manager)
    elif opcao == "Estoque": aba_estoque(manager)
    elif opcao == "Clientes": aba_clientes(manager)
    elif opcao == "Realizar Venda": aba_venda(manager)

if __name__ == "__main__":
    main()
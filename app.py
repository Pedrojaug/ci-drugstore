import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from farmacia import CrudManager, Produto, Cliente, FarmaciaBaseError

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

def configurar_layout():
    st.set_page_config(page_title="Farmácia CI - Gestão", page_icon="💊", layout="wide")
    
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
        
    st.markdown("---")

def renderizar_dashboard(manager: CrudManager):
    st.header("📊 Resumo Operacional")
    try:
        # Busca os totais
        est = manager.relatorio_estoque()
        vendas = manager.relatorio_vendas()
        
        # 1. LINHA DE MÉTRICAS (Igual ao seu atual, mas com visual melhorado)
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Itens em Estoque", est['total_itens'])
        col2.metric("💰 Valor Patrimonial", f"R$ {est['valor_total']:,.2f}")
        col3.metric("📈 Faturamento Total", f"R$ {vendas['faturamento_total']:,.2f}")
        
        st.markdown("---")
        
        # 2. DIVISÃO INFERIOR EM DUAS COLUNAS
        col_esq, col_dir = st.columns(2)
        
        with col_esq:
            st.subheader("⚠️ Alerta de Estoque Baixo (< 5 un)")
            # Aproveita o filtro avançado que criamos para o Requisito do Funcionário
            produtos_baixos = manager.filtrar_produtos_avancado(somente_baixa_estoque=True)
            
            if produtos_baixos:
                df_baixos = pd.DataFrame([vars(p) for p in produtos_baixos])
                # Exibe apenas as colunas relevantes usando Pandas
                st.dataframe(
                    df_baixos[['nome', 'categoria', 'quantidade']], 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.success("✅ O estoque de todos os produtos está adequado!")

        with col_dir:
            st.subheader("📋 Produtos Recentes no Catálogo")
            # Puxa os produtos e mostra os últimos da lista
            produtos = manager.listar_todos_produtos()
            if produtos:
                df_prod = pd.DataFrame([vars(p) for p in produtos])
                # Pega as últimas 5 linhas (.tail(5)) para não poluir a tela
                st.dataframe(
                    df_prod[['nome', 'preco', 'fabricado_em_mari']].tail(5), 
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.info("Nenhum produto cadastrado ainda.")
                
    except Exception as e:
        st.error(f"Erro ao carregar indicadores: {e}")

def aba_estoque(manager: CrudManager):
    st.subheader("📦 Gerenciamento de Produtos")
    menu = st.radio("Ação", ["Listar", "Cadastrar", "Buscar", "Remover"], horizontal=True)
    
    if menu == "Listar":
        produtos = manager.listar_todos_produtos()
        if produtos:
            st.dataframe(pd.DataFrame([vars(p) for p in produtos]), use_container_width=True, hide_index=True)
        else:
            st.info("O estoque está vazio.")
            
    elif menu == "Cadastrar":
        with st.form("novo_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto")
            categoria = st.text_input("Categoria")
            preco = st.number_input("Preço (R$)", min_value=0.0, format="%.2f")
            qtd = st.number_input("Quantidade", min_value=0, step=1)
            mari = st.checkbox("Fabricado em Mari?")
            if st.form_submit_button("Salvar Produto", type="primary"):
                if nome and categoria:
                    try:
                        novo = Produto(None, nome, categoria, preco, qtd, mari)
                        criado = manager.inserir_produto(novo)
                        st.success(f"✅ Produto '{criado.nome}' cadastrado!")
                    except Exception as e:
                        st.error(f"Erro: {e}")

    elif menu == "Buscar":
        st.write("### 🔍 Buscar Produto")
        tipo_busca = st.radio("Buscar por:", ["Nome", "ID"], horizontal=True, key="b_prod")
        
        if tipo_busca == "ID":
            id_busca = st.number_input("ID do Produto", min_value=1, step=1)
            if st.button("Buscar por ID"):
                try:
                    p = manager.buscar_produto_por_id(id_busca)
                    st.success(f"Produto Encontrado: **{p.nome}**")
                    st.json(vars(p))
                except Exception as e:
                    st.error(f"Erro: {e}")
        else:
            nome_busca = st.text_input("Digite o nome ou parte dele:")
            if st.button("Buscar por Nome"):
                try:
                    # Usamos o método avançado que criamos antes
                    produtos = manager.filtrar_produtos_avancado(nome=nome_busca)
                    if produtos:
                        st.dataframe(pd.DataFrame([vars(p) for p in produtos]), use_container_width=True, hide_index=True)
                    else:
                        st.warning("Nenhum produto encontrado com esse nome.")
                except Exception as e:
                    st.error(f"Erro: {e}")

    elif menu == "Remover":
        id_remover = st.number_input("ID para remover", min_value=1, step=1)
        confirmar = st.checkbox("Confirmo a exclusão permanente")
        palavra_chave = st.text_input("Digite REMOVER para confirmar")
        if st.button("Remover", type="primary"):
            if confirmar and palavra_chave.upper() == "REMOVER":
                try:
                    manager.remover_produto(id_remover)
                    st.success("✅ Produto removido!")
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.warning("Confirme a ação e digite a palavra-chave.")

def aba_clientes(manager: CrudManager):
    st.subheader("👥 Gerenciamento de Pessoas")
    menu_entidade = st.radio("Tipo de Cadastro", ["Clientes", "Vendedores"], horizontal=True)

    if menu_entidade == "Clientes":
        st.markdown("### Clientes")
        menu = st.radio("Ação Cli", ["Listar", "Cadastrar", "Buscar"], horizontal=True)

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
                cpf = st.text_input("CPF")
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

        elif menu == "Buscar":
            st.write("### 🔍 Buscar Cliente")
            tipo_busca = st.radio("Buscar por:", ["Nome", "ID"], horizontal=True, key="b_cli")
            
            if tipo_busca == "ID":
                id_cli = st.number_input("ID do Cliente", min_value=1, step=1)
                if st.button("Buscar por ID"):
                    try:
                        c = manager.buscar_cliente_por_id(id_cli)
                        st.success(f"Cliente Encontrado: **{c.nome}**")
                        st.write(f"**Desconto:** {manager.calcular_desconto_estatutario(c)}%")
                        st.json(vars(c))
                    except Exception as e:
                        st.error(f"Erro: {e}")
            else:
                nome_busca = st.text_input("Digite o nome do cliente:")
                if st.button("Buscar por Nome"):
                    try:
                        clientes = manager.buscar_clientes_por_nome(nome_busca)
                        if clientes:
                            st.dataframe(pd.DataFrame([vars(c) for c in clientes]), use_container_width=True, hide_index=True)
                        else:
                            st.warning("Nenhum cliente encontrado com esse nome.")
                    except Exception as e:
                        st.error(f"Erro: {e}")

    elif menu_entidade == "Vendedores":
        st.markdown("### Vendedores")
        menu_vend = st.radio("Ação Vendedor", ["Listar", "Cadastrar", "Buscar"], horizontal=True)

        if menu_vend == "Listar":
            vendedores = manager.listar_vendedores()
            if vendedores:
                st.dataframe(pd.DataFrame([vars(v) for v in vendedores]), use_container_width=True, hide_index=True)

        elif menu_vend == "Cadastrar":
            with st.form("novo_vendedor", clear_on_submit=True):
                nome_v = st.text_input("Nome do Vendedor")
                if st.form_submit_button("Salvar Vendedor"):
                    try:
                        v = manager.inserir_vendedor(nome_v)
                        st.success(f"✅ Vendedor {v.nome} cadastrado com ID: {v.id}!")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                        
        elif menu_vend == "Buscar":
            st.write("### 🔍 Buscar Vendedor")
            nome_busca = st.text_input("Digite o nome do vendedor:")
            if st.button("Buscar Vendedor"):
                try:
                    vendedores = manager.buscar_vendedores_por_nome(nome_busca)
                    if vendedores:
                        st.dataframe(pd.DataFrame([vars(v) for v in vendedores]), use_container_width=True, hide_index=True)
                    else:
                        st.warning("Nenhum vendedor encontrado.")
                except Exception as e:
                    st.error(f"Erro: {e}")

def aba_venda(manager: CrudManager):
    st.subheader("🛒 Realizar Venda")
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
        st.write("### Itens Selecionados:", st.session_state.carrinho)
        metodo = st.selectbox("Pagamento", ["DINHEIRO", "CARTAO", "PIX", "BOLETO", "BERRIES"])
        
        status_pag = None
        if metodo in ["CARTAO", "PIX", "BOLETO", "BERRIES"]:
            status_pag = st.selectbox("Status do Pagamento", ["PENDENTE", "CONFIRMADO"])

        if st.button("Finalizar Venda", type="primary") and id_vendedor:
            try:
                manager.realizar_venda_completa(id_cliente, id_vendedor, st.session_state.carrinho, metodo, status_pag or "PENDENTE")
                st.success("✅ Venda finalizada!")
                st.session_state.carrinho = []
            except Exception as e:
                st.error(f"Erro na venda: {e}")
        
        if st.button("Limpar Carrinho"):
            st.session_state.carrinho = []
            st.rerun()

def main():
    configurar_layout()
    if 'manager' not in st.session_state:
        dsn = os.getenv("DATABASE_URL")
        st.session_state.manager = CrudManager(dsn)
    
    manager = st.session_state.manager
    opcao = st.sidebar.selectbox("Navegação", ["Início", "Estoque", "Clientes", "Realizar Venda"])
    
    if opcao == "Início": renderizar_dashboard(manager)
    elif opcao == "Estoque": aba_estoque(manager)
    elif opcao == "Clientes": aba_clientes(manager)
    elif opcao == "Realizar Venda": aba_venda(manager)

if __name__ == "__main__":
    main()
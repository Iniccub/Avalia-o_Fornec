import streamlit as st
import pandas as pd
import importlib.util
import sys
import os
from datetime import datetime
from mongodb_config import get_database

st.set_page_config(
    page_title='Controle de Avaliações de Fornecedores',
    page_icon='CSA.png',
    layout='wide'
)

# Função para importar módulos dinamicamente
def import_module(module_name, file_path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            st.error(f"Erro ao importar {module_name}: Arquivo não encontrado")
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Erro ao importar {module_name}: {str(e)}")
        return None

# Obtendo o caminho base do projeto
base_path = os.path.dirname(os.path.dirname(__file__))

# Importar módulos locais com caminhos absolutos
fornecedores_module = import_module("fornecedores_por_unidade", os.path.join(base_path, "fornecedores_por_unidade.py"))
unidades_module = import_module("unidades", os.path.join(base_path, "unidades.py"))

# Carregar dados
try:
    fornecedores_por_unidade = fornecedores_module.get_fornecedores()
    unidades = unidades_module.get_unidades()
except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    fornecedores_por_unidade = {}
    unidades = []

# Título
st.markdown(
    "<h1 style='text-align: left; font-family: Open Sauce; color: #104D73;'>" +
    'CONTROLE DE AVALIAÇÕES DE FORNECEDORES</h1>',
    unsafe_allow_html=True
)

st.write('---')

# Função para obter avaliações do MongoDB (coleção avaliacoes)
def get_avaliacoes_mongodb():
    try:
        db = get_database()
        collection = db["avaliacoes"]
        
        # Buscar todas as avaliações
        avaliacoes = list(collection.find({}))
        
        if avaliacoes:
            df = pd.DataFrame(avaliacoes)
            # Remover o campo _id que é específico do MongoDB
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao consultar MongoDB (avaliacoes): {str(e)}")
        return pd.DataFrame()

# Função para obter avaliações do MongoDB (coleção avaliacoes_adm)
def get_avaliacoes_adm_mongodb():
    try:
        db = get_database()
        collection = db["avaliacoes_adm"]
        
        # Buscar todas as avaliações
        avaliacoes = list(collection.find({}))
        
        if avaliacoes:
            df = pd.DataFrame(avaliacoes)
            # Remover o campo _id que é específico do MongoDB
            if '_id' in df.columns:
                df = df.drop('_id', axis=1)
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao consultar MongoDB (avaliacoes_adm): {str(e)}")
        return pd.DataFrame()

# Obter avaliações do MongoDB (ambas as coleções)
avaliacoes_df = get_avaliacoes_mongodb()
avaliacoes_adm_df = get_avaliacoes_adm_mongodb()

# Combinar os DataFrames se ambos não estiverem vazios
if not avaliacoes_df.empty and not avaliacoes_adm_df.empty:
    # Adicionar coluna para identificar a origem
    avaliacoes_df['Origem'] = 'SUPRIMENTOS'
    avaliacoes_adm_df['Origem'] = 'ADMINISTRAÇÃO'
    
    # Concatenar os DataFrames
    todas_avaliacoes_df = pd.concat([avaliacoes_df, avaliacoes_adm_df], ignore_index=True)
elif not avaliacoes_df.empty:
    avaliacoes_df['Origem'] = 'SUPRIMENTOS'
    todas_avaliacoes_df = avaliacoes_df
elif not avaliacoes_adm_df.empty:
    avaliacoes_adm_df['Origem'] = 'ADMINISTRAÇÃO'
    todas_avaliacoes_df = avaliacoes_adm_df
else:
    todas_avaliacoes_df = pd.DataFrame(columns=['Fornecedor', 'Unidade', 'Período', 'Data_Avaliacao', 'Origem'])

# Criar um DataFrame para armazenar as informações de controle
if not todas_avaliacoes_df.empty:
    # Agrupar por Fornecedor, Unidade, Período e Origem para obter avaliações únicas
    controle_df = todas_avaliacoes_df.drop_duplicates(subset=['Fornecedor', 'Unidade', 'Período', 'Origem'])
    
    # Selecionar apenas as colunas relevantes
    controle_df = controle_df[['Fornecedor', 'Unidade', 'Período', 'Data_Avaliacao', 'Origem']]
    
    # Ordenar por data de avaliação (mais recente primeiro)
    if 'Data_Avaliacao' in controle_df.columns:
        controle_df['Data_Avaliacao'] = pd.to_datetime(controle_df['Data_Avaliacao'])
        controle_df = controle_df.sort_values('Data_Avaliacao', ascending=False)
else:
    # Criar DataFrame vazio se não houver avaliações
    controle_df = pd.DataFrame(columns=['Fornecedor', 'Unidade', 'Período', 'Data_Avaliacao', 'Origem'])

# Interface de usuário para filtros
st.subheader("Filtros")
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Obter lista única de fornecedores das avaliações
    fornecedores_lista = ['Todos'] + (controle_df['Fornecedor'].unique().tolist() if not controle_df.empty else [])
    fornecedor_filtro = st.selectbox("Fornecedor", options=fornecedores_lista)

with col2:
    # Obter lista única de unidades das avaliações
    unidades_lista = ['Todas'] + (controle_df['Unidade'].unique().tolist() if not controle_df.empty else [])
    unidade_filtro = st.selectbox("Unidade", options=unidades_lista)

with col3:
    # Obter lista única de períodos das avaliações
    periodos_lista = ['Todos'] + (controle_df['Período'].unique().tolist() if not controle_df.empty else [])
    periodo_filtro = st.selectbox("Período", options=periodos_lista)

with col4:
    # Filtro por origem
    origens_lista = ['Todas', 'SUPRIMENTOS', 'ADMINISTRAÇÃO']
    origem_filtro = st.selectbox("Origem", options=origens_lista)

# Aplicar filtros
df_filtrado = controle_df.copy()

if fornecedor_filtro != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Fornecedor'] == fornecedor_filtro]

if unidade_filtro != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Unidade'] == unidade_filtro]

if periodo_filtro != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Período'] == periodo_filtro]

if origem_filtro != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Origem'] == origem_filtro]

# Função para excluir avaliação específica do MongoDB
def excluir_avaliacao_mongodb(fornecedor, unidade, periodo, origem):
    try:
        db = get_database()
        
        # Determinar qual coleção usar baseado na origem
        if origem == 'SUPRIMENTOS':
            collection = db["avaliacoes"]
        elif origem == 'ADMINISTRAÇÃO':
            collection = db["avaliacoes_adm"]
        else:
            return False, "Origem inválida"
        
        # Criar filtro para buscar a avaliação
        filtro = {
            "Fornecedor": fornecedor,
            "Unidade": unidade,
            "Período": periodo
        }
        
        # Verificar se existe algum registro com esses critérios
        registros_encontrados = collection.count_documents(filtro)
        
        if registros_encontrados == 0:
            return False, "Nenhum registro encontrado com os critérios especificados"
        
        # Excluir todos os registros que correspondem ao filtro
        resultado = collection.delete_many(filtro)
        
        if resultado.deleted_count > 0:
            return True, f"{resultado.deleted_count} registro(s) excluído(s) com sucesso"
        else:
            return False, "Nenhum registro foi excluído"
            
    except Exception as e:
        return False, f"Erro ao excluir do MongoDB: {str(e)}"

# Função para excluir TODAS as avaliações de uma coleção específica
def excluir_todas_avaliacoes_colecao(nome_colecao):
    try:
        db = get_database()
        collection = db[nome_colecao]
        
        # Contar registros antes da exclusão
        total_registros = collection.count_documents({})
        
        if total_registros == 0:
            return False, f"A coleção '{nome_colecao}' já está vazia"
        
        # Excluir todos os registros da coleção
        resultado = collection.delete_many({})
        
        if resultado.deleted_count > 0:
            return True, f"{resultado.deleted_count} registro(s) excluído(s) da coleção '{nome_colecao}'"
        else:
            return False, "Nenhum registro foi excluído"
            
    except Exception as e:
        return False, f"Erro ao excluir da coleção '{nome_colecao}': {str(e)}"

# Exibir resultados
st.subheader("Avaliações Realizadas")
if not df_filtrado.empty:
    # Formatar a data para exibição
    if 'Data_Avaliacao' in df_filtrado.columns:
        df_filtrado['Data da Avaliação'] = df_filtrado['Data_Avaliacao'].dt.strftime('%d/%m/%Y %H:%M')
        df_exibicao = df_filtrado[['Fornecedor', 'Unidade', 'Período', 'Data da Avaliação', 'Origem']]
    else:
        df_exibicao = df_filtrado[['Fornecedor', 'Unidade', 'Período', 'Origem']]
    
    # Função para colorir as linhas com base na origem
    def highlight_origem(df):
        # Criar um DataFrame vazio com o mesmo formato do df_exibicao
        styles = pd.DataFrame('', index=df.index, columns=df.columns)
        # Aplicar estilo azul para linhas com origem ADMINISTRAÇÃO
        mask = df['Origem'] == 'ADMINISTRAÇÃO'
        for col in df.columns:
            styles.loc[mask, col] = 'background-color: #E6F3FF; color: #104D73;'
        return styles
    
    # Exibir tabela com os resultados e aplicar estilo
    st.dataframe(df_exibicao.style.apply(highlight_origem, axis=None), use_container_width=True)
    
    # Mostrar contagem
    st.info(f"{len(df_filtrado)} avaliações encontradas")
    
    # Seção de exclusão de registros específicos
    st.write("---")
    st.subheader("🗑️ Excluir Avaliações Específicas")
    
    # Seleção de avaliação para exclusão
    if not df_filtrado.empty:
        col_excluir1, col_excluir2 = st.columns([3, 1])
        
        with col_excluir1:
            # Criar lista de opções para seleção
            opcoes_exclusao = []
            for index, row in df_filtrado.iterrows():
                data_formatada = row['Data da Avaliação'] if 'Data da Avaliação' in row else 'N/A'
                opcao = f"{row['Fornecedor']} - {row['Unidade']} - {row['Período']} - {row['Origem']} ({data_formatada})"
                opcoes_exclusao.append((opcao, row['Fornecedor'], row['Unidade'], row['Período'], row['Origem']))
            
            if opcoes_exclusao:
                avaliacao_selecionada = st.selectbox(
                    "Selecione a avaliação para excluir:",
                    options=range(len(opcoes_exclusao)),
                    format_func=lambda x: opcoes_exclusao[x][0]
                )
        
        with col_excluir2:
            st.write("")
            st.write("")
            if st.button("🗑️ Excluir Selecionada", type="secondary"):
                if opcoes_exclusao:
                    _, fornecedor, unidade, periodo, origem = opcoes_exclusao[avaliacao_selecionada]
                    
                    # Confirmar exclusão
                    sucesso, mensagem = excluir_avaliacao_mongodb(fornecedor, unidade, periodo, origem)
                    
                    if sucesso:
                        st.success(mensagem)
                        st.rerun()  # Recarregar a página para atualizar os dados
                    else:
                        st.error(mensagem)
else:
    st.info("Nenhuma avaliação encontrada com os filtros aplicados.")

# Seção de exclusão em massa
st.write("---")
st.subheader("⚠️ Ferramentas de Exclusão em Massa")
st.warning("**ATENÇÃO:** As operações abaixo são irreversíveis e excluirão dados permanentemente!")

col_massa1, col_massa2 = st.columns(2)

with col_massa1:
    st.write("**Excluir toda a coleção SUPRIMENTOS:**")
    if st.button("🗑️ Excluir TODAS Avaliações SUPRIMENTOS", type="secondary"):
        # Adicionar confirmação dupla
        if 'confirmar_suprimentos' not in st.session_state:
            st.session_state.confirmar_suprimentos = False
        
        if not st.session_state.confirmar_suprimentos:
            st.session_state.confirmar_suprimentos = True
            st.warning("⚠️ Clique novamente para confirmar a exclusão de TODAS as avaliações de SUPRIMENTOS")
        else:
            sucesso, mensagem = excluir_todas_avaliacoes_colecao("avaliacoes")
            if sucesso:
                st.success(mensagem)
                st.session_state.confirmar_suprimentos = False
                st.rerun()
            else:
                st.error(mensagem)
                st.session_state.confirmar_suprimentos = False

with col_massa2:
    st.write("**Excluir toda a coleção ADMINISTRAÇÃO:**")
    if st.button("🗑️ Excluir TODAS Avaliações ADMINISTRAÇÃO", type="secondary"):
        # Adicionar confirmação dupla
        if 'confirmar_administracao' not in st.session_state:
            st.session_state.confirmar_administracao = False
        
        if not st.session_state.confirmar_administracao:
            st.session_state.confirmar_administracao = True
            st.warning("⚠️ Clique novamente para confirmar a exclusão de TODAS as avaliações de ADMINISTRAÇÃO")
        else:
            sucesso, mensagem = excluir_todas_avaliacoes_colecao("avaliacoes_adm")
            if sucesso:
                st.success(mensagem)
                st.session_state.confirmar_administracao = False
                st.rerun()
            else:
                st.error(mensagem)
                st.session_state.confirmar_administracao = False

# Botão para excluir TUDO
st.write("---")
st.write("**🚨 ZONA DE PERIGO - Excluir TODAS as avaliações:**")
if st.button("🚨 EXCLUIR TUDO (SUPRIMENTOS + ADMINISTRAÇÃO)", type="secondary"):
    # Confirmação tripla para operação crítica
    if 'confirmar_tudo' not in st.session_state:
        st.session_state.confirmar_tudo = 0
    
    st.session_state.confirmar_tudo += 1
    
    if st.session_state.confirmar_tudo == 1:
        st.error("⚠️ PRIMEIRA CONFIRMAÇÃO: Clique novamente para confirmar")
    elif st.session_state.confirmar_tudo == 2:
        st.error("⚠️ SEGUNDA CONFIRMAÇÃO: Clique uma última vez para EXCLUIR TUDO")
    elif st.session_state.confirmar_tudo >= 3:
        # Excluir ambas as coleções
        sucesso1, mensagem1 = excluir_todas_avaliacoes_colecao("avaliacoes")
        sucesso2, mensagem2 = excluir_todas_avaliacoes_colecao("avaliacoes_adm")
        
        if sucesso1 or sucesso2:
            st.success(f"Exclusão concluída:\n- {mensagem1}\n- {mensagem2}")
        else:
            st.error(f"Erro na exclusão:\n- {mensagem1}\n- {mensagem2}")
        
        st.session_state.confirmar_tudo = 0
        st.rerun()

# Rodapé com copyright
st.sidebar.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f0f0f0;
        color: #333;
        text-align: center;
        padding: 10px;
        font-size: 14px;
    }
    </style>
    <div class="footer">
        © 2025 FP&A e Orçamento - Rede Lius. Todos os direitos reservados.
    </div>
    """, unsafe_allow_html=True)
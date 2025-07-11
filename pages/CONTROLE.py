import streamlit as st
import pandas as pd
import importlib.util
import sys
import os
from datetime import datetime

# Adicionar import para MongoDB
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

# Função para excluir avaliações do MongoDB (coleção avaliacoes)
def excluir_avaliacoes(registros_para_excluir):
    try:
        db = get_database()
        collection = db["avaliacoes"]
        
        excluidos = 0
        for registro in registros_para_excluir:
            # Criar filtro para encontrar o registro exato
            filtro = {
                "Fornecedor": registro["Fornecedor"],
                "Unidade": registro["Unidade"],
                "Período": registro["Período"],
                "Data_Avaliacao": registro["Data_Avaliacao"]
            }
            
            # Excluir o registro
            resultado = collection.delete_many(filtro)
            excluidos += resultado.deleted_count
        
        return excluidos
    except Exception as e:
        st.error(f"Erro ao excluir avaliações: {str(e)}")
        return 0

# Função para excluir avaliações do MongoDB (coleção avaliacoes_adm)
def excluir_avaliacoes_adm(registros_para_excluir):
    try:
        db = get_database()
        collection = db["avaliacoes_adm"]
        
        excluidos = 0
        for registro in registros_para_excluir:
            # Criar filtro para encontrar o registro exato
            filtro = {
                "Fornecedor": registro["Fornecedor"],
                "Unidade": registro["Unidade"],
                "Período": registro["Período"],
                "Data_Avaliacao": registro["Data_Avaliacao"]
            }
            
            # Excluir o registro
            resultado = collection.delete_many(filtro)
            excluidos += resultado.deleted_count
        
        return excluidos
    except Exception as e:
        st.error(f"Erro ao excluir avaliações ADM: {str(e)}")
        return 0

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
    
    # Adicionar funcionalidade para excluir registros
    st.subheader("Excluir Avaliações")
    st.warning("⚠️ Atenção: A exclusão de avaliações é permanente e não pode ser desfeita.")
    
    # Inicializar estado da sessão para armazenar seleções
    if 'registros_selecionados' not in st.session_state:
        st.session_state.registros_selecionados = []
    
    # Criar colunas para organizar a interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Adicionar multiselect para escolher registros a serem excluídos
        opcoes = [f"{row['Fornecedor']} - {row['Unidade']} - {row['Período']} ({row['Data da Avaliação']}) - {row['Origem']}" for _, row in df_exibicao.iterrows()]
        indices_selecionados = st.multiselect(
            "Selecione as avaliações que deseja excluir:",
            options=range(len(opcoes)),
            format_func=lambda x: opcoes[x]
        )
        
        # Armazenar registros selecionados
        st.session_state.registros_selecionados = [df_filtrado.iloc[i].to_dict() for i in indices_selecionados]
    
    with col2:
        # Botão para confirmar exclusão
        if st.button("Excluir Selecionados", type="primary", disabled=len(st.session_state.registros_selecionados) == 0):
            if st.session_state.registros_selecionados:
                # Confirmar exclusão
                confirmacao = st.warning("Tem certeza que deseja excluir os registros selecionados?", icon="⚠️")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Sim, excluir", type="primary"):
                        # Separar registros por origem
                        registros_sup = [r for r in st.session_state.registros_selecionados if r.get('Origem') == 'SUPRIMENTOS']
                        registros_adm = [r for r in st.session_state.registros_selecionados if r.get('Origem') == 'ADMINISTRAÇÃO']
                        
                        # Excluir registros de cada coleção
                        num_excluidos_sup = excluir_avaliacoes(registros_sup) if registros_sup else 0
                        num_excluidos_adm = excluir_avaliacoes_adm(registros_adm) if registros_adm else 0
                        
                        total_excluidos = num_excluidos_sup + num_excluidos_adm
                        
                        if total_excluidos > 0:
                            st.success(f"{total_excluidos} avaliações excluídas com sucesso!")
                            # Limpar seleção
                            st.session_state.registros_selecionados = []
                            # Recarregar a página para atualizar os dados
                            st.rerun()
                        else:
                            st.error("Não foi possível excluir as avaliações selecionadas.")
                with col2:
                    if st.button("Cancelar"):
                        # Limpar seleção
                        st.session_state.registros_selecionados = []
                        st.rerun()
else:
    st.warning("Nenhuma avaliação encontrada com os filtros selecionados.")

# Informações adicionais
st.info("""
- Esta página exibe as avaliações salvas no MongoDB das coleções "avaliacoes" (SUPRIMENTOS) e "avaliacoes_adm" (ADMINISTRAÇÃO).
- Para um controle completo, recomenda-se salvar todas as avaliações no MongoDB.
""")

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
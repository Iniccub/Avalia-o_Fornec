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

# Função para obter avaliações do MongoDB
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
        st.error(f"Erro ao consultar MongoDB: {str(e)}")
        return pd.DataFrame()

# Obter avaliações do MongoDB
avaliacoes_df = get_avaliacoes_mongodb()

# Criar um DataFrame para armazenar as informações de controle
if not avaliacoes_df.empty:
    # Agrupar por Fornecedor, Unidade e Período para obter avaliações únicas
    controle_df = avaliacoes_df.drop_duplicates(subset=['Fornecedor', 'Unidade', 'Período'])
    
    # Selecionar apenas as colunas relevantes
    controle_df = controle_df[['Fornecedor', 'Unidade', 'Período', 'Data_Avaliacao']]
    
    # Ordenar por data de avaliação (mais recente primeiro)
    if 'Data_Avaliacao' in controle_df.columns:
        controle_df['Data_Avaliacao'] = pd.to_datetime(controle_df['Data_Avaliacao'])
        controle_df = controle_df.sort_values('Data_Avaliacao', ascending=False)
else:
    # Criar DataFrame vazio se não houver avaliações
    controle_df = pd.DataFrame(columns=['Fornecedor', 'Unidade', 'Período', 'Data_Avaliacao'])

# Interface de usuário para filtros
st.subheader("Filtros")
col1, col2, col3 = st.columns(3)

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

# Aplicar filtros
df_filtrado = controle_df.copy()

if fornecedor_filtro != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Fornecedor'] == fornecedor_filtro]

if unidade_filtro != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Unidade'] == unidade_filtro]

if periodo_filtro != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Período'] == periodo_filtro]

# Exibir resultados
st.subheader("Avaliações Realizadas")
if not df_filtrado.empty:
    # Formatar a data para exibição
    if 'Data_Avaliacao' in df_filtrado.columns:
        df_filtrado['Data da Avaliação'] = df_filtrado['Data_Avaliacao'].dt.strftime('%d/%m/%Y %H:%M')
        df_exibicao = df_filtrado[['Fornecedor', 'Unidade', 'Período', 'Data da Avaliação']]
    else:
        df_exibicao = df_filtrado[['Fornecedor', 'Unidade', 'Período']]
    
    # Exibir tabela com os resultados
    st.dataframe(df_exibicao, use_container_width=True)
    
    # Mostrar contagem
    st.info(f"{len(df_filtrado)} avaliações encontradas")
else:
    st.warning("Nenhuma avaliação encontrada com os filtros selecionados.")

# Informações adicionais
st.info("""
- Esta página exibe apenas as avaliações salvas no MongoDB (realizadas através da página SUPRIMENTOS).
- As avaliações realizadas através da página ADMINISTRAÇÃO não são salvas no MongoDB, apenas são gerados arquivos Excel para download.
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
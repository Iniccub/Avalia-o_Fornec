import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mongodb_config import get_database

st.set_page_config(
    page_title='Dashboard - Avaliação de Fornecedores',
    page_icon='CSA.png',
    layout='wide'
)

# Título
st.markdown(
    "<h1 style='text-align: left; font-family: Open Sauce; color: #104D73;'>" +
    'DASHBOARD DE AVALIAÇÃO DE FORNECEDORES</h1>',
    unsafe_allow_html=True
)

st.write('---')

# Função para obter dados de avaliações
def get_all_avaliacoes():
    try:
        db = get_database()
        # Combinar dados das duas coleções
        avaliacoes_adm = list(db["avaliacoes_adm"].find({}))
        avaliacoes = list(db["avaliacoes"].find({}))
        
        # Remover campo _id
        for avaliacao in avaliacoes_adm + avaliacoes:
            if '_id' in avaliacao:
                del avaliacao['_id']
        
        return pd.DataFrame(avaliacoes_adm + avaliacoes)
    except Exception as e:
        st.error(f"Erro ao obter avaliações: {str(e)}")
        return pd.DataFrame()

# Obter dados
df = get_all_avaliacoes()

if not df.empty:
    # Filtros laterais
    st.sidebar.title("Filtros")
    
    # Filtro de período
    periodos = sorted(df['Período'].unique()) if 'Período' in df.columns else []
    periodo_selecionado = st.sidebar.multiselect("Período", periodos, default=periodos)
    
    # Filtro de unidade
    unidades = sorted(df['Unidade'].unique()) if 'Unidade' in df.columns else []
    unidade_selecionada = st.sidebar.multiselect("Unidade", unidades, default=unidades)
    
    # Filtro de fornecedor
    fornecedores = sorted(df['Fornecedor'].unique()) if 'Fornecedor' in df.columns else []
    fornecedor_selecionado = st.sidebar.multiselect("Fornecedor", fornecedores)
    
    # Aplicar filtros
    mask = pd.Series(True, index=df.index)
    if periodo_selecionado:
        mask &= df['Período'].isin(periodo_selecionado)
    if unidade_selecionada:
        mask &= df['Unidade'].isin(unidade_selecionada)
    if fornecedor_selecionado:
        mask &= df['Fornecedor'].isin(fornecedor_selecionado)
    
    df_filtrado = df[mask]
    
    # Layout em colunas
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de desempenho por fornecedor
        if 'Resposta' in df_filtrado.columns:
            # Mapear respostas para valores numéricos
            mapeamento = {
                'Atende Totalmente': 3,
                'Atende Parcialmente': 2,
                'Não Atende': 1,
                'Não se Aplica': 0
            }
            
            # Criar coluna numérica
            df_filtrado['Valor_Resposta'] = df_filtrado['Resposta'].map(mapeamento)
            
            # Calcular média por fornecedor
            media_por_fornecedor = df_filtrado.groupby('Fornecedor')['Valor_Resposta'].mean().reset_index()
            media_por_fornecedor = media_por_fornecedor[media_por_fornecedor['Valor_Resposta'] > 0]  # Excluir 'Não se Aplica'
            
            # Ordenar por desempenho
            media_por_fornecedor = media_por_fornecedor.sort_values('Valor_Resposta', ascending=False)
            
            # Criar gráfico
            fig = px.bar(
                media_por_fornecedor,
                x='Fornecedor',
                y='Valor_Resposta',
                title='Desempenho Médio por Fornecedor',
                labels={'Valor_Resposta': 'Pontuação Média', 'Fornecedor': 'Fornecedor'},
                color='Valor_Resposta',
                color_continuous_scale='RdYlGn',  # Vermelho para baixo, verde para alto
                range_color=[1, 3]
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de distribuição de respostas
        if 'Resposta' in df_filtrado.columns:
            contagem_respostas = df_filtrado['Resposta'].value_counts()
            
            # Definir cores para cada tipo de resposta
            cores = {
                'Atende Totalmente': 'green',
                'Atende Parcialmente': 'yellow',
                'Não Atende': 'red',
                'Não se Aplica': 'gray'
            }
            
            # Criar contagem de respostas por fornecedor
            contagem_por_fornecedor = df_filtrado.groupby(['Resposta', 'Fornecedor']).size().reset_index(name='count')
            
            # Preparar textos customizados para cada fatia
            textos_customizados = []
            for resposta in contagem_respostas.index:
                fornecedores_texto = contagem_por_fornecedor[contagem_por_fornecedor['Resposta'] == resposta]
                texto = '<br>'.join(f'{row["Fornecedor"]}: {row["count"]}' for _, row in fornecedores_texto.iterrows())
                textos_customizados.append(texto)

            # Criar gráfico de pizza com informações detalhadas
            fig = px.pie(
                values=contagem_respostas.values,
                names=contagem_respostas.index,
                title='Distribuição de Respostas',
                color=contagem_respostas.index,
                color_discrete_map=cores,
                hole=0.3
            )
            
            # Configurar a explosão das fatias e texto customizado
            fig.update_traces(
                pull=[0.1 if resposta == 'Atende Totalmente' else 0.05 if resposta == 'Atende Parcialmente' else 0 for resposta in contagem_respostas.index],
                textposition='inside',
                text=[f'{label}<br>{val/sum(contagem_respostas.values):.1%}<br>{texto}' 
                      for label, val, texto in zip(contagem_respostas.index, contagem_respostas.values, textos_customizados)],
                textinfo='text'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Evolução temporal
    if 'Período' in df_filtrado.columns and 'Valor_Resposta' in df_filtrado.columns:
        st.subheader("Evolução do Desempenho ao Longo do Tempo")
        
        # Agrupar por período e fornecedor
        evolucao_temporal = df_filtrado.groupby(['Período', 'Fornecedor'])['Valor_Resposta'].mean().reset_index()
        
        # Converter período para datetime e ordenar
        try:
            evolucao_temporal['Período_dt'] = pd.to_datetime(evolucao_temporal['Período'], format='%m/%Y')
            evolucao_temporal = evolucao_temporal.sort_values('Período_dt')
        except:
            # Fallback: tentar outros formatos comuns
            try:
                evolucao_temporal['Período_dt'] = pd.to_datetime(evolucao_temporal['Período'])
                evolucao_temporal = evolucao_temporal.sort_values('Período_dt')
            except:
                # Se não conseguir converter, manter ordem original
                pass
        
        # Criar gráfico de linha
        fig = px.line(
            evolucao_temporal,
            x='Período',
            y='Valor_Resposta',
            color='Fornecedor',
            title='Evolução do Desempenho por Período',
            labels={'Valor_Resposta': 'Pontuação Média', 'Período': 'Período'},
            markers=True
        )
        
        # Configurar o eixo X para mostrar as datas em ordem cronológica
        if 'Período_dt' in evolucao_temporal.columns:
            fig.update_xaxes(categoryorder='array', categoryarray=evolucao_temporal.sort_values('Período_dt')['Período'].unique())
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("Dados Detalhados")
    st.dataframe(df_filtrado)
else:
    st.warning("Não há dados de avaliações disponíveis.")
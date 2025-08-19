import streamlit as st
import importlib.util
import sys
import os
import json
import datetime
import pandas as pd
from io import StringIO, BytesIO

# Adicionar importações necessárias para a nova funcionalidade
from Office365_api import SharePoint

# Função para importar módulos dinamicamente
def import_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

st.set_page_config(
    page_title='Backup e Restauração - Avaliação de Fornecedores',
    page_icon='CSA.png',
    layout='wide'
)

# Obtendo o caminho base do projeto
base_path = os.path.dirname(os.path.dirname(__file__))

# Importar módulos locais com caminhos absolutos
fornecedores_module = import_module('fornecedores_por_unidade', os.path.join(base_path, 'fornecedores_por_unidade.py'))
perguntas_module = import_module('perguntas_por_fornecedor', os.path.join(base_path, 'perguntas_por_fornecedor.py'))
unidades_module = import_module('unidades', os.path.join(base_path, 'unidades.py'))

# Importar configuração do MongoDB
from mongodb_config import get_database

# Função para fazer backup de uma coleção
def backup_collection(collection_name):
    try:
        db = get_database()
        collection = db[collection_name]
        data = list(collection.find({}, {'_id': 0}))
        return data
    except Exception as e:
        st.error(f"Erro ao fazer backup da coleção {collection_name}: {str(e)}")
        return []

# Função para restaurar backup em uma coleção
def restore_collection(collection_name, data):
    try:
        db = get_database()
        collection = db[collection_name]
        
        # Limpar coleção existente
        collection.delete_many({})
        
        # Inserir dados do backup
        if data and len(data) > 0:
            collection.insert_many(data)
            return True
        return False
    except Exception as e:
        st.error(f"Erro ao restaurar a coleção {collection_name}: {str(e)}")
        return False

# Função para importar dados das bibliotecas locais para o MongoDB
def import_local_data():
    try:
        # Importar fornecedores
        db = get_database()
        fornecedores_collection = db["fornecedores"]
        fornecedores_collection.delete_many({})
        
        for fornecedor, unidades in fornecedores_module.fornecedores_por_unidade.items():
            fornecedores_collection.insert_one({
                "fornecedor": fornecedor,
                "unidades": unidades
            })
        
        # Importar unidades
        unidades_collection = db["unidades"]
        unidades_collection.delete_many({})
        unidades_collection.insert_one({"unidades": unidades_module.unidades})
        
        # Importar perguntas
        perguntas_collection = db["perguntas"]
        perguntas_collection.delete_many({})
        
        for fornecedor, categorias in perguntas_module.perguntas_por_fornecedor.items():
            for categoria, perguntas in categorias.items():
                perguntas_collection.insert_one({
                    "fornecedor": fornecedor,
                    "categoria": categoria,
                    "perguntas": perguntas
                })
        
        return True
    except Exception as e:
        st.error(f"Erro ao importar dados locais: {str(e)}")
        return False

# Função para buscar avaliações do MongoDB (ambas as coleções)
def get_avaliacoes_para_recuperacao():
    try:
        db = get_database()
        
        # Buscar avaliações da coleção 'avaliacoes' (SUPRIMENTOS)
        avaliacoes_sup = list(db["avaliacoes"].find({}))
        for avaliacao in avaliacoes_sup:
            if '_id' in avaliacao:
                del avaliacao['_id']
        
        # Buscar avaliações da coleção 'avaliacoes_adm' (ADMINISTRAÇÃO)
        avaliacoes_adm = list(db["avaliacoes_adm"].find({}))
        for avaliacao in avaliacoes_adm:
            if '_id' in avaliacao:
                del avaliacao['_id']
        
        # Criar DataFrames e adicionar origem
        df_sup = pd.DataFrame(avaliacoes_sup)
        df_adm = pd.DataFrame(avaliacoes_adm)
        
        if not df_sup.empty:
            df_sup['Origem'] = 'SUPRIMENTOS'
        if not df_adm.empty:
            df_adm['Origem'] = 'ADMINISTRAÇÃO'
        
        # Combinar os DataFrames
        if not df_sup.empty and not df_adm.empty:
            todas_avaliacoes = pd.concat([df_sup, df_adm], ignore_index=True)
        elif not df_sup.empty:
            todas_avaliacoes = df_sup
        elif not df_adm.empty:
            todas_avaliacoes = df_adm
        else:
            todas_avaliacoes = pd.DataFrame()
        
        return todas_avaliacoes
    except Exception as e:
        st.error(f"Erro ao buscar avaliações: {str(e)}")
        return pd.DataFrame()

# Função para gerar arquivo Excel baseado na avaliação selecionada
def gerar_excel_recuperacao(avaliacao_data, origem):
    try:
        # Criar DataFrame com os dados da avaliação
        df_avaliacao = pd.DataFrame(avaliacao_data)
        
        # Criar arquivo Excel em memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_avaliacao.to_excel(writer, index=False)
        output.seek(0)
        
        return output
    except Exception as e:
        st.error(f"Erro ao gerar arquivo Excel: {str(e)}")
        return None

# Função para fazer upload para o SharePoint
def upload_para_sharepoint(nome_arquivo, origem, arquivo_bytes):
    try:
        # Definir pasta baseada na origem
        if origem == 'SUPRIMENTOS':
            sharepoint_folder = "Avaliacao_Fornecedores/SUP"
        elif origem == 'ADMINISTRAÇÃO':
            sharepoint_folder = "Avaliacao_Fornecedores/ADM"
        else:
            return False, "Origem inválida"
        
        # Fazer upload para o SharePoint
        sp = SharePoint()
        response = sp.upload_file(nome_arquivo, sharepoint_folder, arquivo_bytes)
        
        return True, "Upload realizado com sucesso"
    except Exception as e:
        return False, f"Erro no upload: {str(e)}"

# Criar as abas da interface
tabs = st.tabs(["Backup", "Restauração", "Importação de Dados Locais", "Recuperação de Arquivos"])

# Tab de Backup
with tabs[0]:
    st.header("Backup de Dados do MongoDB")
    st.write("Esta função irá fazer backup de todas as coleções do MongoDB e gerar um arquivo JSON para download.")
    
    if st.button("Gerar Backup", key="backup_button"):
        with st.spinner("Gerando backup..."):
            # Fazer backup de todas as coleções
            backup_data = {
                "fornecedores": backup_collection("fornecedores"),
                "unidades": backup_collection("unidades"),
                "perguntas": backup_collection("perguntas"),
                "avaliacoes": backup_collection("avaliacoes"),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Converter para JSON
            json_data = json.dumps(backup_data, ensure_ascii=False, indent=4)
            
            # Criar link para download
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="Baixar Backup",
                data=json_data,
                file_name=f"backup_mongodb_{timestamp}.json",
                mime="application/json"
            )
            
            st.success("Backup gerado com sucesso!")

# Tab de Restauração
with tabs[1]:
    st.header("Restauração de Backup")
    st.write("Faça upload de um arquivo de backup para restaurar os dados no MongoDB.")
    
    uploaded_file = st.file_uploader("Escolha um arquivo de backup", type="json")
    
    if uploaded_file is not None:
        try:
            # Ler o arquivo JSON
            backup_data = json.load(uploaded_file)
            
            # Mostrar informações do backup
            if "timestamp" in backup_data:
                st.info(f"Backup gerado em: {backup_data['timestamp']}")
            
            # Mostrar resumo das coleções
            st.subheader("Resumo do Backup")
            resumo = {}
            for colecao in backup_data.keys():
                if colecao != "timestamp":
                    resumo[colecao] = len(backup_data[colecao])
            
            df_resumo = pd.DataFrame(list(resumo.items()), columns=["Coleção", "Quantidade de Documentos"])
            st.dataframe(df_resumo)
            
            # Botão para restaurar
            if st.button("Restaurar Backup", key="restore_button"):
                with st.spinner("Restaurando backup..."):
                    success = True
                    for colecao in backup_data.keys():
                        if colecao != "timestamp":
                            if not restore_collection(colecao, backup_data[colecao]):
                                success = False
                    
                    if success:
                        st.success("Backup restaurado com sucesso!")
                    else:
                        st.error("Ocorreram erros durante a restauração do backup.")
        
        except Exception as e:
            st.error(f"Erro ao processar o arquivo de backup: {str(e)}")

# Tab de Importação de Dados Locais
with tabs[2]:
    st.header("Importação de Dados Locais")
    st.write("Esta função irá importar os dados das bibliotecas locais para o MongoDB.")
    st.warning("Atenção: Esta operação irá substituir todos os dados existentes no MongoDB pelas informações das bibliotecas locais.")
    
    if st.button("Importar Dados Locais", key="import_button"):
        with st.spinner("Importando dados locais..."):
            if import_local_data():
                st.success("Dados locais importados com sucesso!")
            else:
                st.error("Ocorreram erros durante a importação dos dados locais.")

# Rodapé
st.markdown("""---
<div style='text-align: center; color: gray; font-size: 12px;'>
    © 2024 Sistema Integrado de Colégios - Todos os direitos reservados
</div>
""", unsafe_allow_html=True)

# Nova aba de Recuperação de Arquivos
with tabs[3]:
    st.header("Recuperação de Arquivos Excel")
    st.write("Esta função permite recriar arquivos Excel a partir de avaliações já realizadas e salvá-los no SharePoint.")
    st.info("💡 **Objetivo:** Recriar arquivos perdidos ou com erros a partir dos dados salvos no banco de dados.")
    
    # Buscar avaliações disponíveis
    with st.spinner("Carregando avaliações disponíveis..."):
        todas_avaliacoes = get_avaliacoes_para_recuperacao()
    
    if todas_avaliacoes.empty:
        st.warning("Nenhuma avaliação encontrada no banco de dados.")
    else:
        # Criar resumo das avaliações únicas
        avaliacoes_unicas = todas_avaliacoes.drop_duplicates(
            subset=['Fornecedor', 'Unidade', 'Período', 'Origem']
        )[['Fornecedor', 'Unidade', 'Período', 'Data_Avaliacao', 'Origem']].copy()
        
        # Ordenar por data mais recente
        if 'Data_Avaliacao' in avaliacoes_unicas.columns:
            avaliacoes_unicas = avaliacoes_unicas.sort_values('Data_Avaliacao', ascending=False)
        
        st.subheader(f"📊 Avaliações Disponíveis ({len(avaliacoes_unicas)} encontradas)")
        
        # Filtros para seleção
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fornecedores_disponiveis = ['Todos'] + sorted(avaliacoes_unicas['Fornecedor'].unique().tolist())
            fornecedor_filtro = st.selectbox("Fornecedor", fornecedores_disponiveis)
        
        with col2:
            unidades_disponiveis = ['Todas'] + sorted(avaliacoes_unicas['Unidade'].unique().tolist())
            unidade_filtro = st.selectbox("Unidade", unidades_disponiveis)
        
        with col3:
            periodos_disponiveis = ['Todos'] + sorted(avaliacoes_unicas['Período'].unique().tolist())
            periodo_filtro = st.selectbox("Período", periodos_disponiveis)
        
        with col4:
            origens_disponiveis = ['Todas'] + sorted(avaliacoes_unicas['Origem'].unique().tolist())
            origem_filtro = st.selectbox("Origem", origens_disponiveis)
        
        # Aplicar filtros
        df_filtrado = avaliacoes_unicas.copy()
        
        if fornecedor_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Fornecedor'] == fornecedor_filtro]
        
        if unidade_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Unidade'] == unidade_filtro]
        
        if periodo_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Período'] == periodo_filtro]
        
        if origem_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['Origem'] == origem_filtro]
        
        # Mostrar avaliações filtradas
        if df_filtrado.empty:
            st.warning("Nenhuma avaliação encontrada com os filtros aplicados.")
        else:
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Seleção da avaliação para recuperação
            st.subheader("🔄 Selecionar Avaliação para Recuperação")
            
            # Criar lista de opções para seleção
            opcoes_avaliacao = []
            for _, row in df_filtrado.iterrows():
                opcao = f"{row['Fornecedor']} - {row['Unidade']} - {row['Período']} - {row['Origem']}"
                opcoes_avaliacao.append(opcao)
            
            avaliacao_selecionada = st.selectbox(
                "Escolha a avaliação para recuperar:",
                options=opcoes_avaliacao,
                index=None,
                placeholder="Selecione uma avaliação..."
            )
            
            if avaliacao_selecionada:
                # Extrair informações da avaliação selecionada
                indice_selecionado = opcoes_avaliacao.index(avaliacao_selecionada)
                avaliacao_info = df_filtrado.iloc[indice_selecionado]
                
                # Mostrar detalhes da avaliação selecionada
                st.info(f"**Avaliação Selecionada:**\n"
                       f"- **Fornecedor:** {avaliacao_info['Fornecedor']}\n"
                       f"- **Unidade:** {avaliacao_info['Unidade']}\n"
                       f"- **Período:** {avaliacao_info['Período']}\n"
                       f"- **Origem:** {avaliacao_info['Origem']}\n"
                       f"- **Data da Avaliação:** {avaliacao_info['Data_Avaliacao']}")
                
                # Botão para gerar e salvar arquivo
                if st.button("🚀 Gerar e Salvar Arquivo Excel", type="primary"):
                    with st.spinner("Processando recuperação do arquivo..."):
                        try:
                            # Buscar dados completos da avaliação
                            filtro_avaliacao = {
                                'Fornecedor': avaliacao_info['Fornecedor'],
                                'Unidade': avaliacao_info['Unidade'],
                                'Período': avaliacao_info['Período']
                            }
                            
                            dados_completos = todas_avaliacoes[
                                (todas_avaliacoes['Fornecedor'] == avaliacao_info['Fornecedor']) &
                                (todas_avaliacoes['Unidade'] == avaliacao_info['Unidade']) &
                                (todas_avaliacoes['Período'] == avaliacao_info['Período']) &
                                (todas_avaliacoes['Origem'] == avaliacao_info['Origem'])
                            ]
                            
                            if dados_completos.empty:
                                st.error("Erro: Dados da avaliação não encontrados.")
                            else:
                                # Gerar nome do arquivo
                                nome_fornecedor = "".join(x for x in avaliacao_info['Fornecedor'].replace(' ', '_') if x.isalnum() or x in ['_', '-'])
                                
                                # Converter período do formato DD/MM/YYYY para MES-YY
                                partes_data = avaliacao_info['Período'].split('/')
                                mes_num = partes_data[1]  # MM
                                ano_abrev = partes_data[2][-2:]  # YY (últimos 2 dígitos)
                                
                                # Dicionário para conversão de mês (adicionar no início do arquivo se não existir)
                                meses_abrev = {
                                    '01': 'JAN', '02': 'FEV', '03': 'MAR', '04': 'ABR',
                                    '05': 'MAI', '06': 'JUN', '07': 'JUL', '08': 'AGO',
                                    '09': 'SET', '10': 'OUT', '11': 'NOV', '12': 'DEZ'
                                }
                                nome_periodo = f"{meses_abrev[mes_num]}-{ano_abrev}"
                                
                                nome_unidade = "".join(x for x in avaliacao_info['Unidade'] if x.isalnum() or x in ['_', '-'])
                                
                                if avaliacao_info['Origem'] == 'SUPRIMENTOS':
                                    nome_arquivo = f'{nome_fornecedor}_{nome_periodo}_{nome_unidade}_SUP.xlsx'
                                else:
                                    nome_arquivo = f'{nome_fornecedor}_{nome_periodo}_{nome_unidade}.xlsx'
                                
                                # Gerar arquivo Excel
                                arquivo_excel = gerar_excel_recuperacao(dados_completos.to_dict('records'), avaliacao_info['Origem'])
                                
                                if arquivo_excel:
                                    # Fazer upload para SharePoint
                                    sucesso, mensagem = upload_para_sharepoint(
                                        nome_arquivo, 
                                        avaliacao_info['Origem'], 
                                        arquivo_excel.getvalue()
                                    )
                                    
                                    if sucesso:
                                        st.success(f"✅ **Arquivo recuperado com sucesso!**\n"
                                                  f"📁 **Arquivo:** {nome_arquivo}\n"
                                                  f"📂 **Pasta:** Avaliacao_Fornecedores/{'SUP' if avaliacao_info['Origem'] == 'SUPRIMENTOS' else 'ADM'}\n"
                                                  f"☁️ **Status:** Salvo no SharePoint")
                                        
                                        # Oferecer download local também
                                        st.download_button(
                                            label="💾 Baixar arquivo localmente (opcional)",
                                            data=arquivo_excel.getvalue(),
                                            file_name=nome_arquivo,
                                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                        )
                                    else:
                                        st.error(f"❌ Erro ao salvar no SharePoint: {mensagem}")
                                        
                                        # Oferecer download local como alternativa
                                        st.warning("💾 Download local disponível como alternativa:")
                                        st.download_button(
                                            label="Baixar arquivo Excel",
                                            data=arquivo_excel.getvalue(),
                                            file_name=nome_arquivo,
                                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                                        )
                                else:
                                    st.error("Erro ao gerar arquivo Excel.")
                        
                        except Exception as e:
                            st.error(f"Erro durante o processo de recuperação: {str(e)}")
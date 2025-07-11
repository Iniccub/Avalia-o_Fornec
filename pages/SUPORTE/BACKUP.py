import streamlit as st
import importlib.util
import sys
import os
import json
import datetime
import pandas as pd
from io import StringIO

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

# Interface do Streamlit
st.title("Backup e Restauração de Dados")

tabs = st.tabs(["Backup", "Restauração", "Importação de Dados Locais"])

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
import streamlit as st
import importlib.util
import sys
import os

# Função para importar módulos dinamicamente
def import_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Obtendo o caminho base do projeto
base_path = os.path.dirname(os.path.dirname(__file__))

# Importar módulos locais com caminhos absolutos
fornecedores_module = import_module('fornecedores_por_unidade', os.path.join(base_path, 'fornecedores_por_unidade.py'))
perguntas_module = import_module('perguntas_por_fornecedor', os.path.join(base_path, 'perguntas_por_fornecedor.py'))

# Acessar os atributos dos módulos
fornecedores_por_unidade = getattr(fornecedores_module, 'fornecedores_por_unidade', {})
perguntas_por_fornecedor = getattr(perguntas_module, 'perguntas_por_fornecedor', {})

st.set_page_config(
    page_title='Gestão - Avaliação de Fornecedores',
    page_icon='CSA.png',
    layout='wide'
)

st.title('Gestão de Cadastros')
st.write('---')

tab1, tab2 = st.tabs(['Fornecedores Cadastrados', 'Perguntas Cadastradas'])

with tab1:
    st.subheader('Lista de Fornecedores')
    
    # Criar uma lista de fornecedores com checkbox
    fornecedores_selecionados = {}
    for fornecedor, unidades in fornecedores_por_unidade.items():
        col1, col2, col3 = st.columns([0.1, 1, 1])
        with col1:
            fornecedores_selecionados[fornecedor] = st.checkbox('', key=f'check_{fornecedor}')
        with col2:
            st.write(f"**{fornecedor}**")
        with col3:
            st.write(f"Unidades: {', '.join(unidades)}")
    
    # Botões de ação
    col1, col2 = st.columns(2)
    with col1:
        if st.button('Excluir Selecionados', key='excluir_fornecedores'):
            selecionados = [f for f, v in fornecedores_selecionados.items() if v]
            if selecionados:
                for fornecedor in selecionados:
                    if fornecedor in fornecedores_por_unidade:
                        del fornecedores_por_unidade[fornecedor]
                
                # Salvar alterações
                fornecedores_path = os.path.join(base_path, 'fornecedores_por_unidade.py')
                with open(fornecedores_path, 'w', encoding='utf-8') as f:
                    f.write('fornecedores_por_unidade = {\n')
                    for forn, units in fornecedores_por_unidade.items():
                        f.write(f"    '{forn}': {units},\n")
                    f.write('}\n')
                st.success('Fornecedores excluídos com sucesso!')
                st.rerun()

with tab2:
    st.subheader('Perguntas por Fornecedor')
    
    # Seletor de fornecedor
    fornecedor_selecionado = st.selectbox('Selecione o fornecedor', options=list(fornecedores_por_unidade.keys()))
    
    if fornecedor_selecionado:
        perguntas_fornecedor = perguntas_por_fornecedor.get(fornecedor_selecionado, {})
        
        # Exibir perguntas por categoria
        for categoria in ['Atividades Operacionais', 'Segurança', 'Qualidade']:
            st.write(f"### {categoria}")
            perguntas = perguntas_fornecedor.get(categoria, [])
            
            perguntas_selecionadas = {}
            for idx, pergunta in enumerate(perguntas):
                col1, col2 = st.columns([0.1, 1])
                with col1:
                    perguntas_selecionadas[f"{categoria}_{idx}"] = st.checkbox('', key=f'check_{categoria}_{idx}')
                with col2:
                    st.write(pergunta)
            
            # Botões de ação por categoria
            col1, col2 = st.columns(2)
            with col1:
                if st.button('Excluir Selecionadas', key=f'excluir_{categoria}'):
                    indices_selecionados = [idx for key, val in perguntas_selecionadas.items() if val and key.startswith(categoria)]
                    if indices_selecionados:
                        # Remover perguntas selecionadas
                        novas_perguntas = [p for i, p in enumerate(perguntas) if i not in indices_selecionados]
                        perguntas_por_fornecedor[fornecedor_selecionado][categoria] = novas_perguntas
                        
                        # Salvar alterações
                        perguntas_path = os.path.join(base_path, 'perguntas_por_fornecedor.py')
                        with open(perguntas_path, 'w', encoding='utf-8') as f:
                            f.write('perguntas_por_fornecedor = {\n')
                            for forn, cats in perguntas_por_fornecedor.items():
                                f.write(f"    '{forn}': {{\n")
                                for cat, pergs in cats.items():
                                    f.write(f"        '{cat}': [\n")
                                    for perg in pergs:
                                        f.write(f"            '{perg}',\n")
                                    f.write("        ],\n")
                                f.write("    },\n")
                            f.write('}\n')
                        st.success('Perguntas excluídas com sucesso!')
                        st.rerun()
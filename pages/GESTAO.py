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
    
    # Criar uma lista de fornecedores com checkbox e botão de edição
    fornecedores_selecionados = {}
    for fornecedor, unidades in fornecedores_por_unidade.items():
        col1, col2, col3, col4 = st.columns([0.1, 1, 1, 0.2])
        with col1:
            fornecedores_selecionados[fornecedor] = st.checkbox('', key=f'check_{fornecedor}')
        with col2:
            st.write(f"**{fornecedor}**")
        with col3:
            st.write(f"Unidades: {', '.join(unidades)}")
        with col4:
            if st.button('📝', key=f'edit_{fornecedor}'):
                st.session_state.editing_fornecedor = fornecedor
                st.session_state.editing_unidades = unidades

    # Interface de edição
    if 'editing_fornecedor' in st.session_state:
        with st.form(key='edit_fornecedor_form'):
            st.subheader(f'Editar Fornecedor: {st.session_state.editing_fornecedor}')
            novo_nome = st.text_input('Novo nome do fornecedor', value=st.session_state.editing_fornecedor)
            # Modificar esta linha
            # Filtrar valores default para garantir que existam nas opções
            # Verificar se editing_unidades existe no session_state
            valores_default_validos = []
            if 'editing_unidades' in st.session_state:
                valores_default_validos = [
                    unidade for unidade in st.session_state.editing_unidades 
                    if unidade in unidades
                ]
            
            novas_unidades = st.multiselect(
                'Unidades', 
                options=unidades, 
                default=valores_default_validos
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button('Salvar Alterações'):
                    # Remover fornecedor antigo
                    del fornecedores_por_unidade[st.session_state.editing_fornecedor]
                    # Adicionar fornecedor com novo nome e unidades
                    fornecedores_por_unidade[novo_nome] = novas_unidades
                    
                    # Salvar alterações
                    fornecedores_path = os.path.join(base_path, 'fornecedores_por_unidade.py')
                    with open(fornecedores_path, 'w', encoding='utf-8') as f:
                        f.write('fornecedores_por_unidade = {\n')
                        for forn, units in fornecedores_por_unidade.items():
                            f.write(f"    '{forn}': {units},\n")
                        f.write('}\n')
                    
                    del st.session_state.editing_fornecedor
                    del st.session_state.editing_unidades
                    st.success('Fornecedor atualizado com sucesso!')
                    st.rerun()
            with col2:
                if st.form_submit_button('Cancelar'):
                    del st.session_state.editing_fornecedor
                    del st.session_state.editing_unidades
                    st.rerun()
    
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
    
    fornecedor_selecionado = st.selectbox('Selecione o fornecedor', options=list(fornecedores_por_unidade.keys()))
    
    if fornecedor_selecionado:
        perguntas_fornecedor = perguntas_por_fornecedor.get(fornecedor_selecionado, {})
        
        for categoria in ['Atividades Operacionais', 'Segurança', 'Documentação', 'Qualidade']:
            st.write(f"### {categoria}")
            perguntas = perguntas_fornecedor.get(categoria, [])
            
            perguntas_selecionadas = {}
            for idx, pergunta in enumerate(perguntas):
                col1, col2, col3 = st.columns([0.1, 1, 0.1])
                with col1:
                    perguntas_selecionadas[f"{categoria}_{idx}"] = st.checkbox('', key=f'check_{categoria}_{idx}')
                with col2:
                    st.write(pergunta)
                with col3:
                    if st.button('📝', key=f'edit_{categoria}_{idx}'):
                        st.session_state.editing_categoria = categoria
                        st.session_state.editing_pergunta_idx = idx
                        st.session_state.editing_pergunta = pergunta

            # Interface de edição de pergunta
            if ('editing_categoria' in st.session_state and 
                'editing_pergunta_idx' in st.session_state and 
                st.session_state.editing_categoria == categoria):
                with st.form(key=f'edit_pergunta_form_{categoria}'):
                    st.subheader(f'Editar Pergunta')
                    nova_pergunta = st.text_area('Nova pergunta', value=st.session_state.editing_pergunta)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button('Salvar Alterações'):
                            # Atualizar a pergunta
                            perguntas_por_fornecedor[fornecedor_selecionado][categoria][st.session_state.editing_pergunta_idx] = nova_pergunta
                            
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
                            
                            del st.session_state.editing_categoria
                            del st.session_state.editing_pergunta_idx
                            del st.session_state.editing_pergunta
                            st.success('Pergunta atualizada com sucesso!')
                            st.rerun()
                    with col2:
                        if st.form_submit_button('Cancelar'):
                            del st.session_state.editing_categoria
                            del st.session_state.editing_pergunta_idx
                            del st.session_state.editing_pergunta
                            st.rerun()

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
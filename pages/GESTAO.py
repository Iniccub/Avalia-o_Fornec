import streamlit as st
import importlib.util
import sys
import os
import zipfile
import tempfile
from io import BytesIO

# Adicionar import para SharePoint
from Office365_api import SharePoint

# Função para importar módulos dinamicamente
def import_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

st.set_page_config(
    page_title='Gestão - Avaliação de Fornecedores',
    page_icon='CSA.png',
    layout='wide'
)

# Obtendo o caminho base do projeto
base_path = os.path.dirname(os.path.dirname(__file__))

# Importar módulos locais com caminhos absolutos
fornecedores_module = import_module('fornecedores_por_unidade', os.path.join(base_path, 'fornecedores_por_unidade.py'))
perguntas_module = import_module('perguntas_por_fornecedor', os.path.join(base_path, 'perguntas_por_fornecedor.py'))
unidades_module = import_module('unidades', os.path.join(base_path, 'unidades.py'))

# Acessar os dados usando as funções MongoDB
try:
    fornecedores_por_unidade = fornecedores_module.get_fornecedores()
    unidades = unidades_module.get_unidades()
except Exception as e:
    st.error(f"Erro ao conectar ao MongoDB: {str(e)}")
    fornecedores_por_unidade = getattr(fornecedores_module, 'fornecedores_por_unidade', {})
    unidades = getattr(unidades_module, 'unidades', [])

try:
    perguntas_por_fornecedor = perguntas_module.get_perguntas()
except Exception as e:
    st.error(f"Erro ao conectar ao MongoDB: {str(e)}")
    perguntas_por_fornecedor = getattr(perguntas_module, 'perguntas_por_fornecedor', {})

# Adicionar função para baixar arquivos do SharePoint
def download_sharepoint_files(folders):
    try:
        # Criar um arquivo ZIP em memória
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            sp = SharePoint()
            
            # Para cada pasta, baixar todos os arquivos
            for folder in folders:
                try:
                    # Obter lista de arquivos na pasta
                    files_list = sp._get_files_list(folder)
                    
                    # Se não houver arquivos, continuar para a próxima pasta
                    if not files_list:
                        continue
                    
                    # Baixar cada arquivo e adicionar ao ZIP
                    for file in files_list:
                        try:
                            # Baixar o arquivo
                            file_content = sp.download_file(file.name, folder)
                            
                            # Adicionar ao ZIP com caminho incluindo a pasta
                            zip_file.writestr(f"{folder}/{file.name}", file_content)
                        except Exception as e:
                            st.warning(f"Erro ao baixar arquivo {file.name}: {str(e)}")
                except Exception as e:
                    st.warning(f"Erro ao listar arquivos na pasta {folder}: {str(e)}")
        
        # Retornar ao início do buffer para leitura
        zip_buffer.seek(0)
        return zip_buffer
    except Exception as e:
        st.error(f"Erro ao criar arquivo ZIP: {str(e)}")
        return None

# Adicionar sidebar com botão para download
st.sidebar.title("Ferramentas")
st.sidebar.markdown("---")

if st.sidebar.button("📥 Baixar Avaliações do SharePoint"):
    with st.sidebar.status("Baixando arquivos do SharePoint...", expanded=True) as status:
        # Pastas a serem baixadas
        folders = ["Avaliacao_Fornecedores/ADM", "Avaliacao_Fornecedores/SUP"]
        
        # Baixar arquivos
        st.sidebar.text("Obtendo arquivos...")
        zip_data = download_sharepoint_files(folders)
        
        if zip_data:
            # Oferecer o ZIP para download
            st.sidebar.download_button(
                label="📥 Baixar Arquivo ZIP",
                data=zip_data,
                file_name="Avaliacoes_Fornecedores.zip",
                mime="application/zip"
            )
            status.update(label="Download concluído!", state="complete")
        else:
            status.update(label="Erro ao baixar arquivos", state="error")

# Adicionar rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
    © 2025 FP&A e Orçamento - Rede Lius
</div>
""", unsafe_allow_html=True)

# Rodapé com copyright
st.markdown("""
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

# Conteúdo principal da página
# Obtendo o caminho base do projeto
base_path = os.path.dirname(os.path.dirname(__file__))

# Importar módulos locais com caminhos absolutos
fornecedores_module = import_module('fornecedores_por_unidade', os.path.join(base_path, 'fornecedores_por_unidade.py'))
perguntas_module = import_module('perguntas_por_fornecedor', os.path.join(base_path, 'perguntas_por_fornecedor.py'))

# Acessar os atributos dos módulos
fornecedores_por_unidade = getattr(fornecedores_module, 'fornecedores_por_unidade', {})
perguntas_por_fornecedor = getattr(perguntas_module, 'perguntas_por_fornecedor', {})

st.title('Gestão de Cadastros')
st.write('---')

tab1, tab2 = st.tabs(['Fornecedores Cadastrados', 'Perguntas Cadastradas'])

with tab1:
    st.subheader('Lista de Fornecedores')
    
    # Ordenar fornecedores alfabeticamente
    fornecedores_ordenados = sorted(fornecedores_por_unidade.items())
    
    # Menu suspenso para filtrar fornecedores
    opcoes_filtro = ['Todos os Fornecedores'] + [f[0] for f in fornecedores_ordenados]
    filtro_selecionado = st.selectbox('🔍 Filtrar fornecedor', opcoes_filtro)
    
    # Filtrar fornecedores baseado na seleção
    fornecedores_filtrados = [
        (fornecedor, unidades) 
        for fornecedor, unidades in fornecedores_ordenados 
        if filtro_selecionado == 'Todos os Fornecedores' or fornecedor == filtro_selecionado
    ]
    
    # Criar uma lista de fornecedores com checkbox e botão de edição
    fornecedores_selecionados = {}
    if not fornecedores_filtrados:
        st.info('Nenhum fornecedor encontrado.')
    else:
        for fornecedor, unidades in fornecedores_filtrados:
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
                    # Aqui está o problema - precisamos extrair o índice numérico da chave
                    indices_selecionados = []
                    for key, val in perguntas_selecionadas.items():
                        if val and key.startswith(f"{categoria}_"):
                            # Extrair o índice da chave (formato: "categoria_idx")
                            try:
                                idx = int(key.split('_')[1])
                                indices_selecionados.append(idx)
                            except (IndexError, ValueError):
                                pass
                    
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
import streamlit as st
import importlib.util
import sys
import os
import zipfile
import tempfile
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime, timedelta

# Adicionar import para SharePoint
from Office365_api import SharePoint

# Cache global para conexão SharePoint
_sharepoint_cache = {
    'connection': None,
    'last_used': None,
    'timeout': 300  # 5 minutos
}

# Lock para thread safety
_cache_lock = threading.Lock()

def get_sharepoint_connection():
    """Obter conexão SharePoint com cache para evitar reconexões desnecessárias"""
    with _cache_lock:
        now = datetime.now()
        
        # Verificar se temos uma conexão válida em cache
        if (_sharepoint_cache['connection'] is not None and 
            _sharepoint_cache['last_used'] is not None and 
            (now - _sharepoint_cache['last_used']).seconds < _sharepoint_cache['timeout']):
            return _sharepoint_cache['connection']
        
        # Criar nova conexão
        try:
            _sharepoint_cache['connection'] = SharePoint()
            _sharepoint_cache['last_used'] = now
            return _sharepoint_cache['connection']
        except Exception as e:
            st.error(f"Erro ao conectar ao SharePoint: {str(e)}")
            return None

def download_single_file(file_info):
    """Download de um único arquivo com tratamento de erro individual"""
    file_obj, folder = file_info
    try:
        sp = get_sharepoint_connection()
        if sp is None:
            return None, f"Erro de conexão para {file_obj.name}"
        
        file_content = sp.download_file(file_obj.name, folder)
        return {
            'name': file_obj.name,
            'folder': folder,
            'content': file_content,
            'size': len(file_content)
        }, None
    except Exception as e:
        return None, f"Erro ao baixar {file_obj.name}: {str(e)}"

def get_files_list_optimized(folders):
    """Obter lista de arquivos de todas as pastas de forma otimizada"""
    all_files = []
    sp = get_sharepoint_connection()
    
    if sp is None:
        return []
    
    for folder in folders:
        try:
            files_list = sp._get_files_list(folder)
            if files_list:
                for file_obj in files_list:
                    all_files.append((file_obj, folder))
        except Exception as e:
            st.warning(f"Erro ao listar arquivos na pasta {folder}: {str(e)}")
    
    return all_files

def download_sharepoint_files_optimized(folders, max_workers=3):
    """Versão otimizada do download com processamento paralelo e indicadores de progresso"""
    try:
        # Obter lista de todos os arquivos primeiro
        st.text("📋 Obtendo lista de arquivos...")
        all_files = get_files_list_optimized(folders)
        
        if not all_files:
            st.warning("Nenhum arquivo encontrado nas pastas especificadas.")
            return None
        
        total_files = len(all_files)
        st.text(f"📁 Encontrados {total_files} arquivos para download")
        
        # Criar arquivo ZIP em memória
        zip_buffer = BytesIO()
        
        # Contadores para progresso
        downloaded_count = 0
        failed_count = 0
        total_size = 0
        
        # Criar barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
            # Download paralelo com ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submeter todas as tarefas
                future_to_file = {executor.submit(download_single_file, file_info): file_info 
                                for file_info in all_files}
                
                # Processar resultados conforme completam
                for future in as_completed(future_to_file):
                    file_info = future_to_file[future]
                    file_obj, folder = file_info
                    
                    try:
                        result, error = future.result(timeout=30)  # Timeout de 30s por arquivo
                        
                        if result:
                            # Adicionar arquivo ao ZIP
                            zip_path = f"{folder.replace('/', '_')}/{result['name']}"
                            zip_file.writestr(zip_path, result['content'])
                            
                            downloaded_count += 1
                            total_size += result['size']
                            
                            # Atualizar progresso
                            progress = downloaded_count / total_files
                            progress_bar.progress(progress)
                            
                            # Formatação do tamanho
                            size_mb = total_size / (1024 * 1024)
                            status_text.text(
                                f"✅ {downloaded_count}/{total_files} arquivos baixados "
                                f"({size_mb:.1f} MB) - {result['name']}"
                            )
                        else:
                            failed_count += 1
                            st.warning(f"⚠️ {error}")
                            
                    except Exception as e:
                        failed_count += 1
                        st.warning(f"⚠️ Timeout ou erro ao processar {file_obj.name}: {str(e)}")
        
        # Finalizar progresso
        progress_bar.progress(1.0)
        
        # Estatísticas finais
        final_size_mb = total_size / (1024 * 1024)
        status_text.text(
            f"🎉 Download concluído! {downloaded_count} arquivos baixados "
            f"({final_size_mb:.1f} MB). {failed_count} falhas."
        )
        
        if downloaded_count == 0:
            st.error("Nenhum arquivo foi baixado com sucesso.")
            return None
        
        # Retornar ao início do buffer
        zip_buffer.seek(0)
        return zip_buffer
        
    except Exception as e:
        st.error(f"Erro crítico ao criar arquivo ZIP: {str(e)}")
        return None

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
    perguntas_por_fornecedor = perguntas_module.get_perguntas()
    
    # Verificar se os dados foram obtidos corretamente
    if not unidades or not fornecedores_por_unidade or not perguntas_por_fornecedor:
        raise Exception("Dados vazios retornados do MongoDB")
        
    # Adicionar mensagem de sucesso
    st.success("Dados carregados com sucesso do MongoDB")
    
except Exception as e:
    # Fallback para os dados originais se houver erro
    st.error(f"Erro ao conectar ao MongoDB: {str(e)}. Usando dados locais como fallback.")
    fornecedores_por_unidade = getattr(fornecedores_module, 'fornecedores_por_unidade', {})
    unidades = getattr(unidades_module, 'unidades', [])
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

# Separador antes do botão de download
st.sidebar.markdown("---")

# Substituir o botão atual por um botão unificado
if st.sidebar.button("📥 Baixar Avaliações do SharePoint"):
    with st.sidebar.status("Preparando download...", expanded=True) as status:
        # Pastas a serem baixadas
        folders = ["Avaliacao_Fornecedores/ADM", "Avaliacao_Fornecedores/SUP"]
        
        # Container para mostrar progresso detalhado
        progress_container = st.sidebar.container()
        
        with progress_container:
            # Baixar arquivos com versão otimizada
            zip_data = download_sharepoint_files_optimized(folders, max_workers=3)
        
        if zip_data:
            # Gerar nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Avaliacoes_Fornecedores_{timestamp}.zip"
            
            # Botão de download
            st.sidebar.download_button(
                label="📥 Baixar Arquivo ZIP",
                data=zip_data.getvalue(),
                file_name=filename,
                mime="application/zip",
                use_container_width=True,
                help=f"Clique para baixar o arquivo ZIP com todas as avaliações"
            )
            
            status.update(
                label="✅ Download preparado! Clique no botão acima para salvar.", 
                state="complete"
            )
            
            # Informações adicionais
            file_size_mb = len(zip_data.getvalue()) / (1024 * 1024)
            st.sidebar.info(f"📊 Tamanho do arquivo: {file_size_mb:.1f} MB")
            
        else:
            status.update(label="❌ Erro ao preparar download", state="error")
            st.sidebar.error("Não foi possível baixar os arquivos. Verifique a conexão com o SharePoint.")

# Adicionar rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
    © 2025 FP&A e Orçamento - Rede Lius
</div>
""", unsafe_allow_html=True)

# Conteúdo principal da página
# Não é necessário reimportar os módulos aqui, pois já foram importados no início do arquivo
# e os dados já foram carregados do MongoDB

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
            
            # Buscar todas as unidades disponíveis do MongoDB
            todas_unidades = unidades_module.get_unidades()
            
            # Usar as unidades do fornecedor que está sendo editado como valores padrão
            valores_default_validos = []
            if 'editing_unidades' in st.session_state:
                valores_default_validos = st.session_state.editing_unidades
            
            novas_unidades = st.multiselect(
                'Unidades', 
                options=todas_unidades, 
                default=valores_default_validos
            )
            
            col1, col2 = st.columns(2)
            with col1:
                # Edição de fornecedor
                if st.form_submit_button('Salvar Alterações'):
                    # Remover fornecedor antigo
                    fornecedores_module.remove_fornecedor(st.session_state.editing_fornecedor)
                    # Adicionar fornecedor com novo nome e unidades
                    fornecedores_module.add_fornecedor(novo_nome, novas_unidades)
                    
                    # Atualizar a variável local para refletir as mudanças
                    fornecedores_por_unidade = fornecedores_module.get_fornecedores()
                    
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
        # Exclusão de fornecedores
        if st.button('Excluir Selecionados', key='excluir_fornecedores'):
            selecionados = [f for f, v in fornecedores_selecionados.items() if v]
            if selecionados:
                for fornecedor in selecionados:
                    fornecedores_module.remove_fornecedor(fornecedor)
                
                # Atualizar a variável local para refletir as mudanças
                fornecedores_por_unidade = fornecedores_module.get_fornecedores()
                
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
                        # Edição de pergunta
                        if st.form_submit_button('Salvar Alterações'):
                            # Atualizar a pergunta no MongoDB
                            success = perguntas_module.update_pergunta(
                                fornecedor_selecionado,
                                categoria,
                                st.session_state.editing_pergunta_idx,
                                nova_pergunta
                            )
                            
                            if success:
                                # Atualizar a variável local para refletir as mudanças
                                perguntas_por_fornecedor = perguntas_module.get_perguntas()
                                
                                del st.session_state.editing_categoria
                                del st.session_state.editing_pergunta_idx
                                del st.session_state.editing_pergunta
                                st.success('Pergunta atualizada com sucesso!')
                                st.rerun()
                            else:
                                st.error('Erro ao atualizar a pergunta. Tente novamente.')
                    with col2:
                        if st.form_submit_button('Cancelar'):
                            del st.session_state.editing_categoria
                            del st.session_state.editing_pergunta_idx
                            del st.session_state.editing_pergunta
                            st.rerun()

            # Botões de ação por categoria
            col1, col2 = st.columns(2)
            with col1:
                # Exclusão de perguntas
                if st.button('Excluir Selecionadas', key=f'excluir_{categoria}'):
                    # Extrair índices selecionados
                    indices_selecionados = []
                    for key, val in perguntas_selecionadas.items():
                        if val and key.startswith(f"{categoria}_"):
                            try:
                                idx = int(key.split('_')[1])
                                indices_selecionados.append(idx)
                            except (IndexError, ValueError):
                                pass
                    
                    if indices_selecionados:
                        # Obter perguntas atuais
                        perguntas = perguntas_por_fornecedor[fornecedor_selecionado][categoria]
                        
                        # Remover cada pergunta selecionada
                        for idx in sorted(indices_selecionados, reverse=True):
                            if 0 <= idx < len(perguntas):
                                pergunta = perguntas[idx]
                                perguntas_module.remove_pergunta(fornecedor_selecionado, categoria, pergunta)
                        
                        # Atualizar a variável local para refletir as mudanças
                        perguntas_por_fornecedor = perguntas_module.get_perguntas()
                        
                        st.success('Perguntas excluídas com sucesso!')
                        st.rerun()

# Adicionar após as importações e antes do conteúdo principal

# Modificar a função salvar_fornecedores para usar MongoDB
def salvar_fornecedores(fornecedor, unidades_selecionadas):
    try:
        # Usar a função do módulo para adicionar/atualizar fornecedor
        success = fornecedores_module.add_fornecedor(fornecedor, unidades_selecionadas)
        if success:
            # Atualizar a variável local
            global fornecedores_por_unidade
            fornecedores_por_unidade = fornecedores_module.get_fornecedores()
            return True
        return False
    except Exception as e:
        st.error(f"Erro ao salvar fornecedor: {str(e)}")
        return False

@st.dialog("Cadastrar Novo Fornecedor", width="large")
def cadastrar_fornecedor():
    st.subheader("Cadastro de Novo Fornecedor")
    novo_fornecedor = st.text_input('Nome do fornecedor', key="cadastro_novo_fornecedor")
    
    # Buscar unidades diretamente do MongoDB usando a função do módulo unidades
    unidades_disponiveis = unidades_module.get_unidades()
    unidades_selecionadas = st.multiselect("Selecione as unidades", options=unidades_disponiveis, key="cadastro_unidades_select")

    if st.button("Salvar", key="cadastro_salvar_fornecedor"):
        novo_fornecedor = novo_fornecedor.strip()
        if novo_fornecedor and unidades_selecionadas:
            if novo_fornecedor not in fornecedores_por_unidade:
                # Salvar o novo fornecedor com suas unidades
                if salvar_fornecedores(novo_fornecedor, unidades_selecionadas):
                    st.toast(f'Fornecedor "{novo_fornecedor}" adicionado com sucesso!', icon='✅')
                else:
                    st.error("Erro ao adicionar fornecedor.")
            else:
                st.warning('Fornecedor já existe na lista')
        else:
            st.warning('Por favor, preencha o nome do fornecedor e selecione pelo menos uma unidade')

@st.dialog("Cadastrar Nova Pergunta", width="large")
def cadastrar_pergunta():
    st.subheader("Cadastro de Nova Pergunta")
    # Obter lista de fornecedores das unidades
    todos_fornecedores = list(fornecedores_por_unidade.keys())
    fornecedor = st.selectbox("Selecione o fornecedor", options=todos_fornecedores, key="dialog_fornecedor_select")
    categoria = st.selectbox('Categoria',('Atividades Operacionais', 'Segurança','Documentação', 'Qualidade'), key="dialog_categoria_select")
    nova_pergunta = st.text_area("Nova pergunta", placeholder="Digite a nova pergunta aqui", key="dialog_nova_pergunta")

    if st.button("Salvar", key="dialog_salvar_pergunta"):
        if fornecedor and categoria and nova_pergunta:
            try:
                # Usar a função do módulo para adicionar pergunta
                success = perguntas_module.add_pergunta(fornecedor, categoria, nova_pergunta)
                if success:
                    # Atualizar a variável local
                    global perguntas_por_fornecedor
                    perguntas_por_fornecedor = perguntas_module.get_perguntas()
                    st.success("Pergunta adicionada com sucesso!")
                else:
                    st.warning("Não foi possível adicionar a pergunta.")
            except Exception as e:
                st.error(f"Erro ao adicionar pergunta: {str(e)}")
        else:
            st.warning("Por favor, preencha todos os campos.")

st.sidebar.write('---')

# Adicionar botões para cadastro
if st.sidebar.button('Cadastrar Novo Fornecedor', key='cadastrar_fornecedor_sidebar'):
    cadastrar_fornecedor()

if st.sidebar.button('Cadastrar Nova Pergunta', key='cadastrar_pergunta_sidebar'):
    cadastrar_pergunta()

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
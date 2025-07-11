# Adicionar imports no início do arquivo (após os imports existentes)
import streamlit as st
import pandas as pd
import os
from openpyxl import load_workbook
from streamlit_js_eval import streamlit_js_eval
from io import BytesIO
import importlib.util
import sys

# Adicionar import para MongoDB e SharePoint
from mongodb_config import get_database
from Office365_api import SharePoint

st.set_page_config(
    page_title='Avaliação de Fornecedores - SUP',
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

# Importar módulos locais
fornecedores_module = import_module('fornecedores_por_unidade', 'fornecedores_por_unidade.py')
unidades_module = import_module('unidades', 'unidades.py')
perguntas_module = import_module('perguntas_por_fornecedor', 'perguntas_por_fornecedor.py')

# Acessar os atributos dos módulos usando as novas funções MongoDB
try:
    # Tentar obter dados do MongoDB
    unidades = unidades_module.get_unidades()
    fornecedores_por_unidade = fornecedores_module.get_fornecedores()
    perguntas_por_fornecedor = perguntas_module.get_perguntas()
    
    # Verificar se os dados foram obtidos corretamente
    if not unidades or not fornecedores_por_unidade or not perguntas_por_fornecedor:
        raise Exception("Dados vazios retornados do MongoDB")
        
    # Adicionar mensagem de sucesso
    st.success("Dados carregados com sucesso do MongoDB")
    
except Exception as e:
    # Fallback para os dados originais se houver erro
    st.error(f"Erro ao conectar com MongoDB: {str(e)}. Usando dados locais como fallback.")
    fornecedores_por_unidade = getattr(fornecedores_module, 'fornecedores_por_unidade', {})
    unidades = getattr(unidades_module, 'unidades', [])
    perguntas_por_fornecedor = getattr(perguntas_module, 'perguntas_por_fornecedor', {})

# Listas fixas
meses_raw = ['31/01/2025', '28/02/2025', '31/03/2025', '30/04/2025', '31/05/2025', '30/06/2025', '31/07/2025', '31/08/2025',
         '30/09/2025', '31/10/2025', '30/11/2025', '31/12/2025']

# Dicionário para converter números de mês em abreviações em português
meses_abrev = {
    '01': 'JAN', '02': 'FEV', '03': 'MAR', '04': 'ABR',
    '05': 'MAI', '06': 'JUN', '07': 'JUL', '08': 'AGO',
    '09': 'SET', '10': 'OUT', '11': 'NOV', '12': 'DEZ'
}

# Formatar os meses para exibição
meses = [f"{meses_abrev[data.split('/')[1]]}/{data.split('/')[2][-2:]}" for data in meses_raw]

# Opções de respostas
opcoes = ['Atende Totalmente', 'Atende Parcialmente', 'Não Atende', 'Não se Aplica']

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
    novo_fornecedor = st.text_input('Nome do fornecedor')
    unidades_selecionadas = st.multiselect("Selecione as unidades", options=unidades)

    if st.button("Salvar"):
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

with st.sidebar:
    st.image("CSA.png", width=150)

# Aplicar estilo CSS para centralizar imagens na sidebar
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] [data-testid="stImage"] {
            display: block;
            margin-left: 70px;
            margin-right: auto;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.write('---')

# Sidebar, Caixas de seleção da unidade, período e fornecedor
unidade = st.sidebar.selectbox('Selecione a unidade', index=None, options=unidades, placeholder='Escolha a unidade')
periodo = st.sidebar.selectbox('Selecione o período avaliado', index=None, options=meses, placeholder='Defina o período de avaliação')

# Filtrar fornecedores baseado na unidade selecionada
if unidade:
    # Obter fornecedores que atendem a unidade selecionada
    fornecedores_filtrados = [
        fornecedor for fornecedor, unidades in fornecedores_por_unidade.items()
        if unidade in unidades
    ]
    fornecedor = st.sidebar.selectbox('Selecione o fornecedor a ser avaliado', 
                                     index=None, 
                                     options=fornecedores_filtrados, 
                                     placeholder='Selecione o prestador/fornecedor')
else:
    fornecedor = st.sidebar.selectbox('Selecione o fornecedor a ser avaliado', 
                                     index=None, 
                                     options=[], 
                                     placeholder='Primeiro selecione uma unidade')

st.sidebar.write('---')

#with st.sidebar:
    # Cadastrar novo fornecedor
    #if st.button('Cadastrar fornecedor'):
        #cadastrar_fornecedor()

# Tela para cadastrar nova pergunta
@st.dialog("Cadastrar Nova Pergunta", width="large")
def cadastrar_pergunta():
    st.subheader("Cadastro de Nova Pergunta")
    # Obter lista de fornecedores das unidades
    todos_fornecedores = list(fornecedores_por_unidade.keys())
    fornecedor = st.selectbox("Selecione o fornecedor", options=todos_fornecedores)
    categoria = st.selectbox('Categoria',('Atividades Operacionais', 'Segurança','Documentação', 'Qualidade'))
    nova_pergunta = st.text_area("Nova pergunta", placeholder="Digite a nova pergunta aqui")

    if st.button("Salvar"):
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

#if st.sidebar.button("Cadastrar nova pergunta"):
    #cadastrar_pergunta()

# Título
st.markdown(
    "<h1 style='text-align: left; font-family: Open Sauce; color: #104D73;'>"
    'ADFS - AVALIAÇÃO DE DESEMPENHO DE FORNECEDORES DE SERVIÇOS</h1>'
    
    'Categoria: Documentação',
    unsafe_allow_html=True
)

st.write('---')

# Subtitulo
if fornecedor and unidade and periodo:
    st.subheader(f'Contratada/Fornecedor: {fornecedor}')
    st.write('Vigência: 02/01/2025 a 31/12/2025')
    st.write(f'Unidade: {unidade}')
    st.write(f'Período avaliado: {periodo}')
    st.write('---')

    # Determinação das abas
    tab1, = st.tabs(['Documentação'])

    respostas = []
    perguntas = []

    # Obter perguntas específicas do fornecedor
    perguntas_fornecedor = perguntas_por_fornecedor.get(fornecedor, {})

    with tab1:
        perguntas_tab1 = perguntas_fornecedor.get('Documentação', [])
        for pergunta in perguntas_tab1:
            resposta = st.selectbox(pergunta, options=opcoes, index=None, placeholder='Selecione uma opção', key=pergunta)
            respostas.append(resposta)
            perguntas.append(pergunta)

    st.sidebar.write('---')

    # Após coletar as perguntas e respostas de cada aba
    categorias = (
            ['Documentação'] * len(perguntas_tab1)
    )

    # Inicialização do estado da sessão
    if 'pesquisa_salva' not in st.session_state:
        st.session_state.pesquisa_salva = False
    if 'df_respostas' not in st.session_state:
        st.session_state.df_respostas = None
    if 'nome_arquivo' not in st.session_state:
        st.session_state.nome_arquivo = ""
    if 'output' not in st.session_state:
        st.session_state.output = None
    
    # Botão 'Salvar pesquisa' modificado
    if st.sidebar.button('Salvar pesquisa'):
        try:
            # Verifica se todas as perguntas foram respondidas
            if None in respostas:
                st.warning('Por favor, responda todas as perguntas antes de salvar.')
            else:
                # Cria DataFrame com as respostas
                df_respostas = pd.DataFrame({
                    'Unidade': unidade,
                    'Período': meses_raw[meses.index(periodo)],  # Obtém a data completa usando o índice do mês abreviado
                    'Fornecedor': fornecedor,
                    'categorias': categorias,
                    'Pergunta': perguntas,
                    'Resposta': respostas,
                    'Data_Avaliacao': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                # Formata o nome do arquivo com base no fornecedor e período
                nome_fornecedor = fornecedor.replace(' ', '_')
                nome_periodo = periodo.replace('/', '-')
                nome_unidade = unidade
                nome_arquivo = f'{nome_fornecedor}_{nome_periodo}_{nome_unidade}_SUP.xlsx'

                # Salvar no MongoDB
                try:
                    db = get_database()
                    collection = db["avaliacoes"]
                    
                    # Converter DataFrame para dicionário e inserir no MongoDB
                    avaliacao_dict = df_respostas.to_dict('records')
                    collection.insert_many(avaliacao_dict)
                    
                    st.success("Avaliação salva com sucesso no MongoDB!")
                except Exception as e:
                    st.error(f"Erro ao salvar no MongoDB: {str(e)}")

                # Salva o DataFrame em um objeto BytesIO para download
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_respostas.to_excel(writer, index=False)
                output.seek(0)
                
                # Salvar na sessão para uso posterior
                st.session_state.pesquisa_salva = True
                st.session_state.df_respostas = df_respostas
                st.session_state.nome_arquivo = nome_arquivo
                st.session_state.output = output
                
                # Recarregar a página para mostrar os botões de download e SharePoint
                st.rerun()
        except Exception as e:
            st.error(f"Erro ao processar respostas: {str(e)}")
    
    # Exibir botões de download e SharePoint após salvar a pesquisa
    if st.session_state.pesquisa_salva:
        # Cria um botão de download no Streamlit
        st.download_button(
            label='Clique aqui para baixar o arquivo Excel com as respostas',
            data=st.session_state.output,
            file_name=st.session_state.nome_arquivo,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Adicionar opção para salvar no SharePoint
        col1, col2 = st.columns(2)
        with col1:
            st.success('Respostas processadas com sucesso! Clique no botão acima para baixar o arquivo.')
        
        with col2:
            if st.button('Salvar no SharePoint'):
                try:
                    # Criar uma cópia do arquivo em memória para o SharePoint
                    output_sharepoint = st.session_state.output.getvalue()
                    
                    # Definir a pasta no SharePoint onde o arquivo será salvo
                    sharepoint_folder = "Avaliacao_Fornecedores/SUP"
                    
                    # Adicionar log para debug
                    st.write(f"Tentando salvar arquivo: {st.session_state.nome_arquivo} na pasta: {sharepoint_folder}")
                    
                    # Fazer upload para o SharePoint
                    sp = SharePoint()
                    response = sp.upload_file(st.session_state.nome_arquivo, sharepoint_folder, output_sharepoint)
                    
                    # Adicionar log para verificar a resposta
                    st.write(f"Resposta do SharePoint: {response}")
                    
                    st.success(f'Arquivo {st.session_state.nome_arquivo} salvo com sucesso no SharePoint!')
                except Exception as e:
                    st.error(f"Erro ao salvar no SharePoint: {str(e)}")
                    # Adicionar informações detalhadas do erro
                    import traceback
                    st.error(traceback.format_exc())
    else:
        st.warning('Por favor, selecione a unidade, o período e o fornecedor para iniciar a avaliação.')

    if st.sidebar.button("Preencher nova pesquisa"):
        streamlit_js_eval(js_expressions='parent.window.location.reload()')

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

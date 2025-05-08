import streamlit as st
import pandas as pd
import os
from openpyxl import load_workbook
from streamlit_js_eval import streamlit_js_eval
from io import BytesIO
import importlib.util
import sys

# Função para importar módulos dinamicamente
def import_module(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Importar módulos locais
fornecedores_module = import_module('fornecedores_por_unidade', 'fornecedores_por_unidade.py')
unidades_module = import_module('unidades', 'unidades.py')
perguntas_module = import_module('perguntas_por_fornecedor', 'perguntas_por_fornecedor.py')

# Acessar os atributos dos módulos
fornecedores_por_unidade = getattr(fornecedores_module, 'fornecedores_por_unidade', {})
unidades = getattr(unidades_module, 'unidades', [])
perguntas_por_fornecedor = getattr(perguntas_module, 'perguntas_por_fornecedor', {})

st.set_page_config(
    page_title='Avaliação de Fornecedores - SUP',
    page_icon='CSA.png',
    layout='wide'
)

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


def carregar_fornecedores():
    if os.path.exists(CAMINHO_FORNECEDORES):
        try:
            from fornecedores import fornecedores
            return fornecedores
        except ImportError:
            return []
    return []

CAMINHO_FORNECEDORES = 'fornecedores_por_unidade.py'

def salvar_fornecedores(fornecedor, unidades_selecionadas):
    try:
        # Tentar carregar o dicionário existente
        with open(CAMINHO_FORNECEDORES, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip():
                # Executar o conteúdo do arquivo para obter o dicionário
                local_dict = {}
                exec(content, {}, local_dict)
                fornecedores_dict = local_dict.get('fornecedores_por_unidade', {})
            else:
                fornecedores_dict = {}
    except FileNotFoundError:
        fornecedores_dict = {}

    # Adicionar novo fornecedor mantendo os existentes
    fornecedores_dict[fornecedor] = unidades_selecionadas

    # Salvar o dicionário atualizado de volta no arquivo
    with open(CAMINHO_FORNECEDORES, 'w', encoding='utf-8') as f:
        f.write('fornecedores_por_unidade = {\n')
        for forn, units in fornecedores_dict.items():
            f.write(f"    '{forn}': {units},\n")
        f.write('}\n')

    # Atualizar o módulo e retornar o dicionário atualizado
    fornecedores_module = import_module('fornecedores_por_unidade', 'fornecedores_por_unidade.py')
    return getattr(fornecedores_module, 'fornecedores_por_unidade', {})

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
                salvar_fornecedores(novo_fornecedor, unidades_selecionadas)
                st.toast(f'Fornecedor "{novo_fornecedor}" adicionado com sucesso!', icon='✅')
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

with st.sidebar:
    # Cadastrar novo fornecedor
    if st.button('Cadastrar fornecedor'):
        cadastrar_fornecedor()

# Tela para cadastrar nova pergunta
@st.dialog("Cadastrar Nova Pergunta", width="large")
def cadastrar_pergunta():
    st.subheader("Cadastro de Nova Pergunta")
    # Obter lista de fornecedores das unidades
    todos_fornecedores = list(fornecedores_por_unidade.keys())
    fornecedor = st.selectbox("Selecione o fornecedor", options=todos_fornecedores)
    categoria = st.selectbox('Categoria',('Documentação'))
    nova_pergunta = st.text_area("Nova pergunta", placeholder="Digite a nova pergunta aqui")

    if st.button("Salvar"):
        if fornecedor and categoria and nova_pergunta:
            # Carregar perguntas existentes
            from perguntas_por_fornecedor import perguntas_por_fornecedor

            # Adicionar nova pergunta
            if fornecedor not in perguntas_por_fornecedor:
                perguntas_por_fornecedor[fornecedor] = {}
            if categoria not in perguntas_por_fornecedor[fornecedor]:
                perguntas_por_fornecedor[fornecedor][categoria] = []
            perguntas_por_fornecedor[fornecedor][categoria].append(nova_pergunta)

            # Salvar de volta no arquivo
            with open('perguntas_por_fornecedor.py', 'w', encoding='utf-8') as f:
                f.write('perguntas_por_fornecedor = {\n')
                for forn, cats in perguntas_por_fornecedor.items():
                    f.write(f"    '{forn}': {{\n")
                    for cat, perguntas in cats.items():
                        f.write(f"        '{cat}': [\n")
                        for pergunta in perguntas:
                            f.write(f"            '{pergunta}',\n")
                        f.write("        ],\n")
                    f.write("    },\n")
                f.write('}\n')
            
            st.success("Pergunta adicionada com sucesso!")
        else:
            st.warning("Por favor, preencha todos os campos.")

if st.sidebar.button("Cadastrar nova pergunta"):
    cadastrar_pergunta()

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
        perguntas_tab1 = perguntas_fornecedor.get('Atividades Operacionais', [])
        for pergunta in perguntas_tab1:
            resposta = st.selectbox(pergunta, options=opcoes, index=None, placeholder='Selecione uma opção', key=pergunta)
            respostas.append(resposta)
            perguntas.append(pergunta)

    st.sidebar.write('---')

    # Após coletar as perguntas e respostas de cada aba
    categorias = (
            ['Documentação'] * len(perguntas_tab1)
    )

    if st.sidebar.button('Salvar pesquisa'):
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
                'Resposta': respostas
            })

            # Formata o nome do arquivo com base no fornecedor e período
            nome_fornecedor = fornecedor.replace(' ', '_')
            nome_periodo = periodo.replace('/', '-')
            nome_unidade = unidade
            nome_arquivo = f'{nome_fornecedor}_{nome_periodo}_{unidade}_SUP.xlsx'

            # Define o caminho completo do arquivo
            caminho_pasta = r'Z:\Administrativo e Suprimentos\GESTÃO DE FORNECEDORES\RESPOSTAS AVALIAÇÕES DE FORNECEDORES'
            caminho_completo = os.path.join(caminho_pasta, nome_arquivo)

            try:
                # Salvar o DataFrame diretamente no arquivo Excel
                df_respostas.to_excel(caminho_completo, index=False)
                st.success(f'Arquivo salvo com sucesso em: {caminho_completo}')
            except Exception as e:
                st.error(f'Erro ao salvar o arquivo: {str(e)}. Verifique se você tem permissão de acesso à pasta de rede.')

            # Salva o DataFrame em um objeto BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_respostas.to_excel(writer, index=False)
            output.seek(0)

            # Cria um botão de download no Streamlit
            #st.download_button(
                #label='Clique aqui para baixar o arquivo Excel com as respostas',
                #data=output,
                #file_name=nome_arquivo,
                #mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            #)

            st.success('Respostas processadas com sucesso! Você pode baixar o arquivo acima')
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

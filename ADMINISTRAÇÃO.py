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
        # Criar backup do arquivo atual
        if os.path.exists(CAMINHO_FORNECEDORES):
            backup_path = f"{CAMINHO_FORNECEDORES}.bak"
            os.replace(CAMINHO_FORNECEDORES, backup_path)
        
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
    
    with st.form("formulario_cadastro_fornecedor"):
        novo_fornecedor = st.text_input('Nome do fornecedor')
        unidades_selecionadas = st.multiselect("Selecione as unidades", options=unidades)
        
        submitted = st.form_submit_button("Salvar")
        
        if submitted:
            novo_fornecedor = novo_fornecedor.strip()
            # Adicionar validações extras
            if len(novo_fornecedor) < 3:
                st.warning("O nome do fornecedor deve ter pelo menos 3 caracteres")
                return
            if not unidades_selecionadas:
                st.warning("Selecione pelo menos uma unidade")
                return
            
            # Resto do código permanece igual
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

#st.sidebar.write('---')
#st.sidebar.write('ATENÇÃO 🤚 Área de uso exclusivo da equipe de Suprimentos')

#with st.sidebar:
    # Cadastrar novo fornecedor
    #if st.button('Cadastrar fornecedor'):
        #cadastrar_fornecedor()

# Tela para cadastrar nova pergunta
@st.dialog("Cadastrar Nova Pergunta", width="large")
def cadastrar_pergunta():
    st.subheader("Cadastro de Nova Pergunta")
    
    # Criar um formulário
    with st.form("formulario_cadastro_pergunta"):
        # Obter lista de fornecedores das unidades
        todos_fornecedores = list(fornecedores_por_unidade.keys())
        fornecedor = st.selectbox("Selecione o fornecedor", options=todos_fornecedores)
        categoria = st.selectbox('Categoria',('Atividades Operacionais', 'Segurança', 'Qualidade'))
        nova_pergunta = st.text_area("Nova pergunta", placeholder="Digite a nova pergunta aqui")
        
        # Botão de submit do formulário
        submitted = st.form_submit_button("Salvar")
        
        if submitted:
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

#if st.sidebar.button("Cadastrar nova pergunta"):
    #cadastrar_pergunta()

# Título
st.markdown(
    "<h1 style='text-align: left; font-family: Open Sauce; color: #104D73;'>"
    'ADFS - AVALIAÇÃO DE DESEMPENHO DE FORNECEDORES DE SERVIÇOS</h1>',
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
    tab1, tab2, tab3 = st.tabs(['Atividades Operacionais', 'Segurança', 'Qualidade'])

    respostas = []
    perguntas = []

    # Obter perguntas específicas do fornecedor
    perguntas_fornecedor = perguntas_por_fornecedor.get(fornecedor, {})

    with tab1:
        perguntas_tab1 = perguntas_fornecedor.get('Atividades Operacionais', [])
        for i, pergunta in enumerate(perguntas_tab1):
            resposta = st.selectbox(pergunta, options=opcoes, index=None, 
                                  placeholder='Selecione uma opção', 
                                  key=f'op_{i}_{pergunta}')
            respostas.append(resposta)
            perguntas.append(pergunta)

    with tab2:
        perguntas_tab2 = perguntas_fornecedor.get('Segurança', [])
        for i, pergunta in enumerate(perguntas_tab2):
            resposta = st.selectbox(pergunta, options=opcoes, index=None, 
                                  placeholder='Selecione uma opção', 
                                  key=f'seg_{i}_{pergunta}')
            respostas.append(resposta)
            perguntas.append(pergunta)

    with tab3:
        perguntas_tab3 = perguntas_fornecedor.get('Qualidade', [])
        for i, pergunta in enumerate(perguntas_tab3):
            resposta = st.selectbox(pergunta, options=opcoes, index=None, 
                                  placeholder='Selecione uma opção', 
                                  key=f'qual_{i}_{pergunta}')
            respostas.append(resposta)
            perguntas.append(pergunta)

    st.sidebar.write('---')

    # Após coletar as perguntas e respostas de cada aba
    categorias = (
            ['Atividades Operacionais'] * len(perguntas_tab1) +
            ['Segurança'] * len(perguntas_tab2) +
            ['Qualidade'] * len(perguntas_tab3)
    )

    if st.sidebar.button('Salvar pesquisa'):
        try:
            if None in respostas:
                st.warning('Por favor, responda todas as perguntas antes de salvar.')
            else:
                # Criar DataFrame com as respostas
                df_respostas = pd.DataFrame({
                    'Unidade': unidade,
                    'Período': meses_raw[meses.index(periodo)],
                    'Fornecedor': fornecedor,
                    'categorias': categorias,
                    'Pergunta': perguntas,
                    'Resposta': respostas,
                    'Data_Avaliacao': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                # Formatar nome do arquivo
                nome_fornecedor = "".join(x for x in fornecedor.replace(' ', '_') if x.isalnum() or x in ['_', '-'])
                nome_periodo = periodo.replace('/', '-')
                nome_unidade = "".join(x for x in unidade if x.isalnum() or x in ['_', '-'])
                nome_arquivo = f'{nome_fornecedor}_{nome_periodo}_{nome_unidade}.xlsx'
                
                # Resto do código permanece igual
                # Salva o DataFrame em um objeto BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_respostas.to_excel(writer, index=False)
                output.seek(0)
                
                # Cria um botão de download no Streamlit que permite escolher onde salvar
                st.download_button(
                    label='Clique aqui para salvar o arquivo Excel com as respostas',
                    data=output,
                    file_name=nome_arquivo,
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                
                st.success('Respostas processadas com sucesso! Clique no botão acima para salvar o arquivo.')
                st.success(r'Caminho da pasta onde salvar o arquivo. Copie o endereço a partir daqui: \\\10.10.0.17\Dados\Administrativo e Suprimentos\GESTÃO DE FORNECEDORES\RESPOSTAS AVALIAÇÕES DE FORNECEDORES')
        except Exception as e:
            st.error(f"Erro ao salvar arquivo: {str(e)}")
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

# Verificar existência dos arquivos necessários
required_files = ['fornecedores_por_unidade.py', 'unidades.py', 'perguntas_por_fornecedor.py']
for file in required_files:
    if not os.path.exists(file):
        st.error(f"Arquivo {file} não encontrado. Por favor, verifique se todos os arquivos necessários estão presentes.")
        st.stop()

import PySimpleGUI as sg
import os

# Caminho para o arquivo fornecedores.py
CAMINHO_ARQUIVO = 'fornecedores.py'

# Função para carregar a lista de fornecedores
def carregar_fornecedores():
    if os.path.exists(CAMINHO_ARQUIVO):
        try:
            from fornecedores import fornecedores
            return fornecedores
        except ImportError:
            return []
    return []

# Função para salvar a lista de fornecedores
def salvar_fornecedores(lista):
    with open(CAMINHO_ARQUIVO, 'w', encoding='utf-8') as f:
        f.write('fornecedores = [\n')
        for item in lista:
            f.write(f"    '{item}',\n")
        f.write(']\n')

# Carrega a lista inicial de fornecedores
fornecedores = carregar_fornecedores()

# Layout da interface
layout = [
    [sg.Text('Novo fornecedor:'), sg.InputText(key='-NOVO-')],
    [sg.Button('Adicionar'), sg.Button('Sair')],
    [sg.Text('Lista de Fornecedores:')],
    [sg.Listbox(values=fornecedores, size=(50, 10), key='-LISTA-')]
]

# Cria a janela
janela = sg.Window('Gerenciador de Fornecedores', layout)

# Loop de eventos
while True:
    evento, valores = janela.read()
    if evento in (sg.WINDOW_CLOSED, 'Sair'):
        break
    elif evento == 'Adicionar':
        novo = valores['-NOVO-'].strip()
        if novo and novo not in fornecedores:
            fornecedores.append(novo)
            salvar_fornecedores(fornecedores)
            janela['-LISTA-'].update(fornecedores)
            janela['-NOVO-'].update('')
        elif novo in fornecedores:
            sg.popup('Fornecedor já existe na lista.')
        else:
            sg.popup('Por favor, insira um nome válido.')

janela.close()
fornecedores_por_unidade = {
    'CANTINA FREITAS': ['CSA-BH'],
    'EXPRESSA TURISMO LTDA': ['CSA-BH', 'CSA-CT', 'CSA-NL', 'CSA-GZ', 'CSA-DV'],
    'ACREDITE EXCURSÕES E EXPOSIÇÕES INTINERANTE LTDA': ['CSA-BH'],
    'LEAL VIAGENS E TURISMO': ['CSA-BH'],
    'MINASCOPY NACIONAL EIRELI': ['CSA-BH', 'CSA-CT', 'CSA-NL', 'CSA-GZ', 'CSA-DV'],
    'OTIMIZA VIGILÂNCIA E SEG. PATRIMONIAL': ['CSA-BH', 'CSA-NL', 'CSA-GZ'],
    'PETRUS LOCACAO E SERVICOS LTDA': ['CSA-CT', 'EPSA', 'CSA-GZ', 'CSA-NL', 'CSA-BH'],
    'REAL VANS LOCAÇÕES': ['CSA-GZ'],
    'AC TRANSPORTES E SERVIÇOS LTDA - ACTUR': ['CSA-BH', 'CSA-CT', 'CSA-GZ', 'CSA-NL', 'EPSA'],
    'TRANSCELO TRANSPORTES LTDA': ['CSA-BH'],
    'AC Transportes e Serviços LTDA': [],
    'GULP SÃO TOMAS': ['EPSA'],
    'NUTRIMIX - EXCELÊNCIA EM ALIMENTAÇÃO': ['CSA-CT'],
    'SALADA & TAL ( PAOLA OLIVEIRA COSTA )ELEVADORES ATLAS SCHINDLER LTDA': ['CSA-NL'],
    'TK ELEVADORES BRASIL LTDA': [],
    'ELEVAÇO LTDA': ['EPSA'],
    'JD CONSERVAÇÃO E SERVIÇOS': ['CSA-GZ'],
    'QA - IT ANSWER - CONSULTORIA - N1': ['SIC SEDE'],
    'QA - IT ANSWER - CONSULTORIA - N2': ['SIC SEDE'],
    'MODERNA TURISMO LTDA': ['CSA-BH', 'CSA-CT', 'CSA-NL', 'CSA-GZ', 'CSA-DV'],
    'XINGU ELEVADORES': [],
    'PHP SERVICE EIRELI': ['ILALI'],
    'CAMPOS DE MINAS SERV. ORG. PROG.TURÍSTICOS': ['CSA-CT', 'CSA-GZ'],
    'ACCESS GESTÃO DE DOCUMENTOS LTDA': ['SIC SEDE'],
    'BOCAINA CIENCIAS NATURAIS & EDUCACAO AMBIENTAL': [],
    'NOVA FORMA VIAGENS E TURISMO': [],
    'CONSERVADORA CIDADE LC': ['SIC SEDE'],
    'CONSERVADORA CIDADE PC': ['SIC SEDE'],
    'OTIS ELEVADORES': [],
    'ELEVADORES ATLAS SCHINDLER': ['CSA-CT', 'CSA-GZ'],
    'FORMA CONHECER CIDADES LTDA': ['CSA-NL']
}

# Adicionar no início do arquivo
from mongodb_config import get_database
import streamlit as st

# Usar cache para melhorar performance
@st.cache_data(ttl=300)  # Cache por 5 minutos
def get_fornecedores():
    db = get_database()
    collection = db["fornecedores"]
    
    # Verificar se já existem fornecedores no banco
    if collection.count_documents({}) == 0:
        # Se não existir, inicializar com os dados padrão
        for fornecedor, unidades in fornecedores_por_unidade.items():
            collection.insert_one({
                "fornecedor": fornecedor,
                "unidades": unidades
            })
    
    # Buscar todos os fornecedores
    result = {}
    for doc in collection.find():
        result[doc["fornecedor"]] = doc["unidades"]
    
    return result

def add_fornecedor(nome, unidades):
    if nome and unidades:
        db = get_database()
        collection = db["fornecedores"]
        
        # Verificar se o fornecedor já existe
        existing = collection.find_one({"fornecedor": nome})
        
        if existing:
            # Atualizar unidades do fornecedor existente
            collection.update_one(
                {"fornecedor": nome},
                {"$set": {"unidades": unidades}}
            )
        else:
            # Adicionar novo fornecedor
            collection.insert_one({
                "fornecedor": nome,
                "unidades": unidades
            })
        return True
    return False

def remove_fornecedor(nome):
    if nome:
        db = get_database()
        collection = db["fornecedores"]
        
        # Remover o fornecedor
        result = collection.delete_one({"fornecedor": nome})
        return result.deleted_count > 0
    return False

def get_fornecedores_por_unidade(unidade):
    db = get_database()
    collection = db["fornecedores"]
    
    # Buscar fornecedores que atendem a unidade específica
    result = collection.find({"unidades": unidade})
    return [doc["fornecedor"] for doc in result]

# Inicializar a coleção se for a primeira execução
if __name__ == "__main__":
    get_fornecedores()

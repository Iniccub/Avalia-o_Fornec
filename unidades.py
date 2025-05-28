from mongodb_config import get_database

# Dados originais (mantidos para compatibilidade)
unidades = [
    'CSA-BH',
    'CSA-CT',
    'CSA-NL',
    'CSA-GZ',
    'CSA-DV',
    'EPSA',
    'ESA',
    'AIACOM',
    'ILALI',
    'ADEODATO',
    'SIC SEDE'
]

# Funções para manipular unidades no MongoDB
def get_unidades():
    db = get_database()
    collection = db["unidades"]
    
    # Verificar se já existem unidades no banco
    if collection.count_documents({}) == 0:
        # Se não existir, inicializar com os dados padrão
        collection.insert_one({"unidades": unidades})
        return unidades
    else:
        # Se existir, retornar as unidades do banco
        result = collection.find_one({})
        return result["unidades"]

def add_unidade(unidade):
    if unidade and unidade not in get_unidades():
        db = get_database()
        collection = db["unidades"]
        
        # Atualizar a lista de unidades
        collection.update_one(
            {}, 
            {"$push": {"unidades": unidade}},
            upsert=True
        )
        return True
    return False

def remove_unidade(unidade):
    if unidade and unidade in get_unidades():
        db = get_database()
        collection = db["unidades"]
        
        # Remover a unidade da lista
        collection.update_one(
            {}, 
            {"$pull": {"unidades": unidade}}
        )
        return True
    return False

# Inicializar a coleção se for a primeira execução
if __name__ == "__main__":
    get_unidades()
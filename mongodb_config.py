# Adicionar cache de conexão
import os
from pymongo import MongoClient
import urllib.parse

# Substitua estas informações pelas suas credenciais do MongoDB Atlas
MONGODB_USERNAME = "felipebuccini"
MONGODB_PASSWORD = "6gxJUBSzHCnGTgGD"
MONGODB_CLUSTER = "cluster0.5vfpfvh.mongodb.net"
MONGODB_DATABASE = "avaliacao_fornecedores"

# Variável global para armazenar a conexão
_mongo_client = None

# Função para obter conexão com o MongoDB Atlas
def get_database():
    global _mongo_client
    
    # Reutilizar conexão existente se disponível
    if _mongo_client is not None:
        return _mongo_client[MONGODB_DATABASE]
        
    username = urllib.parse.quote_plus(MONGODB_USERNAME)
    password = urllib.parse.quote_plus(MONGODB_PASSWORD)
    
    # String de conexão para MongoDB Atlas
    connection_string = f"mongodb+srv://{username}:{password}@{MONGODB_CLUSTER}/{MONGODB_DATABASE}?retryWrites=true&w=majority"
    
    # Criar conexão com o MongoDB
    _mongo_client = MongoClient(connection_string)
    
    # Retornar a base de dados
    return _mongo_client[MONGODB_DATABASE]
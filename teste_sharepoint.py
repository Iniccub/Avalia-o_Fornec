# teste_sharepoint.py
from Office365_api import SharePoint
import io

# Criar um arquivo de teste
test_content = io.BytesIO(b"Teste de upload para SharePoint")

# Fazer upload para o SharePoint
try:
    sp = SharePoint()
    response = sp.upload_file("teste.txt", "Documentos Partilhados", test_content.getvalue())
    print(f"Upload bem-sucedido: {response}")
except Exception as e:
    print(f"Erro: {str(e)}")
    import traceback
    print(traceback.format_exc())
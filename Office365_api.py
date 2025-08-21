
import streamlit as st
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File

# Obtém as credenciais do st.secrets
username = "felipe@redelius.com.br"
password = "FasterDominusKey21*#"
sharepoint_site = "https://csasic.sharepoint.com/sites/DadosControladoria"
sharepoint_site_name = "DadosControladoria"
sharepoint_doc = "Documentos Partilhados"


class SharePoint:
    def _auth(self):
        conn = ClientContext(sharepoint_site).with_credentials(
            UserCredential(
                username,
                password
            )
        )
        return conn

    def _get_files_list(self, folder_name):
        conn = self._auth()
        target_folder_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}'
        root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
        root_folder.expand(['Files', 'Folders']).get().execute_query()
        return root_folder.files

    def download_file(self, file_name, folder_name):
        conn = self._auth()
        # Corrigir o caminho para incluir o nome do arquivo
        file_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}/{file_name}'
        file = File.open_binary(conn, file_url)
        return file.content

    def upload_file(self, file_name, folder_name, content):
        conn = self._auth()
        target_folder_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}'
        target_folder = conn.web.get_folder_by_server_relative_path(target_folder_url)
        response = target_folder.upload_file(file_name, content).execute_query()
        return response

    def delete_file(self, file_name, folder_name):
        """Exclui um arquivo do SharePoint"""
        try:
            conn = self._auth()
            file_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder_name}/{file_name}'
            file = conn.web.get_file_by_server_relative_url(file_url)
            file.delete_object().execute_query()
            return True, f"Arquivo {file_name} excluído com sucesso do SharePoint"
        except Exception as e:
            return False, f"Erro ao excluir arquivo do SharePoint: {str(e)}"

    # Adicionar ao arquivo Office365_api.py
    def get_all_files_batch(self, folders):
        """Obter todos os arquivos de múltiplas pastas em uma operação"""
        conn = self._auth()
        all_files = {}
        
        for folder in folders:
            try:
                target_folder_url = f'/sites/{sharepoint_site_name}/{sharepoint_doc}/{folder}'
                root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
                root_folder.expand(['Files']).get().execute_query()
                all_files[folder] = {file.name: file for file in root_folder.files}
            except Exception as e:
                all_files[folder] = {}
        
        return all_files
    
    def verify_files_batch(self, file_checks):
        """Verificar múltiplos arquivos em uma operação
        
        Args:
            file_checks: Lista de dicts com 'filename' e 'folder'
        
        Returns:
            Dict com status de cada arquivo
        """
        # Agrupar por pasta para otimizar
        folders_to_check = set(check['folder'] for check in file_checks)
        all_files = self.get_all_files_batch(list(folders_to_check))
        
        results = {}
        for check in file_checks:
            folder = check['folder']
            filename = check['filename']
            key = f"{folder}/{filename}"
            
            exists = filename in all_files.get(folder, {})
            results[key] = {
                'exists': exists,
                'filename': filename,
                'folder': folder
            }
        
        return results
                
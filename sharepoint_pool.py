import threading
from datetime import datetime, timedelta
from Office365_api import SharePoint

class SharePointPool:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._connections = {}
                    cls._instance._last_used = {}
                    cls._instance._max_idle_time = 300  # 5 minutos
        return cls._instance
    
    def get_connection(self, connection_id="default"):
        """Obter conexão reutilizável do pool"""
        now = datetime.now()
        
        # Verificar se conexão existe e ainda é válida
        if (connection_id in self._connections and 
            connection_id in self._last_used and
            (now - self._last_used[connection_id]).seconds < self._max_idle_time):
            
            self._last_used[connection_id] = now
            return self._connections[connection_id]
        
        # Criar nova conexão
        try:
            self._connections[connection_id] = SharePoint()
            self._last_used[connection_id] = now
            return self._connections[connection_id]
        except Exception as e:
            return None
    
    def cleanup_expired(self):
        """Limpar conexões expiradas"""
        now = datetime.now()
        expired = []
        
        for conn_id, last_used in self._last_used.items():
            if (now - last_used).seconds > self._max_idle_time:
                expired.append(conn_id)
        
        for conn_id in expired:
            self._connections.pop(conn_id, None)
            self._last_used.pop(conn_id, None)

# Função global para obter conexão
def get_sharepoint():
    return SharePointPool().get_connection()
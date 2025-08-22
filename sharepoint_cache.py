import streamlit as st
import time
from typing import Any, Optional

class SharePointCache:
    def __init__(self, default_ttl=300):  # 5 minutos
        self.default_ttl = default_ttl
        self._initialized = False
    
    def _ensure_initialized(self):
        """Garante que o cache está inicializado no session_state"""
        if not self._initialized:
            if 'sp_cache_data' not in st.session_state:
                st.session_state.sp_cache_data = {}
            if 'sp_cache_timestamps' not in st.session_state:
                st.session_state.sp_cache_timestamps = {}
            self._initialized = True
    
    def get(self, key: str, ttl: Optional[int] = None) -> Any:
        """Obter item do cache se ainda válido"""
        self._ensure_initialized()
        
        if key not in st.session_state.sp_cache_data:
            return None
        
        # Verificar se ainda é válido
        timestamp = st.session_state.sp_cache_timestamps.get(key, 0)
        current_time = time.time()
        cache_ttl = ttl if ttl is not None else self.default_ttl
        
        if current_time - timestamp > cache_ttl:
            # Cache expirado
            self.delete(key)
            return None
        
        return st.session_state.sp_cache_data[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Armazenar item no cache"""
        self._ensure_initialized()
        st.session_state.sp_cache_data[key] = value
        st.session_state.sp_cache_timestamps[key] = time.time()
    
    def delete(self, key: str):
        """Remover item do cache"""
        self._ensure_initialized()
        if key in st.session_state.sp_cache_data:
            del st.session_state.sp_cache_data[key]
        if key in st.session_state.sp_cache_timestamps:
            del st.session_state.sp_cache_timestamps[key]
    
    def clear_expired(self):
        """Limpar itens expirados do cache"""
        self._ensure_initialized()
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in st.session_state.sp_cache_timestamps.items():
            if current_time - timestamp > self.default_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
    
    def get_stats(self):
        """Estatísticas do cache"""
        try:
            self._ensure_initialized()
            return {
                'total_items': len(st.session_state.sp_cache_data),
                'cache_size_mb': len(str(st.session_state.sp_cache_data)) / 1024 / 1024
            }
        except AttributeError:
            # session_state ainda não está disponível
            return {
                'total_items': 0,
                'cache_size_mb': 0.0
            }

# Instância global
cache = SharePointCache()
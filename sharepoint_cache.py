import streamlit as st
import time
from typing import Any, Optional

class SharePointCache:
    def __init__(self, default_ttl=300):  # 5 minutos
        if 'sp_cache_data' not in st.session_state:
            st.session_state.sp_cache_data = {}
        if 'sp_cache_timestamps' not in st.session_state:
            st.session_state.sp_cache_timestamps = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str, ttl: Optional[int] = None) -> Any:
        """Obter item do cache se ainda válido"""
        if key not in st.session_state.sp_cache_data:
            return None
        
        timestamp = st.session_state.sp_cache_timestamps.get(key, 0)
        ttl = ttl or self.default_ttl
        
        if time.time() - timestamp > ttl:
            # Cache expirado
            self.delete(key)
            return None
        
        return st.session_state.sp_cache_data[key]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Armazenar item no cache"""
        st.session_state.sp_cache_data[key] = value
        st.session_state.sp_cache_timestamps[key] = time.time()
    
    def delete(self, key: str):
        """Remover item do cache"""
        st.session_state.sp_cache_data.pop(key, None)
        st.session_state.sp_cache_timestamps.pop(key, None)
    
    def clear_expired(self):
        """Limpar itens expirados"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in st.session_state.sp_cache_timestamps.items():
            if current_time - timestamp > self.default_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
    
    def get_stats(self):
        """Estatísticas do cache"""
        return {
            'total_items': len(st.session_state.sp_cache_data),
            'cache_size_mb': len(str(st.session_state.sp_cache_data)) / 1024 / 1024
        }

# Instância global
cache = SharePointCache()
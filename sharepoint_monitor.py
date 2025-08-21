import time
from collections import deque
from datetime import datetime, timedelta

class SharePointMonitor:
    def __init__(self, max_requests_per_minute=30):
        self.max_requests = max_requests_per_minute
        self.requests = deque()
        self.blocked_until = None
    
    def can_make_request(self):
        """Verificar se pode fazer requisição"""
        now = time.time()
        
        # Verificar se ainda está bloqueado
        if self.blocked_until and now < self.blocked_until:
            return False, f"Bloqueado até {datetime.fromtimestamp(self.blocked_until).strftime('%H:%M:%S')}"
        
        # Limpar requisições antigas (> 1 minuto)
        while self.requests and now - self.requests[0] > 60:
            self.requests.popleft()
        
        # Verificar limite
        if len(self.requests) >= self.max_requests:
            self.blocked_until = now + 60  # Bloquear por 1 minuto
            return False, "Limite de requisições atingido"
        
        return True, "OK"
    
    def record_request(self):
        """Registrar nova requisição"""
        self.requests.append(time.time())
    
    def get_stats(self):
        """Estatísticas de uso"""
        now = time.time()
        recent_requests = sum(1 for req_time in self.requests if now - req_time <= 60)
        
        return {
            'requests_last_minute': recent_requests,
            'requests_remaining': max(0, self.max_requests - recent_requests),
            'blocked': self.blocked_until and now < self.blocked_until
        }

# Instância global
monitor = SharePointMonitor()
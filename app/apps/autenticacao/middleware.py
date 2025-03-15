from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from .models import LogAcesso
from typing import Optional, Callable, Any


class AcessoLogMiddleware(MiddlewareMixin):
    """Middleware para registrar logs de acesso à API."""
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Processa a requisição e gera o log de acesso."""
        response = self.get_response(request)
        
        # Verifica se é uma requisição à API
        if request.path.startswith('/api/'):
            # Obtém o usuário autenticado
            usuario = request.user if request.user.is_authenticated else None
            
            # Registra o log de acesso
            LogAcesso.objects.create(
                usuario=usuario,
                ip=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                endpoint=request.path,
                metodo=request.method,
                status_code=response.status_code
            )
        
        return response
    
    def get_client_ip(self, request: HttpRequest) -> str:
        """Obtém o endereço IP do cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
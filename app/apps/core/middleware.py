from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import PermissionDenied
from typing import Optional, Callable, Any


class EmpresaContextMiddleware(MiddlewareMixin):
    """Middleware para gerenciar o contexto da empresa selecionada."""
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return self.get_response(request)
            
        # Obtém a empresa do contexto (de headers ou sessão)
        empresa_id = self._get_empresa_context(request)
        
        if empresa_id:
            # Verifica permissão de acesso à empresa
            if not self._has_empresa_access(request.user, empresa_id):
                raise PermissionDenied("Acesso negado a esta empresa.")
                
            # Seta o contexto da empresa na requisição
            request.empresa_context = empresa_id
            
        return self.get_response(request)
        
    def _get_empresa_context(self, request: HttpRequest) -> Optional[int]:
        """Obtém o ID da empresa do contexto atual."""
        # Prioriza header X-Empresa
        if request.headers.get('X-Empresa'):
            return int(request.headers.get('X-Empresa'))
            
        # Fallback para sessão
        if hasattr(request, 'session') and 'empresa_context' in request.session:
            return request.session['empresa_context']
            
        # Fallback para empresa principal do usuário
        if request.user.empresa_principal:
            return request.user.empresa_principal.codigo
            
        return None
        
    def _has_empresa_access(self, user, empresa_id: int) -> bool:
        """Verifica se o usuário tem acesso à empresa."""
        # Admins têm acesso a todas as empresas
        if user.tipo_usuario == 'admin':
            return True
            
        # Verifica se a empresa está nas empresas com acesso
        return user.acesso_empresas.filter(codigo=empresa_id).exists()


class TelaPermissaoMiddleware(MiddlewareMixin):
    """Middleware para verificar permissões de acesso às telas."""
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return self.get_response(request)
            
        # Mapeamento de rotas para códigos de tela
        rota_para_tela = {
            '/api/funcionarios': 'funcionarios',
            '/api/absenteismos': 'absenteismos',
            '/api/convocacoes': 'convocacoes',
        }
        
        # Identifica a tela atual pela rota
        path = request.path_info
        tela_codigo = None
        
        for rota, codigo in rota_para_tela.items():
            if path.startswith(rota):
                tela_codigo = codigo
                break
                
        if tela_codigo and not self._has_tela_access(request.user, tela_codigo):
            raise PermissionDenied("Acesso negado a esta funcionalidade.")
            
        return self.get_response(request)
        
    def _has_tela_access(self, user, tela_codigo: str) -> bool:
        """Verifica se o usuário tem acesso à tela."""
        # Admins têm acesso a todas as telas
        if user.tipo_usuario == 'admin':
            return True
            
        # Verifica se a tela está nas telas com acesso
        return user.acesso_telas.filter(codigo=tela_codigo).exists()
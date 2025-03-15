from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Usuario
from .serializers import (
    UsuarioSerializer,
    LoginSerializer,
    AlterarSenhaSerializer
)
from typing import Dict, Any

Usuario = get_user_model()


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de usuários."""
    
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request: Request) -> Response:
        """Endpoint para autenticação de usuários."""
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            empresas = serializer.validated_data['empresas']
            telas = serializer.validated_data['telas']
            
            # Gera os tokens JWT para o usuário
            refresh = RefreshToken.for_user(user)
            
            # Adiciona claims personalizados ao token
            if user.empresa_principal:
                refresh['empresa_default'] = user.empresa_principal.codigo
                
            refresh['tipo_usuario'] = user.tipo_usuario
            
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            
            return Response({
                'status': 'success',
                'message': 'Login realizado com sucesso',
                'data': {
                    'user': UsuarioSerializer(user).data,
                    'tokens': tokens,
                    'empresas': empresas,
                    'telas': telas
                }
            }, status=status.HTTP_200_OK)
            
        except serializers.ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Falha na autenticação',
                'errors': e.detail
            }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def alterar_senha(self, request: Request) -> Response:
        """Endpoint para alteração de senha do usuário autenticado."""
        serializer = AlterarSenhaSerializer(
            data=request.data,
            context={'request': request}
        )
        
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'status': 'success',
                'message': 'Senha alterada com sucesso'
            }, status=status.HTTP_200_OK)
            
        except serializers.ValidationError as e:
            return Response({
                'status': 'error',
                'message': 'Falha ao alterar senha',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request: Request) -> Response:
        """Retorna os dados do usuário autenticado."""
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
        
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def selecionar_empresa(self, request: Request) -> Response:
        """Seleciona uma empresa para o contexto atual."""
        empresa_id = request.data.get('empresa_id')
        
        if not empresa_id:
            return Response({
                'status': 'error',
                'message': 'ID da empresa não fornecido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Verifica se o usuário tem acesso à empresa
        if request.user.tipo_usuario != 'admin' and not request.user.acesso_empresas.filter(codigo=empresa_id).exists():
            return Response({
                'status': 'error',
                'message': 'Acesso negado a esta empresa'
            }, status=status.HTTP_403_FORBIDDEN)
            
        # Atualiza o contexto na sessão
        request.session['empresa_context'] = empresa_id
        
        return Response({
            'status': 'success',
            'message': 'Empresa selecionada com sucesso',
            'data': {'empresa_id': empresa_id}
        })
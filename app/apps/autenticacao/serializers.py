from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Empresa, Tela, AcessoEmpresa, AcessoTela, LogAcesso
from typing import Dict, Any, Optional, List

Usuario = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para o modelo de Usuário."""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'password', 'nome', 'tipo_usuario',
            'is_active', 'ultima_sessao', 'data_cadastro',
            'empresa_principal'
        ]
        read_only_fields = ['id', 'ultima_sessao', 'data_cadastro']
    
    def create(self, validated_data: Dict[str, Any]) -> Usuario:
        """Cria um novo usuário com a senha criptografada."""
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance: Usuario, validated_data: Dict[str, Any]) -> Usuario:
        """Atualiza um usuário existente, criptografando a senha se fornecida."""
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """Serializer para autenticação de usuários."""
    
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Valida as credenciais do usuário."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                msg = 'Credenciais inválidas. Verifique email e senha.'
                raise serializers.ValidationError(msg, code='authorization')
            
            if not user.is_active:
                raise serializers.ValidationError('Usuário desativado.', code='authorization')
            
            # Registra a sessão do usuário
            user.registrar_sessao()
            
            # Obtém empresas disponíveis para o usuário
            if user.tipo_usuario == 'admin':
                empresas = Empresa.objects.filter(ativo=True).values('codigo', 'nome_abreviado')
            else:
                empresas = user.acesso_empresas.filter(ativo=True).values('codigo', 'nome_abreviado')
            
            # Obtém telas disponíveis para o usuário
            if user.tipo_usuario == 'admin':
                telas = Tela.objects.filter(ativa=True).values('codigo', 'nome', 'rota_frontend', 'icone')
            else:
                telas = user.acesso_telas.filter(ativa=True).values('codigo', 'nome', 'rota_frontend', 'icone')
            
            attrs['user'] = user
            attrs['empresas'] = list(empresas)
            attrs['telas'] = list(telas)
            return attrs
        else:
            msg = 'Email e senha são obrigatórios.'
            raise serializers.ValidationError(msg, code='authorization')


class AlterarSenhaSerializer(serializers.Serializer):
    """Serializer para alteração de senha."""
    
    senha_atual = serializers.CharField(required=True)
    senha_nova = serializers.CharField(required=True, validators=[validate_password])
    senha_nova_confirmacao = serializers.CharField(required=True)
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Valida as senhas fornecidas."""
        if attrs['senha_nova'] != attrs['senha_nova_confirmacao']:
            raise serializers.ValidationError(
                {"senha_nova_confirmacao": "As senhas não coincidem."}
            )
            
        return attrs
    
    def validate_senha_atual(self, value: str) -> str:
        """Valida se a senha atual está correta."""
        user = self.context['request'].user
        
        if not user.check_password(value):
            raise serializers.ValidationError("Senha atual incorreta.")
            
        return value
    
    def save(self, **kwargs: Any) -> Usuario:
        """Salva a nova senha do usuário."""
        senha_nova = self.validated_data['senha_nova']
        user = self.context['request'].user
        
        user.set_password(senha_nova)
        user.save()
        
        return user
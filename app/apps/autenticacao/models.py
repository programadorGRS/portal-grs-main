from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from typing import Optional, Any, List


class UsuarioManager(BaseUserManager):
    """Gerenciador personalizado para o modelo de Usuário."""
    
    def create_user(self, email: str, password: str, **extra_fields: Any) -> 'Usuario':
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError('O email é obrigatório')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email: str, password: str, **extra_fields: Any) -> 'Usuario':
        """Cria e salva um superusuário com o email e senha fornecidos."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('tipo_usuario', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário precisa ter is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class Empresa(models.Model):
    """Modelo de Empresa."""
    
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField(blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome']
    
    def __str__(self) -> str:
        return self.nome


class Tela(models.Model):
    """Modelo de Tela do sistema."""
    
    # Identificação
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True, null=True)
    
    # Configurações
    rota_frontend = models.CharField(max_length=200, blank=True, null=True)
    icone = models.CharField(max_length=50, blank=True, null=True)
    ordem = models.IntegerField(default=0)
    
    # Permissões disponíveis
    permissoes_disponiveis = models.JSONField(default=dict)
    
    # Controle
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tela'
        verbose_name_plural = 'Telas'
        ordering = ['ordem', 'nome']
    
    def __str__(self) -> str:
        return self.nome


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo de Usuário Personalizado"""
    
    # Campos de Autenticação
    email = models.EmailField(unique=True, db_index=True)
    
    # Informações Pessoais
    nome = models.CharField(max_length=255)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=[
            ('admin', 'Administrador'),
            ('normal', 'Usuário Normal')
        ],
        default='normal'
    )
    
    # Campos de Controle de Acesso
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Metadados de Sessão
    ultima_sessao = models.DateTimeField(null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    # Relacionamentos
    empresa_principal = models.ForeignKey(
        'Empresa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_principais'
    )
    acesso_empresas = models.ManyToManyField(
        'Empresa',
        through='AcessoEmpresa',
        related_name='usuarios_com_acesso'
    )
    acesso_telas = models.ManyToManyField(
        'Tela',
        through='AcessoTela',
        related_name='usuarios_com_acesso'
    )
    
    # Definições do modelo
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['nome']
    
    def __str__(self) -> str:
        return self.email
    
    def get_full_name(self) -> str:
        return self.nome
    
    def get_short_name(self) -> str:
        return self.nome.split()[0] if self.nome else self.email
    
    def registrar_sessao(self) -> None:
        """Registra o timestamp da última sessão do usuário."""
        self.ultima_sessao = timezone.now()
        self.save(update_fields=['ultima_sessao'])


class AcessoEmpresa(models.Model):
    """Modelo para controlar o acesso de usuários a empresas."""
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    data_concessao = models.DateTimeField(auto_now_add=True)
    concedido_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='acessos_concedidos'
    )
    
    class Meta:
        verbose_name = 'Acesso a Empresa'
        verbose_name_plural = 'Acessos a Empresas'
        unique_together = ('usuario', 'empresa')
    
    def __str__(self) -> str:
        return f"{self.usuario.email} -> {self.empresa.nome}"


class AcessoTela(models.Model):
    """Modelo para controlar o acesso de usuários a telas do sistema."""
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tela = models.ForeignKey(Tela, on_delete=models.CASCADE)
    permissoes = models.JSONField(default=dict)
    data_concessao = models.DateTimeField(auto_now_add=True)
    concedido_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='telas_concedidas'
    )
    
    class Meta:
        verbose_name = 'Acesso a Tela'
        verbose_name_plural = 'Acessos a Telas'
        unique_together = ('usuario', 'tela')
    
    def __str__(self) -> str:
        return f"{self.usuario.email} -> {self.tela.nome}"


class LogAcesso(models.Model):
    """Modelo para registro de auditoria de acessos."""
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='logs_acesso'
    )
    data_hora = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField()
    user_agent = models.TextField()
    endpoint = models.CharField(max_length=255)
    metodo = models.CharField(max_length=10)
    status_code = models.IntegerField()
    
    class Meta:
        verbose_name = 'Log de Acesso'
        verbose_name_plural = 'Logs de Acesso'
        ordering = ['-data_hora']
    
    def __str__(self) -> str:
        return f"{self.usuario.email if self.usuario else 'Anônimo'} - {self.data_hora} - {self.endpoint}"
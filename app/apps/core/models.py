from django.db import models
from django.core.validators import RegexValidator
from typing import List, Tuple, Optional


# Constantes
UF_CHOICES: List[Tuple[str, str]] = [
    ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'),
    ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'),
    ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'),
    ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'),
    ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'),
    ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'),
    ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins'),
]

# Validators
cnpj_validator = RegexValidator(
    regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
    message='CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX'
)

cep_validator = RegexValidator(
    regex=r'^\d{5}-\d{3}$',
    message='CEP deve estar no formato XXXXX-XXX'
)


class Empresa(models.Model):
    """Modelo de Empresa"""
    
    # Identificadores
    codigo = models.BigIntegerField(primary_key=True)
    cnpj = models.CharField(
        max_length=20, 
        unique=True, 
        validators=[cnpj_validator]
    )
    
    # Informações Básicas
    nome_abreviado = models.CharField(max_length=60)
    razao_social = models.CharField(max_length=200)
    
    # Endereço Completo
    endereco = models.CharField(max_length=110)
    numero_endereco = models.CharField(max_length=20)
    complemento_endereco = models.CharField(
        max_length=300, 
        null=True, 
        blank=True
    )
    bairro = models.CharField(max_length=80)
    cidade = models.CharField(max_length=50)
    cep = models.CharField(
        max_length=11, 
        validators=[cep_validator]
    )
    uf = models.CharField(
        max_length=2, 
        choices=UF_CHOICES
    )
    
    # Status e Controle
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nome_abreviado']
    
    def __str__(self) -> str:
        return f"{self.nome_abreviado} ({self.codigo})"

class Funcionario(models.Model):
    """Modelo de Funcionário"""
    
    # Chave Primária e Relacionamento
    codigo = models.BigIntegerField(primary_key=True)
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE,
        related_name='funcionarios'
    )
    
    # Informações Pessoais
    nome = models.CharField(max_length=120)
    cpf = models.CharField(max_length=19, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.IntegerField(
        choices=[(1, 'Masculino'), (2, 'Feminino')],
        null=True, 
        blank=True
    )
    estado_civil = models.IntegerField(
        choices=[
            (1, 'Solteiro(a)'),
            (2, 'Casado(a)'),
            (3, 'Separado(a)'),
            (4, 'Desquitado(a)'),
            (5, 'Viúvo(a)'),
            (6, 'Outros'),
            (7, 'Divorciado(a)')
        ],
        null=True, 
        blank=True
    )
    
    # Informações Profissionais
    matricula_funcionario = models.CharField(
        max_length=30, 
        null=True, 
        blank=True
    )
    data_admissao = models.DateField(null=True, blank=True)
    data_demissao = models.DateField(null=True, blank=True)
    situacao = models.CharField(
        max_length=20, 
        choices=[
            ('ATIVO', 'Ativo'),
            ('INATIVO', 'Inativo'),
            ('FERIAS', 'Férias'),
            ('AFASTADO', 'Afastado')
        ]
    )
    
    # Detalhes Profissionais Adicionais
    codigo_unidade = models.CharField(max_length=20, null=True, blank=True)
    nome_unidade = models.CharField(max_length=130, null=True, blank=True)
    codigo_setor = models.CharField(max_length=12, null=True, blank=True)
    nome_setor = models.CharField(max_length=130, null=True, blank=True)
    codigo_cargo = models.CharField(max_length=10, null=True, blank=True)
    nome_cargo = models.CharField(max_length=130, null=True, blank=True)
    
    # Informações de Contato
    email = models.EmailField(max_length=400, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'
        ordering = ['nome']
        unique_together = ('empresa', 'codigo')
    
    def __str__(self) -> str:
        return f"{self.nome} - {self.empresa.nome_abreviado}"
    
    @property
    def esta_ativo(self) -> bool:
        """Verifica se o funcionário está ativo."""
        return self.situacao == 'ATIVO'

class TipoConvocacao(models.Model):
    """Modelo para tipos de convocação."""
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Tipo de Convocação'
        verbose_name_plural = 'Tipos de Convocação'
        ordering = ['nome']
    
    def __str__(self) -> str:
        return self.nome


class Convocacao(models.Model):
    """Modelo de Convocação de Funcionários."""
    
    # Chaves
    id = models.AutoField(primary_key=True)
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE,
        related_name='convocacoes'
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='convocacoes'
    )
    tipo = models.ForeignKey(
        TipoConvocacao,
        on_delete=models.PROTECT,
        related_name='convocacoes'
    )
    
    # Dados da convocação
    data_convocacao = models.DateField()
    data_limite_resposta = models.DateField()
    respondido = models.BooleanField(default=False)
    data_resposta = models.DateTimeField(null=True, blank=True)
    resposta = models.CharField(
        max_length=20,
        choices=[
            ('ACEITO', 'Aceito'),
            ('RECUSADO', 'Recusado'),
            ('PENDENTE', 'Pendente')
        ],
        default='PENDENTE'
    )
    
    # Metadados
    observacoes = models.TextField(blank=True, null=True)
    criado_por = models.ForeignKey(
        'autenticacao.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='convocacoes_criadas'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Convocação'
        verbose_name_plural = 'Convocações'
        ordering = ['-data_convocacao']
    
    def __str__(self) -> str:
        return f"Convocação {self.id} - {self.funcionario.nome} ({self.data_convocacao})"
    
    @property
    def status_display(self) -> str:
        """Retorna o status formatado para exibição."""
        if not self.respondido:
            return "Aguardando resposta"
        return self.get_resposta_display()

class TipoAbsenteismo(models.Model):
    """Modelo para tipos de absenteísmo."""
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    requer_atestado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Tipo de Absenteísmo'
        verbose_name_plural = 'Tipos de Absenteísmo'
        ordering = ['nome']
    
    def __str__(self) -> str:
        return self.nome


class Absenteismo(models.Model):
    """Modelo de registro de absenteísmo de funcionários."""
    
    # Chaves
    id = models.AutoField(primary_key=True)
    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE,
        related_name='absenteismos'
    )
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='absenteismos'
    )
    tipo = models.ForeignKey(
        TipoAbsenteismo,
        on_delete=models.PROTECT,
        related_name='absenteismos'
    )
    
    # Período
    data_inicio = models.DateField()
    data_fim = models.DateField()
    
    # Detalhes
    justificativa = models.TextField(blank=True, null=True)
    possui_atestado = models.BooleanField(default=False)
    atestado = models.FileField(
        upload_to='atestados/%Y/%m/',
        null=True,
        blank=True
    )
    
    # Metadados
    criado_por = models.ForeignKey(
        'autenticacao.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='absenteismos_registrados'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Absenteísmo'
        verbose_name_plural = 'Absenteísmos'
        ordering = ['-data_inicio']
    
    def __str__(self) -> str:
        return f"{self.funcionario.nome} - {self.tipo.nome} ({self.data_inicio} a {self.data_fim})"
    
    @property
    def dias_absenteismo(self) -> int:
        """Calcula a quantidade de dias de absenteísmo."""
        return (self.data_fim - self.data_inicio).days + 1
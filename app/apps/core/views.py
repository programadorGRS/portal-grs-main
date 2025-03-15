from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Empresa, Funcionario, 
    TipoConvocacao, Convocacao,
    TipoAbsenteismo, Absenteismo
)
from .serializers import (
    EmpresaSerializer, FuncionarioSerializer,
    TipoConvocacaoSerializer, ConvocacaoSerializer,
    TipoAbsenteismoSerializer, AbsenteismoSerializer
)


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['codigo', 'cnpj', 'ativo']
    search_fields = ['nome_abreviado', 'razao_social', 'cnpj']
    ordering_fields = ['nome_abreviado', 'razao_social', 'criado_em']


class FuncionarioViewSet(viewsets.ModelViewSet):
    queryset = Funcionario.objects.all()
    serializer_class = FuncionarioSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'situacao', 'codigo_unidade', 'codigo_setor']
    search_fields = ['nome', 'cpf', 'matricula_funcionario', 'email']
    ordering_fields = ['nome', 'data_admissao', 'empresa']

    @action(detail=False, methods=['get'])
    def metricas(self, request: Request) -> Response:
        """Retorna métricas dos funcionários da empresa em contexto."""
        empresa_id = getattr(request, 'empresa_context', None)
        if not empresa_id:
            return Response({
                'status': 'error',
                'message': 'Contexto de empresa não definido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        metricas = FuncionarioService.obter_metricas(empresa_id)
        
        return Response({
            'status': 'success',
            'data': metricas
        })
        
    @action(detail=False, methods=['get'])
    def exportar(self, request: Request) -> HttpResponse:
        """Exporta dados de funcionários para CSV."""
        empresa_id = getattr(request, 'empresa_context', None)
        if not empresa_id:
            return Response({
                'status': 'error',
                'message': 'Contexto de empresa não definido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Filtrar funcionários da empresa
        queryset = self.get_queryset().filter(empresa__codigo=empresa_id)
        
        # Aplicar filtros adicionais
        for param, value in request.query_params.items():
            if param in ['situacao', 'codigo_unidade', 'codigo_setor', 'codigo_cargo']:
                queryset = queryset.filter(**{param: value})
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="funcionarios.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Código', 'Nome', 'CPF', 'Matrícula', 'Situação', 'Unidade', 'Setor', 'Cargo'])
        
        for funcionario in queryset:
            writer.writerow([
                funcionario.codigo,
                funcionario.nome,
                funcionario.cpf,
                funcionario.matricula_funcionario,
                funcionario.situacao,
                funcionario.nome_unidade,
                funcionario.nome_setor,
                funcionario.nome_cargo
            ])
        
        return response


class TipoConvocacaoViewSet(viewsets.ModelViewSet):
    queryset = TipoConvocacao.objects.all()
    serializer_class = TipoConvocacaoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome']


class ConvocacaoViewSet(viewsets.ModelViewSet):
    queryset = Convocacao.objects.all()
    serializer_class = ConvocacaoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'funcionario', 'tipo', 'respondido', 'resposta']
    search_fields = ['funcionario__nome', 'observacoes']
    ordering_fields = ['data_convocacao', 'data_limite_resposta', 'data_resposta']

    @action(detail=False, methods=['get'])
    def metricas(self, request: Request) -> Response:
        """Retorna métricas de convocações da empresa em contexto."""
        empresa_id = getattr(request, 'empresa_context', None)
        if not empresa_id:
            return Response({
                'status': 'error',
                'message': 'Contexto de empresa não definido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        metricas = ConvocacaoService.obter_metricas(empresa_id)
        
        return Response({
            'status': 'success',
            'data': metricas
        })
        
    @action(detail=False, methods=['get'])
    def exportar(self, request: Request) -> HttpResponse:
        """Exporta dados de convocações para CSV."""
        empresa_id = getattr(request, 'empresa_context', None)
        if not empresa_id:
            return Response({
                'status': 'error',
                'message': 'Contexto de empresa não definido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Filtrar convocações da empresa
        queryset = self.get_queryset().filter(empresa__codigo=empresa_id)
        
        # Aplicar filtros adicionais
        for param, value in request.query_params.items():
            if param in ['tipo', 'respondido', 'resposta']:
                queryset = queryset.filter(**{param: value})
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="convocacoes.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Funcionário', 'Tipo', 'Data Convocação', 'Data Limite', 'Status', 'Resposta'])
        
        for conv in queryset:
            writer.writerow([
                conv.id,
                conv.funcionario.nome,
                conv.tipo.nome,
                conv.data_convocacao,
                conv.data_limite_resposta,
                'Respondido' if conv.respondido else 'Pendente',
                conv.get_resposta_display()
            ])
        
        return response


class TipoAbsenteismoViewSet(viewsets.ModelViewSet):
    queryset = TipoAbsenteismo.objects.all()
    serializer_class = TipoAbsenteismoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome']


class AbsenteismoViewSet(viewsets.ModelViewSet):
    queryset = Absenteismo.objects.all()
    serializer_class = AbsenteismoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'funcionario', 'tipo', 'possui_atestado']
    search_fields = ['funcionario__nome', 'justificativa']
    ordering_fields = ['data_inicio', 'data_fim']

    @action(detail=False, methods=['get'])
    def metricas(self, request: Request) -> Response:
        """Retorna métricas de absenteísmo da empresa em contexto."""
        empresa_id = getattr(request, 'empresa_context', None)
        if not empresa_id:
            return Response({
                'status': 'error',
                'message': 'Contexto de empresa não definido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Parâmetros de filtro
        periodo_inicio = request.query_params.get('periodo_inicio')
        periodo_fim = request.query_params.get('periodo_fim')
            
        metricas = AbsenteismoService.obter_metricas(
            empresa_id, 
            periodo_inicio, 
            periodo_fim
        )
        
        return Response({
            'status': 'success',
            'data': metricas
        })
        
    @action(detail=False, methods=['get'])
    def exportar(self, request: Request) -> HttpResponse:
        """Exporta dados de absenteísmo para CSV."""
        empresa_id = getattr(request, 'empresa_context', None)
        if not empresa_id:
            return Response({
                'status': 'error',
                'message': 'Contexto de empresa não definido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Filtrar absenteísmos da empresa
        queryset = self.get_queryset().filter(empresa__codigo=empresa_id)
        
        # Aplicar filtros adicionais
        for param, value in request.query_params.items():
            if param in ['tipo', 'possui_atestado']:
                queryset = queryset.filter(**{param: value})
                
        if 'periodo_inicio' in request.query_params:
            queryset = queryset.filter(data_inicio__gte=request.query_params['periodo_inicio'])
            
        if 'periodo_fim' in request.query_params:
            queryset = queryset.filter(data_fim__lte=request.query_params['periodo_fim'])
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="absenteismos.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Funcionário', 'Tipo', 'Data Início', 'Data Fim', 'Dias', 'Atestado'])
        
        for abs in queryset:
            writer.writerow([
                abs.id,
                abs.funcionario.nome,
                abs.tipo.nome,
                abs.data_inicio,
                abs.data_fim,
                abs.dias_absenteismo,
                'Sim' if abs.possui_atestado else 'Não'
            ])
        
        return response
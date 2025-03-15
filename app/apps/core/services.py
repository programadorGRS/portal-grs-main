from django.db.models import Count, Q, Sum, Avg, F, Value
from django.db.models.functions import Coalesce
from .models import Funcionario, Absenteismo, Convocacao
from typing import Dict, Any, List


class FuncionarioService:
    """Serviço para métricas e operações relacionadas a funcionários."""
    
    @staticmethod
    def obter_metricas(empresa_id: int) -> Dict[str, Any]:
        """Retorna métricas gerais de funcionários da empresa."""
        
        # Contagem total de funcionários
        total = Funcionario.objects.filter(empresa__codigo=empresa_id).count()
        
        # Distribuição por situação
        situacao = Funcionario.objects.filter(
            empresa__codigo=empresa_id
        ).values('situacao').annotate(
            total=Count('id')
        ).order_by('situacao')
        
        # Distribuição por unidade
        unidades = Funcionario.objects.filter(
            empresa__codigo=empresa_id
        ).values('codigo_unidade', 'nome_unidade').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Distribuição por setor
        setores = Funcionario.objects.filter(
            empresa__codigo=empresa_id
        ).values('codigo_setor', 'nome_setor').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        # Distribuição por cargo
        cargos = Funcionario.objects.filter(
            empresa__codigo=empresa_id
        ).values('codigo_cargo', 'nome_cargo').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        return {
            'total_funcionarios': total,
            'distribuicao_situacao': list(situacao),
            'distribuicao_unidades': list(unidades),
            'distribuicao_setores': list(setores),
            'distribuicao_cargos': list(cargos)
        }

class AbsenteismoService:
    """Serviço para métricas e operações relacionadas a absenteísmo."""
    
    @staticmethod
    def obter_metricas(empresa_id: int, periodo_inicio=None, periodo_fim=None) -> Dict[str, Any]:
        """Retorna métricas gerais de absenteísmo da empresa."""
        
        # Filtragem por período
        queryset = Absenteismo.objects.filter(empresa__codigo=empresa_id)
        
        if periodo_inicio:
            queryset = queryset.filter(data_inicio__gte=periodo_inicio)
        if periodo_fim:
            queryset = queryset.filter(data_fim__lte=periodo_fim)
        
        # Total de registros
        total_registros = queryset.count()
        
        # Total de dias
        total_dias = queryset.aggregate(
            total=Sum(F('data_fim') - F('data_inicio') + Value(1))
        )['total'] or 0
        
        # Média de dias
        media_dias = queryset.aggregate(
            media=Avg(F('data_fim') - F('data_inicio') + Value(1))
        )['media'] or 0
        
        # Número de funcionários afastados
        funcionarios_afastados = queryset.values('funcionario').distinct().count()
        
        # Total de funcionários ativos para cálculo do índice
        total_funcionarios = Funcionario.objects.filter(
            empresa__codigo=empresa_id, 
            situacao='ATIVO'
        ).count()
        
        # Índice de absenteísmo (dias de afastamento / (dias do período * total de funcionários))
        if total_funcionarios > 0:
            periodo_dias = 30  # Valor padrão
            indice_absenteismo = (total_dias / (periodo_dias * total_funcionarios)) * 100
        else:
            indice_absenteismo = 0
        
        # Distribuição por tipo
        tipos = queryset.values('tipo__nome').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Absenteísmo por setor
        setores = queryset.values(
            'funcionario__codigo_setor', 
            'funcionario__nome_setor'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        
        # Funcionários com maior frequência de absenteísmo
        top_funcionarios = queryset.values(
            'funcionario__nome', 
            'funcionario__codigo'
        ).annotate(
            total=Count('id')
        ).order_by('-total')[:5]
        
        return {
            'total_registros': total_registros,
            'total_dias_afastamento': total_dias,
            'media_dias_por_atestado': round(media_dias, 2) if media_dias else 0,
            'funcionarios_afastados': funcionarios_afastados,
            'indice_absenteismo': round(indice_absenteismo, 2),
            'distribuicao_por_tipo': list(tipos),
            'absenteismo_por_setor': list(setores),
            'top_funcionarios': list(top_funcionarios)
        }

class ConvocacaoService:
    """Serviço para métricas e operações relacionadas a convocações."""
    
    @staticmethod
    def obter_metricas(empresa_id: int) -> Dict[str, Any]:
        """Retorna métricas gerais de convocações da empresa."""
        
        # Base queryset
        queryset = Convocacao.objects.filter(empresa__codigo=empresa_id)
        
        # Total de exames vencidos (respondidos após a data limite)
        exames_vencidos = queryset.filter(
            data_resposta__gt=F('data_limite_resposta'),
            respondido=True
        ).count()
        
        # Total de exames pendentes (ainda não respondidos)
        exames_pendentes = queryset.filter(
            respondido=False
        ).count()
        
        # Total de exames a vencer (prazo próximo)
        from datetime import date, timedelta
        prazo_futuro = date.today() + timedelta(days=30)
        
        exames_a_vencer = queryset.filter(
            respondido=False,
            data_limite_resposta__gte=date.today(),
            data_limite_resposta__lte=prazo_futuro
        ).count()
        
        # Total de exames em dia (respondidos dentro do prazo)
        exames_em_dia = queryset.filter(
            respondido=True,
            data_resposta__lte=F('data_limite_resposta')
        ).count()
        
        # Distribuição por status
        status_distribuicao = [
            {'status': 'Vencidos', 'total': exames_vencidos},
            {'status': 'Pendentes', 'total': exames_pendentes},
            {'status': 'A Vencer', 'total': exames_a_vencer},
            {'status': 'Em Dia', 'total': exames_em_dia}
        ]
        
        # Distribuição por unidade
        unidades = queryset.values(
            'funcionario__codigo_unidade', 
            'funcionario__nome_unidade'
        ).annotate(
            pendentes=Count('id', filter=Q(respondido=False)),
            em_dia=Count('id', filter=Q(respondido=True, data_resposta__lte=F('data_limite_resposta'))),
            vencidos=Count('id', filter=Q(respondido=True, data_resposta__gt=F('data_limite_resposta')))
        ).order_by('funcionario__nome_unidade')
        
        return {
            'total_exames_vencidos': exames_vencidos,
            'total_exames_pendentes': exames_pendentes,
            'total_exames_a_vencer': exames_a_vencer,
            'total_exames_em_dia': exames_em_dia,
            'distribuicao_por_status': status_distribuicao,
            'distribuicao_por_unidade': list(unidades)
        }
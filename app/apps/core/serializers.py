from rest_framework import serializers
from .models import (
    Empresa, Funcionario, 
    TipoConvocacao, Convocacao,
    TipoAbsenteismo, Absenteismo
)


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'


class FuncionarioSerializer(serializers.ModelSerializer):
    empresa_nome = serializers.StringRelatedField(source='empresa.nome_abreviado', read_only=True)
    
    class Meta:
        model = Funcionario
        fields = '__all__'


class TipoConvocacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoConvocacao
        fields = '__all__'


class ConvocacaoSerializer(serializers.ModelSerializer):
    funcionario_nome = serializers.StringRelatedField(source='funcionario.nome', read_only=True)
    tipo_nome = serializers.StringRelatedField(source='tipo.nome', read_only=True)
    empresa_nome = serializers.StringRelatedField(source='empresa.nome_abreviado', read_only=True)
    
    class Meta:
        model = Convocacao
        fields = '__all__'


class TipoAbsenteismoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAbsenteismo
        fields = '__all__'


class AbsenteismoSerializer(serializers.ModelSerializer):
    funcionario_nome = serializers.StringRelatedField(source='funcionario.nome', read_only=True)
    tipo_nome = serializers.StringRelatedField(source='tipo.nome', read_only=True)
    empresa_nome = serializers.StringRelatedField(source='empresa.nome_abreviado', read_only=True)
    
    class Meta:
        model = Absenteismo
        fields = '__all__'
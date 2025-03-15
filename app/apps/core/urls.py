from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('empresas', views.EmpresaViewSet)
router.register('funcionarios', views.FuncionarioViewSet)
router.register('tipos-convocacao', views.TipoConvocacaoViewSet)
router.register('convocacoes', views.ConvocacaoViewSet)
router.register('tipos-absenteismo', views.TipoAbsenteismoViewSet)
router.register('absenteismos', views.AbsenteismoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
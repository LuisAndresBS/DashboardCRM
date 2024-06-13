from django.urls import path
from .views import calculate_kpi, test_db, test_products, kpi_dashboard, fetch_kpis

urlpatterns = [
    path('test-db/', test_db, name='test_db'),
    path('test-products/', test_products, name='test_products'),
    path('calculate-kpi/', calculate_kpi, name='calculate_kpi'),
    path('kpi-dashboard/', kpi_dashboard, name='kpi_dashboard'),
    path('fetch-kpis/', fetch_kpis, name='fetch_kpis'),
]
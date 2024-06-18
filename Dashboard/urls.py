from django.urls import path
from .controllers import calculate_kpi, kpi_dashboard, fetch_kpis, get_lead_status_distribution, get_average_worth_transaction
# from .controllers.kpi_leads_acomplished import get_lead_status_distribution

urlpatterns = [
    path('calculate-kpi/', calculate_kpi, name='calculate_kpi'),
    path('kpi-dashboard/', kpi_dashboard, name='kpi_dashboard'),
    path('fetch-kpis/', fetch_kpis, name='fetch_kpis'),
    path('get-lead-status-distribution/', get_lead_status_distribution, name='get-lead-status-distribution'),
    path('get-average-worth-transaction/', get_average_worth_transaction, name='get-average-worth-transaction'),
]
from django.shortcuts import render
from django.http import JsonResponse
from .models import Contact, Product, SaleDetail, User, Lead
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def calculate_kpi(request):
    # Obtener parámetros de fecha desde la solicitud
    start_date_str = request.GET.get('start_date', None)
    end_date_str = request.GET.get('end_date', None)

    # Convertir las cadenas de fecha a objetos datetime
    try:
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS'}, status=400)

    # Crear el filtro de fecha
    date_filter = {}
    date_filter_prev = {}
    if start_date:
        date_filter['invoiceDate__gte'] = start_date
        date_filter_prev['invoiceDate__gte'] = start_date - relativedelta(months=1)
    if end_date:
        date_filter['invoiceDate__lte'] = end_date
        date_filter_prev['invoiceDate__lte'] = end_date - relativedelta(months=1)

    # Realizar consultas en la base de datos
    sales = SaleDetail.objects(**date_filter)  # Aplicar el filtro de fecha
    salesprev = SaleDetail.objects(**date_filter_prev)

    # Obtener la cantidad de contactId únicos en el rango de fecha actual
    unique_contact_ids = SaleDetail.objects(**date_filter).distinct('contactId')
    unique_contact_ids_prev = SaleDetail.objects(**date_filter_prev).distinct('contactId')
    unique_contact_count = len(unique_contact_ids)
    unique_contact_count_prev = len(unique_contact_ids_prev)

    # Convertir ambas listas a conjuntos y encontrar la intersección
    current_set = set(unique_contact_ids)
    prev_set = set(unique_contact_ids_prev)
    common_contact_ids = current_set.intersection(prev_set)
    common_contact_ids_count = len(common_contact_ids)
    # print('cantidad contactos inter= ', common_contact_ids_count)

    # cálculo del KPI tasa de retencion de clientes, mide el porcentaje de clientes que 
    # volvieron a realizar una compra luego de realizar una en el mes pasado 
    tasa_retencion_clientes = (common_contact_ids_count / unique_contact_count_prev) * 100

    kpi_result = {
        'start_date': start_date_str,
        'end_date': end_date_str,
        'tasa_retencion_clientes': tasa_retencion_clientes,
    }
    # print('kpi respuesta: ', kpi_result)

    return JsonResponse(kpi_result)

def kpi_dashboard(request):
    latest_sale = SaleDetail.objects.order_by('-invoiceDate').first()
    
    if latest_sale:
        latest_date = latest_sale.invoiceDate
        default_start_date = latest_date.replace(day=1).isoformat()[:10]  # Primer día del mes
        next_month = latest_date.replace(day=28) + timedelta(days=4)  # Garantizar pasar al próximo mes
        default_end_date = (next_month - timedelta(days=next_month.day)).isoformat()[:10]  # Último día del mes
    else:
        default_start_date = '2022-01-01'
        default_end_date = '2022-01-31'
    return render(request, 'dashboard.html', {
        'default_start_date': default_start_date,
        'default_end_date': default_end_date
    })

def fetch_kpis(request):
    date_ranges = [
        ('2011-01-01T00:00:00', '2011-01-31T23:59:59'),
        ('2011-02-01T00:00:00', '2011-02-28T23:59:59'),
        ('2011-03-01T00:00:00', '2011-03-31T23:59:59'),
        ('2011-04-01T00:00:00', '2011-04-30T23:59:59'),
        ('2011-05-01T00:00:00', '2011-05-31T23:59:59'),
    ]
    kpi_results = []

    for start_date, end_date in date_ranges:
        response = calculate_kpi(request, start_date, end_date)
        print('response calular kpi: ', response)
        kpi_results.append(response.json())

    return JsonResponse(kpi_results, safe=False)

def get_lead_status_distribution(request):
    start_date_str = request.GET.get('start_date', None)
    end_date_str = request.GET.get('end_date', None)

    try:
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS'}, status=400)

    if not start_date or not end_date:
        return JsonResponse({'error': 'Missing start_date or end_date'}, status=400)

    # Realizar la agregación para contar los estados
    pipeline = [
        {"$match": {"createdAt": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]

    result = Lead.objects.aggregate(pipeline)
    
    # Convertir el resultado a un diccionario
    status_counts = {item['_id']: item['count'] for item in result}
    total_leads = sum(status_counts.values())

    # Calcular los porcentajes
    status_percentages = {status: (count / total_leads) * 100 for status, count in status_counts.items()}

    return JsonResponse(status_percentages)

def get_average_worth_transaction(request):
    start_date_str = request.GET.get('start_date', None)
    end_date_str = request.GET.get('end_date', None)

    try:
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use ISO format: YYYY-MM-DDTHH:MM:SS'}, status=400)

    if not start_date or not end_date:
        return JsonResponse({'error': 'Missing start_date or end_date'}, status=400)

    # Realizar la agrupacion de detalles por venta, y calcula su valor total
    pipeline = [
        {"$match": {"invoiceDate": {"$gte": start_date, "$lte": end_date}}},
        {"$group": {
            "_id": "$contactId",
            "totalAmount": {"$sum": {"$multiply": ["$unitPrice", "$quantity"]}}
        }}
    ]

    result = SaleDetail.objects.aggregate(pipeline)
    
    # Convertir el resultado a un diccionario
    client_totals = {item['_id']: item['totalAmount'] for item in result}
    total_worth = sum(client_totals.values())
    client_count = len(client_totals)

    # Calcular valor promedio de clientes
    if client_count > 0:
        average_worth = total_worth / client_count
    else:
        average_worth = 0

    return JsonResponse({'average_worth': average_worth})

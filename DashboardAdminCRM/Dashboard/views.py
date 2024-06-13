from django.shortcuts import render
from django.http import JsonResponse
from .models import Contact, Product, SaleDetail, User
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def test_db(request):
    # Crear y guardar un nuevo contacto
    new_contact = Contact(
        id="00001",
        name="Luis Andres",
        email="LuisAndres@example.com",
        phone="79803285",
        address="his home",
        createdAt=datetime.utcnow()
    )
    new_contact.save()

    # Recuperar todos los contactos
    contacts = Contact.objects()
    
    # Devolver los contactos como JSON
    return JsonResponse({'contacts': list(contacts.values())})

def test_products(request):
    # Crear y guardar un nuevo producto
    new_product = Product(
        id=2,
        description="Test Product Description"
    )
    new_product.save()

    # Recuperar todos los productos
    products = Product.objects()
    
    # Devolver los productos como JSON
    return JsonResponse({'products': list(products.values())})

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
    print('date_filter = ', date_filter)
    print('date_filter_prev = ', date_filter_prev)

    # Realizar consultas en la base de datos
    sales = SaleDetail.objects(**date_filter)  # Aplicar el filtro de fecha
    salesprev = SaleDetail.objects(**date_filter_prev)

    # Obtener la cantidad de contactId únicos en el rango de fecha actual
    unique_contact_ids = SaleDetail.objects(**date_filter).distinct('contactId')
    unique_contact_ids_prev = SaleDetail.objects(**date_filter_prev).distinct('contactId')
    unique_contact_count = len(unique_contact_ids)
    unique_contact_count_prev = len(unique_contact_ids_prev)
    print('cantidad contactos = ', unique_contact_count)
    print('cantidad contactos prev = ', unique_contact_count_prev)

    # Convertir ambas listas a conjuntos y encontrar la intersección
    current_set = set(unique_contact_ids)
    prev_set = set(unique_contact_ids_prev)
    common_contact_ids = current_set.intersection(prev_set)
    common_contact_ids_count = len(common_contact_ids)
    print('cantidad contactos inter= ', common_contact_ids_count)

    # cálculo del KPI tasa de retencion de clientes, mide el porcentaje de clientes que 
    # volvieron a realizar una compra luego de realizar una en el mes pasado 
    tasa_retencion_clientes = (common_contact_ids_count / unique_contact_count_prev) * 100

    # Resultado del KPI
    kpi_result = {
        'start_date': start_date_str,
        'end_date': end_date_str,
        'tasa_retencion_clientes': tasa_retencion_clientes,
    }
    print('kpi respuesta: ', kpi_result)

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
    return render(request, 'dashboard/dashboard.html', {
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

from django.shortcuts import render, redirect,get_object_or_404
from .forms import LeadForm
from .models import Leads,Product,Service,CompanySettings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date


def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
    else:
        form = UserCreationForm()

    # Apply 'form-control' class to all fields (always)
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        # login(request, user)  # You can enable this if you want auto-login after signup
        return redirect('login')

    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
    else:
        form = AuthenticationForm()

    # Apply Bootstrap styling
    for field in form.fields.values():
        existing_classes = field.widget.attrs.get('class', '')
        field.widget.attrs['class'] = f'{existing_classes} form-control'.strip()

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('leads:lead_list')  # Change redirect as needed

    return render(request, 'registration/login.html', {'form': form})

# @login_required
# def add_lead(request):
#     if request.method == 'POST':
#         form = LeadForm(request.POST)
#         if form.is_valid():
#             lead = form.save(commit=False)
#             lead.user = request.user
#             lead.save()
#             messages.success(request, 'Lead added successfully!')
#             return redirect('add_lead')  # Key change: Redirect after POST
#     else:
#         form = LeadForm()
#     return render(request, 'add_lead.html', {'form': form})
# # @login_required
# # def view_leads(request):
# #     leads = Leads.objects.filter(user=request.user)
# #     today = date.today()
# #     return render(request, 'view_leads.html', {'leads': leads, 'today': today})


# @login_required
# def view_leads(request):
#     leads = Leads.objects.filter(user=request.user)
#     today = date.today()

#     for lead in leads:
#         service_data = []
#         for service_code in lead.services_want or []:
#             service_label = dict(Leads.SERVICE_CHOICES).get(service_code, service_code.title())
#             selected_products = lead.service_products.get(service_code, []) if lead.service_products else []
            
#             product_labels = []
#             for prod_code in selected_products:
#                 product_label = dict(Leads.SERVICE_PRODUCTS.get(service_code, [])).get(prod_code, prod_code)
#                 product_labels.append(product_label)

#             # Add an entry for each selected product
#             if product_labels:
#                 for label in product_labels:
#                     service_data.append({'name': service_label, 'product': label})
#             else:
#                 # If no products selected, still show the service
#                 service_data.append({'name': service_label, 'product': '-'})

#         lead.services_with_products = service_data

#     return render(request, 'view_leads.html', {
#         'leads': leads,
#         'today': today
#     })

# @login_required
# def view_lead(request, pk):
#     lead = get_object_or_404(Leads, pk=pk, user=request.user)
    
#     # Prepare service-product data for the template
#     service_data = []
#     for service_code in lead.services_want or []:
#         service_label = dict(Leads.SERVICE_CHOICES).get(service_code, service_code.title())
#         selected_products = lead.service_products.get(service_code, []) if lead.service_products else []
        
#         product_labels = []
#         for prod_code in selected_products:
#             product_label = dict(Leads.SERVICE_PRODUCTS.get(service_code, [])).get(prod_code, prod_code)
#             product_labels.append(product_label)

#         service_data.append({
#             'name': service_label,
#             'products': product_labels if product_labels else ['-']
#         })

#     context = {
#         'lead': lead,
#         'today': date.today(),
#         'services_with_products': service_data
#     }
    
#     return render(request, 'view_lead.html', context)

# @login_required
# def view_lead(request, pk):
#     lead = get_object_or_404(Leads, pk=pk, user=request.user)
#     return render(request, 'view_lead.html', {'lead': lead})

# @login_required
# def edit_lead(request, pk):
#     lead = get_object_or_404(Leads, pk=pk, user=request.user)
#     if request.method == 'POST':
#         form = LeadForm(request.POST, instance=lead)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Lead updated successfully!')
#             return redirect('view_leads')
#     else:
#         form = LeadForm(instance=lead)
#     return render(request, 'edit_lead.html', {'form': form, 'lead': lead})


@login_required
def delete_lead(request, pk):
    lead = get_object_or_404(Leads, pk=pk, user=request.user)
    if request.method == 'POST':
        lead.delete()
        messages.success(request, 'Lead deleted successfully!')
        return redirect('view_leads')
    return redirect('view_leads')

from django.utils.dateparse import parse_date


@login_required
def lead_report(request):
    selected_date = request.GET.get('follow_up_date')
    leads = Leads.objects.all()

    if selected_date:
        parsed_date = parse_date(selected_date)
        if parsed_date:
            leads = leads.filter(follow_up_date=parsed_date)

    context = {
        'leads': leads,
        'selected_date': selected_date,
    }
    return render(request, 'report.html', context)


def check_phone_exists(request):
    phone = request.GET.get('phone')
    exists = False
    if phone:
        exists = Leads.objects.filter(phone=phone).exists()
    return JsonResponse({'exists': exists})



@login_required
def view_leads(request):
    leads = Leads.objects.filter(user=request.user)
    today = date.today()

    # Prepare lead data with services and products
    for lead in leads:
        service_data = []
        # Fetch the related services for the lead
        for service in lead.services_want.all():  # Change to a ManyToManyField
            selected_products = lead.products_interested.filter(service=service)
            
            product_labels = []
            for product in selected_products:
                product_labels.append(product.name)

            # Add an entry for each selected product
            if product_labels:
                for label in product_labels:
                    service_data.append({'name': service.name, 'product': label})
            else:
                # If no products selected, still show the service
                service_data.append({'name': service.name, 'product': '-'})

        lead.services_with_products = service_data

    # Check if no leads exist for the logged-in user
    if not leads:
        messages.info(request, "You don't have any leads yet.")

    return render(request, 'view_leads.html', {
        'leads': leads,
        'today': today
    })



@login_required
def view_lead(request, pk):
    lead = get_object_or_404(Leads, pk=pk, user=request.user)
    
    # Prepare service-product data for the template
    service_data = []
    for service in lead.services_want.all():  # Use ManyToManyField to get services
        selected_products = lead.products_interested.filter(service=service)
        
        product_labels = []
        for product in selected_products:
            product_labels.append({
                'name': product.name,
                'price': product.price
            })

        service_data.append({
            'name': service.name,
            'products': product_labels if product_labels else ['-']
        })

    context = {
        'lead': lead,
        'today': date.today(),
        'services_with_products': service_data
    }
    
    return render(request, 'view_lead.html', context)

@login_required
def add_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.user = request.user
            lead.save()
            
            # Save many-to-many relationships
            form.save_m2m()  # This saves the services_want field
            
            # Handle products separately
            for service in lead.services_want.all():
                product_field_name = f'products_{service.id}'
                product_ids = request.POST.getlist(product_field_name)
                lead.products_interested.add(*product_ids)
            
            messages.success(request, 'Lead added successfully!')
            print(f"Services selected: {lead.services_want.all()}")
            print(f"Products selected: {lead.products_interested.all()}")
            return redirect('add_lead')
    else:
        form = LeadForm()
    
    return render(request, 'add_lead.html', {'form': form})

@login_required
def edit_lead(request, pk):
    lead = get_object_or_404(Leads, pk=pk, user=request.user)
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead updated successfully!')
            return redirect('view_leads')
    else:
        form = LeadForm(instance=lead)
    return render(request, 'edit_lead.html', {'form': form, 'lead': lead})

from django.db.models import Sum

# def preview_quotation(request, lead_id):
#     lead = Leads.objects.get(id=lead_id)

#     # Prepare the services and products
#     services_with_products = []
    
#     for service in lead.services_want.all():
#         products = lead.products_interested.filter(service=service)
#         for product in products:
#             services_with_products.append({
#                 'service_name': service.name,
#                 'product_name': product.name,
#                 'price': product.price,
#             })

#     total_price = sum(item['price'] for item in services_with_products)

#     context = {
#         'lead': lead,
#         'services_with_products': services_with_products,
#         'total_price': total_price,
#     }
#     return render(request, 'preview_quotation.html', context)



from decimal import Decimal

def preview_quotation(request, lead_id):
    lead = get_object_or_404(Leads, id=lead_id)
    company_settings = CompanySettings.load()
    
    services_with_products = []
    
    for service in lead.services_want.all():
        products = lead.products_interested.filter(service=service)
        for product in products:
            services_with_products.append({
                'service_name': service.name,
                'product_name': product.name,
                'price': product.price,  # This is Decimal
            })

    subtotal = sum(item['price'] for item in services_with_products)
    tax_rate = Decimal(str(company_settings.tax_rate))  # Convert to Decimal
    tax_amount = subtotal * tax_rate / Decimal('100')
    total_price = subtotal + tax_amount
    
    context = {
        'lead': lead,
        'services_with_products': services_with_products,
        'subtotal': subtotal,
        'tax_rate': float(tax_rate),  # Convert to float for template display
        'tax_amount': tax_amount,
        'total_price': total_price,
        'quotation_number': f"G{lead_id}",
        'quotation_date': datetime.now(),
    }
    return render(request, 'preview_quotation.html', context)
def send_quotation(request, lead_id):
    lead = get_object_or_404(Leads, id=lead_id)
    # Your email or WhatsApp sending logic here
    # (send email to lead.email)
    
    messages.success(request, f'Quotation sent to {lead.name} successfully!')
    return redirect('view_leads')

from datetime import datetime
import openpyxl
from django.http import HttpResponse
from .models import Leads

def download_leads_excel(request):
    # Create an Excel workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Leads"
    
    # Write headers
    headers = ['Name', 'Phone', 'Email', 'Shop Name', 'Place', 'Location', 'Type', 'Status', 'Follow-up', 'Remarks', 'Service', 'Product']
    ws.append(headers)
    
    # Fetch all leads from the database
    leads = Leads.objects.all()
    
    # Iterate over each lead and add to the Excel file
    for lead in leads:
        # Format the follow-up date
        follow_up = lead.follow_up_date.strftime('%Y-%m-%d') if lead.follow_up_date else 'N/A'
        
        # Iterate through the services for each lead
        for service in lead.services_want.all():
            # Iterate through the products related to each service
            for product in lead.products_interested.filter(service=service):
                # Append a row for each combination of service and product
                ws.append([
                    lead.name,
                    lead.phone,
                    lead.email,
                    lead.shop_name,
                    lead.place,
                    lead.location,
                    lead.shop_type,
                    lead.status,
                    follow_up,
                    lead.remarks if lead.remarks else 'N/A',
                    service.name,  # Service name
                    product.name  # Product name
                ])
    
    # Set the response content type and disposition for file download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="leads.xlsx"'
    
    # Save the workbook to the response
    wb.save(response)
    
    return response

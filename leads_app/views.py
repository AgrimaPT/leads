from django.shortcuts import render, redirect,get_object_or_404
from .forms import LeadForm,CompanySignupForm,CompanyProfileForm,ServiceForm,ProductForm
from .models import Leads,Product,Service,CompanyProfile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date


def signup_view(request):
    # if request.method == 'POST':
    #     form = UserCreationForm(request.POST)
    # else:
    #     form = UserCreationForm()
    form = UserCreationForm(request.POST or None)

    # Apply 'form-control' class to all fields (always)
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        try:
            Employee.objects.create(user=user)  # Automatically create an Employee profile
        except Exception as e:
            print(f"Error creating employee: {e}")
        # login(request, user)  # You can enable this if you want auto-login after signup
        return redirect('login')

    return render(request, 'registration/signup.html', {'form': form})


from .models import CompanyProfile, Employee


@login_required
def company_dashboard(request):
    if not CompanyProfile.objects.filter(user=request.user).exists():
        messages.error(request, "Access denied.")
        return redirect('login')

    company = CompanyProfile.objects.get(user=request.user)
    return render(request, 'company_dashboard.html', {'company': company})


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
        return redirect('view_leads')  # Change redirect as needed

    return render(request, 'registration/login.html', {'form': form})

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
    employee = Employee.objects.get(user=request.user)
    leads = Leads.objects.filter(user=employee)  # Show newest first
    today = date.today()

    for lead in leads:
        service_data = []
        
        # Check if lead has any services (ManyToManyField)
        if lead.services_want.exists():  
            for service in lead.services_want.all():
                selected_products = lead.products_interested.filter(service=service)
                
                product_labels = [product.name for product in selected_products]
                
                if product_labels:
                    for label in product_labels:
                        service_data.append({'name': service.name, 'product': label})
                else:
                    service_data.append({'name': service.name, 'product': '-'})
        else:
            # Add empty entry if no services
            service_data.append({'name': 'No service selected', 'product': '-'})
        
        lead.services_with_products = service_data

    if not leads.exists():
        messages.info(request, "You don't have any leads yet.")

    return render(request, 'view_leads.html', {
        'leads': leads,
        'today': today,
        'employee': employee
    })



@login_required
def view_lead(request, pk):
    employee = get_object_or_404(Employee, user=request.user)
    lead = get_object_or_404(Leads, pk=pk, user=employee)
    
    service_data = []
    for service in lead.services_want.all():
        selected_products = lead.products_interested.filter(service=service)
        
        product_labels = [{
            'name': product.name,
            'price': product.price
        } for product in selected_products]

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
    employee = Employee.objects.get(user=request.user)
    if request.method == 'POST':
        form = LeadForm(request.POST, request.FILES)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.user = employee
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
    
    return render(request, 'add_lead.html', {'form': form,'employee':employee})

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django import forms
from .models import Employee, Leads, Service



@login_required
def edit_lead(request, pk):
    employee = get_object_or_404(Employee, user=request.user)
    lead = get_object_or_404(Leads, pk=pk, user=employee)
    services = Service.objects.prefetch_related('products').all()

    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        
        # Add dynamic product fields for selected services
        selected_services_ids = request.POST.getlist('services_want', [])
        for service_id in selected_services_ids:
            try:
                service = Service.objects.get(id=service_id)
                field_name = f'products_{service.id}'
                form.fields[field_name] = forms.ModelMultipleChoiceField(
                    queryset=service.products.all(),
                    widget=forms.CheckboxSelectMultiple,
                    required=False
                )
            except (Service.DoesNotExist, ValueError):
                continue

        if form.is_valid():
            lead = form.save(commit=False)
            lead.save()

            # Clear existing selections
            lead.services_want.clear()
            lead.products_interested.clear()

            # Save services
            if 'services_want' in form.cleaned_data:
                lead.services_want.set(form.cleaned_data['services_want'])

            # Save products for each service
            for service in form.cleaned_data.get('services_want', []):
                field_name = f'products_{service.id}'
                if field_name in request.POST:
                    product_ids = request.POST.getlist(field_name)
                    lead.products_interested.add(*product_ids)

            messages.success(request, 'Lead updated successfully!')
            return redirect('view_leads')
        else:
            # Add error messages to help debug
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LeadForm(instance=lead)
        
        # Initialize dynamic product fields for existing services
        for service in lead.services_want.all():
            field_name = f'products_{service.id}'
            form.fields[field_name] = forms.ModelMultipleChoiceField(
                queryset=service.products.all(),
                widget=forms.CheckboxSelectMultiple,
                required=False,
                initial=lead.products_interested.filter(service=service)
            )

    return render(request, 'edit_lead.html', {
        'form': form,
        'lead': lead,
        'services': services
    })



from django.db.models import Sum
from decimal import Decimal

def preview_quotation(request, lead_id):
    employee = get_object_or_404(Employee, user=request.user)
    
    # Now use the employee instance to filter the lead
    lead = get_object_or_404(Leads, id=lead_id, user=employee)
    company_settings = get_object_or_404(CompanyProfile)

    
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

@login_required
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
@login_required
def company_dashboard(request):
    if not CompanyProfile.objects.filter(user=request.user).exists():
        return redirect('home_selection_view')
    company = get_object_or_404(CompanyProfile, user=request.user)
    # Get all employees of the company
    # employees = Employee.objects.filter(user__companyprofile=company)

    # Get all leads added by those employees
    # leads = Leads.objects.filter(user__in=employees).order_by('-created_at')
    leads= Leads.objects.all()
    return render(request, 'company_dashboard.html', {
        'company': company,
        'leads': leads
    })
def company_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if user is a company
            if CompanyProfile.objects.filter(user=user).exists():
                login(request, user)
                return redirect('company_dashboard')
            else:
                messages.error(request, 'You are not authorized as a company user.')
    else:
        form = AuthenticationForm()

    # Add Bootstrap styling
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    return render(request, 'registration/company_login.html', {'form': form})

def company_signup(request):
    if request.method == 'POST':
        form = CompanySignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('view_leads')  # or wherever you want to redirect
    else:
        form = CompanySignupForm()
    return render(request, 'registration/company_signup.html', {'form': form})


@login_required
def view_company_profile(request):
    company = get_object_or_404(CompanyProfile, user=request.user)
    return render(request, 'view_profile.html', {'company': company})

@login_required
def edit_company_profile(request):
    company = CompanyProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect('view_company_profile')
    else:
        form = CompanyProfileForm(instance=company)

    return render(request, 'edit_profile.html', {'form': form})


def home_selection_view(request):
    return render(request, 'registration/home_selection.html')



from django.shortcuts import render
from .models import Leads, Service, Product


from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse
from .models import Leads, Service, Product
from django.utils import timezone


@login_required
def lead_report(request):
    employee = get_object_or_404(Employee, user=request.user)
    # lead = get_object_or_404(Leads, user=employee)
    # Get all leads count
    all_leads_queryset = Leads.objects.filter(user=employee)
    all_leads_serialized = serializers.serialize("json", all_leads_queryset)
    total_leads = all_leads_queryset.count()
    # total_leads = Leads.objects.count()
    
    # Get leads by status
    leads_by_status = {}
    statuses = Leads.STATUS_CHOICES
    for status, _ in statuses:
        leads = Leads.objects.filter(status=status,user=employee).order_by('-created_at')
        leads_by_status[status] = {
            'leads': leads,
            'count': leads.count(),
            'serialized': serializers.serialize('json', leads)
        }
    
    # Get leads by service
    leads_by_service = {}
    services = Service.objects.all()
    for service in services:
        leads = Leads.objects.filter(services_want=service,user=employee)
        leads_by_service[service] = {
            'leads': leads,
            'count': leads.count(),
            'serialized': serializers.serialize('json', leads)
        }
    
    # Get leads by product
    leads_by_product = {}
    products = Product.objects.all()
    for product in products:
        leads = Leads.objects.filter(products_interested=product,user=employee)
        leads_by_product[product] = {
            'leads': leads,
            'count': leads.count(),
            'serialized': serializers.serialize('json', leads)
        }
    
    # Get summary stats
    # converted_leads = Leads.objects.filter(status='converted').count()
    # active_leads = Leads.objects.filter(status='active').count()
    # lost_leads = Leads.objects.filter(status='lost').count()
    
    context = {
        'total_leads': total_leads,
        # 'converted_leads': converted_leads,
        # 'active_leads': active_leads,
        # 'lost_leads': lost_leads,
        'current_date': timezone.now(),
        'leads_by_status': leads_by_status,
        'leads_by_service': leads_by_service,
        'leads_by_product': leads_by_product,
        'services': services,
        'products': products,
        'all_leads': all_leads_serialized,

    }
    
    return render(request, 'report.html', context)

from django.urls import reverse

@login_required
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('company_dashboard'))
    else:
        form = ServiceForm()
    return render(request, 'add_service.html', {'form': form})


@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_dashboard')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

def service_product_list(request):
    services = Service.objects.prefetch_related('products')  # Efficient fetching
    return render(request, 'service_product_list.html', {'services': services})


def edit_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('service_product_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'edit_service.html', {'form': form})

def delete_service(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        return redirect('service_product_list')
    return redirect('service_product_list')

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('service_product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
    return redirect('service_product_list')

# def employee_leads(request):
#     employees = Employee.objects.all().select_related('user')
#     return render(request, 'employee_leads.html', {'employees': employees})
from django.db.models import Count, Q
from django.shortcuts import render
from .models import Employee  # adjust import as needed

def employee_leads(request):
    # Annotate each employee with total_leads and hot_leads using ORM
    employees = Employee.objects.all().select_related('user').annotate(
        total_leads=Count('leads'),
        hot_leads=Count('leads', filter=Q(leads__status='hot'))
    )

    return render(request, 'employee_leads.html', {'employees': employees})


def employee_leads_detail(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    leads = Leads.objects.filter(user=employee).select_related('user')
    return render(request, 'includes/leads_table.html', {'leads': leads, 'employee': employee})
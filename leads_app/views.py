from django.shortcuts import render, redirect,get_object_or_404
from .forms import LeadForm,CompanySignupForm,CompanyProfileForm,ServiceForm,ProductForm
from .models import Leads,Product,Service,CompanyProfile,LeadProduct
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date


def signup_view(request):
    
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
        return redirect(reverse('view_leads', kwargs={'username': request.user.username}))
  # Change redirect as needed

    return render(request, 'registration/login.html', {'form': form})

@login_required
def delete_lead(request, pk,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    lead = get_object_or_404(Leads, pk=pk, user=request.user)
    if request.method == 'POST':
        lead.delete()
        messages.success(request, 'Lead deleted successfully!')
        return redirect('view_leads')
    return redirect('view_leads')

from django.utils.dateparse import parse_date

def check_phone_exists(request):
    phone = request.GET.get('phone')
    exists = False
    if phone:
        exists = Leads.objects.filter(phone=phone).exists()
    return JsonResponse({'exists': exists})




@login_required
def view_leads(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    employee = Employee.objects.get(user=request.user)
    leads = Leads.objects.filter(user=employee).exclude(Q(status='closed') | Q(status='lost'))  # Show newest first
    today = date.today()
    for lead in leads:
        service_data = []

        if lead.services_want.exists():
            for service in lead.services_want.all():
                selected_products = lead.products_interested.filter(service=service)

                if selected_products.exists():
                    for product in selected_products:
                        try:
                            lead_product = LeadProduct.objects.get(lead=lead, product=product)
                            label_with_qty = f"{product.name} ({lead_product.quantity})"
                        except LeadProduct.DoesNotExist:
                            label_with_qty = f"{product.name} (1)"

                        service_data.append({'name': service.name, 'product': label_with_qty})
                else:
                    service_data.append({'name': service.name, 'product': '-'})
        else:
            service_data.append({'name': 'No service selected', 'product': '-'})

        lead.services_with_products = service_data

    if not leads.exists():
        messages.info(request, "You don't have any leads yet.")

    follow_ups = Leads.objects.filter(
            user=employee,
            follow_up_date__lte=timezone.now().date()
        ).exclude(Q(status='closed') | Q(status='lost')).order_by('follow_up_date')
            


    return render(request, 'view_leads.html', {
        'leads': leads,
        'today': today,
        'employee': employee,
        'follow_ups':follow_ups
    })



@login_required
def view_lead(request, pk,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    employee = get_object_or_404(Employee, user=request.user)
    lead = get_object_or_404(Leads, pk=pk, user=employee)
    
    
    service_data = []
    for service in lead.services_want.all():
        selected_products = lead.products_interested.filter(service=service)

        product_labels = []
        for product in selected_products:
            try:
                lead_product = LeadProduct.objects.get(lead=lead, product=product)
                product_labels.append({
                    'name': product.name,
                    'price': product.price,
                    'quantity': lead_product.quantity
                })
            except LeadProduct.DoesNotExist:
                product_labels.append({
                    'name': product.name,
                    'price': product.price,
                    'quantity': 1
                })

        service_data.append({
            'name': service.name,
            'products': product_labels if product_labels else ['-']
        })


        
    context = {
        'lead': lead,
        'today': date.today(),
        'services_with_products': service_data,
        
    }
    
    return render(request, 'view_lead.html', context)

@login_required
def add_lead(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
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
                # lead.products_interested.add(*product_ids)
                for pid in product_ids:
                    quantity_str = request.POST.get(f'quantity_{pid}', '1')
                    try:
                        quantity = int(quantity_str)
                        if quantity < 1:
                            quantity = 1
                    except ValueError:
                        quantity = 1

                    LeadProduct.objects.create(lead=lead, product_id=pid, quantity=quantity)
            
            messages.success(request, 'Lead added successfully!')
           
            return redirect('add_lead', username=request.user.username)
    else:
        form = LeadForm()
    
    return render(request, 'add_lead.html', {'form': form,'employee':employee})

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django import forms
from .models import Employee, Leads, Service



@login_required
def edit_lead(request, pk,username):
    if request.user.username != username:
        return redirect('home_selection_view')
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
            # for service in form.cleaned_data.get('services_want', []):
            #     field_name = f'products_{service.id}'
            #     if field_name in request.POST:
            #         product_ids = request.POST.getlist(field_name)
            #         lead.products_interested.add(*product_ids)
            # Save products and quantities
            for service in form.cleaned_data.get('services_want', []):
                field_name = f'products_{service.id}'
                product_ids = request.POST.getlist(field_name)

                for product_id in product_ids:
                    quantity_field = f'quantity_{service.id}_{product_id}'
                    quantity = request.POST.get(quantity_field)

                    try:
                        quantity = int(quantity)
                    except (ValueError, TypeError):
                        quantity = 1  # Default quantity

                    LeadProduct.objects.create(
                        lead=lead,
                        product_id=product_id,
                        quantity=quantity
                    )


            messages.success(request, 'Lead updated successfully!')
            return redirect('view_leads', username=request.user.username)

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

from decimal import Decimal
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .models import Leads, Employee, CompanyProfile

from decimal import Decimal
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .models import Leads, Employee, CompanyProfile, LeadProduct

def preview_quotation(request, lead_id,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    employee = get_object_or_404(Employee, user=request.user)
    lead = get_object_or_404(Leads, id=lead_id, user=employee)
    company_settings = get_object_or_404(CompanyProfile)

    services_with_products = []
    subtotal = Decimal('0.00')

    # Fetch LeadProduct entries to access product + quantity
    lead_products = LeadProduct.objects.filter(lead=lead).select_related('product', 'product__service')

    for lp in lead_products:
        product = lp.product
        quantity = lp.quantity
        unit_price = product.price
        total_price = unit_price * quantity
        photo_url = product.photo.url if product.photo else None


        services_with_products.append({
            'service_name': product.service.name,
            'product_name': product.name,
            'unit_price': product.price,
            'quantity': quantity,
            'photo':photo_url,
            'total_price': total_price,
            
        })

        subtotal += total_price

    tax_rate = Decimal(str(company_settings.tax_rate))
    tax_amount = subtotal * tax_rate / Decimal('100')
    total_price = subtotal + tax_amount

    context = {
        'lead': lead,
        'services_with_products': services_with_products,
        'subtotal': subtotal,
        'tax_rate': float(tax_rate),
        'tax_amount': tax_amount,
        'total_price': total_price,
        'quotation_number': f"G{lead_id}",
        'quotation_date': datetime.now(),
        'company':company_settings
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
def company_dashboard(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    if not CompanyProfile.objects.filter(user=request.user).exists():
        return redirect('home_selection_view')
    company = get_object_or_404(CompanyProfile, user=request.user)
    # Get all employees of the company
    # employees = Employee.objects.filter(user__companyprofile=company)


    # Get all leads added by those employees
    # leads = Leads.objects.filter(user__in=employees).order_by('-created_at')
    leads= Leads.objects.all()

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
                return redirect('company_dashboard',username=user.username)
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
            return redirect('home_selection_view')  # or wherever you want to redirect
    else:
        form = CompanySignupForm()
    return render(request, 'registration/company_signup.html', {'form': form})


@login_required
def view_company_profile(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    company = get_object_or_404(CompanyProfile, user=request.user)
    return render(request, 'view_profile.html', {'company': company})

@login_required
def edit_company_profile(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    company = CompanyProfile.objects.get(user=request.user)

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect('view_company_profile', username=request.user.username)
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
def lead_report(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
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

    follow_ups = Leads.objects.filter(
        user=employee,
        follow_up_date__lte=timezone.now().date()
    ).exclude(Q(status='closed') | Q(status='lost')).order_by('follow_up_date')
        
    
    
    context = {
        'total_leads': total_leads,
        
        'current_date': timezone.now(),
        'leads_by_status': leads_by_status,
        'leads_by_service': leads_by_service,
        'leads_by_product': leads_by_product,
        'services': services,
        'products': products,
        'all_leads': all_leads_serialized,
        'follow_ups': follow_ups,

    }
    
    return render(request, 'report.html', context)

from django.urls import reverse

@login_required
def add_service(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_product_list', username=username)

    else:
        form = ServiceForm()
    return redirect('service_product_list', username=username)


@login_required
def add_product(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('service_product_list', username=username)
    else:
        form = ProductForm()
    return redirect('service_product_list', username=username)

def service_product_list(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    services = Service.objects.prefetch_related('products')  # Efficient fetching
    return render(request, 'service_product_list.html', {'services': services})


def edit_service(request, pk,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated successfully!')
            return redirect('service_product_list', username=username)
    else:
        form = ServiceForm(instance=service)
    return redirect('service_product_list', username=username)

def delete_service(request, pk,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Service deleted successfully!')
        # return redirect('service_product_list')
    return redirect('service_product_list', username=username)

def edit_product(request, pk,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            
    else:
        form = ProductForm(instance=product)
    return redirect('service_product_list', username=username)

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

def employee_leads(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    # Annotate each employee with total_leads and hot_leads using ORM
    employees = Employee.objects.all().select_related('user').annotate(
        total_leads=Count('leads'),
        hot_leads=Count('leads', filter=Q(leads__status='hot'))
    )

    return render(request, 'employee_leads.html', {'employees': employees})


def employee_leads_detail(request, employee_id,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    employee = get_object_or_404(Employee, pk=employee_id)
    leads = Leads.objects.filter(user=employee).select_related('user')
    return render(request, 'partials/employee_leads_detail.html', {'leads': leads, 'employee': employee})


@login_required
def employee_profile(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    employee = Employee.objects.get(user=request.user)
    return render(request, 'employee_profile.html', {'employee': employee})


from .forms import EmployeeProfileForm

@login_required
def edit_employee_profile(request,username):
    if request.user.username != username:
        return redirect('home_selection_view')
    employee = Employee.objects.get(user=request.user)

    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_profile', username=request.user.username)
    else:
        form = EmployeeProfileForm(instance=employee)
    
    return render(request, 'edit_employee_profile.html', {'form': form})
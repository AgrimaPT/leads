from django.shortcuts import render, redirect,get_object_or_404
from .forms import LeadForm
from .models import Leads
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string


# def signup_view(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
        
#         if form.is_valid():
#             user = form.save()
#             # login(request, user)
#             return redirect('login')  # or wherever you want to go after signup
#     else:
#         form = UserCreationForm()
#     return render(request, 'registration/signup.html', {'form': form})

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

@login_required
def add_lead(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.user = request.user
            lead.save()
            messages.success(request, 'Lead added successfully!')
            return redirect('add_lead')  # Key change: Redirect after POST
    else:
        form = LeadForm()
    return render(request, 'add_lead.html', {'form': form})
@login_required
def view_leads(request):
    leads = Leads.objects.filter(user=request.user)
    return render(request, 'view_leads.html', {'leads': leads})


@login_required
def view_lead(request, pk):
    lead = get_object_or_404(Leads, pk=pk, user=request.user)
    return render(request, 'view_lead.html', {'lead': lead})

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


@login_required
def delete_lead(request, pk):
    lead = get_object_or_404(Leads, pk=pk, user=request.user)
    if request.method == 'POST':
        lead.delete()
        messages.success(request, 'Lead deleted successfully!')
        return redirect('view_leads')
    return redirect('view_leads')

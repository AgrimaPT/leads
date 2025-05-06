

from django import forms
from .models import Leads,Service,Product,CompanyProfile
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User




from django import forms
from .models import Leads, Service, Product



# class LeadForm(forms.ModelForm):
#     services_want = forms.ModelMultipleChoiceField(
#         queryset=Service.objects.none(),  # Placeholder for now
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Leads
#         fields = ['name', 'phone', 'email', 'shop_name', 'place', 'location', 'shop_type', 'services_want', 'status', 'follow_up_date', 'remarks']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Set queryset at runtime (this is the fix!)
#         self.fields['services_want'].queryset = Service.objects.all()

#         # Dynamically create product fields per service
#         services = self.fields['services_want'].queryset
#         for service in services:
#             self.fields[f'products_{service.id}'] = forms.ModelMultipleChoiceField(
#                 queryset=Product.objects.filter(service=service),
#                 widget=forms.CheckboxSelectMultiple,
#                 required=False,
#                 label=f'{service.name} Products',
#                 initial=[]
#             )

#         # Store services and products mapping (for template use)
#         self.SERVICE_PRODUCTS = {
#             service.id: Product.objects.filter(service=service)
#             for service in services
#         }

class CompanySignupForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'logo', 'address', 'phone', 'email', 'tax_rate']

    def save(self, commit=True):
        user = User.objects.create_user(username=self.cleaned_data['username'], password=self.cleaned_data['password'])
        profile = super().save(commit=False)
        profile.user = user
        if commit:
            profile.save()
        return user
    

from django import forms
from .models import Leads, Service, Product

# class LeadForm(forms.ModelForm):
#     services_want = forms.ModelMultipleChoiceField(
#         queryset=Service.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Leads
#         fields = ['name', 'phone', 'email', 'shop_name', 'place', 'location', 'shop_type', 'services_want', 'status', 'follow_up_date', 'remarks']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Dynamically create product fields based on services
#         if 'services_want' in self.data:
#             # If form has been submitted, update the available product fields dynamically
#             selected_services = self.data.getlist('services_want')  # Get selected service ids from POST data
#             self.create_product_fields(selected_services)
#         else:
#             # If it's a GET request, just initialize the fields for all services
#             self.create_product_fields()

#     def create_product_fields(self, selected_services=None):
#         # Create product fields dynamically based on selected services
#         if selected_services is None:
#             selected_services = Service.objects.values_list('id', flat=True)
        
#         for service in Service.objects.filter(id__in=selected_services):
#             self.fields[f'products_{service.id}'] = forms.ModelMultipleChoiceField(
#                 queryset=Product.objects.filter(service=service),
#                 widget=forms.CheckboxSelectMultiple,
#                 required=False,
#                 label=f'{service.name} Products',
#                 initial=[]  # Avoid pre-selecting products
#             )

#     def clean(self):
#         cleaned_data = super().clean()

#         # Validate that products are selected for the services that were chosen
#         services_want = cleaned_data.get('services_want')

#         for service in services_want:
#             product_field_name = f'products_{service.id}'
#             selected_products = cleaned_data.get(product_field_name)

#             if selected_products is None or len(selected_products) == 0:
#                 self.add_error(product_field_name, f"Please select at least one product for {service.name}")

#         return cleaned_data



# class LeadForm(forms.ModelForm):
#     services_want = forms.ModelMultipleChoiceField(
#         queryset=Service.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Leads
#         fields = ['name', 'phone', 'email', 'shop_name', 'place', 'location', 'shop_type', 'services_want', 'status', 'follow_up_date', 'remarks']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Store initial services for template rendering
#         self.initial_services = []
#         if self.instance and self.instance.pk:
#             self.initial_services = [str(s.id) for s in self.instance.services_want.all()]
        
#         # Initialize all product fields
#         self.create_product_fields()
        
#         # Set initial values for product fields
#         if self.instance and self.instance.pk:
#             for service in self.instance.services_want.all():
#                 field_name = f'products_{service.id}'
#                 if field_name in self.fields:
#                     self.fields[field_name].initial = self.instance.products_interested.filter(service=service)

#     def create_product_fields(self):
#         # Create product fields for all services
#         for service in Service.objects.all():
#             field_name = f'products_{service.id}'
#             self.fields[field_name] = forms.ModelMultipleChoiceField(
#                 queryset=Product.objects.filter(service=service),
#                 widget=forms.CheckboxSelectMultiple,
#                 required=False,
#                 label=f'{service.name} Products'
#             )

#     def clean(self):
#         cleaned_data = super().clean()
#         services_want = cleaned_data.get('services_want', [])

#         for service in services_want:
#             product_field_name = f'products_{service.id}'
#             selected_products = cleaned_data.get(product_field_name, [])

#             if not selected_products:
#                 self.add_error(product_field_name, f"Please select at least one product for {service.name}")

#         return cleaned_data

class LeadForm(forms.ModelForm):
    services_want = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Leads
        fields = ['name', 'phone', 'email', 'shop_name', 'place', 'location', 
                 'shop_type','lead_image', 'services_want', 'status', 'follow_up_date', 'remarks']


    # def clean_phone(self):
    #     phone = self.cleaned_data.get('phone')
    #     if Leads.objects.filter(phone=phone).exists():
    #         raise forms.ValidationError("A lead with this phone number already exists.")
    #     return phone

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Get the current instance (if it exists)
        if self.instance and self.instance.pk:
            # If phone number hasn't changed, no need to check
            if self.instance.phone == phone:
                return phone
        # Check if phone number already exists for other leads
        if Leads.objects.filter(phone=phone).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise forms.ValidationError("A lead with this phone number already exists.")
        return phone

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
        
    #     # Store initial services for template
    #     self.initial_services = []
    #     if self.instance.pk:
    #         self.initial_services = [str(s.id) for s in self.instance.services_want.all()]
    #         # Initialize all product fields
    #         self.create_product_fields()
    #         # Set initial values for product fields
    #         for service in self.instance.services_want.all():
    #             field_name = f'products_{service.id}'
    #             if field_name in self.fields:
    #                 self.fields[field_name].initial = self.instance.products_interested.filter(service=service)

    # def create_product_fields(self):
    #     # Create product fields for all services that have products
    #     for service in Service.objects.all():
    #         products = Product.objects.filter(service=service)
    #         if products.exists():  # Only create field if service has products
    #             field_name = f'products_{service.id}'
    #             self.fields[field_name] = forms.ModelMultipleChoiceField(
    #                 queryset=products,
    #                 widget=forms.CheckboxSelectMultiple,
    #                 required=False,
    #                 label=f'{service.name} Products'
    #             )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Store initial services for template
        self.initial_services = []
        if self.instance.pk:
            self.initial_services = [str(s.id) for s in self.instance.services_want.all()]
            # Initialize product fields for each selected service
            self.create_product_fields()
            # Set initial values for product fields
            for service in self.instance.services_want.all():
                field_name = f'products_{service.id}'
                if field_name in self.fields:
                    # Set the initial products associated with this service
                    self.fields[field_name].initial = self.instance.products_interested.filter(service=service)

    def create_product_fields(self):
        # Create product fields for services that have products
        for service in Service.objects.all():
            products = Product.objects.filter(service=service)
            if products.exists():  # Only create field if service has products
                field_name = f'products_{service.id}'
                self.fields[field_name] = forms.ModelMultipleChoiceField(
                    queryset=products,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                    label=f'{service.name} Products'
                )



class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'logo', 'address', 'email', 'phone', 'website', 'tax_rate']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'code']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['service', 'name', 'code', 'price']
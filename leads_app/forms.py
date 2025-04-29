# from django import forms
# from .models import Leads

# class LeadForm(forms.ModelForm):
#     class Meta:
#         model = Leads
#         exclude = ['user']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add Bootstrap classes to form fields
#         for field in self.fields:
#             self.fields[field].widget.attrs.update({'class': 'form-control'})
            
#     def clean(self):
#         cleaned_data = super().clean()
#         # Add any custom validation here
#         # Example:
#         # if cleaned_data.get('some_field') == 'invalid':
#         #     self.add_error('some_field', 'Custom error message')
#         return cleaned_data


# from django import forms
# from .models import Leads
# from multiselectfield.forms.fields import MultiSelectFormField

# class LeadForm(forms.ModelForm):
#     services_want = MultiSelectFormField(
#         choices=Leads.SERVICE_CHOICES,  # Just pass the choices
#         widget=forms.CheckboxSelectMultiple
#     )

#     class Meta:
#         model = Leads
#         exclude = ['user']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add Bootstrap classes to form fields (except for CheckboxSelectMultiple fields)
#         for field in self.fields:
#             widget = self.fields[field].widget
#             if not isinstance(widget, forms.CheckboxSelectMultiple):
#                 widget.attrs.update({'class': 'form-control'})
    
#     def clean(self):
#         cleaned_data = super().clean()
#         # Add any custom validation here
#         return cleaned_data


# from django import forms
# from .models import Leads
# from multiselectfield import MultiSelectField

# class LeadForm(forms.ModelForm):
#     class Meta:
#         model = Leads
#         exclude = ['user']
#         widgets = {
#             'services_want': forms.CheckboxSelectMultiple,
#             'follow_up_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control'  # Ensures Bootstrap style
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         # Add Bootstrap classes to form fields
#         for field_name, field in self.fields.items():
#             # Skip adding form-control to these special widgets
#             if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
#                 field.widget.attrs.update({'class': 'form-control'})
            
#             # Add specific classes for certain fields if needed
            
#             if field_name == 'remarks':
#                 field.widget.attrs.update({'rows': 3})

#     def clean(self):
#         cleaned_data = super().clean()
        
#         # Example custom validation
#         # phone = cleaned_data.get('phone')
#         # if phone and len(phone) < 10:
#         #     self.add_error('phone', 'Phone number must be at least 10 digits')
            
#         return cleaned_data



# from django import forms
# from .models import Leads
# from multiselectfield import MultiSelectField

# class LeadForm(forms.ModelForm):
#     # Define products for each service as class variables
#     SERVICE_PRODUCTS = {
#         'digital_marketing': [
#             ('seo', 'SEO'),
#             ('social_media', 'Social Media Marketing'),
#             ('ppc', 'Pay-Per-Click Advertising'),
#             ('email_marketing', 'Email Marketing'),
#         ],
#         'software': [
#             ('erp', 'ERP Software'),
#             ('crm', 'CRM Software'),
#             ('inventory', 'Inventory Management'),
#         ],
#         'web_development': [
#             ('ecommerce', 'E-commerce Website'),
#             ('blog', 'Blog Website'),
#             ('portfolio', 'Portfolio Website'),
#         ],
#         'graphic_design': [
#             ('logo', 'Logo Design'),
#             ('brochure', 'Brochure Design'),
#             ('social_media_graphics', 'Social Media Graphics'),
#         ],
#     }

#     class Meta:
#         model = Leads
#         exclude = ['user', 'service_products']  # We'll handle service_products separately
#         widgets = {
#             'services_want': forms.CheckboxSelectMultiple(attrs={
#                 'class': 'service-checkbox',
#                 'data-toggle': 'collapse'  # For Bootstrap collapse functionality
#             }),
#             'follow_up_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control'
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
               
#         # Add Bootstrap classes to form fields
#         for field_name, field in self.fields.items():
#             if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
#                 field.widget.attrs.update({'class': 'form-control'})
            
#             if field_name == 'remarks':
#                 field.widget.attrs.update({'rows': 3})

#         # Add product selection fields dynamically
#         for service_code, products in self.SERVICE_PRODUCTS.items():
#             field_name = f'products_{service_code}'
#             self.fields[field_name] = forms.MultipleChoiceField(
#                 choices=products,
#                 required=False,
#                 widget=forms.CheckboxSelectMultiple(attrs={
#                     'class': 'product-checkbox',
#                     'data-service': service_code
#                 }),
                
                
#                 label=f'Select {self.Meta.model.SERVICE_CHOICES[service_code]} products'
#             )

#         # Initialize product fields with existing data
#         if self.instance and self.instance.service_products:
#             for service_code, products in self.instance.service_products.items():
#                 field_name = f'products_{service_code}'
#                 if field_name in self.fields:
#                     self.initial[field_name] = products

#     def clean(self):
#         cleaned_data = super().clean()
        
#         # Collect all selected products and build the service_products dictionary
#         service_products = {}
#         selected_services = cleaned_data.get('services_want', [])
        
#         for service_code in selected_services:
#             field_name = f'products_{service_code}'
#             selected_products = cleaned_data.get(field_name, [])
#             if selected_products:
#                 service_products[service_code] = selected_products
        
#         cleaned_data['service_products'] = service_products
        
#         return cleaned_data

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.service_products = self.cleaned_data['service_products']
#         if commit:
#             instance.save()
#         return instance



from django import forms
from .models import Leads,Service,Product
from multiselectfield import MultiSelectField


# class LeadForm(forms.ModelForm):
#     # Define products for each service
#     SERVICE_PRODUCTS = {
#         'digital_marketing': [
#             ('seo', 'SEO'),
#             ('social_media', 'Social Media Marketing'),
#             ('ppc', 'Pay-Per-Click Advertising'),
#             ('email_marketing', 'Email Marketing'),
#         ],
#         'software': [
#             ('erp', 'ERP Software'),
#             ('crm', 'CRM Software'),
#             ('inventory', 'Inventory Management'),
#         ],
#         'web_development': [
#             ('ecommerce', 'E-commerce Website'),
#             ('blog', 'Blog Website'),
#             ('portfolio', 'Portfolio Website'),
#         ],
#         'graphic_design': [
#             ('logo', 'Logo Design'),
#             ('brochure', 'Brochure Design'),
#             ('social_media_graphics', 'Social Media Graphics'),
#         ],
#     }

#     class Meta:
#         model = Leads
#         exclude = ['user', 'service_products']  # We'll handle service_products manually
#         widgets = {
#             'services_want': forms.CheckboxSelectMultiple(attrs={
#                 'class': 'service-checkbox',
#                 'data-toggle': 'collapse'
#             }),
#             'follow_up_date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control'
#             }),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Add Bootstrap classes to form fields
#         for field_name, field in self.fields.items():
#             if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
#                 field.widget.attrs.update({'class': 'form-control'})
#             if field_name == 'remarks':
#                 field.widget.attrs.update({'rows': 3})

#         # Create a dictionary from SERVICE_CHOICES for label lookup
#         service_label_dict = dict(self.Meta.model.SERVICE_CHOICES)

#         # Add product selection fields dynamically based on services
#         for service_code, products in self.SERVICE_PRODUCTS.items():
#             field_name = f'products_{service_code}'
#             self.fields[field_name] = forms.MultipleChoiceField(
#                 choices=products,
#                 required=False,
#                 widget=forms.CheckboxSelectMultiple(attrs={
#                     'class': 'product-checkbox',
#                     'data-service': service_code
#                 }),
#                 label=f'Select {service_label_dict.get(service_code, service_code.capitalize())} products'
#             )

#         # Initialize product fields if editing an instance
#         if self.instance and self.instance.service_products:
#             for service_code, products in self.instance.service_products.items():
#                 field_name = f'products_{service_code}'
#                 if field_name in self.fields:
#                     self.initial[field_name] = products

#     def clean(self):
#         cleaned_data = super().clean()

#         # Build the service_products dictionary from selected checkboxes
#         service_products = {}
#         selected_services = cleaned_data.get('services_want', [])

#         for service_code in selected_services:
#             field_name = f'products_{service_code}'
#             selected_products = cleaned_data.get(field_name, [])
#             if selected_products:
#                 service_products[service_code] = selected_products

#         cleaned_data['service_products'] = service_products
#         return cleaned_data
    


#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.service_products = self.cleaned_data['service_products']
#         if commit:
#             instance.save()
#         return instance






# class LeadForm(forms.ModelForm):
#     services_want = forms.ModelMultipleChoiceField(
#         queryset=Service.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )
#     products_interested = forms.ModelMultipleChoiceField(
#         queryset=Product.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=False
#     )

#     class Meta:
#         model = Leads
#         fields = ['name', 'phone', 'email', 'shop_name', 'place', 'location', 'shop_type', 'services_want', 'products_interested', 'status', 'follow_up_date', 'remarks']




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

#         # Dynamically create product fields per service
#         services = Service.objects.all()
#         for service in services:
#             self.fields[f'products_{service.code}'] = forms.ModelMultipleChoiceField(
#                 queryset=Product.objects.filter(service=service),
#                 widget=forms.CheckboxSelectMultiple,
#                 required=False,
#                 label=f'{service.name} Products'
#             )

#         # Store services and products mapping (for template)
#         self.SERVICE_PRODUCTS = {service.code: Product.objects.filter(service=service) for service in services}


from django import forms
from .models import Leads, Service, Product

class LeadForm(forms.ModelForm):
    services_want = forms.ModelMultipleChoiceField(
        queryset=Service.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Leads
        fields = ['name', 'phone', 'email', 'shop_name', 'place', 'location', 'shop_type', 'services_want', 'status', 'follow_up_date', 'remarks']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically create product fields per service
        services = Service.objects.all()
        for service in services:
            self.fields[f'products_{service.code}'] = forms.ModelMultipleChoiceField(
                queryset=Product.objects.filter(service=service),
                widget=forms.CheckboxSelectMultiple,
                required=False,
                label=f'{service.name} Products',
                initial=[]  # Avoid pre-selecting products
            )

        # Store services and products mapping (for template)
        self.SERVICE_PRODUCTS = {service.code: Product.objects.filter(service=service) for service in services}

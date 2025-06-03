

from django import forms
from .models import Leads,Service,Product,CompanyProfile,Employee
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User




from django import forms
from .models import Leads, Service, Product


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UsernameField
from django.core.exceptions import ValidationError


class EmployeeSignupForm(forms.Form):
    username = UsernameField(max_length=150)
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    company_code = forms.CharField(max_length=20)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        username = self.cleaned_data["username"]
        password = self.cleaned_data["password1"]
        company_code = self.cleaned_data["company_code"]

        user = User.objects.create_user(username=username, password=password)

        try:
            company = CompanyProfile.objects.get(company_code=company_code)
        except CompanyProfile.DoesNotExist:
            raise ValidationError("Invalid company code")

        employee = Employee(user=user, company=company)
        if commit:
            employee.save()
        return employee


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


    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        # If editing an existing lead and phone number hasn't changed, allow it
        if self.instance and self.instance.pk and self.instance.phone == phone:
            return phone

        if not self.company:
            raise forms.ValidationError("Company not set for this form.")

        # Filter leads with the same phone number in the same company
        existing_leads = Leads.objects.filter(phone=phone, user__company=self.company)

        # Exclude the current instance if editing
        if self.instance and self.instance.pk:
            existing_leads = existing_leads.exclude(pk=self.instance.pk)

        if existing_leads.exists():
            raise forms.ValidationError("A lead with this phone number already exists in your company.")
        
        return phone

    
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if self.company:
            self.fields['services_want'].queryset = Service.objects.filter(company=self.company)
        else:
            self.fields['services_want'].queryset = Service.objects.none()

        # Store initial services for template
        self.initial_services = []
        if self.instance.pk:
            self.initial_services = [str(s.id) for s in self.instance.services_want.all()]
            self.create_product_fields(initial=True)
        else:
            self.create_product_fields(initial=False)


    def create_product_fields(self, initial=False):
        if not self.company:
            return

        services = Service.objects.filter(company=self.company)

        for service in services:
            products = Product.objects.filter(service=service, company=self.company)
            if products.exists():
                field_name = f'products_{service.id}'
                self.fields[field_name] = forms.ModelMultipleChoiceField(
                    queryset=products,
                    widget=forms.CheckboxSelectMultiple,
                    required=False,
                    label=f'{service.name} Products'
                )
                if initial and self.instance.pk:
                    self.fields[field_name].initial = self.instance.products_interested.filter(service=service)




class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'logo', 'address', 'email', 'phone', 'website', 'tax_rate','q_coverpage', 'q_proposalpage', 'q_thankyoupage']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'code']

        def __init__(self, *args, **kwargs):
            self.company = kwargs.pop('company', None)
            super().__init__(*args, **kwargs)
        
        def save(self, commit=True):
            instance = super().save(commit=False)
            if self.company:
                instance.company = self.company
            if commit:
                instance.save()
            return instance

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['service', 'name', 'code', 'price','photo']
    
#     # def __init__(self, *args, **kwargs):
#     #     super().__init__(*args, **kwargs)
#     #     self.fields['price'].required = False


#     def __init__(self, *args, **kwargs):
#         self.company = kwargs.pop('company', None)
#         super().__init__(*args, **kwargs)

#         self.fields['price'].required = False
#         if self.company:
#             self.fields['service'].queryset = Service.objects.filter(company=self.company)

#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         if self.company:
#             instance.company = self.company
#         if commit:
#             instance.save()
#         return instance



# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['service', 'name', 'code', 'price', 'photo']

#     def __init__(self, *args, **kwargs):
#         self.company = kwargs.pop('company', None)
#         super().__init__(*args, **kwargs)
#         self.fields['price'].required = False

#         if self.company:
#             self.fields['service'].queryset = Service.objects.filter(company=self.company)

#     def clean(self):
#         cleaned_data = super().clean()
#         service = cleaned_data.get("service")

#         print("Selected service:", service)
#         print("Service's company ID:", service.company_id if service else None)
#         print("Form's company ID:", self.company.id if self.company else None)

#         if self.company and service:
#             if service.company_id != self.company.id:
#                 raise forms.ValidationError("The service does not belong to the same company as the product.")
#         return cleaned_data

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['service', 'name', 'code', 'price', 'photo']

#     def __init__(self, *args, **kwargs):
#         self.company = kwargs.pop('company', None)
#         super().__init__(*args, **kwargs)
#         self.fields['price'].required = False

#         # Filter services to only show those belonging to the company
#         if self.company:
#             self.fields['service'].queryset = Service.objects.filter(company=self.company)
#         else:
#             self.fields['service'].queryset = Service.objects.none()

#     def clean(self):
#         cleaned_data = super().clean()
#         service = cleaned_data.get("service")

#         if self.company and service:
#             if service.company != self.company:
#                 raise forms.ValidationError(
#                     "The selected service doesn't belong to your company. "
#                     "Please select a service from your company."
#                 )
#         return cleaned_data

#     def save(self, commit=True):
#         product = super().save(commit=False)
#         if self.company:
#             product.company = self.company
#         if commit:
#             product.save()
#         return product



# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['service', 'name', 'code', 'price', 'photo']

#     def __init__(self, *args, **kwargs):
#         self.company = kwargs.pop('company', None)
#         super().__init__(*args, **kwargs)
        
#         print(f"Initializing form for company: {self.company.id if self.company else 'None'}")
        
#         if self.company:
#             services = Service.objects.filter(company=self.company)
#             print(f"Available services for company {self.company.id}: {[s.id for s in services]}")
#             self.fields['service'].queryset = services
#         else:
#             self.fields['service'].queryset = Service.objects.none()

#     def clean(self):
#         cleaned_data = super().clean()
#         service = cleaned_data.get('service')
        
#         if self.company and service:
#             if service.company != self.company:
#                 print(f"Service {service.id} belongs to company {service.company.id}, but form expects {self.company.id}")
#                 raise forms.ValidationError(
#                     "The selected service doesn't belong to your company. "
#                     f"Service belongs to company ID {service.company.id}, "
#                     f"your company ID is {self.company.id}"
#                 )
#         return cleaned_data

    
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         if self.company:
#             instance.company = self.company
#         if commit:
#             instance.full_clean()
#             instance.save()
#         return instance

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['service', 'name', 'code', 'price', 'photo']

#     def __init__(self, *args, **kwargs):
#         self.company = kwargs.pop('company', None)
#         super().__init__(*args, **kwargs)

#         if self.company:
#             self.fields['service'].queryset = Service.objects.filter(company=self.company)
#         else:
#             self.fields['service'].queryset = Service.objects.none()

#     def clean(self):
#         cleaned_data = super().clean()
#         if not self.company:
#             raise forms.ValidationError("Company not specified.")
        
#         service = cleaned_data.get('service')
#         if service and service.company != self.company:
#             raise forms.ValidationError("The selected service doesn't belong to your company.")
#         return cleaned_data

#     def save(self, commit=True):
#         product = super().save(commit=False)
#         product.company = self.company
#         if commit:
#             product.save()
#         return product

from django import forms
from .models import Product, Service

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['service', 'name', 'price', 'photo']
        
    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if self.company:
            self.fields['service'].queryset = Service.objects.filter(company=self.company)
    
    def save(self, commit=True):
        product = super().save(commit=False)
        product.company = self.company
        if commit:
            product.save()
        return product
class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name','email','phone', 'profile_pic'] 
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


from django import forms
from .models import Leads
from multiselectfield import MultiSelectField

class LeadForm(forms.ModelForm):
    class Meta:
        model = Leads
        exclude = ['user']
        widgets = {
            'services_want': forms.CheckboxSelectMultiple,
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to form fields
        for field_name, field in self.fields.items():
            # Skip adding form-control to these special widgets
            if not isinstance(field.widget, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                field.widget.attrs.update({'class': 'form-control'})
            
            # Add specific classes for certain fields if needed
            
            if field_name == 'remarks':
                field.widget.attrs.update({'rows': 3})

    def clean(self):
        cleaned_data = super().clean()
        
        # Example custom validation
        # phone = cleaned_data.get('phone')
        # if phone and len(phone) < 10:
        #     self.add_error('phone', 'Phone number must be at least 10 digits')
            
        return cleaned_data

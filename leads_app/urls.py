from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('add/', views.add_lead, name='add_lead'),
    path('leads/', views.view_leads, name='view_leads'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('leads/<int:pk>/', views.view_lead, name='view_lead'),
    path('leads/<int:pk>/edit/', views.edit_lead, name='edit_lead'),
    path('leads/<int:pk>/delete/', views.delete_lead, name='delete_lead'),
    path('leads/report/', views.lead_report, name='lead_report'),
    path('ajax/check-phone/', views.check_phone_exists, name='check_phone'),
    path('lead/<int:lead_id>/quotation/', views.preview_quotation, name='preview_quotation'),
    path('lead/<int:lead_id>/send-quotation/', views.send_quotation, name='send_quotation'),
    path('download/excel/', views.download_leads_excel, name='download_leads_excel'),

]
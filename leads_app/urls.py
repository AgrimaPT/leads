from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home_selection_view, name='home_selection_view'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home_selection_view'), name='logout'),
    # path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', views.signup_view, name='employee_signup'),
    path('<str:username>/add/', views.add_lead, name='add_lead'),
    path('<str:username>/leads/', views.view_leads, name='view_leads'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    #path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('<str:username>/leads/<int:pk>/', views.view_lead, name='view_lead'),
    path('<str:username>/leads/<int:pk>/edit/', views.edit_lead, name='edit_lead'),
    path('leads/<int:pk>/delete/', views.delete_lead, name='delete_lead'),
    path('<str:username>/leads/report/', views.lead_report, name='lead_report'),
    path('ajax/check-phone/', views.check_phone_exists, name='check_phone'),
    path('<str:username>/lead/<int:lead_id>/quotation/', views.preview_quotation, name='preview_quotation'),
    path('lead/<int:lead_id>/send-quotation/', views.send_quotation, name='send_quotation'),
    path('download/excel/', views.download_leads_excel, name='download_leads_excel'),


    path('company/login/', views.company_login_view, name='company_login'),
    path('company/signup/', views.company_signup, name='company_signup'),
    path('<str:username>/company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('<str:username>/company_profile/view/', views.view_company_profile, name='view_company_profile'),

    path('<str:username>/company_profile/edit/', views.edit_company_profile, name='edit_company_profile'),
    path('<str:username>/service-products/', views.service_product_list, name='service_product_list'),

    path('<str:username>/service/add/', views.add_service, name='add_service'),
    path('<str:username>/product/add/', views.add_product, name='add_product'),


    path('<str:username>/service/edit/<int:pk>/', views.edit_service, name='edit_service'),
    path('<str:username>/service/delete/<int:pk>/', views.delete_service, name='delete_service'),
    path('<str:username>/product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:pk>/', views.delete_product, name='delete_product'),

    path('<str:username>/employees/', views.employee_leads, name='employee_leads'),
    path('<str:username>/employee-leads/<int:employee_id>/', views.employee_leads_detail, name='employee_leads_detail'),

    path('<str:username>/profile/', views.employee_profile, name='employee_profile'),
    path('<str:username>/profile/edit/', views.edit_employee_profile, name='edit_employee_profile'),
]   


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
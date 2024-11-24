from django.urls import path
from .views import add_bank_details, bank_details_list, save_mappings

urlpatterns = [
    path('add_bank_details/', add_bank_details, name='add_bank_details'),
    path('bank_details_list/', bank_details_list, name='bank_details_list'),
    path('save-mappings/', save_mappings, name='save_mappings'),

]

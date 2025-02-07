from django.urls import path,include
from . import views 
from .views import *


urlpatterns=[
    path('',views.index, name='index'),
    path('login/',CustomLoginView.as_view(), name='signin'),

    path('create-item/', views.create_item, name='create_item'),
    path('list/', views.items_list, name='list'),

    path('create_record/', views.create_record, name='create_record'),
    path('record/', views.records, name='record'),
    path('update-drug-issued-record/<int:pk>/',RecordUpdateView.as_view(),name='update_record'),

    path('get_items_for_unit/<int:unit_id>/', views.get_items_for_unit, name='get_items_for_unit'),
    path('worth/', views.worth, name='worth'),

    path('restock/', views.restock, name='restock'),
    path('retocked-list/', views.restocked_list, name='restocked'),
    path('update-restocked-drug/<int:pk>/',RestockUpdateView.as_view(),name='update_restock'),
    path('',include('django.contrib.auth.urls')),

    path('item_pdf/', views.item_pdf, name='item_pdf'),
    path('record-pdf/', views.record_pdf, name='record_pdf'),
    path('restock-pdf/', views.restock_pdf, name='restock_pdf'),

    path("restock/<int:pk>/delete/", ReStockDeleteView.as_view(), name="delete_restock"),
    path("record/<int:pk>/delete/", RecordDeleteView.as_view(), name="delete_record"),

    path('item-report/', views.item_report, name='item_report'),
    path('item-report-pdf/', views.item_report_pdf, name='item_report_pdf'),

    path('record_report/', views.record_report, name='record_report'),
    path('record_report_pdf/', views.record_report_pdf, name='record_report_pdf'),

    path('restock-report/', views.restock_report, name='restock_report'),
    path('restock-report-pdf/', views.restock_report_pdf, name='restock_report_pdf'),


]

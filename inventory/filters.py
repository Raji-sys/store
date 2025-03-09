import django_filters
from .models import *
from django import forms
from django.utils import timezone
from datetime import datetime, time

class ItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(label="ITEM",field_name='name', lookup_expr='icontains')
    date_added = django_filters.DateFilter(label="DATE ADDED",field_name='date_added',lookup_expr='exact',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    date_added1 = django_filters.DateFilter(label="DATE ADDED FROM",field_name='date_added',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])    
    date_added2 = django_filters.DateFilter(label="DATE ADDED TO",field_name='date_added',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    expiration_date1 = django_filters.DateFilter(label="EXPIRY DATE FROM",field_name='expiration_date',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    expiration_date2 = django_filters.DateFilter(label="EXPIRY DATE TO",field_name='expiration_date',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])        
    vendor = django_filters.CharFilter(label="VENDOR",field_name='vendor', lookup_expr='icontains')
    added_by = django_filters.CharFilter(label="ADDED BY",field_name='added_by__username', lookup_expr='icontains')
    unit = django_filters.CharFilter(label="STORE UNIT",field_name='unit__name', lookup_expr='icontains')

    class Meta:
        model = Item
        exclude= ['total_value','cost','updated_at','expiration_date','total_purchased_quantity','issued_to','unit_price','invoice_number','store_receiving_voucher']


class RecordFilter(django_filters.FilterSet):
    date_issued = django_filters.DateFilter(label="DATE ISSUED",field_name='date_issued',lookup_expr='exact',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    item = django_filters.CharFilter(label="ITEM",field_name='item__name', lookup_expr='icontains')
    unit = django_filters.CharFilter(label="STORE UNIT",field_name='unit__name', lookup_expr='icontains')
    vendor = django_filters.CharFilter(label="VENDOR",field_name='item__vendor', lookup_expr='icontains')
    issued_to = django_filters.CharFilter(label="ISSUED TO",field_name='issued_to', lookup_expr='icontains')
    issued_by = django_filters.CharFilter(label="ISSUED BY",field_name='issued_by__username', lookup_expr='icontains')
    date_issued1 = django_filters.DateFilter(label="DATE FROM",field_name='date_issued',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),)
    date_issued2 = django_filters.DateFilter(label="DATE TO",field_name='date_issued',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),)

    class Meta:
        model = Record
        exclude= ['balance','quantity','updated_at','siv','requisition_number']


class RestockFilter(django_filters.FilterSet):
    item = django_filters.CharFilter(label="ITEM",field_name='item__name', lookup_expr='icontains')
    unit = django_filters.CharFilter(label="STORE UNIT",field_name='unit__name', lookup_expr='icontains')
    vendor_name = django_filters.CharFilter(label="VENDOR",field_name='vendor_name', lookup_expr='icontains')
    restocked_by = django_filters.CharFilter(label="BY",field_name='restocked_by__username', lookup_expr='icontains')
    expiration_date1 = django_filters.DateFilter(label="EXPIRY DATE FROM",field_name='expiration_date',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),)
    expiration_date2 = django_filters.DateFilter(label="EXPIRY DATE TO",field_name='expiration_date',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),)
    purchase_date = django_filters.DateFilter(label="DATE RESTOCKED",field_name='purchase_date',lookup_expr='exact',widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y'])
    purchase_date1 = django_filters.DateFilter(label="DATE FROM",field_name='purchase_date',lookup_expr='gte',widget=forms.DateInput(attrs={'type':'date'}),)
    purchase_date2 = django_filters.DateFilter(label="DATE TO",field_name='purchase_date',lookup_expr='lte',widget=forms.DateInput(attrs={'type':'date'}),)

    class Meta:
        model = ReStock
        exclude= ['invoice_number','quantity_purchased','store_receiving_voucher','expiration_date']

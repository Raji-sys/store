from .models import *
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from import_export.admin import ImportMixin
from simple_history.admin import SimpleHistoryAdmin

admin.site.site_header="ADMIN PANEL"
admin.site.index_title="STORE INVENTORY MANAGEMENT SYSTEM"
admin.site.site_title="NOHD STORE"

    
@admin.register(Unit)
class UnitAdmin(ImportMixin,admin.ModelAdmin):
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']
    


from django.contrib import admin
from .models import ReStock
from simple_history.admin import SimpleHistoryAdmin

# Your regular ReStock admin registration
@admin.register(ReStock)
class ReStockAdmin(SimpleHistoryAdmin):
    search_fields = ['item__name','vendor_name']
    list_display = ('item', 'vendor_name','quantity_purchased', 'purchase_date', 'expiration_date', 'invoice_number', 'store_receiving_voucher')
    autocomplete_fields = ['item',]
    history_list_display = ['quantity_purchased', 'purchase_date', 'expiration_date']

# Get the automatically created historical model for ReStock
HistoricalReStock = ReStock.history.model

@admin.register(HistoricalReStock)
class HistoricalReStockAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'item',
        'vendor_name',
        'quantity_purchased',
        'purchase_date',
        'expiration_date',
        'invoice_number',
        'store_receiving_voucher',
        'history_date',
        'history_user',
        'history_type',  # '+' creation, '~' update, '-' deletion
    )
    list_filter = ('history_type', 'history_date', 'history_user')
    search_fields = ('item__name','vendor_name', 'invoice_number')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(history_type__in=['-', '~'])


@admin.register(Item)
class ItemAdmin(ImportMixin, admin.ModelAdmin):
    readonly_fields = ('unit_price', )
    exclude = ('added_by',)  
    list_display = ['name', 'total_value', 'total_purchased_quantity','total_issued', 'vendor', 'invoice_number', 'store_receiving_voucher', 'unit_price', 'unit', 'current_balance', 'expiration_date', 'added_by', 'date_added', 'updated_at']
    list_filter = ['date_added', 'unit', 'added_by']
    search_fields = ['name']
    list_per_page = 10
    ordering = ['unit', 'name']
    autocomplete_fields = ['unit']

    def total_value(self, obj):
        return obj.total_purchased_quantity * obj.unit_price if obj.unit_price else 0

    total_value.short_description = 'Total Value'

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.save()



@admin.register(Record)
class RecordAdmin(SimpleHistoryAdmin):
    exclude = ('issued_by', 'balance')
    list_display = ['item', 'item_date', 'issued_to', 'issued_by_username', 'quantity', 'siv', 'requisition_number', 'balance', 'date_issued', 'updated_at']
    search_fields = ['item__name', 'issued_to']
    list_filter = ['issued_to', 'item', 'item__vendor', 'item__date_added']
    list_per_page = 10
    autocomplete_fields = ['item']
    history_list_display = ['quantity']  # Fields to track in history view
    
    # Your existing methods remain the same
    def save_model(self, request, obj, form, change):
        obj.clean()
        obj.issued_by = request.user
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            messages.error(request, f"Error: {e.message}")

    def item_date(self, obj):
        return obj.item.date_added

    def issued_by_username(self, obj):
        return obj.issued_by.username if obj.issued_by else None

    issued_by_username.short_description = "Issued By"
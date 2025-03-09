from .filters import ItemFilter, RecordFilter, RestockFilter
from .forms import ItemForm, RecordForm, ReStockForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Item, Record, ReStock
import datetime
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.conf import settings
import os
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from .decorators import superuser_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q, Sum
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import datetime
from django.forms import modelformset_factory
from django.views.generic import DeleteView


class HEADRequiredMixin(LoginRequiredMixin,UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='HEAD').exists()

# -------------------------------------------------------------------
# PDF Utility Functions
# -------------------------------------------------------------------
def fetch_resources(uri, rel):
    """
    Handles fetching static and media resources when generating the PDF.
    """
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

def generate_pdf(context, template_name):
    """
    Render a PDF from the given context and template using xhtml2pdf.
    Returns a BytesIO buffer or None on error.
    """
    template = get_template(template_name)
    html = template.render(context)
    buffer = BytesIO()
    pisa_status = pisa.CreatePDF(
        html, dest=buffer, encoding='utf-8', link_callback=fetch_resources
    )
    if pisa_status.err:
        return None
    buffer.seek(0)
    return buffer

def pdf_generator(buffer):
    """
    Streaming generator for sending PDF data.
    """
    chunk_size = 8192
    while True:
        chunk = buffer.read(chunk_size)
        if not chunk:
            break
        yield chunk

# -------------------------------------------------------------------
# Login and Index Views
# -------------------------------------------------------------------
def user_is_in(user):
    return not user.is_authenticated

@method_decorator(user_passes_test(user_is_in, login_url='/'), name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'login.html'
    success_url = reverse_lazy('/')

@login_required
def index(request):
    return render(request, 'inventory/index.html')

# -------------------------------------------------------------------
# Worth (Store Value) Report
# -------------------------------------------------------------------
@superuser_required
def worth(request):
    total_store_value = Item.total_store_value()
    now = datetime.now()
    today = now.strftime('%d-%B-%Y at: %I:%M %p')
    context = {'total_store_value': total_store_value, 'today': today}
    return render(request, 'inventory/worth.html', context)

# -------------------------------------------------------------------
# Create and List Items
# -------------------------------------------------------------------
@login_required
@transaction.atomic
def create_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            try:
                item = form.save(commit=False)
                item.added_by = request.user
                item.save()
                messages.success(request, f"Item '{item.name}' created successfully")
                return redirect('list')
            except Exception as e:
                messages.error(request, f"Error creating item: {e}")
    else:
        form = ItemForm()
    return render(request, 'inventory/create_item.html', {'form': form})

@login_required
def items_list(request):
    # Optionally filter by date range or search query
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    query = request.GET.get('q')

    items = Item.objects.all().order_by('-updated_at')
    if date_from:
        items = items.filter(updated_at__gte=date_from)
    if date_to:
        items = items.filter(updated_at__lte=date_to)
    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(vendor__icontains=query) |
            Q(unit__name__icontains=query) |
            Q(added_by__username__icontains=query)
        )

    pgn = Paginator(items, 10)
    pn = request.GET.get('page')
    po = pgn.get_page(pn)
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'items': items,
        'po': po,
        'query': query or ''
    }
    return render(request, 'inventory/items_list.html', context)

@login_required
def item_pdf(request):
    # Get any filtering parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    query = request.GET.get('q')
    
    items = Item.objects.all().order_by('-updated_at')
    if date_from:
        items = items.filter(updated_at__gte=date_from)
    if date_to:
        items = items.filter(updated_at__lte=date_to)
    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(vendor__icontains=query) |
            Q(unit__name__icontains=query) |
            Q(added_by__username__icontains=query)
        )
    
    # Prepare filter keys for display in the report
    keys = []
    if query:
        keys.append(f": {query}")
    if date_from or date_to:
        date_range = f"Date range: {date_from or 'any'} to {date_to or 'any'}"
        keys.append(date_range)
    
    context = {
        'f': items,
        'keys': keys,
        'result': f"GENERATED ON: {datetime.now().strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}",
        'pagesize': 'A4',
        'orientation': 'Portrait'
    }
    
    pdf_buffer = generate_pdf(context, 'inventory/item_pdf.html')
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    filename = datetime.now().strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="gen_by_{request.user}_{filename}"'
    return response

class ItemUpdateView(HEADRequiredMixin, UpdateView):
    model = Item
    form_class = ItemForm
    template_name = 'create_item.html'
    success_url = reverse_lazy('list')
  
    def form_valid(self, form):
        form.instance.added_by = self.request.user
        messages.success(self.request, "Item updated successfully.")
        return super().form_valid(form)

# -------------------------------------------------------------------
# Create, List, Update Records (Issuances)
# -------------------------------------------------------------------
@login_required
def records(request):
    # Filter records by optional date range and query
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    query = request.GET.get('q')
    
    records_qs = Record.objects.select_related('unit', 'item').order_by('-updated_at')
    if date_from:
        records_qs = records_qs.filter(updated_at__gte=date_from)
    if date_to:
        records_qs = records_qs.filter(updated_at__lte=date_to)
    if query:
        records_qs = records_qs.filter(
            Q(item__name__icontains=query) |
            Q(item__vendor__icontains=query) |
            Q(issued_to__name__icontains=query)|
            Q(unit__name__icontains=query) |
            Q(issued_by__username__icontains=query)
        )
    total_quantity = records_qs.aggregate(total=Sum('quantity'))['total'] or 0
    pgn = Paginator(records_qs, 10)
    page_number = request.GET.get('page')
    po = pgn.get_page(page_number)
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'records': records_qs,
        'po': po,
        'query': query or '',
        'total_quantity': total_quantity
    }
    return render(request, 'inventory/record.html', context)

@login_required
def record_pdf(request):
    # Filter records for PDF export
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    query = request.GET.get('q')
    
    records_qs = Record.objects.select_related('unit', 'item').order_by('-updated_at')
    if date_from:
        records_qs = records_qs.filter(updated_at__gte=date_from)
    if date_to:
        records_qs = records_qs.filter(updated_at__lte=date_to)
    if query:
        records_qs = records_qs.filter(
            Q(item__name__icontains=query) |
            Q(item__vendor__icontains=query) |
            Q(issued_to__name__icontains=query) |
            Q(unit__name__icontains=query) |
            Q(issued_by__username__icontains=query)
        )
    
    keys = []
    if query:
        keys.append(f": {query}")
    if date_from or date_to:
        date_range = f"Date range: {date_from or 'any'} to {date_to or 'any'}"
        keys.append(date_range)
    
    context = {
        'f': records_qs,
        'keys': keys,
        'result': f"GENERATED ON: {datetime.now().strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}",
        'pagesize': 'A4',
        'orientation': 'Portrait'
    }
    
    pdf_buffer = generate_pdf(context, 'inventory/record_pdf.html')
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    filename = datetime.now().strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="gen_by_{request.user}_{filename}"'
    return response

# For creating multiple records at once using a formset.
@login_required
def create_record(request):
    RecordFormSet = modelformset_factory(Record, form=RecordForm, extra=1)
    if request.method == "POST":
        formset = RecordFormSet(request.POST)
        if formset.is_valid():
            try:
                instances = formset.save(commit=False)
                with transaction.atomic():
                    for instance in instances:
                        instance.issued_by = request.user
                        instance.save()
                messages.success(request, "Records created successfully.")
                return redirect('record')
            except ValidationError as e:
                for form in formset:
                    form.add_error(None, str(e))
    else:
        formset = RecordFormSet(queryset=Record.objects.none())
    return render(request, 'inventory/create_record.html', {'formset': formset})


class RecordUpdateView(HEADRequiredMixin, UpdateView):
    model = Record
    form_class = RecordForm
    template_name = 'inventory/update_record.html'

    def form_valid(self, form):
        try:
            with transaction.atomic():
                form.save()
            messages.success(self.request, "Record updated successfully.")
            return redirect('record')
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

# -------------------------------------------------------------------
# Restock (Replenish Items) Views
# -------------------------------------------------------------------
@login_required
def restock(request):
    if request.method == 'POST':
        form = ReStockForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    restock_instance = form.save(commit=False)
                    restock_instance.restocked_by = request.user
                    restock_instance.save()
                messages.success(request, f"Restocked {restock_instance.quantity_purchased} units of {restock_instance.item.name}")
                return redirect('restocked')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = ReStockForm()
    return render(request, 'inventory/restock.html', {'form': form})


class RestockUpdateView(HEADRequiredMixin,UpdateView):
    model = ReStock
    form_class = ReStockForm
    template_name = 'inventory/restock.html'
    success_url = reverse_lazy('restocked')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.restocked_by != self.request.user:
            raise PermissionDenied("You cannot edit this restock record")
        return obj
    
    def form_valid(self, form):
        try:
            with transaction.atomic():
                form.instance.restocked_by = self.request.user
                # Lock the related item record
                item = Item.objects.select_for_update().get(pk=form.instance.item_id)
                form.save()
                item.refresh_from_db()  # Update item values after restock
            messages.success(self.request, "Restock record updated successfully")
            return super().form_valid(form)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

@login_required
def restocked_list(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    query = request.GET.get('q')
    
    restock_qs = ReStock.objects.select_related('unit', 'item').order_by('-purchase_date')
    if date_from:
        restock_qs = restock_qs.filter(date__gte=date_from)
    if date_to:
        restock_qs = restock_qs.filter(date__lte=date_to)
    if query:
        restock_qs = restock_qs.filter(
            Q(item__name__icontains=query) |
            Q(vendor_name__icontains=query) |
            Q(unit__name__icontains=query) |
            Q(restocked_by__username__icontains=query)
        )
    
    pgn = Paginator(restock_qs, 10)
    pn = request.GET.get('page')
    po = pgn.get_page(pn)
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'restock': restock_qs,
        'po': po,
        'query': query or ''
    }
    return render(request, 'inventory/restocked_list.html', context)

@login_required
def restock_pdf(request):
    # Filter restock records for PDF export
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    query = request.GET.get('q')
    
    restock_qs = ReStock.objects.select_related('unit', 'item').order_by('-purchase_date')
    if date_from:
        restock_qs = restock_qs.filter(date__gte=date_from)
    if date_to:
        restock_qs = restock_qs.filter(date__lte=date_to)
    if query:
        restock_qs = restock_qs.filter(
            Q(item__name__icontains=query) |
            Q(vendor_name__icontains=query) |
            Q(unit__name__icontains=query) |
            Q(restocked_by__username__icontains=query)
        )
    
    keys = []
    if query:
        keys.append(f": {query}")
    if date_from or date_to:
        date_range = f"Date range: {date_from or 'any'} to {date_to or 'any'}"
        keys.append(date_range)
    
    context = {
        'f': restock_qs,
        'keys': keys,
        'result': f"GENERATED ON: {datetime.now().strftime('%d-%B-%Y at %I:%M %p')}\nBY: {request.user}",
        'pagesize': 'A4',
        'orientation': 'Portrait'
    }
    
    pdf_buffer = generate_pdf(context, 'inventory/restock_pdf.html')
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    filename = datetime.now().strftime('on_%d_%m_%Y_at_%I_%M%p.pdf')
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="gen_by_{request.user}_{filename}"'
    return response

@login_required
def get_items_for_unit(request, unit_id):
    """
    Returns a JSON response with items for the given unit id.
    """
    items = Item.objects.filter(unit_id=unit_id).order_by('name')
    item_list = [
        {
            'id': item.id,
            'name': item.name,
            'vendor': item.vendor if item.vendor else 'N/A',
        }
        for item in items
    ]
    return JsonResponse({'items': item_list})


class ReStockDeleteView(HEADRequiredMixin,DeleteView):
    model = ReStock
    template_name = "inventory/restock_delete.html"
    success_url = reverse_lazy("restocked")  

    def form_valid(self, form):
        restock = self.get_object()
        try:
            restock.delete()
            messages.success(self.request, "Restock entry deleted successfully.")
        except ValidationError as e:
            messages.error(self.request, e.messages[0])
            return redirect("restocked")
        return super().form_valid(form)


class RecordDeleteView(HEADRequiredMixin,DeleteView):
    model = Record
    template_name = "inventory/record_delete.html"
    success_url = reverse_lazy("record")  
    
    def post(self, request, *args, **kwargs):
        record = self.get_object()
        messages.success(request, f"Record for {record.item.name} deleted successfully.")
        return super().post(request, *args, **kwargs)


@login_required
def item_report(request):
    itemfilter=ItemFilter(request.GET, queryset=Item.objects.all().order_by('-updated_at'))
    filtered_qs = itemfilter.qs
    total_count = filtered_qs.count()
    pgn = Paginator(filtered_qs, 10)
    page_number = request.GET.get('page')
    po = pgn.get_page(page_number)
   
    get_copy = request.GET.copy()
    if 'page' in get_copy:
       del get_copy['page']
    filter_params = get_copy.urlencode()

    context = {
        'itemfilter': itemfilter,
        'total_count':total_count,
        'po':po,
        'filter_params':get_copy.urlencode()
        }
    return render(request, 'inventory/item_report.html', context)


def item_report_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d/%m/%Y_at_%I.%M%p.pdf')
    f = ItemFilter(request.GET, queryset=Item.objects.all()).qs
    
    context = {'f': f, 'pagesize': 'A4', 'orientation': 'Portrait'}
    pdf_buffer = generate_pdf(context, 'inventory/item_report_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Report__{filename}"'
    return response


@login_required
def record_report(request):
   recordfilter = RecordFilter(request.GET, queryset=Record.objects.all().order_by('-updated_at'))
   filtered_qs = recordfilter.qs
   total_count = filtered_qs.count()
   pgn = Paginator(filtered_qs, 10)
   page_number = request.GET.get('page')
   po = pgn.get_page(page_number)
   
   get_copy = request.GET.copy()
   if 'page' in get_copy:
       del get_copy['page']
   filter_params = get_copy.urlencode()
   
   context = {
       'recordfilter': recordfilter,
       'po': po,
       'filter_params': filter_params,
       'total_count': total_count
   }
   return render(request, 'inventory/record_report.html', context)


def record_report_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d/%m/%Y_at_%I.%M%p.pdf')
    f = RecordFilter(request.GET, queryset=Record.objects.all()).qs
    
    context = {'f': f, 'pagesize': 'A4', 'orientation': 'Portrait'}
    pdf_buffer = generate_pdf(context, 'inventory/record_report_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Report__{filename}"'
    return response


@login_required
def restock_report(request):
   restockfilter = RestockFilter(request.GET, queryset=ReStock.objects.all().order_by('-purchase_date'))
   filtered_qs = restockfilter.qs
   total_count = filtered_qs.count()
   pgn = Paginator(filtered_qs, 10)
   page_number = request.GET.get('page')
   po = pgn.get_page(page_number)
   
   get_copy = request.GET.copy()
   if 'page' in get_copy:
       del get_copy['page']
   filter_params = get_copy.urlencode()
   
   context = {
       'restockfilter': restockfilter,
       'po': po,
       'filter_params': filter_params,
       'total_count': total_count
   }
   return render(request, 'inventory/restock_report.html', context)


def restock_report_pdf(request):
    ndate = datetime.now()
    filename = ndate.strftime('on_%d/%m/%Y_at_%I.%M%p.pdf')
    f = RestockFilter(request.GET, queryset=ReStock.objects.all()).qs
    
    context = {'f': f, 'pagesize': 'A4', 'orientation': 'Portrait'}
    pdf_buffer = generate_pdf(context, 'inventory/restock_report_pdf.html')
    
    if pdf_buffer is None:
        return HttpResponse('Error generating PDF', status=500)
    
    response = StreamingHttpResponse(pdf_generator(pdf_buffer), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Report__{filename}"'
    return response
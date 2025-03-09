from django import forms
from .models import *


class ItemForm(forms.ModelForm):
    expiration_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    class Meta:
        model = Item
        # fields = ['name','vendor','invoice_number','store_receiving_voucher','unit','unit_price','expiration_date','total_purchased_quantity']  
        fields = ['unit','name','vendor','unit_price','expiration_date','total_purchased_quantity']  

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required=False    
            field.widget.attrs.update({'class':'text-center text-xs focus:outline-none border border-blue-300 p-2 w-fit rounded shadow-lg hover:shadow-xl'})


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        # fields = ['unit','item','issued_to','quantity','siv','requisition_number']  
        fields = ['unit','item','issued_to','quantity']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Provide the queryset for the 'item' field
        self.fields['item'].queryset = Item.objects.all()
        for field in self.fields.values():
            field.required=False    
            field.widget.attrs.update({'class':'text-center text-xs focus:outline-none border border-blue-300 p-2 w-fit rounded shadow-lg hover:shadow-xl'})

    def clean(self):
        cleaned_data=super().clean()
        quantity=cleaned_data.get('quantity')
        unit=cleaned_data.get('unit')
        item=cleaned_data.get('item')
        
        if quantity and quantity <= 0:
            raise forms.ValidationError("quantity must me a positive value")

        if item is not None:
            balance=item.current_balance

        if quantity and balance is not None:
            quantity_to_issue=min(quantity,balance)
            if quantity_to_issue <= 0:
                raise forms.ValidationError("sorry, not enough items in your balance")
        return cleaned_data


class ReStockForm(forms.ModelForm):
    expiration_date=forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    class Meta:
        model = ReStock
        # fields = ['unit','item','vendor_name','invoice_number','store_receiving_voucher','quantity_purchased','expiration_date']  
        fields = ['unit','item','vendor_name','quantity_purchased','expiration_date']  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Provide the queryset for the 'item' field
        self.fields['item'].queryset = Item.objects.all()
        for field in self.fields.values():
            field.required=False    
            field.widget.attrs.update({'class':'text-center text-xs focus:outline-none border border-blue-300 p-2 w-fit rounded shadow-lg hover:shadow-xl'})

    def clean(self):
        cleaned_data=super().clean()
        unit=cleaned_data.get('unit')
        item=cleaned_data.get('item')
        return cleaned_data
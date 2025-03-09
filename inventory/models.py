from decimal import Decimal
from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from simple_history.models import HistoricalRecords

# -------------------------------------------------------------------
# Department (unchanged)
# -------------------------------------------------------------------
class Department(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name


# -------------------------------------------------------------------
# Unit (unchanged)
# -------------------------------------------------------------------
class Unit(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# -------------------------------------------------------------------
# Item – Old fields, new robust logic
# -------------------------------------------------------------------
class Item(models.Model):
    date_added = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=100)
    vendor = models.CharField(max_length=100, null=True, blank=True)
    # invoice_number = models.IntegerField(null=True, blank=True)  # INTEGER per old model
    # store_receiving_voucher = models.CharField(max_length=30, null=True, blank=True)
    added_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='added_items'
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, null=True, blank=True, related_name='units'
    )
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    # NOTE: In the old model this field was a DecimalField with no default.
    total_purchased_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        # Improved validations:
        if not self.name:
            raise ValidationError(_("Item name is required"))
        if self.total_purchased_quantity is not None and self.total_purchased_quantity < 0:
            raise ValidationError(_("Total purchased quantity cannot be negative"))
        if self.unit_price is not None and self.unit_price < 0:
            raise ValidationError(_("Unit price cannot be negative"))
        if self.expiration_date and self.expiration_date < timezone.now().date():
            raise ValidationError(_("Expiration date cannot be in the past"))
        super().clean()

    def save(self, *args, **kwargs):
        # Use atomic transactions and full_clean() for bullet-proof persistence.
        with transaction.atomic():
            self.full_clean()
            super().save(*args, **kwargs)

    @property
    def total_issued(self):
        """
        Old model computed property.
        Sums the quantity issued (via all related Record objects).
        """
        result = self.records.aggregate(total=models.Sum('quantity'))['total']
        return result or Decimal('0')

    @property
    def current_balance(self):
        """
        Old model computed property:
        total_purchased_quantity minus total issued.
        """
        if self.total_purchased_quantity is not None:
            return self.total_purchased_quantity - self.total_issued
        return Decimal('0')

    @property
    def total_value(self):
        """
        Computes total value as current balance * unit_price.
        """
        if self.unit_price is not None:
            return self.current_balance * self.unit_price
        return Decimal('0')
    
    @classmethod
    def total_store_value(cls):
        """
        Computes the total store value by summing the total_value
        of all items. Uses an atomic transaction to ensure consistency.
        """
        with transaction.atomic():
            total = sum((item.total_value for item in cls.objects.all()), Decimal('0'))
        return total

# -------------------------------------------------------------------
# Record – Old fields, new robust logic
# -------------------------------------------------------------------
class Record(models.Model):
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, null=True, blank=True, related_name="records"
    )
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, null=True, blank=True, related_name="records"
    )
    # issued_to = models.CharField(
    #     max_length=100, choices=Department.choices, null=True, blank=True
    # )
    issued_to = models.ForeignKey(Department, on_delete=models.CASCADE,null=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_issued = models.DateField(auto_now_add=True,null=True)
    issued_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='records'
    )
    # siv = models.CharField(max_length=30, null=True, blank=True)
    # requisition_number = models.CharField(max_length=30, null=True, blank=True)
    # Field name “balance” remains unchanged, even though we compute it below.
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()
    
    def clean(self):
        super().clean()
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError({"quantity": _("Quantity must be positive")})
        if not self.item:
            raise ValidationError(_("Item is required"))
        # Use atomic block and select_for_update for safe validation.
        with transaction.atomic():
            item = Item.objects.select_for_update().get(pk=self.item_id)
            if self.pk:
                # If updating, compute the net change in quantity.
                original = Record.objects.get(pk=self.pk)
                net_change = self.quantity - original.quantity
                if item.current_balance - net_change < 0:
                    raise ValidationError(
                        _("Insufficient stock. Available: %(balance)s"),
                        params={'balance': item.current_balance},
                    )
            else:
                if item.current_balance < self.quantity:
                    raise ValidationError(
                        _("Insufficient stock. Available: %(balance)s"),
                        params={'balance': item.current_balance},
                    )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Lock the related item record.
            item = Item.objects.select_for_update().get(pk=self.item_id)
            # Re-run validations with an exclusive lock.
            self.full_clean()
            # For new records or updates, check again the available balance.
            if self.pk:
                original = Record.objects.select_for_update().get(pk=self.pk)
                net_change = self.quantity - original.quantity
                if item.current_balance - net_change < 0:
                    raise ValidationError(
                        _("Update would result in negative balance. Current balance: %(balance)s, Change: %(change)s"),
                        params={'balance': item.current_balance, 'change': net_change},
                    )
            else:
                if item.current_balance < self.quantity:
                    raise ValidationError(
                        _("Insufficient stock. Current balance: %(balance)s, Requested: %(quantity)s"),
                        params={'balance': item.current_balance, 'quantity': self.quantity},
                    )
            # Save the record.
            super().save(*args, **kwargs)
            # After saving, update the 'balance' field to reflect the item's current balance.
            # (Note: since Item.current_balance is computed from live aggregation,
            # this step is for legacy compatibility.)
            item = Item.objects.get(pk=self.item_id)  # refresh without select_for_update
            self.balance = item.current_balance
            super(Record, self).save(update_fields=['balance'])

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            item = Item.objects.select_for_update().get(pk=self.item_id)
            # Before deletion, check that “undoing” this record would not result in inconsistency.
            # (Since total_issued is computed on the fly, we assume deletion is safe if the record exists.)
            super().delete(*args, **kwargs)
            # Optionally, you could verify post-deletion balances here.

    def __str__(self):
        return self.item.name if self.item else "Record"


# -------------------------------------------------------------------
# ReStock – Old fields, new robust logic
# -------------------------------------------------------------------
class ReStock(models.Model):
    unit = models.ForeignKey(
        Unit, on_delete=models.CASCADE, null=True, blank=True, related_name="restock_items"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=100, null=True, blank=True)
    quantity_purchased = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    restocked_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='drug_restocking')
    history = HistoricalRecords()

    def clean(self):
        super().clean()
        if self.quantity_purchased is None or self.quantity_purchased <= 0:
            raise ValidationError({"quantity_purchased": _("Quantity must be positive")})
        if self.expiration_date and self.expiration_date < timezone.now().date():
            raise ValidationError({"expiration_date": _("Expiration date cannot be in the past")})
        if not self.item:
            raise ValidationError(_("Item is required"))

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.full_clean()
            # Lock the related item.
            item = Item.objects.select_for_update().get(pk=self.item_id)
            # Determine if this is an update or a new record.
            if self.pk:
                original = ReStock.objects.select_for_update().get(pk=self.pk)
                net_change = self.quantity_purchased - original.quantity_purchased
                new_total = (item.total_purchased_quantity or Decimal('0')) + net_change
                # Ensure that the new total purchased is not less than what has been issued.
                if new_total < item.total_issued:
                    raise ValidationError(
                        _("Cannot reduce stock below issued amount. Current issued: %(issued)s"),
                        params={'issued': item.total_issued},
                    )
                item.total_purchased_quantity = new_total
            else:
                current = item.total_purchased_quantity or Decimal('0')
                item.total_purchased_quantity = current + self.quantity_purchased
            item.full_clean()
            item.save(update_fields=['total_purchased_quantity'])
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            item = Item.objects.select_for_update().get(pk=self.item_id)
            new_total = (item.total_purchased_quantity or Decimal('0')) - self.quantity_purchased
            if new_total < item.total_issued:
                raise ValidationError(
                    _("Cannot delete restock - would reduce stock below issued amount. Current issued: %(issued)s"),
                    params={'issued': item.total_issued},
                )
            item.total_purchased_quantity = new_total
            item.full_clean()
            item.save(update_fields=['total_purchased_quantity'])
            super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity_purchased} of {self.item.name} purchased on {self.purchase_date}"

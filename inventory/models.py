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
class Department(models.TextChoices):
    A_AND_E_SPINE = 'A&E SPINE', 'A&E SPINE'
    A_AND_E_THEATRE = 'A&E THEATRE', 'A&E THEATRE'
    A_AND_E_TRAUMA = 'A&E TRAUMA', 'A&E TRAUMA'
    ACTU = 'ACTU', 'ACTU'
    ACUTE_BURNS_UNIT = 'ACUTE BURNS UNIT', 'ACUTE BURNS UNIT'
    AMENITY_WARD = 'AMENITIY WARD', 'AMENITIY WARD'
    AMINU_DANTATA_WARD = 'AMINU DANTATA WARD', 'AMINU DANTATA WARD'
    ANAESTHESIA = 'ANAESTHESIA', 'ANAESTHESIA'
    APPOINTMENT_AND_PROMOTION = 'APPOINTMENT AND PROMOTION', 'APPOINTMENT AND PROMOTION'
    BILLING_ACCOUNT = 'BILLING ACCOUNT', 'BILLING ACCOUNT'
    BIO_MEDICAL = 'BIO-MEDICAL ENGR', 'BIO-MEDICAL ENGR'
    BOARD_SECTION = 'BOARD SECTION', 'BOARD SECTION'
    BURNS_AND_PLASTIC_UNIT = 'BURNS AND PLASTIC UNIT', 'BURNS AND PLASTIC UNIT'
    CASH_OFFICE = 'CASH OFFICE', 'CASH OFFICE'
    CATERTING = 'CATERING', 'CATERING'
    CHILDRENS_WARD = 'CHILDRENS WARD', 'CHILDRENS WARD'
    CLINICAL_SERVICES = 'CLINICAL SERVICES', 'CLINICAL SERVICES'
    COMMERCIAL_CATERTING = 'COMMERCIAL CATERING', 'COMMERCIAL CATERING'
    COMPOUND_OFFICE = 'COMPOUND OFFICE', 'COMPOUND OFFICE'
    CSSU = 'CSSU', 'CSSU'
    GENERAL_ADMIN = 'GENERAL ADMIN', 'GENERAL ADMIN'
    DA_OFFICE = "DA's OFFICE", "DA's OFFICE"
    DDA_S_ACCOUNT = "DDA's (ACCOUNT)", "DDA's (ACCOUNT)"
    DISCIPLINE = 'DISCIPLINE', 'DISCIPLINE'
    ENGINEERING = 'ENGINEERING', 'ENGINEERING'
    FEMALE_WARD = 'FEMALE WARD', 'FEMALE WARD'
    FINAL_ACCOUNT = 'FINAL ACCOUNT', 'FINAL ACCOUNT'
    HAEMODIALYSIS = 'HAEMODIALYSIS', 'HAEMODIALYSIS'
    ICU = 'ICU', 'ICU'
    INFORMATION_TECHNOLOGY_UNIT = 'INFORMATION TECHNOLOGY UNIT', 'INFORMATION TECHNOLOGY UNIT'
    INTERNAL_AUDIT = 'INTERNAL AUDIT', 'INTERNAL AUDIT'
    INPLANT_STORE = 'INPLANT STORE', 'INPLANT STORE'
    JUNIOR_STAFF = 'JUNIOR STAFF', 'JUNIOR STAFF'
    LAUNDRY = 'LAUNDRY', 'LAUNDRY'
    MAIN_POWER = 'MAIN POWER', 'MAIN POWER'
    THEATRE_SIDE = 'THEATRE SIDE', 'THEATRE SIDE'
    SOPD_SIDE = 'SOPD SIDE', 'SOPD SIDE'
    TRANSPORT_DEPARTMENT = 'TRANSPORT DEPARTMENT', 'TRANSPORT DEPARTMENT'
    MEDICAL_DIRECTORS_HOUSE = "MEDICAL DIRECTOR'S HOUSE", "MEDICAL DIRECTOR'S HOUSE"
    LEGAL_UNIT = 'LEGAL UNIT', 'LEGAL UNIT'
    MAIN_OPERATING_THEATRE = 'MAIN OPERATING THEATRE', 'MAIN OPERATING THEATRE'
    MALE_WARD_1 = 'MALE WARD 1', 'MALE WARD 1'
    MALE_WARD_2 = 'MALE WARD 2', 'MALE WARD 2'
    MAXILLOFACIAL = 'MAXILLOFACIAL', 'MAXILLOFACIAL'
    MD_OFFICE = "MD's OFFICE", "MD's OFFICE"
    MEDICAL_ILLUSTRATION = 'MEDICAL ILLUSTRATION', 'MEDICAL ILLUSTRATION'
    MEDICAL_LIBRARY = 'MEDICAL LIBRARY', 'MEDICAL LIBRARY'
    MEDICAL_RECORD = 'MEDICAL RECORD', 'MEDICAL RECORD'
    MEDICAL_SOCIAL_WELFARE = 'MEDICAL SOCIAL WELFARE', 'MEDICAL SOCIAL WELFARE'
    MSSD = 'MSSD', 'MSSD'
    NHIA_ECG = 'NHIA (E.C.G)', 'NHIA (E.C.G)'
    NHIA_SECRETARY = 'NHIA SECRETARY', 'NHIA SECRETARY'
    NHIA = 'NHIA', 'NHIA'
    NURSING_EDUCATION = 'NURSING EDUCATION', 'NURSING EDUCATION'
    NURSING_SERVICES = 'NURSING SERVICES', 'NURSING SERVICES'
    O_AND_G_THEATRE = 'O&G THEATRE', 'O&G THEATRE'
    O_AND_G_UNIT = 'O&G UNIT', 'O&G UNIT'
    OCCUPATIONAL_THERAPHY = 'OCCUPATIONAL THERAPHY', 'OCCUPATIONAL THERAPHY'
    ORTHOPAEDIC_CAST = 'ORTHOPAEDIC CAST', 'ORTHOPAEDIC CAST'
    ORTHOPAEDIC_CONSULTANT = 'ORTHOPAEDIC CONSULTANT', 'ORTHOPAEDIC CONSULTANT'
    ORTHOPAEDIC_UNIT = 'ORTHOPAEDIC UNIT', 'ORTHOPAEDIC UNIT'
    OXYGEN_PLANT = 'OXYGEN PLANT', 'OXYGEN PLANT'
    P_AND_O_ICRC = 'P & O (ICRC)', 'P & O (ICRC)'
    PATHOLOGY = 'PATHOLOGY', 'PATHOLOGY'
    PAYROLL = 'PAYROLL', 'PAYROLL'
    PENSION_AND_STAFF_WELFARE = 'PENSION AND STAFF WELFARE', 'PENSION AND STAFF WELFARE'
    PERSONNEL = 'PERSONNEL', 'PERSONNEL'
    PHARMACY = 'PHARMACY', 'PHARMACY'
    PHYSIOTHERAPHY = 'PHYSIOTHERAPHY', 'PHYSIOTHERAPHY'
    PLANNING_UNIT = 'PLANNING UNIT', 'PLANNING UNIT'
    PROCUMENT = 'PROCUMENT', 'PROCUMENT'
    PROSTHETIC_AND_OTHOTICS = 'PROSTHETIC AND OTHOTICS', 'PROSTHETIC AND OTHOTICS'
    PROTOCOL_UNIT = 'PROTOCOL UNIT', 'PROTOCOL UNIT'
    PUBLIC_HEALTH = 'PUBLIC HEALTH', 'PUBLIC HEALTH'
    RADIOLOGY = 'RADIOLOGY', 'RADIOLOGY'
    RET = 'RET', 'RET'
    REVENUE = 'REVENUE', 'REVENUE'
    RGISTRTY = 'REGISTRY', 'REGISTRY'
    SCHOOL_OF_P_AND_O = 'SCHOOL OF P AND O', 'SCHOOL OF P AND O'
    SCHOOL_CONTINUOUS_EDUCATION = 'SCHOOL CONTINUOUS EDUCATION', 'SCHOOL CONTINUOUS EDUCATION'
    SECURITY_OFFICE = 'SECURITY OFFICE', 'SECURITY OFFICE'
    SENIOR_STAFF = 'SENIOR STAFF', 'SENIOR STAFF'
    SERVICOM = 'SERVICOM', 'SERVICOM'
    SOCAST = 'SOCAST', 'SOCAST'
    SOPD = 'S.O.P.D', 'S.O.P.D'
    SPINE_COMPLEX = 'SPINE COMPLEX', 'SPINE COMPLEX'
    SPINE_EXTENSION = 'SPINE EXTENSION', 'SPINE EXTENSION'
    SPINE_OPD = 'SPINE OPD', 'SPINE OPD'
    SPINE_WARD = 'SPINE WARD', 'SPINE WARD'
    STORE_AND_SUPPLIES = 'STORE AND SUPPLIES', 'STORE AND SUPPLIES'
    TELEPHONE = 'TELEPHONE', 'TELEPHONE'
    TRANSPORT = 'TRANSPORT', 'TRANSPORT'
    TAILORING_UNIT = 'TAILORING UNIT', 'TAILORING UNIT'


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
    invoice_number = models.IntegerField(null=True, blank=True)  # INTEGER per old model
    store_receiving_voucher = models.CharField(max_length=30, null=True, blank=True)
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
    issued_to = models.CharField(
        max_length=100, choices=Department.choices, null=True, blank=True
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    date_issued = models.DateField(auto_now_add=True,null=True)
    issued_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='records'
    )
    siv = models.CharField(max_length=30, null=True, blank=True)
    requisition_number = models.CharField(max_length=30, null=True, blank=True)
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
    invoice_number = models.IntegerField(null=True, blank=True)  # INTEGER as in old model
    store_receiving_voucher = models.CharField(max_length=30, null=True, blank=True)
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

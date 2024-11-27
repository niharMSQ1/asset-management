from django.db import models

class HardwareAssetsServiceNow(models.Model):
    inventory_number = models.CharField(max_length=255, unique=True)
    condition = models.CharField(max_length=255)
    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    warranty_info = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, unique=False)

    bank_loan = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, blank=True)
    expected_life_years = models.PositiveIntegerField()
    asset_end_date = models.DateField(null=True, blank=True)
    months_to_replace = models.PositiveIntegerField()
    three_month_end_alert = models.BooleanField(default=False)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    end_of_life_expected_value = models.DecimalField(max_digits=10, decimal_places=2)

    straight_line_depreciation_annual = models.DecimalField(max_digits=10, decimal_places=2)
    straight_line_depreciation_monthly = models.DecimalField(max_digits=10, decimal_places=2)

    current_value = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.item_name} ({self.inventory_number})"

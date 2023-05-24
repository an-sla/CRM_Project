from django.db import models
from django.contrib.auth.models import User


class CustomerPersonalData(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    customer_number = models.IntegerField(unique=True)


class CustomerData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Add 'blank=True'
    customer_personal_data = models.OneToOneField(CustomerPersonalData, on_delete=models.CASCADE, null=True,
                                                  default=None)

    satisfaction_score = models.IntegerField()
    cltv = models.IntegerField()
    number_of_referrals = models.IntegerField()
    tenure_in_months = models.IntegerField()
    offer = models.CharField(max_length=255)
    phone_service = models.BooleanField()
    avg_monthly_long_distance_charges = models.FloatField()
    multiple_lines = models.BooleanField()
    internet_type = models.CharField(max_length=255)
    avg_monthly_gb_download = models.IntegerField()
    online_security = models.BooleanField()
    online_backup = models.BooleanField()
    premium_tech_support = models.BooleanField()
    streaming_tv = models.BooleanField()
    streaming_movies = models.BooleanField()
    streaming_music = models.BooleanField()
    unlimited_data = models.BooleanField()
    contract = models.CharField(max_length=255)
    paperless_billing = models.BooleanField()
    payment_method = models.CharField(max_length=255)
    monthly_charge = models.FloatField()
    total_charges = models.FloatField()
    total_refunds = models.FloatField()
    total_extra_data_charges = models.IntegerField()
    total_long_distance_charges = models.FloatField()
    population = models.IntegerField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    gender = models.CharField(max_length=255)
    age = models.IntegerField()
    married = models.BooleanField()
    number_of_dependents = models.IntegerField()

    class Meta:
        verbose_name_plural = "Customer Data"

    def __str__(self):
        return f"Customer {self.pk}"


class SupportRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.TextField()
    occurrence = models.TextField()
    additional_info = models.TextField(blank=True, null=True)
    submission_time = models.DateTimeField(auto_now_add=True)

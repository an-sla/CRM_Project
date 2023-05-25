import os
import sys
import pandas as pd
import django
from my_app.models import CustomerData


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoCRM.settings')
django.setup()


def load_data():
    data = pd.read_csv('new_clients.csv')
    for index, row in data.iterrows():
        CustomerData.objects.create(
            satisfaction_score=row['satisfaction_score'],
            customer_status=row['customer_status'],
            cltv=row['cltv'],
            number_of_referrals=row['number_of_referrals'],
            tenure_in_months=row['tenure_in_months'],
            offer=row['offer'],
            phone_service=row['phone_service'],
            avg_monthly_long_distance_charges=row['avg_monthly_long_distance_charges'],
            multiple_lines=row['multiple_lines'],
            internet_type=row['internet_type'],
            avg_monthly_gb_download=row['avg_monthly_gb_download'],
            online_security=row['online_security'],
            online_backup=row['online_backup'],
            device_protection_plan=row['device_protection_plan'],
            premium_tech_support=row['premium_tech_support'],
            streaming_tv=row['streaming_tv'],
            streaming_movies=row['streaming_movies'],
            streaming_music=row['streaming_music'],
            unlimited_data=row['unlimited_data'],
            contract=row['contract'],
            paperless_billing=row['paperless_billing'],
            payment_method=row['payment_method'],
            monthly_charge=row['monthly_charge'],
            total_charges=row['total_charges'],
            total_refunds=row['total_refunds'],
            total_extra_data_charges=row['total_extra_data_charges'],
            total_long_distance_charges=row['total_long_distance_charges'],
            population=row['population'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            gender=row['gender'],
            age=row['age'],
            married=row['married'],
            number_of_dependents=row['number_of_dependents']
        )

    print("Data loaded successfully.")


if __name__ == '__main__':
    load_data()

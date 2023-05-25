import os
import django
from faker import Faker
from my_app.models import CustomerPersonalData, CustomerData


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoCRM.settings')
django.setup()


def update_customer_data(number_of_customers):
    fake = Faker()

    customers_to_update = CustomerData.objects.filter(customer_personal_data__isnull=True)[:number_of_customers]

    for customer in customers_to_update:
        first_name = fake.first_name()
        last_name = fake.last_name()
        customer_number = fake.unique.random_number(digits=6)

        customer_personal_data = CustomerPersonalData.objects.create(
            first_name=first_name,
            last_name=last_name,
            customer_number=customer_number,
        )

        customer.customer_personal_data = customer_personal_data
        customer.save()

    print(f"Updated {number_of_customers} customers.")

if __name__ == "__main__":
    update_customer_data(1961)


# This is a little Easter Egg used for testing the customer-search functionality:

# Check if customer_number 100000 exists
if not CustomerPersonalData.objects.filter(customer_number=100000).exists():
    # Get the 1957th entry by ID
    try:
        entry_1957 = CustomerPersonalData.objects.all().order_by('id')[1956]
    except IndexError:
        print("The 1957th entry does not exist.")
    else:
        # Update the entry
        entry_1957.first_name = 'John'
        entry_1957.last_name = 'Backus'
        entry_1957.customer_number = 100000
        entry_1957.save()
        print("The 1957th entry has been updated.")
else:
    print("The customer_number 100000 already exists.")

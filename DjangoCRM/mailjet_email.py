# A
from mailjet_rest import Client

def send_email(subject, message, from_email, to_emails):
    api_key = 'your_mailjet_api_key'  # Replace with your Mailjet API key
    api_secret = 'your_mailjet_api_secret'  # Replace with your Mailjet API secret

    mailjet = Client(auth=('e072459ff8cce16fef6c3c321f485f97', '6dc6ffc883ee2efc642017b6d4df3901'), version='v3.1')

    data = {
        'Messages': [
            {
                'From': {'Email': from_email},
                'To': [{'Email': email} for email in to_emails],
                'Subject': subject,
                'HTMLPart': message
            }
        ]
    }

    result = mailjet.send.create(data=data)
    return result.status_code

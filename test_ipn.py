import requests

# Replace with your actual ngrok https URL
url = " https://2d2c8962791a.ngrok-free.app/paypal-ipn/"

data = {
    "mc_gross": "19.95",
    "invoice": "1234",
    "receiver_email": "businessavanshika@testshop.com",
    "payment_status": "Completed",
    "mc_currency": "USD",
    "txn_id": "TEST_TXN_12345"
}

response = requests.post(url, data=data)

print("Status:", response.status_code)
print("Response:", response.text)

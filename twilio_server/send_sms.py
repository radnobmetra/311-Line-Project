import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

twilio_sid = os.getenv("TWILIO_SID")
twilio_token = os.getenv("TWILIO_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
client = Client(twilio_sid, twilio_token)

message = client.messages.create(
    body="TESTING",
    from_=twilio_number, 
    to="+18777804236", #This is the virtual phone number
)

print(f"Message sent! SID: {message.sid}")  
import serial
import re
from twilio.rest import Client

# Twilio Credentials (Replace with your actual credentials)
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890"  # Twilio number
YOUR_PHONE_NUMBER = "+0987654321"    # Your actual phone number

# Serial Configuration
SERIAL_PORT = "COM3"  # Change this based on your system (e.g., '/dev/ttyUSB0' for Linux)
BAUD_RATE = 9600

# Twilio Client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def extract_data(line):
    """Extract alcohol level, latitude, and longitude from serial data."""
    alcohol_match = re.search(r"Alcohol Level: (\d+)", line)
    gps_match = re.search(r"📍 Latitude: ([\d\.\-]+) , Longitude: ([\d\.\-]+)", line)

    alcohol_level = int(alcohol_match.group(1)) if alcohol_match else None
    latitude = float(gps_match.group(1)) if gps_match else None
    longitude = float(gps_match.group(2)) if gps_match else None

    return alcohol_level, latitude, longitude

def send_sms(alcohol_level, latitude, longitude):
    """Send an SMS alert."""
    message_body = f"🚨 Alert! Alcohol level detected: {alcohol_level}. \nLocation: {latitude}, {longitude}"

    message = client.messages.create(
        body=message_body,
        from_=TWILIO_PHONE_NUMBER,
        to=YOUR_PHONE_NUMBER
    )
    print(f"📩 SMS Sent: {message.sid}")

def make_alert_call(alcohol_level, latitude, longitude):
    """Make a call and read the alert message when picked up."""
    message_body = f"🚨 Alert! Alcohol level detected: {alcohol_level}. Location: {latitude}, {longitude}"

    call = client.calls.create(
        twiml=f"<Response><Say>{message_body}</Say></Response>",
        from_=TWILIO_PHONE_NUMBER,
        to=YOUR_PHONE_NUMBER
    )
    print(f"📞 Call Initiated: {call.sid}")

try:
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print("Listening for data...")
        while True:
            line = ser.readline().decode("utf-8").strip()
            if line:
                print("Serial Output:", line)
                alcohol_level, latitude, longitude = extract_data(line)

                if alcohol_level and alcohol_level > 450:  # Triggers on high alcohol level
                    print(f"🚨 High Alcohol Level Detected: {alcohol_level}")
                    
                    # Send SMS
                    send_sms(alcohol_level, latitude, longitude)
                    
                    # Make Call
                    make_alert_call(alcohol_level, latitude, longitude)

except serial.SerialException as e:
    print(f"Error: {e}")
    

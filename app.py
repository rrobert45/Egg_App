import time
import board
import adafruit_ahtx0
import RPi.GPIO as GPIO
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from flask import Flask, render_template, request

# Initialize GPIO pins for temperature and humidity control
GPIO.setmode(GPIO.BCM)
temp_pin = 23  # Change to appropriate GPIO pin for temperature control relay
humid_pin = 24  # Change to appropriate GPIO pin for humidity control relay
GPIO.setup(temp_pin, GPIO.OUT)
GPIO.setup(humid_pin, GPIO.OUT)

# Initialize AHT20 temperature and humidity sensor
i2c = board.I2C()
sensor = adafruit_ahtx0.AHTx0(i2c)

# Initialize Flask web application
app = Flask(__name__)

# Load configuration from JSON file
with open('config.json') as f:
    config = json.load(f)

# Initialize MongoDB database
uri = config['uri']
client = MongoClient(uri)
db = client[config['database']]
incubator = db[config['collection']]

# Retrieve start date and humidity ranges from configuration
start_date = datetime.strptime(config['start_date'], '%Y-%m-%d').date()
humidity_ranges = config['humidity_ranges']

# Define temperature and humidity thresholds
temp_low = 98.3  # Fahrenheit
temp_high = 100.0  # Fahrenheit
humid_low = humidity_ranges[0][0]  # Percent
humid_high = humidity_ranges[0][1]  # Percent

# Initialize variables for egg turning
turn_pin = 25  # Change to appropriate GPIO pin for egg turning relay
GPIO.setup(turn_pin, GPIO.OUT)
turn_interval = 2 * 60 * 60  # 2 hours in seconds
turn_duration = 2 * 60  # 2 minutes in seconds
last_turn = time.time()

# Define functions for temperature and humidity control
def set_temp(value):
    if value:
        GPIO.output(temp_pin, GPIO.LOW)
    else:
        GPIO.output(temp_pin, GPIO.HIGH)

def set_humid(value):
    if value:
        GPIO.output(humid_pin, GPIO.LOW)
    else:
        GPIO.output(humid_pin, GPIO.HIGH)

# Define function for egg turning
def turn_eggs():
    GPIO.output(turn_pin, GPIO.LOW)
    time.sleep(turn_duration)
    GPIO.output(turn_pin, GPIO.HIGH)

# Define function for calculating incubation day
def calculate_day():
    delta = datetime.now().date() - start_date
    return delta.days + 1

# Define function for calculating humidity based on incubation day
def calculate_humidity(day):
    if day >= 18:
        return 70
    else:
        for range in humidity_ranges:
            if day <= range[2]:
                return range[1]
        return 0

# Define function for logging data to MongoDB
def log_data(temperature, humidity, day):
    data = {'timestamp': datetime.now(), 'temperature': temperature, 'humidity': humidity, 'day': day}
    incubator.insert_one(data)

# Define Flask route for displaying web interface
@app.route('/')
def index():
    temperature = sensor.temperature * 1.8 + 32  # Convert to Fahrenheit
    humidity = sensor.relative_humidity
    temp_state = 'On' if GPIO.input(temp_pin) == GPIO.LOW else 'Off'
    humid_state = 'On' if GPIO.input(humid_pin) == GPIO.LOW else 'Off'
    day = calculate_day()
    progress = day / 21 * 100
    start_date_str = config['start_date']
    start_date = datetime.strptime(start_date_str, '%m-%d-%Y').date()
    hatch_day = start_date + timedelta(days=21)
    return render_template('index.html', temperature=temperature, humidity=humidity, temp_state=temp_state, humid_state=humid_state, day=day, progress=progress, hatch_day=hatch_day.strftime('%m-%d-%Y'), start_date=start_date.strftime('%m-%d-%Y'))
# Define Flask route for triggering egg turning
@app.route('/turn')
def turn():
    global last_turn
    if time.time() - last_turn >= turn_interval:
        last_turn = time.time()
        turn_eggs()
        return 'Egg turning triggered'
    else:
        return 'Egg turning already triggered within the last 2 hours'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

    try:
        # Main program loop
        while True:
            # Read temperature and humidity from sensor
            temperature = round(sensor.temperature * 1.8 + 32, 1)  # Convert Celsius to Fahrenheit and round to the nearest tenth
            humidity = round(sensor.relative_humidity, 1)  # Round humidity to the nearest tenth

            # Control temperature based on user-defined thresholds
            if temperature < temp_low:
                set_temp(True)
            elif temperature > temp_high:
                set_temp(False)

            # Control humidity based on calculated humidity ranges
            day = calculate_day()
            humid_target = calculate_humidity(day)
            if humid_target == 0:
                set_humid(False)
            elif humidity < humid_target - 2:
                set_humid(True)
            elif humidity > humid_target + 2:
                set_humid(False)

            # Log data to MongoDB
            log_data(temperature, humidity, day)

            # Wait 10 seconds before repeating loop
            time.sleep(10)

    except KeyboardInterrupt:
        # Cleanup GPIO pins
        GPIO.cleanup()
Egg Incubator

This Python program uses a Raspberry Pi 4B, an AHT20 temperature and humidity sensor, and a low signal relay to control the temperature and humidity in an egg incubator. The program includes an automatic egg turning feature, a web interface for monitoring the temperature, humidity, and incubation progress, and a MongoDB database for logging incubator performance data.

To use this program, follow these steps:

1. Install the required hardware, including the Raspberry Pi 4B, the AHT20 sensor, and the low signal relay.

2. Install the necessary software packages by running the following command in your terminal:

   pip install -r requirements.txt

3. Modify the `config.json` file to specify the start date of the incubation and the desired humidity ranges for different days of the incubation period.

4. Connect the low signal relay to the appropriate GPIO pins on the Raspberry Pi 4B. Update the `app.py` file to reflect the correct GPIO pin numbers for temperature control, humidity control, and egg turning.

5. Start the program by running the following command in your terminal:

   python app.py

6. View the egg incubator web interface by navigating to `http://<raspberrypi_IP_address>:5000` in your web browser.

7. Use the web interface to monitor the temperature, humidity, and incubation progress of the egg incubator. Use the egg turning feature to trigger egg turning manually or automatically.

Note: The `RPi.GPIO` library used for GPIO control requires root access. Therefore, you will need to run the program with `sudo` privileges or by adding your user to the `gpio` group using the `adduser` command.

For more information, please consult the documentation for the Raspberry Pi 4B, the AHT20 sensor, the low signal relay, the Python libraries used in this program, and the Flask web framework.

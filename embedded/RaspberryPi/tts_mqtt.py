import json
import paho.mqtt.client as mqtt
import subprocess
import dotenv
import os
import ssl

dotenv.load_dotenv()

MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT"))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
MQTT_SECRET = os.environ.get("MQTT_SECRET")
MQTT_TOPIC = os.environ.get("MQTT_TOPIC")


FILE_NAME = "binary_text.txt"


def on_message(client, userdata, msg):
    try:
        print("Received message")
        value = msg.payload.decode("utf-8")
        value = json.loads(value)

        print(value)

        with open(FILE_NAME, "w", encoding="utf-8") as f:
            f.write(value.get("audio_base64", ""))

        if value.get("audio_base64") is not None:
            subprocess.run(["python3", "binary_text_to_speech.py"])
    except Exception as e:
        print(f"Error processing message: {e}")


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)


ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = mqtt.Client()
client.username_pw_set(MQTT_USERNAME, MQTT_SECRET)
client.tls_set_context(ssl_context)
client.on_message = on_message
client.on_connect = on_connect
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)
client.loop_forever()

import json
import platform
import argparse
import os
import struct
import wave
from datetime import datetime
from dotenv import load_dotenv
import requests

import pvporcupine
from pvrecorder import PvRecorder

import pyaudio
from pydub import AudioSegment
import paho.mqtt.client as mqtt
import ssl

load_dotenv()

PLATFORM = platform.system().lower()

PICOVOICE_API_KEY = os.environ.get(f"PICOVOICE_API_KEY_{PLATFORM.upper()}")
MQTT_BROKER_HOST = os.environ.get("MQTT_BROKER_HOST")
MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT"))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")
MQTT_SECRET = os.environ.get("MQTT_SECRET")
MQTT_TOPIC = os.environ.get("MQTT_TOPIC")
MQTT_TOPIC_COMMAND = os.environ.get("MQTT_TOPIC_COMMAND")

KEYWORD_PATHS = f"./tori_{PLATFORM}.ppn"
MODEL_PATH = "./porcupine_params_ko.pv"
FILE_NAME = "binary_text.txt"

API_CONNECT_URL = f"{os.environ.get('FASTAPI_URL')}"

if not all(
    [
        MQTT_BROKER_HOST,
        MQTT_BROKER_PORT,
        MQTT_USERNAME,
        MQTT_SECRET,
        MQTT_TOPIC,
        MQTT_TOPIC_COMMAND,
    ]
):
    raise ValueError("One or more MQTT environment variables are not set.")


def convert_wav_to_mp3(wav_filename, mp3_filename):
    try:
        audio = AudioSegment.from_wav(wav_filename)
        audio.export(mp3_filename, format="mp3")
    except Exception as e:
        print("Error converting WAV to MP3:", e)
    finally:
        if os.path.exists(wav_filename):
            os.remove(wav_filename)


def delete_mp3(mp3_filename):
    if os.path.exists(mp3_filename):
        os.remove(mp3_filename)


def get_stt_result(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        response = requests.post(
            f"{API_CONNECT_URL}/stt-tts/speech-to-text/file", files={"file": audio_file}
        )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword_paths", nargs="+", default=None)
    parser.add_argument("--library_path", default=None)
    parser.add_argument("--sensitivities", nargs="+", type=float, default=None)
    parser.add_argument(
        "--audio_device_index", type=int, default=-1 if PLATFORM == "windows" else 1
    )
    parser.add_argument("--output_path", default=None)
    parser.add_argument("--show_audio_devices", action="store_true")
    args = parser.parse_args()

    def _connect_mqtt():
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        mqtt_client = mqtt.Client()
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_SECRET)
        mqtt_client.tls_set_context(ssl_context)
        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
        mqtt_client.loop_start()

        return mqtt_client

    def _publish_mqtt(message: str) -> None:
        if mqtt_client is not None:
            mqtt_client.publish(MQTT_TOPIC, message)

    def _publish_mqtt_command(command: str) -> None:
        if mqtt_client is not None:
            msg_payload = json.dumps({"type": "command", "command": command})
            mqtt_client.publish(MQTT_TOPIC_COMMAND, msg_payload)

    if args.show_audio_devices:
        for i, device in enumerate(PvRecorder.get_available_devices()):
            print("Device %d: %s" % (i, device))
        return
    keyword_paths = (
        args.keyword_paths if args.keyword_paths is not None else [KEYWORD_PATHS]
    )
    if args.sensitivities is None:
        args.sensitivities = [0.5] * len(keyword_paths)
    if len(keyword_paths) != len(args.sensitivities):
        raise ValueError(
            "Number of keywords does not match the number of sensitivities."
        )

    try:
        if PICOVOICE_API_KEY is None:
            raise ValueError("PICOVOICE_API_KEY environment variable is not set.")

        for kp in keyword_paths:
            if not os.path.isfile(kp):
                raise ValueError("Keyword path '%s' does not point to a file" % kp)

        porcupine = pvporcupine.create(
            access_key=PICOVOICE_API_KEY,
            library_path=args.library_path,
            model_path=MODEL_PATH,
            keyword_paths=keyword_paths,
            sensitivities=args.sensitivities,
        )
    except Exception as e:
        print("Failed to initialize Porcupine:", e)
        raise

    keywords = []
    for x in keyword_paths:
        keyword_phrase_part = os.path.basename(x).replace(".ppn", "").split("_")
        if len(keyword_phrase_part) > 6:
            keywords.append(" ".join(keyword_phrase_part[0:-6]))
        else:
            keywords.append(keyword_phrase_part[0])

    print("Porcupine version: %s" % porcupine.version)

    recorder = PvRecorder(
        frame_length=porcupine.frame_length, device_index=args.audio_device_index
    )

    mqtt_client = _connect_mqtt()
    recorder.start()

    wav_file = None
    if args.output_path is not None:
        wav_file = wave.open(args.output_path, "w")
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)

    print("Listening ... (press Ctrl+C to exit)")

    try:
        while True:
            pcm = recorder.read()
            result = porcupine.process(pcm)

            if wav_file is not None:
                wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

            if result >= 0:
                _publish_mqtt_command("call_tori")
                print("[%s] Detected %s" % (str(datetime.now()), keywords[result]))
                record_seconds = 3

                frame_to_read = int(
                    (porcupine.sample_rate / porcupine.frame_length) * record_seconds
                )
                frames = []
                for _ in range(frame_to_read):
                    pcm_data = recorder.read()
                    frames.extend(pcm_data)
                wav_filename = "temp.wav"
                try:
                    wf = wave.open(wav_filename, "wb")
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(porcupine.sample_rate)
                    wf.writeframes(struct.pack("h" * len(frames), *frames))
                    wf.close()
                except Exception as e:
                    print(f"Failed to save temporary WAV file: {e}")
                    continue

                mp3_filename = (
                    f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
                )
                convert_wav_to_mp3(wav_filename, mp3_filename)

                try:
                    stt = get_stt_result(mp3_filename)
                    print("STT Result:", stt.get("text", stt))
                    _publish_mqtt(stt.get("text", ""))
                except requests.exceptions.RequestException as e:
                    print("STT request failed:", e)
                except Exception as e:
                    print("STT upload or MQTT publish failed:", e)
                finally:
                    delete_mp3(mp3_filename)
                    print("Ready ...")
    except KeyboardInterrupt:
        print("Stopping ...")
    finally:
        recorder.delete()
        porcupine.delete()
        if wav_file is not None:
            wav_file.close()
        if mqtt_client is not None:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()


if __name__ == "__main__":
    main()

from pydub import AudioSegment
from pydub.playback import play
import base64
import io


FILE_NAME = "binary_text.txt"

class TextToSpeech:
    def find_file(self):
        with open(FILE_NAME, "r") as file:
            encoded_text = file.read().strip()
        return encoded_text
    
    def decode_text(self, encoded_text):
        decoded_bytes = base64.b64decode(encoded_text)
        return decoded_bytes
    
    def play_audio(self, audio_bytes):
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        play(audio_segment)


def main():
    tts = TextToSpeech()
    encoded_text = tts.find_file()
    audio_bytes = tts.decode_text(encoded_text)
    tts.play_audio(audio_bytes)


if __name__ == "__main__":
    main()
FROM python:3.11-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
  libcamera-apps \
  libcamera-dev \
  python3-opencv \
  mosquitto \
  mosquitto-clients \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-libav \
  portaudio19-dev \
  libsndfile1 \
  ffmpeg \
  alsa-utils \
  supervisor \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY binary_text_to_speech.py .
COPY camera_server.py .
COPY main.py .
COPY main_pico.py .
COPY tts_mqtt.py .
COPY porcupine_params_ko.pv .
COPY tori_linux.ppn .

# supervisord 설정 파일 생성
RUN echo "[supervisord]\n\
  nodaemon=true\n\
  logfile=/var/log/supervisor/supervisord.log\n\
  pidfile=/var/run/supervisord.pid\n\
  \n\
  [program:main]\n\
  command=python3 main.py\n\
  directory=/app\n\
  autostart=true\n\
  autorestart=true\n\
  stderr_logfile=/var/log/supervisor/main.err.log\n\
  stdout_logfile=/var/log/supervisor/main.out.log\n\
  \n\
  [program:main_pico]\n\
  command=python3 main_pico.py\n\
  directory=/app\n\
  autostart=true\n\
  autorestart=true\n\
  stderr_logfile=/var/log/supervisor/main_pico.err.log\n\
  stdout_logfile=/var/log/supervisor/main_pico.out.log\n\
  \n\
  [program:tts_mqtt]\n\
  command=python3 tts_mqtt.py\n\
  directory=/app\n\
  autostart=true\n\
  autorestart=true\n\
  stderr_logfile=/var/log/supervisor/tts_mqtt.err.log\n\
  stdout_logfile=/var/log/supervisor/tts_mqtt.out.log" > /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /var/log/supervisor

ENV PYTHONUNBUFFERED=1

EXPOSE 8081

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

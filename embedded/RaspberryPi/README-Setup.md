```bash
sudo apt update
sudo apt upgrade
sudo apt install -y libcamera-apps libcamera-dev

APT_LIBCAMERA_PATH="/usr/lib/python3/dist-packages/libcamera" 
PYENV_SITE_PACKAGES="/home/buriburi/.pyenv/versions/3.11.14/lib/python3.11/site-packages"

ln -s $APT_LIBCAMERA_PATH $PYENV_SITE_PACKAGES/libcamera

sudo apt install -y python3-opencv

sudo apt-get install -y mosquitto mosquitto-clients

sudo systemctl start mosquitto
sudo systemctl enable mosquitto

pip install aiortc pyopenvidu websockets

sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-libav
```
# 우분투에서 ros 실행

## roslaunch dofbot_config demo.launch

---

## 쥬피터랩 실행

jupyter lab

```txt
http://192.168.253.128:8888
```

---

## app 실행

로봇 USB 목록
ls -l /dev/serial/by-path

```txt
lrwxrwxrwx 1 root root 13 11月 12 14:42 pci-0000:02:00.0-usb-0:2.1:1.0-port0 -> ../../ttyUSB0
lrwxrwxrwx 1 root root 13 11月 12 14:42 pci-0000:02:00.0-usb-0:2.2:1.0-port0 -> ../../ttyUSB1
```

cd S13P31E108/embedded/BotControl

python app_mqtt_sep_topic.py which_arm=left
python app_mqtt_sep_topic.py which_arm=right

---

## 비디오 USB 목록

ls -l /dev/v4l/by-path | sed 's/ -> /\t-> /'

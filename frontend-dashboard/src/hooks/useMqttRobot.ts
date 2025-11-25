// useMqttRobot.ts
import { useState, useEffect, useRef } from "react";
import mqtt, { MqttClient } from "mqtt";
import { useRobotLog } from "../hooks/useRobotLog";
import type { BackboneStatus } from "../components/types/robot";

interface RobotStatus {
  joint0: number;
  joint1: number;
  joint2: number;
  joint3: number;
  joint4: number;
  joint5: number;
  gripper: number;
  lastUpdated?: Date;
  connected: boolean;
}

interface MqttRobotState {
  leftArm: RobotStatus;
  rightArm: RobotStatus;
  backbone: BackboneStatus;
  connectionStatus: "connected" | "disconnected" | "connecting";
}

const MQTT_CONFIG = {
  brokerUrl: import.meta.env.VITE_MQTT_BROKER_URL,
  username: import.meta.env.VITE_MQTT_USERNAME,
  password: import.meta.env.VITE_MQTT_PASSWORD,
  baseTopic: "buriburi",
  clientId: "frontend-web",
  topics: {
    rx: "buriburi/robot/rx", // 프론트엔드 -> 로봇 (사용안함)
    tx: "buriburi/robot/joint", // 로봇 -> 프론트엔드 (관절 각도)
    event: "buriburi/robot/event", // 로봇 -> 백엔드 (로봇 시작/완료)
  },
};

const DEFAULT_ROBOT_STATUS: RobotStatus = {
  joint0: 90,
  joint1: 90,
  joint2: 90,
  joint3: 90,
  joint4: 90,
  joint5: 90,
  gripper: 0,
  connected: false,
};

const DEFAULT_BACKBONE_STATUS: BackboneStatus = {
  neckYaw: 90,
  neckPitch: 90,
  waistYaw: 90,
};

export function useMqttRobot(): MqttRobotState {
  const [state, setState] = useState<MqttRobotState>({
    leftArm: { ...DEFAULT_ROBOT_STATUS },
    rightArm: { ...DEFAULT_ROBOT_STATUS },
    backbone: { ...DEFAULT_BACKBONE_STATUS },
    connectionStatus: "disconnected",
  });

  const clientRef = useRef<MqttClient | null>(null);

  const initialized = useRef(false);

  const { appendLog } = useRobotLog(20);

  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const connect = () => {
      if (clientRef.current) return;

      setState((prev) => ({ ...prev, connectionStatus: "connecting" }));

      const clientId = `${MQTT_CONFIG.clientId}-${Math.random()
        .toString(16)
        .slice(2)}`;

      try {
        const client = mqtt.connect(MQTT_CONFIG.brokerUrl, {
          clientId,
          username: MQTT_CONFIG.username,
          password: MQTT_CONFIG.password,
          keepalive: 30,
          reconnectPeriod: 2000,
        });

        client.on("connect", () => {
          console.log("MQTT Connected");
          setState((prev) => ({ ...prev, connectionStatus: "connected" }));

          // 로봇 관절 각도 수신 토픽 구독
          client.subscribe(MQTT_CONFIG.topics.tx, (err) => {
            if (err) {
              console.error("Subscribe error:", err);
            } else {
              console.log("Subscribed to:", MQTT_CONFIG.topics.tx);
            }
          });

          // 로봇 상태 이벤트 수신 토픽 구독
          client.subscribe(MQTT_CONFIG.topics.event, (err) => {
            if (err) {
              console.error("Subscribe error:", err);
            } else {
              console.log("Subscribed to:", MQTT_CONFIG.topics.event);
            }
          });

          // 연결 확인용 hello 메시지
          client.publish(
            MQTT_CONFIG.topics.rx,
            JSON.stringify({
              type: "hello",
              agent: "frontend",
              timestamp: new Date().toISOString(),
            })
          );
        });

        client.on("message", (topic, payload) => {
          try {
            const data = JSON.parse(payload.toString());
            // console.log(data)

            // 로컬스토리지 저장
            if (topic === MQTT_CONFIG.topics.event) {
              if (data.robot_id === "robot_left") {
                appendLog({
                  type: data.type,
                  ts: data.ts,
                  rb_command: data.command,
                });
              }
            }

            // joint_state 메시지 처리
            if (data.type === "joint_state" && Array.isArray(data.angles)) {
              const robotId = data.robot_id;
              const angles = data.angles;

              if (data.robot_id == "robot_left") {
                // console.log(data)
              }

              if (robotId === "robot_left" || robotId === "robot_right") {
                const robotStatus: RobotStatus = {
                  joint0: angles[0] ?? 90,
                  joint1: angles[1] ?? 90,
                  joint2: angles[2] ?? 90,
                  joint3: angles[3] ?? 90,
                  joint4: angles[4] ?? 90,
                  joint5: angles[5] ?? 90,
                  gripper: angles[6] ?? 0,
                  lastUpdated: new Date(),
                  connected: true,
                };

                setState((prev) => ({
                  ...prev,
                  [robotId === "robot_left" ? "leftArm" : "rightArm"]:
                    robotStatus,
                }));
              } else if (robotId === "robot_backbone") {
                const backboneStatus: BackboneStatus = {
                  neckYaw: angles[0] ?? 90,
                  neckPitch: angles[1] ?? 90,
                  waistYaw: angles[2] ?? 90,
                  lastUpdated: new Date(),
                };

                setState((prev) => ({
                  ...prev,
                  backbone: backboneStatus,
                }));
              }
            }
          } catch (error) {
            console.error("Failed to parse MQTT message:", error);
          }
        });

        client.on("error", (error) => {
          console.error("MQTT error:", error);
          setState((prev) => ({ ...prev, connectionStatus: "disconnected" }));
        });

        client.on("close", () => {
          console.log("MQTT disconnected");
          setState((prev) => ({
            ...prev,
            connectionStatus: "disconnected",
            leftArm: { ...prev.leftArm, connected: false },
            rightArm: { ...prev.rightArm, connected: false },
          }));
        });

        client.on("reconnect", () => {
          console.log("MQTT reconnecting...");
          setState((prev) => ({ ...prev, connectionStatus: "connecting" }));
        });

        clientRef.current = client;
      } catch (error) {
        console.error("MQTT connection failed:", error);
        setState((prev) => ({ ...prev, connectionStatus: "disconnected" }));
      }
    };

    connect();

    return () => {
      if (clientRef.current) {
        clientRef.current.end(true);
        clientRef.current = null;
      }
    };
  }, [appendLog]);

  return state;
}

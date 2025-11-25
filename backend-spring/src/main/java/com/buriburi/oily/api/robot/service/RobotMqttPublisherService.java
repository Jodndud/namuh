package com.buriburi.oily.api.robot.service;

import com.buriburi.oily.api.robot.constant.RobotCommandMap;
import com.buriburi.oily.api.robot.entity.RobotStatus;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.integration.mqtt.support.MqttHeaders;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.support.MessageBuilder;
import org.springframework.stereotype.Service;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class RobotMqttPublisherService {

    private final RobotSTOMPService robotSTOMPService;

    @Value("${spring.mqtt.topic}")
    private String DEFAULT_TOPIC;

    @Qualifier("mqttOutboundChannel")
    private final MessageChannel mqttOutboundChannel;

    private static final Map<String, RobotStatus> CMD_TO_STATUS = Map.ofEntries(
            Map.entry("good_morning", RobotStatus.GOOD_MORNING),
            Map.entry("good_night",  RobotStatus.GOOD_NIGHT),
            Map.entry("ate_all",     RobotStatus.ATE_ALL),
            Map.entry("hungry",      RobotStatus.HUNGRY)
    );

    /**
     * command를 MQTT로 발행하고, 매핑되는 상태를 Redis/WS에 반영.
     */
    public void publishAndSync(String command, String robotId) {
        try {
            // 1) MQTT payload 생성
            String payload = buildPayload(command, robotId);

            // 2) MQTT 발행
            var message = MessageBuilder.withPayload(payload)
                    .setHeader(MqttHeaders.TOPIC, DEFAULT_TOPIC)
                    .build();

            mqttOutboundChannel.send(message);

            log.info("✅ [MQTT OUT] command={}, robotId={}, topic={}, payload={}",
                    command, robotId, DEFAULT_TOPIC, payload);

            // 3) Redis & STOMP 상태 갱신
//            RobotStatus status = RobotCommandMap.getStatus(command);
//            Long targetRobotId = 1L;
//            if (status == null) {
//                robotSTOMPService.updateStatus(targetRobotId, "UNKNOWN");
//                return;
//            }
//            robotSTOMPService.updateStatus(targetRobotId, status.name());

        } catch (Exception e) {
            log.error("❌ [MQTT OUT] command 발행 실패. command={}, robotId={}", command, robotId, e);
        }
    }

    private String buildPayload(String command, String robotId) {
        return """
                {
                  "type": "command",
                  "command": "%s",
                  "robot_id": "%s"
                }
                """.formatted(command, robotId != null ? robotId : DEFAULT_TOPIC)
                .replace("\n", "")
                .replace("  ", " ");
    }
}

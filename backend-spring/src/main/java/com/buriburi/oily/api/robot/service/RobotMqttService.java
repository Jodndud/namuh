package com.buriburi.oily.api.robot.service;

import com.buriburi.oily.api.robot.entity.RobotStatus;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.messaging.Message;
import org.springframework.stereotype.Service;
import com.buriburi.oily.api.robot.constant.RobotCommandMap;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class RobotMqttService {

    private final ObjectMapper objectMapper;
    private final RobotSTOMPService robotSTOMPService;

    // command → RobotStatus 매핑 규칙
    private static final Map<String, RobotStatus> CMD_TO_STATUS = Map.ofEntries(
            Map.entry("init_pose", RobotStatus.IDLE),
            Map.entry("make_heart", RobotStatus.HEART),
            Map.entry("make_hug", RobotStatus.HUG),
            Map.entry("make_hello", RobotStatus.HI),
            Map.entry("rock", RobotStatus.ROCK),
            Map.entry("scissors", RobotStatus.SCISSORS),
            Map.entry("paper", RobotStatus.PAPER),
            Map.entry("good_morning", RobotStatus.GOOD_MORNING),
            Map.entry("good_night", RobotStatus.GOOD_NIGHT),
            Map.entry("ate_all", RobotStatus.ATE_ALL),
            Map.entry("hungry", RobotStatus.HUNGRY)
    );

    @ServiceActivator(inputChannel = "mqttInputChannel")
    public void handleMqttMessage(Message<?> message) {
        String payloadStr = String.valueOf(message.getPayload());
//        log.info("📥 MQTT payload: {}", payloadStr);

        try {
            JsonNode root = objectMapper.readTree(payloadStr);
            String command = root.path("command").asText(null);
            if (command == null) {
                return;
            }

            RobotStatus status = RobotCommandMap.getStatus(command);
            Long robotId = 1L;
            robotSTOMPService.updateStatus(robotId, status.name());

        } catch (Exception e) {
            log.error("❌ Failed to process MQTT payload: {}", payloadStr, e);
        }
    }

    private RobotStatus mapCommandToStatus(String command) {
        if (command == null) return RobotStatus.UNKNOWN;
        return CMD_TO_STATUS.getOrDefault(command.toLowerCase(), RobotStatus.UNKNOWN);
    }
}
package com.buriburi.oily.api.robot.service;

import com.buriburi.oily.api.robot.dto.in.RobotStatusMessage;
import com.buriburi.oily.api.robot.entity.RobotStatus;
import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.response.BaseResponseStatus;
import com.buriburi.oily.global.util.RedisUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;

@Slf4j
@Service
@RequiredArgsConstructor
public class RobotSTOMPService {

    private final SimpMessagingTemplate messagingTemplate;
    private final RedisUtils redisUtils;

    private static String topicOf(Long robotId) {
        return "/sub/robot/" + robotId;
    }

    private static String redisKeyOf(Long robotId) {
        return "robot:status:" + robotId;
    }

    /**
     * MQTT메시지 Redis저장
     */
    public void updateStatus(Long robotId, String statusRaw) {
        RobotStatus status = parseStatus(statusRaw);
        RobotStatusMessage message = new RobotStatusMessage(robotId, status.name());

        redisUtils.setValue(redisKeyOf(robotId), message); // 저장
        messagingTemplate.convertAndSend(topicOf(robotId), message); // 전송
    }

    private RobotStatus parseStatus(String raw) {
        if (!StringUtils.hasText(raw)) {
            throw new BaseException(BaseResponseStatus.INVALID_INPUT_VALUES);
        }
        try {
            return RobotStatus.valueOf(raw.trim().toUpperCase());
        } catch (IllegalArgumentException ex) {
            throw new BaseException(BaseResponseStatus.INVALID_INPUT_VALUES);
        }
    }
}
// RobotWsController.java (기존 RobotController 대체 권장)
package com.buriburi.oily.api.robot.controller;

import com.buriburi.oily.api.robot.dto.in.RobotStatusRequest;
import com.buriburi.oily.api.robot.dto.in.RobotStatusMessage;
import com.buriburi.oily.api.robot.entity.RobotStatus;
import com.buriburi.oily.api.robot.service.RobotSTOMPService;
import com.buriburi.oily.global.util.RedisUtils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.handler.annotation.DestinationVariable;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.simp.annotation.SubscribeMapping;
import org.springframework.stereotype.Controller;

@Controller
@RequiredArgsConstructor
@Slf4j
public class RobotSTOMPController {

    private final RedisUtils redisUtils;

    private static String redisKeyOf(Long robotId) {
        return "robot:status:" + robotId;
    }

    /**
     * 클라이언트가 "/sub/robot/{robotId}" 구독할 때,
     * Redis에 status가 있으면 1번 내려주고,
     * 없으면 null (전송 없음) 처리.
     */
    @SubscribeMapping("/robot/{robotId}")
    public RobotStatusMessage initialStatus(@DestinationVariable Long robotId) {
        return redisUtils.getValue(redisKeyOf(robotId), RobotStatusMessage.class)
                .orElse(null); // 없으면 초기 상태 없음 -> 이후 실시간 업데이트만 받음
    }
}
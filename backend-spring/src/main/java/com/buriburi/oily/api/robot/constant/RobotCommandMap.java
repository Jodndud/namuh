package com.buriburi.oily.api.robot.constant;

import com.buriburi.oily.api.robot.entity.RobotStatus;

import java.util.Map;

/**
 * MQTT / Redis / STOMP 등에서 사용하는
 * 로봇 command → RobotStatus 매핑 상수.
 */
public final class RobotCommandMap {

    private RobotCommandMap() {} // 생성자 private → 인스턴스화 방지

    public static final Map<String, RobotStatus> COMMAND_TO_STATUS = Map.ofEntries(
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
            Map.entry("hungry", RobotStatus.HUNGRY),
            Map.entry("set_joint", RobotStatus.SET_JOINT)
    );

    public static RobotStatus getStatus(String command) {
        if (command == null) return RobotStatus.UNKNOWN;
        return COMMAND_TO_STATUS.getOrDefault(command.toLowerCase(), RobotStatus.UNKNOWN);
    }
}

package com.buriburi.oily.api.robot.dto.in;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class RobotStatusMessage {
    private Long id;
    private String status;
}

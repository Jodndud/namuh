package com.buriburi.oily.api.robot.properties;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Getter
@Setter
@Component
@ConfigurationProperties(prefix = "robot.scheduler.cron")

public class RobotSchedulerCronProperties {
    private String goodMorning;
    private String goodNight;
    private String ateAll;
    private String hungry;
}

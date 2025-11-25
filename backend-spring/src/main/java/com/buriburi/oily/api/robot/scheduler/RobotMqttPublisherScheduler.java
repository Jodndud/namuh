package com.buriburi.oily.api.robot.scheduler;

import com.buriburi.oily.api.robot.service.RobotMqttPublisherService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import static com.buriburi.oily.global.constant.BaseConstants.TIME_ZONE;

@Slf4j
@Component
@RequiredArgsConstructor
public class RobotMqttPublisherScheduler {

    private final RobotMqttPublisherService robotCommandPublisher;

    // 매일 08:00 - 굿모닝
    @Scheduled(cron = "${robot.scheduler.cron.good-morning}", zone = TIME_ZONE)
    public void scheduleGoodMorning() {
        robotCommandPublisher.publishAndSync("good_morning", "all");
    }

    // 매일 21:00 - 굿나잇
    @Scheduled(cron = "${robot.scheduler.cron.good-night}", zone = TIME_ZONE)
    public void scheduleGoodNight() {
        robotCommandPublisher.publishAndSync("good_night", "all");
    }

    // 매일 13:00 - 다 먹었음
    @Scheduled(cron = "${robot.scheduler.cron.ate-all}", zone = TIME_ZONE)
    public void scheduleAteAll() {
        robotCommandPublisher.publishAndSync("ate_all", "all");
    }

    // 매일 12:00 - 배고픔
    @Scheduled(cron = "${robot.scheduler.cron.hungry}", zone = TIME_ZONE)
    public void scheduleHungry() {
        robotCommandPublisher.publishAndSync("hungry", "all");
    }
}
package com.buriburi.oily.api.robot.repository;

import com.buriburi.oily.api.robot.entity.Robot;
import org.springframework.data.jpa.repository.JpaRepository;

public interface RobotRepository extends JpaRepository<Robot, Long> {
}

package com.buriburi.oily.api.robot.entity;

import com.buriburi.oily.api.robot.entity.RobotStatus;
import com.buriburi.oily.global.support.BaseEntity;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor
@Table(name = "robot")
public class Robot extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "code", nullable = false, length = 10)
    private String code;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false, length = 30)
    private RobotStatus status;

    @Column(name = "title", nullable = false, length = 10)
    private String title;

    // 상태 변경 메서드
    public void updateStatus(RobotStatus status) {
        if (status != null) {
            this.status = status;
        }
    }
}


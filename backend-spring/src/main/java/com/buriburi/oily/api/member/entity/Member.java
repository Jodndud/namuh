package com.buriburi.oily.api.member.entity;

import com.buriburi.oily.global.support.BaseEntity;
import jakarta.persistence.*;
import lombok.*;
import org.springframework.util.StringUtils;

@Entity
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Member {
    /**
     * PK
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 이메일 (로그인 ID)
     */
    @Column(nullable = false, length = 100)
    private String email;

    /**
     * 닉네임 (2~10자)
     */
    @Column(nullable = false, length = 10)
    private String nickname;

    /**
     * 권한
     */
    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    private Role role;

    /**
     * 고유 UUID
     */
    @Column(nullable = false, length = 60)
    private String uuid;

    public void updateNickname(String nickname) {
        if (StringUtils.hasText(nickname)) {
            this.nickname = nickname;
        }
    }
}

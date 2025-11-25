package com.buriburi.oily.api.member.entity;

import jakarta.persistence.*;
import lombok.*;

/**
 * 회원 소셜 계정 연동 엔티티.
 *
 * <p>
 * 외부 소셜 로그인 계정을 회원 계정에 매핑한다.
 * </p>
 *
 * <ul>
 * <li>email은 고유(UNIQUE)</li>
 * <li>(provider_name, provider_id) 조합은 고유(UNIQUE)</li>
 * <li>member_id, provider_name에 인덱스 생성</li>
 * </ul>
 */
@Entity
@Table(name = "member_social", uniqueConstraints = {
        @UniqueConstraint(name = "uk_msocial_email", columnNames = "email"),
        @UniqueConstraint(name = "uk_msocial_provider", columnNames = { "provider_name", "provider_id" })
}, indexes = {
        @Index(name = "idx_msocial_member", columnList = "member_id"),
        @Index(name = "idx_msocial_pname", columnList = "provider_name")
})
@Getter
@Setter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MemberSocial {

    /** PK */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 연동 대상 회원 */
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "member_id", nullable = false, foreignKey = @ForeignKey(name = "FK_member_social_member"))
    private Member member;

    /** 소셜 이메일 (고유) */
    @Column(name = "email", nullable = false, length = 100)
    private String email;

    /** 소셜 제공자 (GOOGLE / NAVER / KAKAO) */
    @Enumerated(EnumType.STRING)
    @Column(name = "provider_name", nullable = false, length = 10)
    private SocialProvider providerName;

    /** 제공자 내부 식별자 (provider_name과의 복합 고유) */
    @Column(name = "provider_id", nullable = false, length = 255)
    private String providerId;
}


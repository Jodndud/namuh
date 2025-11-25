package com.buriburi.oily.api.media.entity;

import com.buriburi.oily.global.support.BaseEntity;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

/**
 * 미디어 파일 메타정보 엔티티
 * <p>
 * 경매/후기/카드/카테고리/회원 등의 리소스에 연결되는 이미지·영상의 메타데이터를 저장한다.
 * </p>
 * <ul>
 * <li>(type, owner_id, seq_no) 복합 고유 제약으로 리소스별 대표/순번 유일성 보장</li>
 * <li>url은 고유(UNIQUE)하게 관리</li>
 * <li>(type, owner_id) 조회용 복합 인덱스와 owner_id 단일 인덱스 제공</li>
 * </ul>
 */
@Entity
@Table(name = "media", uniqueConstraints = {
        @UniqueConstraint(name = "uk_media_owner_seq", columnNames = {"type", "owner_id", "seq_no"})}, indexes = {
        @Index(name = "idx_media_type_owner", columnList = "type,owner_id"),
        @Index(name = "idx_media_owner", columnList = "owner_id")})
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Media extends BaseEntity {

    /**
     * 미디어 ID (PK)
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * 소유 리소스 타입 (예: AUCTION_ITEM, MEMBER_PROFILE 등)
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false, length = 30)
    private MediaType type;

    /**
     * 소유 리소스 ID
     */
    @Column(name = "owner_id", nullable = false)
    private Long ownerId;

    /**
     * 접근 key (고유)
     */
    @Column(name = "s3key_or_url", nullable = false, length = 255)
    private String s3keyOrUrl;

    /**
     * MIME 타입 (예: image/jpeg)
     */
    @Column(name = "mime_type", length = 30)
    private String mimeType;

    /**
     * 리소스 내 정렬 순번 (1=대표)
     */
    @Column(name = "seq_no", nullable = false)
    private Integer seqNo;

    /**
     * 순번 설정
     *
     * @param seq
     */
    public void setSeqNo(int seq) {
        this.seqNo = seq;
    }
}

package com.buriburi.oily.api.media.dto.response;

import com.buriburi.oily.api.media.entity.Media;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

public record SmileThumbnailResponse(
        @Schema(description = "미디어 ID") Long id,
        @Schema(description = "소유자 ID") Long owner_id,
        @Schema(description = "S3 Key 또는 URL") String s3key_or_url,
        @Schema(description = "MIME 타입") String mime_type,
        @Schema(description = "미디어 유형") String type,
        @Schema(description = "순번") Integer seq_no,
        @Schema(description = "생성 시각") LocalDateTime created_at,
        @Schema(description = "수정 시각") LocalDateTime updated_at
) {
    public static SmileThumbnailResponse from(Media media) {
        return new SmileThumbnailResponse(
                media.getId(),
                media.getOwnerId(),
                media.getS3keyOrUrl(),
                media.getMimeType(),
                media.getType().name(),
                media.getSeqNo(),
                media.getCreatedAt(),
                media.getUpdatedAt()
        );
    }
}
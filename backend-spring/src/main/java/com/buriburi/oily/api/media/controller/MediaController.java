package com.buriburi.oily.api.media.controller;

import com.buriburi.oily.api.media.dto.response.SmileOwnerVideoResponse;
import com.buriburi.oily.api.media.dto.response.SmileThumbnailResponse;
import com.buriburi.oily.api.media.service.MediaService;
import com.buriburi.oily.global.response.BaseResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@Tag(name = "Media", description = "범용 미디어 API")
@Validated
@RestController
@RequestMapping("/v1/media")
@RequiredArgsConstructor
public class MediaController {

    private final MediaService mediaService;

    @Operation(summary = "S3 연결 헬스체크 테스트",
            description = "S3 버킷 접근이 가능한지 확인합니다.")
    @GetMapping("/health-check")
    public BaseResponse<Boolean> healthCheck() {
        return BaseResponse.onSuccess(mediaService.healthCheck());
    }

    @Operation(summary = "웃음 영상 썸네일 전체 조회", description = "type이 ROBOT_VIDEO_TUMBNAIL인 미디어를 전체 반환합니다.")
    @GetMapping("/smile-videos")
    public BaseResponse<List<SmileThumbnailResponse>> getSmileVideos() {
        return BaseResponse.onSuccess(mediaService.findAllSmileVideoThumbnails());
    }

    @Operation(summary = "특정 소유자의 웃음 영상 조회")
    @GetMapping("/smile-videos/{seq_no}")
    public BaseResponse<List<SmileOwnerVideoResponse>> getSmileVideosByOwner(
            @PathVariable("seq_no") Integer seqNo
    ) {
        return BaseResponse.onSuccess(mediaService.findSmileVideoThumbnailsBySeqNo(seqNo));
    }
}

package com.buriburi.oily.api.channel.controller;

import com.buriburi.oily.api.channel.dto.in.ConnectionRequestDto;
import com.buriburi.oily.api.channel.dto.out.SessionResponseDto;
import com.buriburi.oily.api.channel.dto.out.TokenResponseDto;
import com.buriburi.oily.api.channel.service.ChannelService;
import com.buriburi.oily.global.response.BaseResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RequestMapping("/v1/channels")
@Tag(name = "WebRTC Session Channel")
@RequiredArgsConstructor
@RestController
public class ChannelController {

    private final ChannelService channelService;

    @Operation(summary = "WebRTC 채널 연결 및 토큰 발급",
            description = "채널 ID와 역할(PUBLISHER/SUBSCRIBER)을 기반으로 OpenVidu 토큰을 발급합니다. 세션이 없으면 자동 생성됩니다.")
    @PostMapping("/{channelId}/connections")
    public BaseResponse<TokenResponseDto> createConnection(
            @Parameter(description = "참여자 모두가 공유할 고유 채널 ID") @PathVariable String channelId,
            @Valid @RequestBody ConnectionRequestDto requestDto) {
        return BaseResponse.onSuccess(channelService.createConnection(channelId, requestDto));
    }

    @Operation(summary = "WebRTC 채널 정보 조회",
            description = "현재 채널의 세션 ID와 참여자 ID 목록을 조회합니다.")
    @GetMapping("/{channelId}")
    public BaseResponse<SessionResponseDto> getChannelInfo(@Parameter(description = "조회할 채널 ID") @PathVariable String channelId) {
        return BaseResponse.onSuccess(channelService.getSessionInfo(channelId));
    }

    @Operation(summary = "WebRTC 채널 참여자 퇴장",
            description = "특정 참여자를 채널에서 퇴장시킵니다.")
    @DeleteMapping("/{channelId}/connections/{participantId}")
    public BaseResponse<Void> leaveChannel(
            @Parameter(description = "채널 ID") @PathVariable String channelId,
            @Parameter(description = "퇴장시킬 참여자 ID") @PathVariable String participantId
    ) {
        channelService.leaveSession(channelId, participantId);
        return BaseResponse.onSuccess();
    }
}

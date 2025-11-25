package com.buriburi.oily.api.channel.dto.in;

import jakarta.validation.constraints.NotNull;

public record ConnectionRequestDto(
        @NotNull(message = "참여 ID를 입력해주세요.")
        String participantId,

        @NotNull(message = "역할을 입력해주세요. ")
        String role
) {
}

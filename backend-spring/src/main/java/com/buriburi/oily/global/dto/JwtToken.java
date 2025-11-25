package com.buriburi.oily.global.dto;

import lombok.Builder;

@Builder
public record JwtToken(
        String grantType,
        String accessToken,
        String refreshToken
) {
}

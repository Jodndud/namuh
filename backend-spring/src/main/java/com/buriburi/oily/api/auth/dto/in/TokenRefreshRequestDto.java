package com.buriburi.oily.api.auth.dto.in;

import jakarta.validation.constraints.NotBlank;

public record TokenRefreshRequestDto(
        @NotBlank String refreshToken
) {}

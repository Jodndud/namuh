package com.buriburi.oily.api.auth.dto.out;

import lombok.Builder;
import lombok.Getter;
import lombok.ToString;
import org.springframework.web.util.UriComponentsBuilder;

/**
 * 소셜 로그인 응답 DTO
 */
@ToString
@Getter
@Builder
public class SocialSignInResponseDto {
    private Boolean isFirstLogin;
    private Integer code;

    public static String toQueryParams(boolean isFirstLogin) {
        return UriComponentsBuilder.newInstance()
                .queryParam("code", 200)
                .queryParam("isFirstLogin", isFirstLogin)
                .build().getQuery();
    }
}

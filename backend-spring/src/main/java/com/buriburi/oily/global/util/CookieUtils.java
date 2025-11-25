package com.buriburi.oily.global.util;

import com.buriburi.oily.global.constant.SecurityConstants;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseCookie;
import org.springframework.stereotype.Component;

/**
 * HTTP 쿠키 관련 유틸리티 기능을 제공하는 클래스
 */
@Component
public class CookieUtils {

    @Value("${spring.profiles.active:local}") // 현재 활성화된 프로파일을 주입받습니다.
    private String activeProfile;

    public void setRefreshTokenCookie(HttpServletResponse response, String refreshToken, int time) {
        boolean isProduction = activeProfile.equalsIgnoreCase("prod") || activeProfile.equalsIgnoreCase("production");

        ResponseCookie refreshCookie = ResponseCookie.from(SecurityConstants.REFRESH_TITLE, refreshToken)
                .httpOnly(true)
                .path("/")
                .maxAge(time)
                .secure(isProduction)
                .sameSite(isProduction ? "None" : "Lax")
                .build();
        response.addHeader("Set-Cookie", refreshCookie.toString()); // TODO-SECURITY: 추후 RT 쿠키 헤더 노출 제거 필요
    }
}

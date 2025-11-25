package com.buriburi.oily.global.security.handler.strategy;

import com.buriburi.oily.api.auth.dto.out.SocialSignInResponseDto;
import com.buriburi.oily.api.auth.service.TokenAuthService;
import com.buriburi.oily.global.properties.SecurityOAuth2Properties;
import com.buriburi.oily.global.security.dto.UserDetailsDto;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * 기존 소셜 계정이 있을 경우 -> 서버 자체 JWT 토큰 발행 후 로그인 성공
 */
@Component
@RequiredArgsConstructor
public class UserDetailsDtoSuccessHandlerStrategy implements OAuth2SuccessHandlerStrategy {

    private final TokenAuthService tokenAuthService;
    // private final OAuth2Utils oAuth2Utils;

    private final SecurityOAuth2Properties securityOAuth2Properties;

    @Override
    public boolean supports(Authentication authentication, HttpServletRequest request) {
        return authentication.getPrincipal() instanceof UserDetailsDto;
                // && !oAuth2Utils.isSocialLink(request);
    }

    @Override
    public void handle(Authentication authentication, HttpServletRequest request, HttpServletResponse response) throws IOException {
        UserDetailsDto userDetailsDto = (UserDetailsDto) authentication.getPrincipal();
        tokenAuthService.issueJwt(userDetailsDto, response);
        /*
         * 지정 리다이렉트 경로로 로그인 정보를 쿼리 파라미터에, RefreshToken은 Cookie 에 담아 리턴(리다이렉트라 AccessToken은 응답되지 않음)
         */
        String queryParams = SocialSignInResponseDto.toQueryParams(false);
        String targetUrl = securityOAuth2Properties.getClientRedirectUri() + "?" + queryParams;
        response.setStatus(HttpServletResponse.SC_FOUND); // 302
        response.setHeader("Location", targetUrl);
    }
}

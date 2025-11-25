package com.buriburi.oily.api.auth.service;

import static com.buriburi.oily.global.constant.SecurityConstants.*;
import com.buriburi.oily.global.dto.JwtToken;
import com.buriburi.oily.global.security.dto.UserDetailsDto;
import com.buriburi.oily.global.security.provider.TokenBlackListService;
import com.buriburi.oily.global.security.provider.TokenProvider;
import com.buriburi.oily.global.security.provider.TokenService;
import com.buriburi.oily.global.util.CookieUtils;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;

import java.time.Duration;

@Service
@RequiredArgsConstructor
public class TokenAuthServiceImpl implements TokenAuthService {

    private final TokenService tokenService;
    private final TokenBlackListService tokenBlackListService;

    private final CookieUtils cookieUtils;
    private final TokenProvider tokenProvider;

    @Value("${security.jwt.expire-time.refresh-token}")
    private Duration refreshExpiration;


    @Override
    public void issueJwt(UserDetailsDto userDetails, HttpServletResponse response) {
        JwtToken jwtToken = tokenService.generateToken(userDetails);
        response.addHeader(HttpHeaders.AUTHORIZATION, GRANT_TYPE + jwtToken.accessToken());
        cookieUtils.setRefreshTokenCookie(response, jwtToken.refreshToken(), (int) refreshExpiration.getSeconds());
    }

    @Override
    public void signOut(HttpServletRequest request, HttpServletResponse response) {
        String accessToken = tokenProvider.getTokenFromRequest(request);
        String memberUuid = tokenProvider.getSubjectFromToken(accessToken);

        tokenService.deleteRefreshToken(memberUuid);
        tokenBlackListService.addBlacklistAccessToken(accessToken);
        cookieUtils.setRefreshTokenCookie(response, "", 0);
    }

    @Override
    public void refreshAccessToken(HttpServletResponse response, String refreshToken) {
        JwtToken newTokens = tokenService.refresh(refreshToken);
        response.addHeader(HttpHeaders.AUTHORIZATION, GRANT_TYPE + newTokens.accessToken());
        cookieUtils.setRefreshTokenCookie(response, newTokens.refreshToken(), (int) refreshExpiration.getSeconds());
    }
}

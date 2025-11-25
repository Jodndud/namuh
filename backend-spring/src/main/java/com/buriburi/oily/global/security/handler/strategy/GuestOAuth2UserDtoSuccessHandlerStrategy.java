package com.buriburi.oily.global.security.handler.strategy;

import com.buriburi.oily.api.auth.service.SocialSignUpService;
import com.buriburi.oily.api.auth.service.TokenAuthService;
import com.buriburi.oily.api.member.entity.Member;
import com.buriburi.oily.global.properties.SecurityOAuth2Properties;
import com.buriburi.oily.global.security.dto.GuestOAuth2UserDto;
import com.buriburi.oily.global.security.dto.UserDetailsDto;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * 최초 OAuth 로그인일 경우 -> 일반 회원가입 진행
 */
@Component
@RequiredArgsConstructor
public class GuestOAuth2UserDtoSuccessHandlerStrategy implements OAuth2SuccessHandlerStrategy {

    private final SocialSignUpService socialSignUpService;
    private final TokenAuthService tokenAuthService;
    private final SecurityOAuth2Properties securityOAuth2Properties;

    @Override
    public boolean supports(Authentication authentication, HttpServletRequest request) {
        return authentication.getPrincipal() instanceof GuestOAuth2UserDto;
    }

    @Override
    public void handle(Authentication authentication, HttpServletRequest request, HttpServletResponse response) throws IOException {
        GuestOAuth2UserDto guestOAuth2UserDto = (GuestOAuth2UserDto) authentication.getPrincipal();

        // 소셜 정보를 바탕으로 DB에 신규 회원 정보를 저장하고, 저장된 Member 객체를 반환받음
        Member newMember = socialSignUpService.signUp(guestOAuth2UserDto.getOAuth2UserInfo());

        // 반환받은 Member 객체로 UserDetailsDto를 생성
        UserDetailsDto userDetailsDto = new UserDetailsDto(newMember, guestOAuth2UserDto.getOAuth2UserInfo());

        // 생성된 UserDetailsDto를 기반으로 JWT를 발급
        tokenAuthService.issueJwt(userDetailsDto, response);

        // 로그인 성공 후 최종적으로 클라이언트를 리다이렉트시킴
        String targetUrl = securityOAuth2Properties.getClientRedirectUri(); // 또는 로그인 성공 페이지
        response.setStatus(HttpServletResponse.SC_FOUND); // 302
        response.setHeader("Location", targetUrl);
    }
}

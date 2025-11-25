package com.buriburi.oily.global.security.dto;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.core.user.OAuth2User;

import java.util.Collection;
import java.util.Collections;
import java.util.Map;

/**
 * 최초 OAuth 로그인일 경우 -> 회원가입 추가 진행
 */
@Getter
@RequiredArgsConstructor
public class GuestOAuth2UserDto implements OAuth2User {

    private Map<String, Object> attributes;
    private final OAuth2UserInfo oAuth2UserInfo;

    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return Collections.singletonList(new SimpleGrantedAuthority("ROLE_GUEST"));
    }

    @Override
    public String getName() {
        return this.oAuth2UserInfo.getProviderId();
    }
}

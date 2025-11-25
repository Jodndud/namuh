package com.buriburi.oily.global.security.provider;

import com.buriburi.oily.api.member.entity.SocialProvider;
import com.buriburi.oily.global.security.dto.OAuth2UserInfo;
import org.springframework.security.oauth2.core.user.OAuth2User;

public interface OAuth2UserInfoFactory {
    boolean supports(SocialProvider providerName);

    OAuth2UserInfo create(OAuth2User oAuth2User);
}

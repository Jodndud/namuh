package com.buriburi.oily.global.security.provider;

import com.buriburi.oily.api.member.entity.SocialProvider;
import com.buriburi.oily.global.security.dto.GoogleUserInfo;
import com.buriburi.oily.global.security.dto.OAuth2UserInfo;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Component;

@Component
public class GoogleOAuth2UserInfoFactory implements OAuth2UserInfoFactory {
    @Override
    public boolean supports(SocialProvider providerName) {
        return SocialProvider.GOOGLE.equals(providerName);
    }

    @Override
    public OAuth2UserInfo create(OAuth2User oAuth2User) {
        return new GoogleUserInfo(oAuth2User.getAttributes());
    }
}

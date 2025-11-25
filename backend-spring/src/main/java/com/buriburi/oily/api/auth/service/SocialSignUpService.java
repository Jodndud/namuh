package com.buriburi.oily.api.auth.service;

import com.buriburi.oily.api.member.entity.Member;
import com.buriburi.oily.global.security.dto.OAuth2UserInfo;

public interface SocialSignUpService {
    Member signUp(OAuth2UserInfo oAuth2UserInfo);
}

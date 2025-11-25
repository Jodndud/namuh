package com.buriburi.oily.api.member.entity;

import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.response.BaseResponseStatus;
import org.springframework.util.StringUtils;

import java.util.Locale;

/**
 * 소셜 로그인 제공자
 */
public enum SocialProvider {
    GOOGLE,
    NAVER,
    KAKAO;

    public static SocialProvider from(String providerName) {
        if (!StringUtils.hasText(providerName)) {
            throw new BaseException(BaseResponseStatus.UNSUPPORTED_SOCIAL_PROVIDER);
        }
        try {
            return SocialProvider.valueOf(providerName.toUpperCase(Locale.ROOT));
        } catch (IllegalArgumentException e) {
            throw new BaseException(BaseResponseStatus.UNSUPPORTED_SOCIAL_PROVIDER);
        }
    }
}

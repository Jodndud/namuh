package com.buriburi.oily.global.constant;

/**
 * Security 관련 상수 정의
 */
public final class SecurityConstants {

    private SecurityConstants() {
    }

    public static final String GRANT_TYPE = "Bearer ";
    public static final String AUTHORITIES_CLAIM = "auth";
    public static final String MEMBER_CLAIM = "member";

    public static final String BLACKLIST_ACCESS_PREFIX = "jwt-blacklist-at:";
    public static final String BLACKLIST_REFRESH_PREFIX = "jwt-blacklist-rt:";

    public static final String REFRESH_PREFIX = "jwt-rt:";
    public static final String REFRESH_MEMBER_MAPPING_PREFIX = "member-rt:";
    public static final String REFRESH_TITLE ="refreshToken";

    // 소셜 연동 관련
    public static final String SOCIAL_SIGNUP_TOKEN_PREFIX = "social-signup-token:";
    public static final String SOCIAL_LINK_TOKEN_PREFIX = "social-link-token:";
    public static final String SOCIAL_LINK_SESSION_NAME = "social-link-request";
    public static final String SOCIAL_LINK_SESSION_TOKEN_NAME = "social-link-token";
}

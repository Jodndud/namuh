package com.buriburi.oily.global.properties;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Spring Security OAuth2 관련 설정을 담는 클래스
 *
 * @param authorizeUri      로그인을 위해 리디렉션 될 OAuth2 서비스의 인증 엔드포인트 URI
 * @param redirectUri       인증 성공 후 인증 코드(Authorization code)와 함께 리디렉션될 백엔드 서버의 콜백 URI
 * @param clientRedirectUri 모든 인증 절차를 마친 후 최종적으로 리디렉션시킬 프론트엔드 애플리케이션의 URI
 */
@Getter
@Setter
@ConfigurationProperties(prefix = "spring.security.oauth2")
public class SecurityOAuth2Properties {
    private String authorizeUri;
    private String redirectUri;
    private String clientRedirectUri;
}

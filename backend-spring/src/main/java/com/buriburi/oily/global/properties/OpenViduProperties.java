package com.buriburi.oily.global.properties;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Openvidu 관련 환경변수를 주입받는 클래스
 */
@Getter
@Setter
@Component
@ConfigurationProperties(prefix = "openvidu")
public class OpenViduProperties {
    private String url;
    private String secret;
    private String sessionPrefix;
}

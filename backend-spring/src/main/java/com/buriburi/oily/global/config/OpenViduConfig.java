package com.buriburi.oily.global.config;

import com.buriburi.oily.global.properties.OpenViduProperties;
import io.openvidu.java.client.OpenVidu;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Openvidu의 Configuration 클래스
 */
@Configuration
@RequiredArgsConstructor
@EnableConfigurationProperties({OpenViduProperties.class})
public class OpenViduConfig {

    private final OpenViduProperties openViduProperties;

    @Bean
    public OpenVidu openVidu() {
        return new OpenVidu(openViduProperties.getUrl(), openViduProperties.getSecret());
    }
}

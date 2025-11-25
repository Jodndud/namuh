package com.buriburi.oily.global.properties;

import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.List;

@ConfigurationProperties(prefix = "security.cors")
public record SecurityCorsProperties(
        List<String> allowedOrigins,
        List<String> allowedMethods,
        List<String> allowedHeaders,
        Boolean allowCredentials,
        List<String> exposedHeaders,
        Long maxAge
) {
}

package com.buriburi.oily.global.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import static com.buriburi.oily.global.constant.SecurityConstants.*;

@Slf4j
@Configuration
public class SwaggerConfig {

    @Value("${swagger.uri}")
    private String swaggerUri;

    @Bean
    OpenAPI openAPI() {
        String securityJwtName = "JWT";

        SecurityRequirement securityRequirement = new SecurityRequirement().addList(securityJwtName);
        Components components = new Components().addSecuritySchemes(securityJwtName, new SecurityScheme().name(securityJwtName).type(SecurityScheme.Type.HTTP).scheme(GRANT_TYPE.trim()).bearerFormat(securityJwtName));

        return new OpenAPI().addSecurityItem(securityRequirement).components(components).addServersItem(new Server().url(swaggerUri)).info(apiInfo());
    }

    private Info apiInfo() {
        return new Info().title("Buriburi - Oily Service").version("v1")
                .description("Oily Server API Documentation")
                .version("1.0.0");
    }
}

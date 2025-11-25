package com.buriburi.oily;

import com.buriburi.oily.global.properties.SecurityCorsProperties;
import io.swagger.v3.oas.annotations.OpenAPIDefinition;
import io.swagger.v3.oas.annotations.servers.Server;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties(SecurityCorsProperties.class)
@OpenAPIDefinition(servers = {
        @Server(url= "/spring")
})
public class OilyApplication {
    public static void main(String[] args) {
        SpringApplication.run(OilyApplication.class, args);
    }

}

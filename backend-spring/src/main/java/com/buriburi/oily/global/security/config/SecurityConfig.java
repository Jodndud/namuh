package com.buriburi.oily.global.security.config;

import com.buriburi.oily.api.member.entity.Role;
import com.buriburi.oily.global.properties.SecurityCorsProperties;
import com.buriburi.oily.global.properties.SecurityOAuth2Properties;

import com.buriburi.oily.global.properties.SecurityRoleProperties;
import com.buriburi.oily.global.properties.SecurityWhitelistProperties;
import com.buriburi.oily.global.security.filter.BaseExceptionHandlerFilter;
import com.buriburi.oily.global.security.handler.*;
import com.buriburi.oily.global.security.filter.JwtAuthenticationFilter;
import com.buriburi.oily.global.security.provider.CustomOauth2UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.autoconfigure.security.servlet.PathRequest;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityCustomizer;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.util.StringUtils;
import org.springframework.web.cors.*;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
@EnableConfigurationProperties({
        SecurityCorsProperties.class, SecurityOAuth2Properties.class,
        SecurityWhitelistProperties.class, SecurityRoleProperties.class
})
public class SecurityConfig {

    /* properties */
    private final SecurityCorsProperties corsProperties;
    private final SecurityWhitelistProperties whitelistProperties;
    private final SecurityOAuth2Properties oauth2Properties;
    private final SecurityRoleProperties roleProperties;

    /* filter */
    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final BaseExceptionHandlerFilter baseExceptionHandlerFilter;

    /* handler */
    private final CustomOauth2UserService oAuth2UserService;
    private final OAuth2SuccessHandler oAuth2LoginSuccessHandler;

    private final CustomAccessDeniedHandler accessDeniedHandler;
    private final CustomAuthenticationEntryPoint authenticationEntryPoint;

    private final ClientRegistrationRepository clientRegistrationRepository;

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        return http
                /* 기본 보안 설정 */
                .cors(c -> c.configurationSource(corsConfigurationSource()))
                .csrf(AbstractHttpConfigurer::disable)
                .formLogin(AbstractHttpConfigurer::disable)
                .httpBasic(AbstractHttpConfigurer::disable)
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))

                /* 경로별 인가 규칙 설정 */
                .authorizeHttpRequests(auth -> {
                    whitelistProperties.getParsedWhitelist().forEach((method, urls) -> {
                        if (urls != null && !urls.isEmpty()) {
                            String[] urlPatterns = urls.stream().filter(StringUtils::hasText).map(String::trim)
                                    .toArray(String[]::new);
                            if (urlPatterns.length > 0) {
                                auth.requestMatchers(method, urlPatterns).permitAll();
                            }
                        }
                    });
                    auth.requestMatchers(roleProperties.admin().toArray(new String[0]))
                            .hasAuthority(Role.ADMIN.getRoleName());
                    auth.anyRequest().authenticated();
                })

                /* OAuth2 설정 */
                .oauth2Login(oauth -> oauth
                        .authorizationEndpoint(endpoint -> endpoint
                                .authorizationRequestResolver(  // 인가 URI: 사용자가 구글 로그인 페이지로 리다이렉트될 때 쓰는 엔드포인트
                                        new CustomAuthorizationRequestResolver(clientRegistrationRepository, oauth2Properties.getAuthorizeUri())
                                )
                        )
                        .redirectionEndpoint(endpoint -> endpoint       // 콜백 URI: 구글이 code를 돌려줄 때 호출되는 엔드포인트
                                .baseUri(oauth2Properties.getRedirectUri())
                        )
                        .userInfoEndpoint(userInfo -> userInfo
                                .userService(oAuth2UserService))
                        .successHandler(oAuth2LoginSuccessHandler)
                )

                /* 커스텀 JWT 필터 등록 */
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
                .addFilterBefore(baseExceptionHandlerFilter, JwtAuthenticationFilter.class)

                /* Exception Handler */
                .exceptionHandling(exception -> exception
                        .authenticationEntryPoint(authenticationEntryPoint) // 인증
                        .accessDeniedHandler(accessDeniedHandler)      // 실패(401)
                )
                .build();
    }

    /* 정적 리소스(js, css, image 등)에 대해 Spring Security 필터 체인을 적용하지 않도록 설정 */
    @Bean
    public WebSecurityCustomizer webSecurityCustomizer() {
        return web -> web.ignoring().requestMatchers(PathRequest.toStaticResources().atCommonLocations());
    }

    /* CORS 정책 설정 */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();

        configuration.setAllowedOrigins(corsProperties.allowedOrigins());
        configuration.setAllowedMethods(corsProperties.allowedMethods());
        configuration.setAllowedHeaders(corsProperties.allowedHeaders());
        configuration.setAllowCredentials(corsProperties.allowCredentials());
        configuration.setExposedHeaders(corsProperties.exposedHeaders());
        configuration.setMaxAge(corsProperties.maxAge());

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}

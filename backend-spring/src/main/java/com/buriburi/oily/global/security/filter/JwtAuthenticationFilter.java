package com.buriburi.oily.global.security.filter;

import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.properties.SecurityWhitelistProperties;

import static com.buriburi.oily.global.response.BaseResponseStatus.*;

import com.buriburi.oily.global.security.provider.TokenBlackListService;
import com.buriburi.oily.global.security.provider.TokenProvider;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.util.StringUtils;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final TokenProvider tokenProvider;
    private final TokenBlackListService tokenBlackListService;
    private final SecurityWhitelistProperties securityWhitelistProperties;
    private final AntPathMatcher antPathMatcher = new AntPathMatcher();

    @Override
    protected void doFilterInternal(@NonNull HttpServletRequest request, @NonNull HttpServletResponse response,
                                    @NonNull FilterChain filterChain) throws ServletException, IOException {
        String contextPath = request.getContextPath();
        String uri = request.getRequestURI().substring(contextPath.length());
        String method = request.getMethod();
        boolean permitAll = isPermitAll(method, uri);

        String token = tokenProvider.getTokenFromRequest(request);

        if (!StringUtils.hasText(token)) {
            filterChain.doFilter(request, response);
            return;
        }

        // 토큰이 있으면 항상 시도
        try {
            // 토큰이 유효한지 검사
            if (tokenProvider.validateToken(token)) {
                // 블랙리스트에 있는지 검사
                if (tokenBlackListService.isBlacklistAccessToken(token)) {
                    // 보호 경로라면 즉시 에러, permitAll 이면 게스트 처리
                    if (!permitAll)
                        throw new BaseException(INVALID_JWT_TOKEN);
                    SecurityContextHolder.clearContext();
                } else {
                    // 토큰이 유효하면 인증 정보를 설정
                    Authentication authentication = tokenProvider.getAuthentication(token);
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                }
            } else {
                // 유효하지 않은 토큰
                if (!permitAll) {
                    throw new BaseException(INVALID_JWT_TOKEN);
                }
                SecurityContextHolder.clearContext(); // permitAll이면 게스트로
            }
        } catch (BaseException ex) {
            // 보호 경로에서의 에러는 그대로 던지게 하고,
            // (전역 예외 핸들러/EntryPoint에서 401 응답 처리)
            throw ex;
        } catch (Exception ex) {
            // 기타 예외도 보호 경로면 에러, permitAll이면 게스트
            if (!permitAll) {
                throw ex;
            }
            SecurityContextHolder.clearContext();
        }

        filterChain.doFilter(request, response);
    }

    private boolean isPermitAll(String method, String uri) {
        return securityWhitelistProperties.getParsedWhitelist().entrySet().stream().anyMatch(entry -> {
            String httpMethodFromConfig = entry.getKey().name();
            boolean methodMatches = httpMethodFromConfig.equalsIgnoreCase(method);
            if (!methodMatches) {
                return false;
            }
            return entry.getValue().stream().anyMatch(pattern -> antPathMatcher.match(pattern, uri));
        });
    }
}

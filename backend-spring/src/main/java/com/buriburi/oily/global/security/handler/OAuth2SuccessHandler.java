package com.buriburi.oily.global.security.handler;

import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.security.handler.strategy.OAuth2SuccessHandlerStrategy;

import com.buriburi.oily.global.util.OAuth2Utils;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.web.authentication.AuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.List;

@Component
@RequiredArgsConstructor
public class OAuth2SuccessHandler implements AuthenticationSuccessHandler {

    private final List<OAuth2SuccessHandlerStrategy> strategies;
    private final OAuth2Utils oAuth2Utils;

    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws IOException, ServletException {
        try {
            for (OAuth2SuccessHandlerStrategy strategy : strategies) {
                if (strategy.supports(authentication, request)) {
                    strategy.handle(authentication, request, response);
                    return;
                }
            }
        } catch (BaseException e) {
            throw oAuth2Utils.oauth2Exception(e.getStatus());
        }
    }
}
package com.buriburi.oily.global.security.handler.strategy;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.core.Authentication;

import java.io.IOException;

/**
 * OAuth2 인증 성공 후 유형에 따라 처리할 로직 분기
 */
public interface OAuth2SuccessHandlerStrategy {

    boolean supports(Authentication authentication, HttpServletRequest request);

    void handle(Authentication authentication, HttpServletRequest request, HttpServletResponse response) throws IOException;

}

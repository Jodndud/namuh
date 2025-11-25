package com.buriburi.oily.global.security.handler;

import com.buriburi.oily.global.response.BaseResponseStatus;
import com.buriburi.oily.global.util.ErrorResponseUtils;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class CustomAuthenticationEntryPoint implements AuthenticationEntryPoint {

    private static final Logger log = LoggerFactory.getLogger(CustomAuthenticationEntryPoint.class);

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response,
                         AuthenticationException authException) throws IOException, ServletException {
        log.warn("Authentication required: {}", authException.getMessage());
        ErrorResponseUtils.setErrorResponse(response, BaseResponseStatus.AUTHENTICATION_REQUIRED);
    }
}

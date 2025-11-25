package com.buriburi.oily.global.security.handler;

import com.buriburi.oily.global.response.BaseResponseStatus;
import com.buriburi.oily.global.util.ErrorResponseUtils;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

@Component
public class CustomAccessDeniedHandler implements AccessDeniedHandler {

    private static final Logger log = LoggerFactory.getLogger(CustomAccessDeniedHandler.class);

    @Override
    public void handle(HttpServletRequest request, HttpServletResponse response,
                       AccessDeniedException accessDeniedException) throws IOException, ServletException {
        log.warn("Access Denied for request {}: {}", request.getRequestURI(), accessDeniedException.getMessage());
        ErrorResponseUtils.setErrorResponse(response, BaseResponseStatus.ACCESS_DENIED);
    }
}

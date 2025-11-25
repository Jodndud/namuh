package com.buriburi.oily.api.auth.controller;

import com.buriburi.oily.api.auth.service.TokenAuthService;
import com.buriburi.oily.global.constant.SecurityConstants;
import com.buriburi.oily.global.response.BaseResponse;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/v1/auth")
public class AuthController {

    private final TokenAuthService tokenAuthService;

    @PostMapping("/refresh")
    public BaseResponse<Void> refresh(
            @CookieValue(value = SecurityConstants.REFRESH_TITLE) String refreshToken, HttpServletResponse response
    ) {
        tokenAuthService.refreshAccessToken(response, refreshToken);
        return BaseResponse.onSuccess();
    }

    @PostMapping("/logout")
    public BaseResponse<Void> logout(HttpServletRequest request, HttpServletResponse response) {
        tokenAuthService.signOut(request, response);
        return BaseResponse.onSuccess();
    }
}

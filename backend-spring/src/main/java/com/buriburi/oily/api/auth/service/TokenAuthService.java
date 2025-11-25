package com.buriburi.oily.api.auth.service;

import com.buriburi.oily.global.security.dto.UserDetailsDto;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

public interface TokenAuthService {

    void issueJwt(UserDetailsDto userDetails, HttpServletResponse response);

    void signOut(HttpServletRequest request, HttpServletResponse response);

    void refreshAccessToken(HttpServletResponse response, String refreshToken);
}

package com.buriburi.oily.global.security.provider;

import org.springframework.stereotype.Service;

@Service
public interface TokenBlackListService {
    void addBlacklistAccessToken(String accessToken);

    void addBlacklistRefreshToken(String refreshToken);

    boolean isBlacklistAccessToken(String accessToken);

    boolean isBlacklistRefreshToken(String refreshToken);
}

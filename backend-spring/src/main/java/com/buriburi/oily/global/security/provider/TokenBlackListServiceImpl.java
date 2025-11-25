package com.buriburi.oily.global.security.provider;

import static com.buriburi.oily.global.constant.SecurityConstants.*;
import com.buriburi.oily.global.util.RedisUtils;
import io.jsonwebtoken.Claims;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.Date;

/**
 * JWT 토큰을 블랙리스트에 추가하고 검증하는 서비스 구현체
 */
@Service
@RequiredArgsConstructor
public class TokenBlackListServiceImpl implements TokenBlackListService {

    private final RedisUtils redisUtils;
    private final TokenProvider tokenProvider;

    private void addBlacklist(String prefix, String token) {
        String key = prefix + token;
        Claims claims = tokenProvider.parseClaims(token);
        Date expiration = claims.getExpiration();
        long now = System.currentTimeMillis();
        long remaining = expiration.getTime() - now;

        if (remaining > 0) {
            redisUtils.setValue(key, "blacklisted", Duration.ofMillis(remaining)); // 남은 만료 시간까지 블랙리스트 처리
        }
    }

    @Override
    public void addBlacklistAccessToken(String accessToken) {
        addBlacklist(BLACKLIST_ACCESS_PREFIX, accessToken);
    }

    @Override
    public void addBlacklistRefreshToken(String refreshToken) {
        addBlacklist(BLACKLIST_REFRESH_PREFIX, refreshToken);
    }

    private boolean isBlacklist(String prefix, String token) {
        String key = prefix + token;
        return redisUtils.keyExists(key);
    }

    @Override
    public boolean isBlacklistAccessToken(String accessToken) {
        return isBlacklist(BLACKLIST_ACCESS_PREFIX, accessToken);
    }

    @Override
    public boolean isBlacklistRefreshToken(String refreshToken) {
        return isBlacklist(BLACKLIST_REFRESH_PREFIX, refreshToken);
    }
}

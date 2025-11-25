package com.buriburi.oily.global.security.provider;


import com.buriburi.oily.global.dto.JwtToken;
import com.buriburi.oily.global.security.dto.UserDetailsDto;

public interface TokenService {
    JwtToken generateToken(UserDetailsDto userDetails);

    JwtToken refresh(String refreshToken);

    void deleteRefreshToken(String memberUuid);
}

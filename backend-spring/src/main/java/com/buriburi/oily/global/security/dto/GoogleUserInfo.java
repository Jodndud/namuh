package com.buriburi.oily.global.security.dto;

import com.buriburi.oily.api.member.entity.SocialProvider;
import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.Map;

@Getter
@AllArgsConstructor
public class GoogleUserInfo implements OAuth2UserInfo {

    private final Map<String, Object> attributes;

    @Override
    public SocialProvider getProvider() {
        return SocialProvider.GOOGLE;
    }

    @Override
    public String getProviderId() {
        return (String) attributes.get("sub");
    }

    @Override
    public String getEmail() {
        return (String) attributes.get("email");
    }

    @Override
    public String getName() {
        return (String) attributes.getOrDefault("name", "user");
    }

    @Override
    public Map<String, Object> getAttributes() {
        return attributes;
    }
}

package com.buriburi.oily.global.security.config;

import jakarta.servlet.http.HttpServletRequest;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.web.DefaultOAuth2AuthorizationRequestResolver;
import org.springframework.security.oauth2.client.web.OAuth2AuthorizationRequestResolver;
import org.springframework.security.oauth2.core.endpoint.OAuth2AuthorizationRequest;

import java.util.HashMap;
import java.util.Map;

public class CustomAuthorizationRequestResolver implements OAuth2AuthorizationRequestResolver {

    private final OAuth2AuthorizationRequestResolver defaultResolver;

    public CustomAuthorizationRequestResolver(ClientRegistrationRepository repo, String authorizationRequestBaseUri) {
        defaultResolver = new DefaultOAuth2AuthorizationRequestResolver(repo, authorizationRequestBaseUri);
    }

    @Override
    public OAuth2AuthorizationRequest resolve(HttpServletRequest request) {
        OAuth2AuthorizationRequest req = defaultResolver.resolve(request);
        if (req != null) {
            return customAuthorizationRequest(req);
        }
        return null;
    }

    @Override
    public OAuth2AuthorizationRequest resolve(HttpServletRequest request, String clientRegistrationId) {
        OAuth2AuthorizationRequest req = defaultResolver.resolve(request, clientRegistrationId);
        if (req != null) {
            return customAuthorizationRequest(req);
        }
        return null;
    }

    private OAuth2AuthorizationRequest customAuthorizationRequest(OAuth2AuthorizationRequest oldReq) {
        Map<String, Object> additionalParams = new HashMap<>(oldReq.getAdditionalParameters());
        additionalParams.put("prompt", "select_account");

        return OAuth2AuthorizationRequest.from(oldReq)
                .additionalParameters(additionalParams)
                .build();
    }
}

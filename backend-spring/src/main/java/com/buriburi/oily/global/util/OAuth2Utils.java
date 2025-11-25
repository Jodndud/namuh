package com.buriburi.oily.global.util;

import com.buriburi.oily.global.constant.SecurityConstants;
import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.response.BaseResponseStatus;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.OAuth2Error;
import org.springframework.stereotype.Component;

@Component
public class OAuth2Utils {

    public OAuth2AuthenticationException oauth2Exception(BaseResponseStatus status) {
        return new OAuth2AuthenticationException(
                new OAuth2Error(status.name().toLowerCase()),
                new BaseException(status)
        );
    }

    /**
     * 회원가입과 로그인 절차를 한꺼번에 처리하므로 현재 사용하지 않음
     */
    public boolean isSocialLink(HttpServletRequest request) {
        HttpSession session = request.getSession(false);
        return isSocialLink(session);
    }

    public boolean isSocialLink(HttpSession session) {
        return session != null && "true".equals(session.getAttribute(SecurityConstants.SOCIAL_LINK_SESSION_NAME));
    }

}

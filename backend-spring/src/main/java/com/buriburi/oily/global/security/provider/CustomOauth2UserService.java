package com.buriburi.oily.global.security.provider;

import com.buriburi.oily.api.member.entity.MemberSocial;
import com.buriburi.oily.api.member.entity.SocialProvider;
import com.buriburi.oily.api.member.repository.MemberSocialRepository;
import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.response.BaseResponseStatus;
import com.buriburi.oily.global.security.dto.GuestOAuth2UserDto;
import com.buriburi.oily.global.security.dto.OAuth2UserInfo;
import com.buriburi.oily.global.security.dto.UserDetailsDto;
import com.buriburi.oily.global.util.OAuth2Utils;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.OAuth2Error;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
@Slf4j
@RequiredArgsConstructor
public class CustomOauth2UserService extends DefaultOAuth2UserService {

    private final MemberSocialRepository memberSocialRepository;
    private final List<OAuth2UserInfoFactory> oAuth2UserInfoFactories;
    private final OAuth2Utils oAuth2Utils;

    /**
     * 소셜 정보 또는 멤버 정보를 담은 OAuth2User(UserDetails) 객체를 생성
     * - 요청 성공 (CustomOAuth2SuccessHandler 에서 처리)
     * - 요청 실패 (CustomAuthenticationEntryPoint 에서 처리(JWT 필터로 내려감))
     */
    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        try {
            OAuth2User oAuth2User = super.loadUser(userRequest);
            SocialProvider providerName = SocialProvider.from(userRequest.getClientRegistration().getRegistrationId());

            // Provider 별로 OAuth2UserInfo 구현체 선택
            OAuth2UserInfo oAuth2UserInfo = oAuth2UserInfoFactories.stream()
                    .filter(factory -> factory.supports(providerName))
                    .findFirst()
                    .map(factory -> factory.create(oAuth2User))
                    .orElseThrow(() -> new BaseException(BaseResponseStatus.UNSUPPORTED_SOCIAL_PROVIDER));

            // Handler 에 내려줄 유저 정보 객체 생성
            Optional<MemberSocial> memberSocial = memberSocialRepository.findByProviderNameAndProviderId(providerName, oAuth2UserInfo.getProviderId());

            if (memberSocial.isPresent()) { // 기존에 가입한 소셜 계정 -> 로그인 진행
                return new UserDetailsDto(memberSocial.get().getMember(), oAuth2UserInfo);
            }

            return new GuestOAuth2UserDto(oAuth2UserInfo); // 최초 소셜 로그인 사용자 -> 해당 이메일 주소로 일반 회원가입 진행
        } catch (BaseException e) {
            log.warn("[Security] loadUser failed with BaseException: {}", e.getStatus().getMessage());
            throw oAuth2Utils.oauth2Exception(e.getStatus());
        }
    }
}

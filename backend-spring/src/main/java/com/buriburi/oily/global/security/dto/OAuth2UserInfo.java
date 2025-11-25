package com.buriburi.oily.global.security.dto;

import com.buriburi.oily.api.member.entity.Member;
import com.buriburi.oily.api.member.entity.MemberSocial;
import com.buriburi.oily.api.member.entity.Role;
import com.buriburi.oily.api.member.entity.SocialProvider;

import java.util.Map;
import java.util.UUID;

public interface OAuth2UserInfo {
    SocialProvider getProvider();
    String getProviderId(); // sub(google), id(kakao/naver 변환 시)
    String getEmail();
    String getName();
    Map<String, Object> getAttributes();

    default Member toMemberEntity(String nickname) {
        return Member.builder()
                .uuid(UUID.randomUUID().toString())
                .nickname(nickname)
                .email(getEmail())
                .role(Role.USER)
                .build();
    }

    default MemberSocial toMemberSocialEntity(Member member) {
        return MemberSocial.builder()
                .member(member)
                .email(getEmail())
                .providerId(getProviderId())
                .providerName(getProvider())
                .build();
    }
}

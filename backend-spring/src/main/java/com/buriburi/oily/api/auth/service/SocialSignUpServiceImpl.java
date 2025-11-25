package com.buriburi.oily.api.auth.service;

import com.buriburi.oily.api.member.entity.Member;
import com.buriburi.oily.api.member.repository.MemberRepository;
import com.buriburi.oily.api.member.repository.MemberSocialRepository;
import com.buriburi.oily.global.security.dto.OAuth2UserInfo;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import java.time.Duration;

@Service
@RequiredArgsConstructor
public class SocialSignUpServiceImpl implements SocialSignUpService {

    private final MemberRepository memberRepository;
    private final MemberSocialRepository memberSocialRepository;
    private final NicknameService nicknameService;

    @Value("${expire-time.sign-up-expire-time}")
    private Duration socialSignUpExpMin;

    @Override
    public Member signUp(OAuth2UserInfo oAuth2UserInfo) {
        // 랜덤 닉네임 생성
        String randomNickname = nicknameService.getRandomNickname();

        // Member 및 MemberSocial 엔티티 생성 및 저장
        Member newMember = oAuth2UserInfo.toMemberEntity(randomNickname);
        memberRepository.save(newMember);
        memberSocialRepository.save(oAuth2UserInfo.toMemberSocialEntity(newMember));
        return newMember;
    }
}

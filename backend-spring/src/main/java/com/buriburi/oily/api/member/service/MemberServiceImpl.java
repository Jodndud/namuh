package com.buriburi.oily.api.member.service;

import com.buriburi.oily.api.member.dto.in.UpdateNicknameRequest;
import com.buriburi.oily.api.member.entity.Member;
import com.buriburi.oily.api.member.repository.MemberRepository;
import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.response.BaseResponseStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

@Service
@RequiredArgsConstructor
@Transactional
public class MemberServiceImpl implements MemberService {

    private final MemberRepository memberRepository;

    @Override
    public void updateNickname(Member member, UpdateNicknameRequest requestDto) {
        if (requestDto == null || !StringUtils.hasText(requestDto.nickname())) {
            throw new BaseException(BaseResponseStatus.INVALID_INPUT_VALUES);
        }

        String newNickname = requestDto.nickname().trim();

        // 중복 닉네임 체크
        if (memberRepository.existsByNickname(newNickname)) {
            throw new BaseException(BaseResponseStatus.DUPLICATE_NICKNAME);
        }

        // member null 방어 (비정상 인증 상황)
        if (member == null || member.getId() == null) {
            throw new BaseException(BaseResponseStatus.INVALID_JWT_TOKEN);
        }

        // 엔티티 조회 (영속 상태 보장용)
        Member foundMember = memberRepository.findById(member.getId())
                .orElseThrow(() -> new BaseException(BaseResponseStatus.NOT_FOUND));

        foundMember.updateNickname(newNickname);
    }
}

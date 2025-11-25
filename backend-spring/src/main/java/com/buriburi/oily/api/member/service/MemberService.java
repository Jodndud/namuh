package com.buriburi.oily.api.member.service;

import com.buriburi.oily.api.member.dto.in.UpdateNicknameRequest;
import com.buriburi.oily.api.member.entity.Member;
import jakarta.servlet.http.HttpServletRequest;

public interface MemberService {
    void updateNickname(Member member, UpdateNicknameRequest requestDto);
}

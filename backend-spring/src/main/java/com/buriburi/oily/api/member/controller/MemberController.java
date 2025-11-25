package com.buriburi.oily.api.member.controller;

import com.buriburi.oily.api.member.dto.in.UpdateNicknameRequest;
import com.buriburi.oily.api.member.entity.Member;
import com.buriburi.oily.api.member.service.MemberService;
import com.buriburi.oily.global.response.BaseResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@Tag(name = "Member", description = "유저 정보 조회 및 수정 API")
@RestController
@RequiredArgsConstructor
@RequestMapping("/v1/member")
@Validated
public class MemberController {

    private final MemberService memberService;

    @Operation(summary = "닉네임 수정 API", description = "입력한 닉네임으로 수정합니다.")
    @PatchMapping("/me")
    public BaseResponse<Void> updateNickname(
            @AuthenticationPrincipal(expression = "member") Member member,
            @Valid @RequestBody UpdateNicknameRequest requestDto
    ) {
        memberService.updateNickname(member, requestDto);
        return BaseResponse.onSuccess();
    }
}

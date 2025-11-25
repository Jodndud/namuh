package com.buriburi.oily.api.auth.dto.out;

import com.buriburi.oily.api.member.entity.Member;
import lombok.Builder;

/**
 * AccessToken 에 담을 사용자 정보
 */
@Builder
public record MemberClaimDto(String uuid, String nickname) {
    public static MemberClaimDto from(Member member) {
        return MemberClaimDto.builder()
                .uuid(member.getUuid())
                .nickname(member.getNickname())
                .build();
    }
}

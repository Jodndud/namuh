package com.buriburi.oily.api.member.dto.in;

import com.buriburi.oily.global.constant.ErrorMessages;
import com.buriburi.oily.global.constant.Patterns;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

import static com.buriburi.oily.global.constant.ErrorMessages.*;

public record UpdateNicknameRequest(
        @Schema(description = "변경할 닉네임", example = "말랑한고양이1234")
        @NotBlank(message = NICKNAME_NOT_FOUND)
        @Pattern(regexp = Patterns.NICKNAME_REGEX, message = ErrorMessages.INVALID_NICKNAME)
        String nickname
){}

package com.buriburi.oily.global.constant;

import java.util.regex.Pattern;

public final class Patterns {
    private Patterns() {
    }

    // 이메일 형식 검증: 매우 느슨한 이메일 형식 검증(실무에서는 더 엄격한 정책/화이트리스트 필요할 수 있음)
    public static final Pattern SIMPLE_EMAIL = Pattern.compile("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$");

    // 닉네임 형식 검증: 영문/한글/숫자만 허용, 길이 2~10
    public static final String NICKNAME_REGEX = "^[0-9A-Za-z가-힣]{2,10}$";
    public static final Pattern NICKNAME_PATTERN = Pattern.compile(NICKNAME_REGEX);

    // 공백 불가
    public static final String NO_WHITESPACE = "^(?=\\s*\\S).*$";
}

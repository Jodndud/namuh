package com.buriburi.oily.api.auth.service;

import com.buriburi.oily.api.member.repository.MemberRepository;
import com.buriburi.oily.global.constant.Patterns;
import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.response.BaseResponseStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Random;

@Service
@Transactional(readOnly = true)
@RequiredArgsConstructor
public class NicknameServiceImpl implements NicknameService {
    private final MemberRepository memberRepository;

    private static final String[] adjectives = {
            "귀여운", "발랄한", "똑똑한", "용감한", "상냥한", "행복한",
            "느긋한", "온화한", "대담한", "당당한", "재빠른", "조용한", "부드러운", "당돌한",
            "하품하는", "신사적인"
    };

    private static final String[] nouns = {
            "강아지", "고양이", "햄스터", "토끼", "거북이", "고슴도치", "말티즈", "푸들", "치와와",
            "오징어", "꼬마", "스피츠", "쇠똥구리", "해파리", "닭강정", "참치", "다람쥐", "이구아나", "기니피그", "도롱뇽",
            "컵케잌", "바람", "문어", "문어빵", "계란빵", "신사", "타코야끼", "타코"
    };

    private final Random random = new Random();

    public String generateNickname() {
        for (int i = 0; i < 20; i++) { // 20회까지 시도
            String adjective = adjectives[random.nextInt(adjectives.length)];
            String noun = nouns[random.nextInt(nouns.length)];

            final int MAX_NICKNAME_LENGTH = 10;
            final int NUMBER_SUFFIX_LENGTH = 4;

            if ((adjective.length() + noun.length()) <= (MAX_NICKNAME_LENGTH - NUMBER_SUFFIX_LENGTH)) {
                String numberSuffix = String.format("%04d", random.nextInt(10000));
                String nickname = adjective + noun + numberSuffix;

                if (nickname.length() <= MAX_NICKNAME_LENGTH && Patterns.NICKNAME_PATTERN.matcher(nickname).matches()) {
                    return nickname;
                }
            }
        }
        // fallback: 랜덤 숫자 기반 닉네임 (8자리 보장)
        return "유저" + String.format("%04d", random.nextInt(10000)); // 예: 유저0042
    }

    @Override
    public String getRandomNickname() {
        for (int i = 0; i < 10; i++) {
            String nickname = generateNickname();
            if (!memberRepository.existsByNickname(nickname)) {
                return nickname;
            }
        }
        throw new BaseException(BaseResponseStatus.NICKNAME_GENERATION_FAILED);
    }
}

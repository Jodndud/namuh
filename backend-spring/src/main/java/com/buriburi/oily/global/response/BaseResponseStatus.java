package com.buriburi.oily.global.response;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;

@Getter
@AllArgsConstructor
public enum BaseResponseStatus {

    /**
     * 2XX: Success(요청 성공)
     */
    SUCCESS(HttpStatus.OK, true, 200, "요청에 성공하였습니다."),

    /**
     * 4XX: Client Error(사용자 요청 에러)
     */
    INVALID_PARAMETER(HttpStatus.BAD_REQUEST, false, 400, "잘못된 요청입니다."),
    PAYLOAD_TOO_LARGE(HttpStatus.PAYLOAD_TOO_LARGE, false, 413, "파일 업로드 용량 초과입니다. (파일 당 요청합계 제한을 확인하세요.)"),
    NOT_FOUND(HttpStatus.NOT_FOUND, false, 404, "요청하신 정보를 찾을 수 없습니다."),

    /* 401 UNAUTHORIZED: 인증 실패 */
    AUTHENTICATION_REQUIRED(HttpStatus.UNAUTHORIZED, false, 401, "인증이 필요한 요청입니다."),
    INVALID_JWT_TOKEN(HttpStatus.UNAUTHORIZED, false, 401, "유효하지 않은 JWT 토큰입니다."),
    EXPIRED_JWT_TOKEN(HttpStatus.UNAUTHORIZED, false, 401, "만료된 JWT 토큰입니다."),
    UNSUPPORTED_JWT_TOKEN(HttpStatus.UNAUTHORIZED, false, 401, "지원되지 않는 형식의 JWT 토큰입니다."),
    INVALID_TOKEN_CLAIM(HttpStatus.UNAUTHORIZED, false, 401, "토큰의 클레임 정보가 올바르지 않습니다."),

    /* 403 FORBIDDEN: 인가 실패 (권한 없음) */
    ACCESS_DENIED(HttpStatus.FORBIDDEN, false, 403, "접근 권한이 없습니다."),

    NO_EXIST_USER(HttpStatus.NOT_FOUND, false, 404, "존재하지 않는 계정입니다."),

    /**
     * 5XX: Server Error(서버 에러)
     */
    INTERNAL_SERVER_ERROR(HttpStatus.CONFLICT, false, 500, "서버에서 예기치 않은 오류가 발생했습니다."),
    OPENVIDU_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR, false, 500, "OpenVidu 서버에서 예기치 않은 오류가 발생했습니다."),
    DATABASE_CONSTRAINT_VIOLATION(HttpStatus.CONFLICT, false, 509, "데이터베이스 제약 조건을 위반했습니다."
            + "(유니크 키 중복, 외래 키 위반, NOT NULL 위반 등에서 발생합니다.)"),

    /**
     * General Exceptions
     * -1500
     */
    INVALID_INPUT_VALUES(HttpStatus.BAD_REQUEST, false, -1502, "입력 데이터가 올바르지 않습니다."),
    DUPLICATE_NICKNAME(HttpStatus.BAD_REQUEST, false, -1503, "중복된 닉네임 입니다."),

    /**
     * OpenVidu(WebRTC) Exceptions
     * -1600
     */
    OPENVIDU_TOKEN_NOT_FOUND(HttpStatus.BAD_REQUEST, false, -1600, "세션 접근 권한이 없습니다."),
    OPENVIDU_SESSION_NOT_FOUND(HttpStatus.NOT_FOUND, false, -1604, "존재하지 않는 세션입니다."),

    /**
     * AWS 에러
     * -1700
     */
    S3_FILE_UPLOAD_FAILED(HttpStatus.INTERNAL_SERVER_ERROR, false, -1700, "파일 업로드에 실패했습니다."),

    /**
     * 소셜 관련 에러
     * -1800
     */
    UNSUPPORTED_SOCIAL_PROVIDER(HttpStatus.BAD_REQUEST, false, -1800, "지원하지 않는 소셜 로그인 타입입니다."),
    EXPIRED_SOCIAL_SIGNUP(HttpStatus.NOT_FOUND, false, -1804, "회원가입 시간이 만료되었습니다. 다시 시도해주세요."),
    NICKNAME_GENERATION_FAILED(HttpStatus.CONFLICT, false, -1806, "회원가입 중 닉네임 생성을 실패했습니다.");


    private final HttpStatusCode httpStatusCode;
    private final boolean isSuccess;
    private final int code;
    private final String message;
}

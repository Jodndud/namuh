package com.buriburi.oily.global.response;

import org.springframework.http.HttpStatus;
import org.springframework.http.HttpStatusCode;

import static com.buriburi.oily.global.response.BaseResponseStatus.*;

public record BaseResponse<T>(
        HttpStatusCode httpsStatus,
        Boolean isSuccess,
        String message,
        int code,
        T result
) {

    /**
     * 성공 응답
     */
    public static <T> BaseResponse<T> onSuccess(T result) {
        return new BaseResponse<T>(HttpStatus.OK, true, SUCCESS.getMessage(), SUCCESS.getCode(), result);
    }

    public static BaseResponse<Void> onSuccess() {
        return new BaseResponse<>(HttpStatus.OK, true, SUCCESS.getMessage(), SUCCESS.getCode(), null);
    }

    /**
     * 실패 응답
     */
    public static <T> BaseResponse<T> onFailure(BaseResponseStatus status) {
        return new BaseResponse<T>(status.getHttpStatusCode(), status.isSuccess(), status.getMessage(), status.getCode(), null);
    }

    public static <T> BaseResponse<T> onFailure(BaseResponseStatus status, String message) {
        return new BaseResponse<T>(status.getHttpStatusCode(), status.isSuccess(), message, status.getCode(), null);
    }

    public BaseResponse(T result) {
        this(HttpStatus.OK, true, SUCCESS.getMessage(), SUCCESS.getCode(), result);
    }

    public BaseResponse() {
        this(HttpStatus.OK, true, SUCCESS.getMessage(), SUCCESS.getCode(), null);
    }

    public BaseResponse(BaseResponseStatus status) {
        this(status.getHttpStatusCode(), status.isSuccess(), status.getMessage(), status.getCode(), null);
    }

    public BaseResponse(BaseResponseStatus status, String message) {
        this(status.getHttpStatusCode(), status.isSuccess(), message, status.getCode(), null);
    }
}

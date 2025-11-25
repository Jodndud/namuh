package com.buriburi.oily.global.exception;

import com.buriburi.oily.global.response.BaseResponseStatus;
import lombok.Getter;

@Getter
public class BaseException extends RuntimeException {

    private final BaseResponseStatus status;

    public BaseException(BaseResponseStatus status) {
        this.status = status;
    }
}

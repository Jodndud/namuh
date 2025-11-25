package com.buriburi.oily.global.exception;

import com.buriburi.oily.global.response.BaseResponse;
import com.buriburi.oily.global.response.BaseResponseStatus;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.multipart.MaxUploadSizeExceededException;
import org.springframework.web.multipart.MultipartException;


/**
 * 프로젝트 전역의 Controller 단에서 발생하는 예외를 처리
 */
@RestControllerAdvice
public class GlobalExceptionHandler {
    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(BaseException.class)
    protected BaseResponse<Void> baseError(BaseException e) {
        log.error("BaseException -> {}({})", e.getStatus(), e.getStatus().getMessage(), e);
        return new BaseResponse<>(e.getStatus());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    protected BaseResponse<Void> handleValidException(MethodArgumentNotValidException e) {
        String message = e.getFieldErrors().get(0).getDefaultMessage();
        log.error("MethodArgumentNotValidException -> {}", message);
        return BaseResponse.onFailure(BaseResponseStatus.INVALID_PARAMETER, message);
    }

    @ExceptionHandler(RuntimeException.class)
    protected BaseResponse<Void> handleRuntimeException(RuntimeException e) {
        log.error("RuntimeException -> {}", e.getMessage(), e);
        return BaseResponse.onFailure(BaseResponseStatus.INTERNAL_SERVER_ERROR);
    }

    @ExceptionHandler({MaxUploadSizeExceededException.class, MultipartException.class})
    protected BaseResponse<Void> handleMaxUploadSize(Exception ex) {
        log.error("Multipart size exceeded: {}", ex.getMessage());
        return BaseResponse.onFailure(BaseResponseStatus.PAYLOAD_TOO_LARGE);
    }

    @ExceptionHandler(IllegalStateException.class)
    public BaseResponse<Void> handleIllegalState(IllegalStateException ex) {
        String msg = ex.getMessage();
        if (msg != null && msg.contains("exceeds its maximum permitted size")) {
            log.error("Multipart size exceeded (IllegalState): {}", msg);
            return BaseResponse.onFailure(BaseResponseStatus.INVALID_PARAMETER);
        }
        throw ex; // 업로드 초과 케이스가 아니면 기존 흐름 유지
    }
}

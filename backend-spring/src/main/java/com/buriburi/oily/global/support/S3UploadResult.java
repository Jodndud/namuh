package com.buriburi.oily.global.support;

import lombok.Builder;
import lombok.Getter;

/**
 * S3 업로드 결과
 * <p>
 * DB/응답에 필요한 key, url, 원본파일명, 타입, 크기 정보를 담는다.
 * </P>
 *
 * @PARAM key S3 오브젝트 키
 * @PARAM url 퍼블릭 접근 가능한 URL(버킷 정책/설정에 따름)
 * @PARAM originalFilename 원본 파일명
 * @PARAM contentType MIME 타입
 * @PARAM size 바이트 크기
 * @RETURN 없음
 */
@Getter
@Builder
public class S3UploadResult {
    private final String key;
    private final String originalFilename;
    private final String contentType;
    private final long size;
}

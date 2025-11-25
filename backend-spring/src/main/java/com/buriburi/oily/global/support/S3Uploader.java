package com.buriburi.oily.global.support;

import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.response.BaseResponseStatus;
import com.sksamuel.scrimage.ImmutableImage;
import com.sksamuel.scrimage.webp.WebpWriter;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.core.sync.RequestBody;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.PutObjectRequest;
import software.amazon.awssdk.services.s3.presigner.S3Presigner;
import software.amazon.awssdk.services.s3.presigner.model.GetObjectPresignRequest;

import java.io.IOException;
import java.time.Duration;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class S3Uploader {

    private static final Logger log = LoggerFactory.getLogger(S3Uploader.class);

    private final S3Client s3Client;

    private final S3Presigner s3Presigner;

    // application.yaml에 설정한 버킷 이름을 주입받기
    @Value("${spring.cloud.aws.s3.bucket}")
    private String bucket;

    // WebP로 변환할 이미지 콘텐츠 타입 목록
    private static final List<String> CONVERTIBLE_IMAGE_TYPES = Arrays.asList(MediaType.IMAGE_JPEG_VALUE, MediaType.IMAGE_PNG_VALUE);

    /**
     * S3에 파일을 업로드하고, 키와 URL을 함께 반환
     * JPG, PNG 파일은 WebP로 변환하여 업로드
     *
     * @PARAM multipartFile 업로드 파일
     * @PARAM dirName 디렉토리 명(예: "inquiries", "profiles")
     * @RETURN S3UploadResult (key, url, originalFilename, contentType, size)
     */
    public S3UploadResult upload(MultipartFile multipartFile, String dirName) {
        if (multipartFile == null || multipartFile.isEmpty())
            return null;

        String originalFileName = multipartFile.getOriginalFilename();
        boolean isConvertibleImage = isConvertibleImage(multipartFile.getContentType());

        byte[] processedBytes;
        String processedContentType;
        String uniqueFileKey;

        try {
            processedBytes = multipartFile.getBytes();

            if (isConvertibleImage) {
                /* Webp 로 변환 */
                log.debug("[S3-WEBP] Start WebP image conversion: originalFileName={}", originalFileName);
                processedBytes = convertToWebInMemory(processedBytes);
                processedContentType = "image/webp";

                uniqueFileKey = dirName + "/" + UUID.randomUUID() + ".webp";
                log.debug("[S3-WEBP] Image WebP conversion complete: newKey={}", uniqueFileKey);
            } else { /* 원본 데이터 사용 */
                processedContentType = multipartFile.getContentType();
                String extension = "";
                if (originalFileName != null && originalFileName.contains(".")) {
                    extension = originalFileName.substring(originalFileName.lastIndexOf("."));
                }
                uniqueFileKey = dirName + "/" + UUID.randomUUID() + extension;
            }
        } catch (IOException e) {
            log.error("[S3] File processing failed (getBytes): dirName={} originalFileName={} -> {}", dirName, originalFileName, e.getMessage(), e);
            throw new BaseException(BaseResponseStatus.S3_FILE_UPLOAD_FAILED);
        }

        if (log.isDebugEnabled()) {
            log.debug("[S3] Preparing for upload: dirName={} originalFileName={} size={} contentType={}", dirName, originalFileName,
                    multipartFile.getSize(), multipartFile.getContentType());
        }

        PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                .bucket(bucket)
                .key(uniqueFileKey)
                .contentType(processedContentType)
                .contentLength((long) processedBytes.length)
                .build();

        /* S3 업로드 */
        try {
            s3Client.putObject(putObjectRequest, RequestBody.fromBytes(processedBytes));
            if (log.isDebugEnabled()) {
                log.debug("[S3] Upload complete: key={}", uniqueFileKey);
            }
        } catch (Exception e) { // AWS SDK v2 Exception 처리
            log.error("[S3] Upload failed: dirName={} originalFileName={} -> {}", dirName, originalFileName, e.getMessage(),
                    e);
            throw new BaseException(BaseResponseStatus.S3_FILE_UPLOAD_FAILED);
        }

        // key 포함 정보 반환 (url은 presign 으로 추후 요청시 별도 발급)
        return S3UploadResult.builder()
                .key(uniqueFileKey)
                .originalFilename(originalFileName)
                .contentType(processedContentType)
                .size((long) processedBytes.length)
                .build();
    }

    private byte[] convertToWebInMemory(byte[] originalFileBytes) throws IOException {
        return ImmutableImage.loader().fromBytes(originalFileBytes).bytes(WebpWriter.DEFAULT);
    }

    private boolean isConvertibleImage(String contentType) {
        if (!StringUtils.hasText(contentType)) {
            return false;
        }
        return CONVERTIBLE_IMAGE_TYPES.contains(contentType.toLowerCase());
    }

    /**
     * S3에서 파일을 삭제
     *
     * @param fileKey = 삭제할 파일의 DB에 저장된 값
     */
    public void delete(String fileKey) {
        if (!StringUtils.hasText(fileKey)) {
            if (log.isDebugEnabled())
                log.debug("[S3] 삭제 건너뜀: 빈 key");
            return;
        }

        try {
            if (log.isDebugEnabled())
                log.debug("[S3] 삭제 시도: key={}", fileKey);
            DeleteObjectRequest deleteObjectRequest = DeleteObjectRequest.builder().bucket(bucket).key(fileKey).build();
            s3Client.deleteObject(deleteObjectRequest);
            if (log.isDebugEnabled())
                log.debug("[S3] 삭제 완료: key={}", fileKey);
        } catch (Exception e) {
            log.error("S3 파일 삭제에 실패했습니다. fileKey: {}", fileKey, e);
        }
    }

    /**
     * 프리사인 GET URL 발급 (기본 5분)
     */
    public String getPresignedGetUrl(String fileKey) {
        if (log.isDebugEnabled())
            log.debug("[S3] Presign 요청(기본 5분): key={}", fileKey);
        return getPresignedGetUrl(fileKey, Duration.ofMinutes(5));
    }

    public String getPresignedGetUrl(String fileKey, Duration ttl) {
        if (!StringUtils.hasText(fileKey)) {
            if (log.isDebugEnabled())
                log.debug("[S3] Presign 건너뜀: 빈 key");
            return null;
        }
        Duration effective = (ttl == null ? Duration.ofMinutes(5) : ttl);
        if (log.isDebugEnabled()) {
            log.debug("[S3] Presign 생성: key={} ttlSec={}", fileKey, effective.toSeconds());
        }
        var get = GetObjectRequest.builder().bucket(bucket).key(fileKey).build();
        var req = GetObjectPresignRequest.builder().signatureDuration(effective).getObjectRequest(get).build();
        String url = s3Presigner.presignGetObject(req).url().toString();
        if (log.isDebugEnabled())
            log.debug("[S3] Presign └─완료: key={} ttlSec={}", fileKey, effective.toSeconds());
        return url;
    }

    /**
     * 키/URL 입력 시 → 프리사인 URL로 변환 키면 presign, 이미 http(s)면 그대로 반환
     */
    public String resolvePresignedUrl(String urlOrKey, Duration ttl) {
        if (!StringUtils.hasText(urlOrKey)) {
            if (log.isDebugEnabled())
                log.debug("[S3] Presign └─변환 건너뜀: 빈 입력");
            return null;
        }
        String lower = urlOrKey.toLowerCase();
        if (lower.startsWith("http://") || lower.startsWith("https://")) {
            if (log.isDebugEnabled())
                log.debug("[S3] Presign └─불필요: 이미 URL -> {}", urlOrKey);
            return urlOrKey;
        }
        if (log.isDebugEnabled()) {
            log.debug("[S3] Presign └─변환 시도: key={} ttlSec={}", urlOrKey,
                    (ttl == null ? Duration.ofMinutes(5) : ttl).toSeconds());
        }
        return getPresignedGetUrl(urlOrKey, ttl);
    }

    /**
     * S3 연결 확인
     * <p>
     * 버킷에서 객체 리스트 호출로 연결 검증
     * </P>
     *
     * @RETURN true=정상 연결, false=실패
     */
    public boolean healthCheck() {
        try {
            s3Client.listObjectsV2(b -> b.bucket(bucket).maxKeys(1));
            if (log.isDebugEnabled())
                log.debug("[S3] 헬스체크 성공");
            return true;
        } catch (Exception e) {
            log.error("S3 연결 확인 실패", e);
            return false;
        }
    }

}
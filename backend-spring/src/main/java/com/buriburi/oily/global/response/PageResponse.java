package com.buriburi.oily.global.response;

import org.springframework.data.domain.Page;

import java.util.List;

/**
 * Spring Data {@link Page} 객체를 단순화하여 클라이언트 응답으로 전달하기 위한 DTO
 * <p>불필요한 메타 정보는 제거하고, 핵심적인 페이징 정보와 콘텐츠만 포함한다.</p>
 */
public record PageResponse<T>(
        List<T> content,
        int page,   // 현재 페이지 번호 (0부터 시작)
        int size,   // 페이지 크기 (한 페이지 당 데이터 수)
        long totalElements,  // 전체 데이터 개수
        int totalPages  // 전체 페이지 수
) {
    /**
     * Spring Data {@link Page}를 {@link PageResponse}로 변환한다.
     *
     * @param p   변환할 Page 객체
     * @param <T> 콘텐츠 타입
     * @return 변환된 pageResponse
     */
    public static <T> PageResponse<T> fron(Page<T> p) {
        return new PageResponse<>(
                p.getContent(),
                p.getNumber(),
                p.getSize(),
                p.getTotalElements(),
                p.getTotalPages()
        );
    }
}

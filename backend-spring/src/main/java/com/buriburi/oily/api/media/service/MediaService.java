package com.buriburi.oily.api.media.service;

import com.buriburi.oily.api.media.dto.response.SmileOwnerVideoResponse;
import com.buriburi.oily.api.media.dto.response.SmileThumbnailResponse;

import java.util.List;

public interface MediaService {
    boolean healthCheck();
    List<SmileThumbnailResponse> findAllSmileVideoThumbnails();
    List<SmileOwnerVideoResponse> findSmileVideoThumbnailsBySeqNo(Integer seqNo);
}

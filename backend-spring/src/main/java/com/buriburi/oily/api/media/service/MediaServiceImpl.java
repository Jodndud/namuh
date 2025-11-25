package com.buriburi.oily.api.media.service;

import com.buriburi.oily.api.media.dto.response.SmileOwnerVideoResponse;
import com.buriburi.oily.api.media.dto.response.SmileThumbnailResponse;
import com.buriburi.oily.api.media.entity.MediaType;
import com.buriburi.oily.api.media.repository.MediaRepository;
import com.buriburi.oily.global.support.S3Uploader;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static com.buriburi.oily.api.media.entity.MediaType.ROBOT_VIDEO;

@Service
@RequiredArgsConstructor
public class MediaServiceImpl implements MediaService {
    private final S3Uploader s3Uploader;
    private final MediaRepository mediaRepository;

    @Override
    @Transactional(readOnly = true)
    public boolean healthCheck() {
        return s3Uploader.healthCheck();
    }

    @Override
    @Transactional(readOnly = true)
    public List<SmileThumbnailResponse> findAllSmileVideoThumbnails() {
        return mediaRepository.findAllByTypeOrderByCreatedAtDesc(MediaType.ROBOT_VIDEO_THUMBNAIL)
                .stream()
                .map(SmileThumbnailResponse::from)
                .toList();
    }

    @Override
    @Transactional(readOnly = true)
    public List<SmileOwnerVideoResponse> findSmileVideoThumbnailsBySeqNo(Integer seqNo) {
        return mediaRepository.findAllByTypeAndSeqNoOrderByCreatedAtDesc(MediaType.ROBOT_VIDEO, seqNo)
                .stream()
                .map(SmileOwnerVideoResponse::from)
                .toList();
    }
}

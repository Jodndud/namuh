package com.buriburi.oily.api.media.repository;

import com.buriburi.oily.api.media.entity.Media;
import com.buriburi.oily.api.media.entity.MediaType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface MediaRepository extends JpaRepository<Media,Long> {
    List<Media> findAllByTypeOrderByCreatedAtDesc(MediaType type);
    List<Media> findAllByTypeAndSeqNoOrderByCreatedAtDesc(MediaType type, Integer seqNo);
}

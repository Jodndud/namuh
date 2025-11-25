package com.buriburi.oily.api.member.repository;

import com.buriburi.oily.api.member.entity.MemberSocial;
import com.buriburi.oily.api.member.entity.SocialProvider;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface MemberSocialRepository extends JpaRepository<MemberSocial, Long> {
    @EntityGraph(attributePaths = {"member", "member.role"})
    Optional<MemberSocial> findByProviderNameAndProviderId(SocialProvider providerName, String providerId);
}

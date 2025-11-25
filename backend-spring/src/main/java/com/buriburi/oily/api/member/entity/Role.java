package com.buriburi.oily.api.member.entity;

import lombok.Getter;

/** 회원 권한 */
@Getter
public enum Role {
    USER("ROLE_USER"),
    ADMIN("ROLE_ADMIN");

    private final String roleName;

    Role(String roleName) {
        this.roleName = roleName;
    }
}



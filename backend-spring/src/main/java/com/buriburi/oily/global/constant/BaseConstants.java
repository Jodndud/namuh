package com.buriburi.oily.global.constant;

import java.time.ZoneId;

/**
 * Base 상수 정의
 */
public final class BaseConstants {
    private BaseConstants() {
    }
    public static final String TIME_ZONE= "Asia/Seoul";
    public static final ZoneId ZONE_ID = ZoneId.of(TIME_ZONE);

}

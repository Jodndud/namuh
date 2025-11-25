package com.buriburi.oily.global.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnection;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.StringRedisTemplate;

/**
 * Redis 스타트업 핑 로거
 * <P>
 * 애플리케이션 시작 직후 Redis에 PING을 보내 연결/권한을 점검하고 결과를 로그로 남깁니다. 실패 시 즉시 알 수 있도록 ERROR
 * 로그를 남기며, 필요 시 fail-fast 옵션으로 부팅을 중단할 수 있습니다.
 * </P>
 *
 * @PARAM 없음(빈 주입)
 * @RETURN ApplicationRunner 빈
 */
@Configuration
public class RedisStartupLogger {

    private static final Logger log = LoggerFactory.getLogger(RedisStartupLogger.class);

    @Value("${redis.fail-fast:false}")
    private boolean failFast; // true면 시작 시 Redis 미연결 시 예외로 부팅 중단

    /**
     * 애플리케이션 시작 직후 1회 Redis PING 및 로그 출력
     * <P>
     * 호스트/포트/DB 등 연결 정보를 INFO로 남기고, 응답/예외를 구분해 로그합니다.
     * </P>
     *
     * @PARAM template StringRedisTemplate
     * @RETURN ApplicationRunner
     */
    @Bean
    public ApplicationRunner redisPingLogger(StringRedisTemplate template) {
        return args -> {
            RedisConnectionFactory f = template.getConnectionFactory();
            String where = resolveLocation(f);

            try (RedisConnection c = f.getConnection()) {
                String pong = c.ping();
                if ("PONG".equalsIgnoreCase(pong)) {
                    log.info("[Redis] Connected: {} (PING=PONG)", where);
                } else {
                    log.warn("[Redis] Ping responded non-PONG: {} (resp={})", where, pong);
                }
            } catch (Exception e) {
                log.error("[Redis] Connection/PING failed: {} - {}", where, e.getMessage(), e);
                if (failFast) {
                    throw new IllegalStateException("Redis fail-fast enabled: startup aborted.", e);
                }
            }
        };
    }

    /**
     * 연결 팩토리에서 호스트/포트 등 위치 정보 추출
     * <P>
     * Lettuce 사용 시 호스트/포트/DB를 표시, 그 외 구현은 단순 클래스명만 표기합니다.
     * </P>
     *
     * @PARAM f RedisConnectionFactory
     * @RETURN 위치 설명 문자열
     */
    private String resolveLocation(RedisConnectionFactory f) {
        if (f instanceof LettuceConnectionFactory l) {
            String host = l.getHostName();
            int port = l.getPort();
            int db = l.getDatabase();
            boolean ssl = Boolean.TRUE.equals(l.isUseSsl());
            return host + ":" + port + "/db" + db + (ssl ? " (ssl)" : "");
        }
        return f.getClass().getSimpleName();
    }
}

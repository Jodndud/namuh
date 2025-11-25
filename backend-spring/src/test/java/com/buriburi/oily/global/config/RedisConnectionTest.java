package com.buriburi.oily.global.config;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.redis.core.StringRedisTemplate;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
class RedisConnectionTest {

    @Autowired
    private StringRedisTemplate stringRedisTemplate;

    @Test
    void redisConnectionWorks() {
        stringRedisTemplate.opsForValue().set("test:key", "hello-redis");
        String value = stringRedisTemplate.opsForValue().get("test:key");
        assertThat(value).isEqualTo("hello-redis");
    }
}

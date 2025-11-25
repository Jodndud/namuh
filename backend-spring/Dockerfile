# syntax=docker/dockerfile:1.6

# ---------- Build stage ----------
FROM eclipse-temurin:17-jdk-jammy AS build
WORKDIR /app

# (선택) 테스트 스킵 여부를 빌드 인자로 제어
ARG SKIP_TESTS=true

# Gradle 래퍼/의존성만 먼저 복사해서 캐시 극대화
COPY gradlew settings.gradle* build.gradle* gradle.properties* ./
COPY gradle ./gradle
# 실행권한 + CRLF 방지
RUN chmod +x gradlew && sed -i 's/\r$//' gradlew

RUN ./gradlew dependencies

# 이후 소스 복사
COPY . .

# 실행권한 + CRLF 방지
RUN chmod +x gradlew && sed -i 's/\r$//' gradlew

# BuildKit(--mount) 없이 빌드 실행
RUN ./gradlew clean bootJar $( [ "$SKIP_TESTS" = "true" ] && echo "-x test" )

# 실행 JAR 하나만 확정해 복사 준비(*-plain.jar 제외)
RUN set -eu; \
    JAR_FILE="$(ls build/libs/*.jar | grep -v 'plain' | head -n 1)"; \
    [ -n "$JAR_FILE" ] || { echo "No runnable JAR found"; exit 1; }; \
    cp "$JAR_FILE" /app/app.jar

# ---------- Runtime stage ----------
FROM eclipse-temurin:17-jre-jammy AS runtime
WORKDIR /app

# 비루트 유저
RUN addgroup --system spring && adduser --system --ingroup spring spring
USER spring

# 빌드 산출물 복사
COPY --from=build /app/app.jar /app/app.jar

# 포트 노출 및 옵션
EXPOSE 8080
ENV JAVA_OPTS=""

# 엔트리포인트
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/app.jar"]

package com.buriburi.oily.api.channel.service;

import static com.buriburi.oily.global.constant.ChannelConstants.*;

import com.buriburi.oily.api.channel.dto.in.ConnectionRequestDto;
import com.buriburi.oily.api.channel.dto.out.SessionResponseDto;
import com.buriburi.oily.api.channel.dto.out.TokenResponseDto;
import com.buriburi.oily.global.exception.BaseException;
import com.buriburi.oily.global.properties.OpenViduProperties;
import com.buriburi.oily.global.response.BaseResponseStatus;
import com.buriburi.oily.global.support.ServerDataParser;
import io.openvidu.java.client.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class ChannelServiceImpl implements ChannelService {

    private final OpenViduProperties openViduProperties;
    private final OpenVidu openVidu;

    /**
     * 세션을 찾거나 생성한 후, 토큰을 발급
     */
    @Override
    public TokenResponseDto createConnection(String channelId, ConnectionRequestDto requestDto) {
        final String customSessionId = generateCustomSessionId(channelId);

        try {
            openVidu.fetch();
            Session session = openVidu.getActiveSession(customSessionId);

            // 세션이 없으면 새로 생성
            if (session == null) {
                session = openVidu.createSession(SessionProperties
                        .fromJson(Map.of(DATA_SESSION_ID, customSessionId))
                        .build());
            }

            // 연결을 위한 serverData 생성
            String serverData = String.format("{\"%s\":\"%s\"}", DATA_PARTICIPANT_ID, requestDto.participantId());

            // OpenVidu role 설정 ("PUBLISHER", "SUBSCRIBER" 문자열을 Enum으로 변환)
            OpenViduRole openViduRole = OpenViduRole.valueOf(requestDto.role().toUpperCase());

            // Connection 속성 설정
            ConnectionProperties props = ConnectionProperties
                    .fromJson(Map.of(
                            "data", serverData,
                            "role", openViduRole.name()
                    ))
                    .build();

            // 토큰 생성 및 반환
            Connection connection = session.createConnection(props);
            return new TokenResponseDto(connection.getToken());
        } catch (OpenViduJavaClientException | OpenViduHttpException e) {
            throw new BaseException(BaseResponseStatus.OPENVIDU_SERVER_ERROR);
        } catch (IllegalArgumentException e) {
            throw new BaseException(BaseResponseStatus.INVALID_INPUT_VALUES);
        }
    }

    /**
     * 세션 정보 조회
     */
    @Override
    public SessionResponseDto getSessionInfo(String channelId) {
        final String customSessionId = generateCustomSessionId(channelId);

        try {
            openVidu.fetch();
            Session session = openVidu.getActiveSession(customSessionId);

            return SessionResponseDto.toDto(session);
        } catch (OpenViduJavaClientException | OpenViduHttpException e) {
            throw new BaseException(BaseResponseStatus.OPENVIDU_SERVER_ERROR);
        }
    }

    /**
     * 특정 사용자를 세션에서 퇴장시킴 (TODO: 관리자 or 방장 기능에 가까우므로 이후 권한 확인 로직이 추가되어야 함)
     */
    @Override
    public void leaveSession(String channelId, String participantId) {
        final String customSessionId = generateCustomSessionId(channelId);

        try {
            openVidu.fetch();
            Session session = openVidu.getActiveSession(customSessionId);
            if (session == null) { // 이미 세션이 있으면 성공 처리 (TODO: OpenVidu 세션의 모든 연결을 순회하며 일치하는 participantId를 찾는 방식이 아니라, 요청 유저 정보와 Redis or DB 조회를 통해서 처리해야 함)
                return;
            }

            Connection connection = session.getActiveConnections().stream()
                    .filter(c -> participantId.equals(
                            ServerDataParser.getText(ServerDataParser.parse(c.getServerData()), DATA_PARTICIPANT_ID)
                    ))
                    .findFirst()
                    .orElse(null);  // 토큰이 없으면 null

            if (connection == null) {   // 이 참여자가 세션에 없음. 성공 처리
                return;
            }

            // 마지막 참여자이거나, 혹은 유일한 PUBLISHER가 나갔을 때 세션 종료
            if (session.getActiveConnections().size() == 1) {
                session.close();
            } else {
                session.forceDisconnect(connection);
            }
        } catch (OpenViduJavaClientException | OpenViduHttpException e) {
            throw new BaseException(BaseResponseStatus.OPENVIDU_SERVER_ERROR);
        }
    }

    /**
     * OpenVidu 세션 ID 발급
     */
    private String generateCustomSessionId(String channelId) {
        return openViduProperties.getSessionPrefix() + channelId;
    }
}

package com.buriburi.oily.api.channel.dto.out;

import static com.buriburi.oily.global.constant.ChannelConstants.*;

import com.buriburi.oily.global.support.ServerDataParser;
import io.openvidu.java.client.Session;
import lombok.Builder;

import java.util.List;
import java.util.Objects;

public record SessionResponseDto(
        String sessionId,
        Integer participantCount,
        List<String> participantIds
) {
    @Builder
    public SessionResponseDto(String sessionId, Integer participantCount,
                              List<String> participantIds) {
        this.sessionId = sessionId;
        this.participantCount = participantCount;
        this.participantIds = participantIds;
    }

    public static SessionResponseDto toDto(Session session) {
        if (session == null) {
            return SessionResponseDto.builder()
                    .sessionId(null)
                    .participantCount(0)
                    .participantIds(List.of())
                    .build();
        }

        List<String> activeParticipantIds = session.getActiveConnections().stream()
                .map(c -> {
                    var sd = ServerDataParser.parse(c.getServerData());

                    return ServerDataParser.getText(sd, DATA_PARTICIPANT_ID);
                })
                .filter(Objects::nonNull)   // ID가 없는 연결은 제외
                .toList();

        return SessionResponseDto.builder()
                .sessionId(session.getSessionId())
                .participantIds(activeParticipantIds)
                .participantCount(activeParticipantIds.size())
                .build();
    }
}

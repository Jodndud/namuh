package com.buriburi.oily.api.channel.service;

import com.buriburi.oily.api.channel.dto.in.ConnectionRequestDto;
import com.buriburi.oily.api.channel.dto.out.SessionResponseDto;
import com.buriburi.oily.api.channel.dto.out.TokenResponseDto;

public interface ChannelService {
    TokenResponseDto createConnection(String channelId, ConnectionRequestDto requestDto);

    SessionResponseDto getSessionInfo(String channelId);

    void leaveSession(String channelId, String participantId);
}

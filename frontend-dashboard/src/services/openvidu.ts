// OpenVidu API 서비스 함수들

export interface OpenViduConnection {
  participantId: string;
  role: 'PUBLISHER' | 'SUBSCRIBER';
}

export interface OpenViduTokenResponse {
  httpStatus: {
    error: boolean;
    is4xxClientError: boolean;
    is5xxServerError: boolean;
    isInformational: boolean;
    isSuccessful: boolean;
    is3xxRedirection: boolean;
  };
  isSuccess: boolean;
  message: string;
  code: string;
  result: {
    token: string;
  };
}

/**
 * 채널에 연결을 위한 토큰을 요청하는 함수
 * @param channelId - 연결할 채널 ID
 * @param participantId - 참가자 ID
 * @param role - 참가자 역할 (PUBLISHER/SUBSCRIBER)
 * @returns Promise<OpenViduTokenResponse>
 */
export async function createChannelConnection(
  channelId: string,
  participantId: string,
  role: 'PUBLISHER' | 'SUBSCRIBER' = 'SUBSCRIBER'
): Promise<OpenViduTokenResponse> {
  const baseUrl = 'https://api.buriburi.monster/spring';
  
  const requestBody: OpenViduConnection = {
    participantId,
    role
  };

  try {
    const response = await fetch(`${baseUrl}/v1/channels/${channelId}/connections`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 필요시 Authorization 헤더 추가
        // 'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data: OpenViduTokenResponse = await response.json();
    return data;
  } catch (error) {
    console.error('Failed to create channel connection:', error);
    throw error;
  }
}

/**
 * 환경 변수 또는 설정에서 OpenVidu 서버 URL을 가져오는 함수
 */
export function getOpenViduServerUrl(): string {
  return 'https://rtc.buriburi.monster';
}

/**
 * 환경 변수 또는 설정에서 OpenVidu 시크릿을 가져오는 함수
 */
export function getOpenViduSecret(): string {
  return '108_eksv}<xQKd'; // 스크린샷에서 확인된 시크릿
}
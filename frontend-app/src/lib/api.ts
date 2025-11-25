import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
    baseURL: baseURL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    console.error('요청 인터셉터 오류', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터
let isRefreshing = false;
let pendingRequests: Array<(token: string) => void> = [];

function onRefreshed(token: string) {
  pendingRequests.forEach((cb) => cb(token));
  pendingRequests = [];
}

api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        // 다른 요청이 리프레시 중이면 큐에 대기 후 재시도
        return new Promise((resolve) => {
          pendingRequests.push((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      try {
        isRefreshing = true;
        const refreshRes = await api.post('/auth/refresh', {}, { withCredentials: true });

        const authHeader = refreshRes.headers['authorization'] || refreshRes.headers['Authorization'];
        const newAccessToken = String(authHeader || '').replace(/^Bearer\s+/i, '').trim();
        if (!newAccessToken) {
          throw new Error('새 토큰 발급 실패');
        }

        localStorage.setItem('accessToken', newAccessToken);
        api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;
        onRefreshed(newAccessToken);

        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (e) {
        // 리프레시 실패 시 로그인 화면으로 유도
        localStorage.removeItem('accessToken');
        // 라우터 접근이 어려우므로 하드 리다이렉트
        if (typeof window !== 'undefined') {
          window.location.href = '/signin';
        }
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
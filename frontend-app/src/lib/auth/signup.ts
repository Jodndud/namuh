import api from '@/lib/api';

// 회원가입&로그인 (구글로그인 버튼 클릭 시 호출)
export const signIn = async () => {
  const res = await api.get("/auth/redirect", {});
	return res.data;
};


// authClient.js

// 백엔드 API base URL (같은 도메인이면 빈 문자열)
const API_BASE = "http://10.122.2.122:5000";

// 로컬스토리지 토큰 관리
function getTokens() {
  return {
    accessToken: localStorage.getItem("access_token"),
    refreshToken: localStorage.getItem("refresh_token"),
    tokenType: localStorage.getItem("token_type") || "Bearer",
  };
}

function saveTokens(data) {
  if (!data) return;
  if (data.access_token) localStorage.setItem("access_token", data.access_token);
  if (data.refresh_token) localStorage.setItem("refresh_token", data.refresh_token);
  if (data.token_type) localStorage.setItem("token_type", data.token_type);
}

function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("token_type");
}

function redirectToLogin() {
  clearTokens();
  // 필요하면 현재 위치를 쿼리에 붙일 수도 있음: `/login?next=${encodeURIComponent(location.pathname)}`
  window.location.href = "./login";
}

// 동시에 여러 요청이 실패할 때 refresh 1번만 돌리도록 공유 Promise
let refreshPromise = null;

// refresh token으로 access token 재발급
async function refreshAccessToken() {
  const { refreshToken, accessToken } = getTokens();
  if (!refreshToken) {
    redirectToLogin();
    throw new Error("No refresh token");
  }

  // 이미 refresh 중이면 그거 기다리기
  if (refreshPromise) {
    return refreshPromise;
  }
  refreshPromise = (async () => {
    const res = await fetch(API_BASE + "/auth/refresh", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken, access_token: accessToken }),
    });

    if (!res.ok) {
      clearTokens();
      redirectToLogin();
      throw new Error("Failed to refresh token");
    }

    const data = await res.json();
    saveTokens(data);
    return data.access_token;
  })();

  try {
    const accessToken = await refreshPromise;
    return accessToken;
  } finally {
    // 성공/실패 관계없이 한 번 끝나면 초기화
    refreshPromise = null;
  }
}

/**
 * 인증이 필요한 API 요청용 공통 함수
 *
 * 사용 예:
 *   const res = await apiFetch("/api/timetable");
 *   const data = await res.json();
 */
export async function apiFetch(input, init = {}, retry = true) {
  const url = input.startsWith("http") ? input : API_BASE + input;
  const { accessToken, tokenType } = getTokens();

  if (!accessToken) {
    redirectToLogin();
    throw new Error("No access token");
  }

  const headers = new Headers(init.headers || {});
  headers.set("Authorization", `${tokenType} ${accessToken}`);
  headers.set("Accept", "application/json");

  const options = {
    ...init,
    headers,
  };

  const res = await fetch(url, options);

  // 401/403 등 인증 오류면 refresh 시도
  if ((res.status === 401 || res.status === 403) && retry) {
    try {
      await refreshAccessToken(); // 새 access token 발급
    } catch (e) {
      // refresh 실패하면 refreshAccessToken 안에서 login으로 보냄
      throw e;
    }
    // 새 토큰으로 한 번 더 시도 (retry=false로 무한루프 방지)
    return apiFetch(input, init, false);
  }

  // refresh 후에도 또 401/403이면 로그인 페이지로
  if ((res.status === 401 || res.status === 403) && !retry) {
    redirectToLogin();
    throw new Error("Unauthorized after refresh");
  }

  return res;
}

function logout() {
  clearTokens();
  window.location.href = "/login";
}

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("logout-btn");
  if (btn) {
    btn.addEventListener("click", logout);
  }
});
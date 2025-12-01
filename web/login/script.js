// 로그인 페이지 전용 JS

// 같은 도메인에서 /auth/login 을 쓴다면 빈 문자열이면 됨.
const LOGIN_API = "http://10.122.2.122:5000/auth/login"; // 예: "http://localhost:4000" 로 변경 가능

function showLoginMessage(el, type, text) {
  if (!el) return;
  el.className = "message"; // reset
  if (type) el.classList.add(type);
  if (text && text.trim() !== "") {
    el.textContent = text;
    el.classList.add("visible");
  } else {
    el.textContent = "";
    el.classList.remove("visible");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("login-form");
  if (!loginForm) return;

  const loginMessage = document.getElementById("login-message");
  const tokenPreview = document.getElementById("token-preview");

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    showLoginMessage(loginMessage, null, "");
    if (tokenPreview) {
      tokenPreview.style.display = "none";
      tokenPreview.textContent = "";
    }

    const id = document.getElementById("login-id").value.trim();
    const password = document.getElementById("login-password").value;

    if (!id || !password) {
      showLoginMessage(loginMessage, "error", "아이디와 비밀번호를 모두 입력해주세요.");
      return;
    }

    try {
      const res = await fetch(LOGIN_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ id, password }),
      });
      
      const data = await res.json();

      if (!res.ok) {
        const detail = data.detail || "로그인에 실패했습니다.";
        showLoginMessage(loginMessage, "error", "로그인에 실패했습니다. 아이디와 비밀번호를 다시 확인해주세요");
        return;
      }

      // 기대 응답:
      // {
      //   "access_token": "...",
      //   "refresh_token": "...",
      //   "token_type": "bearer"
      // }
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      localStorage.setItem("token_type", data.token_type);

      showLoginMessage(loginMessage, "success", "로그인 성공! 토큰이 저장되었습니다.");

      if (tokenPreview) {
        tokenPreview.style.display = "block";
        tokenPreview.textContent =
          "access_token: " + data.access_token + "\n\n" +
          "refresh_token: " + data.refresh_token + "\n\n" +
          "token_type: " + data.token_type;
      }

    //   필요하면 여기서 리다이렉트
      window.location.href = "/";

    } catch (err) {
      console.error(err);
      showLoginMessage(loginMessage, "error", "네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
    }
  });
});
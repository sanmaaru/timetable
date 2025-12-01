// 회원가입 페이지 전용 JS

// 같은 도메인에서 /auth/signup 을 쓴다면 빈 문자열이면 됨.
const SIGNUP_API = "http://10.122.2.122:5000/auth/signup"; // 예: "http://localhost:4000" 로 변경 가능

function showSignupMessage(el, type, text) {
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
  const signupForm = document.getElementById("signup-form");
  if (!signupForm) return;

  const signupMessage = document.getElementById("signup-message");

  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    showSignupMessage(signupMessage, null, "");

    const email = document.getElementById("signup-email").value.trim();
    const id = document.getElementById("signup-id").value.trim();
    const password = document.getElementById("signup-password").value;
    const identifier = document.getElementById("signup-identifier").value.trim();

    // Pydantic 조건에 맞는 간단 검증
    if (id.length < 3 || id.length > 20) {
      showSignupMessage(signupMessage, "error", "아이디는 3~20 글자여야 합니다.");
      return;
    }
    if (password.length < 3) {
      showSignupMessage(signupMessage, "error", "비밀번호는 3글자 이상이어야 합니다.");
      return;
    }
    if (identifier.length !== 8) {
      showSignupMessage(signupMessage, "error", "식별자는 정확히 8글자여야 합니다.");
      return;
    }

    try {
      const res = await fetch(SIGNUP_API, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, id, password, identifier }),
      });

      const data = await res.json();

      if (!res.ok) {
        const detail = data.detail || "회원가입에 실패했습니다.";
        if (detail.includes('already exists')) {
            showSignupMessage(signupMessage, "error", "아이디 혹은 이메일이 이미 사용 중 입니다");
            return;
        }

        showSignupMessage(signupMessage, "error", "회원가입에 실패하였습니다. 정보를 다시 확인해주세요")
        return;
      }

      showSignupMessage(signupMessage, "success", "회원가입 성공! 이제 로그인해주세요.");

      // 자동으로 /login으로 이동
      setTimeout(() => {
        window.location.href = "/login";
      }, 1500);
    } catch (err) {
      console.error(err);
      showSignupMessage(signupMessage, "error", "네트워크 오류가 발생했습니다. 잠시 후 다시 시도해주세요.");
    }
  });
});
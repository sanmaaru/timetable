import { apiFetch } from "./authClient.js";

// =============================
// 1. 시간표 로드
// =============================
async function loadTimetable() {
  try {
    const res = await apiFetch("/timetable");
    const data = await res.json(); // data는 이미 JS 객체
    return JSON.parse(data);
  } catch (err) {
    console.error("시간표 로드 실패:", err);
    return null;
  }
}

// =============================
// 2. 테마 관련 함수 (다크/라이트 + OS + 토글)
// =============================

function setTheme(theme) {
  const root = document.documentElement;
  const toggle = document.querySelector(".theme-toggle");

  root.dataset.theme = theme;

  if (toggle) {
    toggle.setAttribute(
      "aria-label",
      theme === "dark" ? "라이트 모드로 전환" : "다크 모드로 전환"
    );
  }
}

function initTheme() {
  const saved = localStorage.getItem("theme");
  let theme = saved === "dark" || saved === "light" ? saved : null;

  if (!theme) {
    const prefersDark =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    theme = prefersDark ? "dark" : "light";
  }

  setTheme(theme);

  const toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const current =
        document.documentElement.dataset.theme === "light" ? "light" : "dark";
      const next = current === "dark" ? "light" : "dark";
      setTheme(next);
      localStorage.setItem("theme", next);
    });
  }
}

// =============================
// 3. 시간표 렌더링 함수 (객체 버전)
// =============================

function renderTimetable(studentData) {
  const timetableEl = document.getElementById("timetable");
  const nameEl = document.getElementById("student-name");
  const idEl = document.getElementById("student-id");
  const avatarEl = document.getElementById("avatar-initial");

  if (!timetableEl || !nameEl || !idEl || !avatarEl) {
    console.error("필요한 DOM 요소를 찾지 못했습니다.");
    return;
  }

  timetableEl.innerHTML = "";

  const dayOrder = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const dayLabel = {
    Mon: "월",
    Tue: "화",
    Wed: "수",
    Thu: "목",
    Fri: "금",
    Sat: "토",
    Sun: "일",
  };

  const usedDaysSet = new Set();
  let maxPeriod = 0;

  studentData.timetable.forEach((cls) => {
    cls.periods.forEach((p) => {
      usedDaysSet.add(p.day);
      if (p.period > maxPeriod) maxPeriod = p.period;
    });
  });

  const usedDays = Array.from(usedDaysSet).sort(
    (a, b) => dayOrder.indexOf(a) - dayOrder.indexOf(b)
  );

  timetableEl.style.gridTemplateColumns =
    "64px " + usedDays.map(() => "minmax(120px, 1fr)").join(" ");

  const cornerCell = document.createElement("div");
  cornerCell.className = "timetable-header corner-cell";
  cornerCell.textContent = "교시";
  timetableEl.appendChild(cornerCell);

  usedDays.forEach((dayKey) => {
    const dayHeader = document.createElement("div");
    dayHeader.className = "timetable-header day-header";
    dayHeader.textContent = dayLabel[dayKey] + "요일";
    timetableEl.appendChild(dayHeader);
  });

  for (let period = 1; period <= maxPeriod; period++) {
    const periodCell = document.createElement("div");
    periodCell.className = "timetable-period";
    periodCell.textContent = period + "교시";
    timetableEl.appendChild(periodCell);

    usedDays.forEach((dayKey) => {
      const cell = document.createElement("div");
      cell.className = "timetable-cell";

      const classesHere = studentData.timetable.filter((cls) =>
        cls.periods.some((p) => p.day === dayKey && p.period === period)
      );

      if (classesHere.length === 0) {
        cell.classList.add("empty");
      } else {
        classesHere.forEach((cls) => {
          const card = document.createElement("div");
          card.className = "subject-card";
          if (classesHere.length > 1) {
            card.classList.add("conflict");
          }

          card.innerHTML = `
            <div class="subject-name">
              <span>${cls.subject}</span>
              <span class="division">${cls.division}분반</span>
            </div>
            <div class="subject-meta">
              <span>${cls.teacher}</span>
              <span>${cls.room}</span>
            </div>
          `;

          cell.appendChild(card);
        });
      }

      timetableEl.appendChild(cell);
    });
  }

  nameEl.textContent = studentData.name;
  idEl.textContent = studentData.id;

  const avatarInitial = (() => {
    const name = (studentData.name || "").trim();
    if (name.length <= 2) return name || "?";
    return name[0] + name[name.length - 1];
  })();
  avatarEl.textContent = avatarInitial;
}

// JSON 문자열로 넣고 싶을 때 쓸 수 있는 헬퍼 (디버깅용)
function renderTimetableFromJson(jsonString) {
  try {
    const data = JSON.parse(jsonString);
    if (!data || !data.timetable) {
      console.error("timetable 필드가 없는 JSON입니다.");
      return;
    }
    renderTimetable(data);
  } catch (e) {
    console.error("JSON 파싱 에러:", e);
  }
}
window.renderTimetableFromJson = renderTimetableFromJson;

// =============================
// 4. 페이지 로드 시 순서
// =============================

document.addEventListener("DOMContentLoaded", async () => {
  initTheme();

  const data = await loadTimetable();  // ✅ 여기서 await
  if (!data) {
    console.error("시간표 데이터를 불러오지 못했습니다.");
    return;
  }

  renderTimetable(data);               // ✅ 이미 JS 객체라 그대로 사용
});

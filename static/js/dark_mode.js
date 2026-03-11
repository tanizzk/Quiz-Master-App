const darkToggle = document.getElementById("dark-mode-toggle");
const root = document.documentElement;

const applyTheme = (theme) => {
  root.setAttribute("data-theme", theme);
  if (darkToggle) {
    darkToggle.textContent = theme === "dark" ? "Light mode" : "Dark mode";
  }
};

const stored = localStorage.getItem("quizTheme") || "light";
applyTheme(stored);

darkToggle?.addEventListener("click", () => {
  const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
  applyTheme(next);
  localStorage.setItem("quizTheme", next);
});

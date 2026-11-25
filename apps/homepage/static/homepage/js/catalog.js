"use strict";

// Переключение плотности карточек. Без JavaScript каталог тоже работает.
const button = document.getElementById("view-toggle");
const grid = document.getElementById("catalog-grid");
if (button && grid) {
  button.hidden = false;
  button.addEventListener("click", () => {
    const compact = grid.classList.toggle("compact");
    button.setAttribute("aria-pressed", String(compact));
    button.textContent = compact ? "Обычный вид" : "Компактный вид";
  });
}

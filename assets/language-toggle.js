document.documentElement.classList.add("js");

document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll("[data-language-toggle]");
  const extraLanguages = document.querySelectorAll("[data-extra-language]");

  if (!extraLanguages.length) {
    buttons.forEach((button) => {
      button.hidden = true;
    });
    return;
  }

  const showLabel = "顯示 EN · JP · KR / Show EN · JP · KR";
  const hideLabel = "隱藏 EN · JP · KR / Hide EN · JP · KR";
  let expanded = false;

  const render = () => {
    document.documentElement.classList.toggle("languages-expanded", expanded);
    extraLanguages.forEach((element) => {
      element.hidden = !expanded;
    });
    buttons.forEach((button) => {
      button.setAttribute("aria-expanded", String(expanded));
      button.textContent = expanded ? hideLabel : showLabel;
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      expanded = !expanded;
      render();
    });
  });

  render();
});

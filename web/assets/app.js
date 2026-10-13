const form = document.querySelector("#compare-form");
const statusBox = document.querySelector("#status");
const submitButton = document.querySelector("#submit-button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusBox.classList.remove("error");
  statusBox.textContent = "PDF 벡터를 분석하고 있습니다. 도면 크기에 따라 시간이 걸릴 수 있습니다...";
  submitButton.disabled = true;

  try {
    const response = await fetch("/api/compare", {
      method: "POST",
      body: new FormData(form),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "비교에 실패했습니다.");
    }
    window.location.href = data.report_url;
  } catch (error) {
    statusBox.classList.add("error");
    statusBox.textContent = error.message;
    submitButton.disabled = false;
  }
});

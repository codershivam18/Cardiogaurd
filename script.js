document.addEventListener("DOMContentLoaded", function () {

  const form = document.getElementById("predictForm");
  const submitBtn = document.getElementById("predictBtn");
  const currentSmokerSelect = document.getElementById("currentSmoker");
  const cigsPerDayInput = document.getElementById("cigsPerDay");

  // Dynamic logic for Cigarettes Per Day
  if (currentSmokerSelect && cigsPerDayInput) {
    currentSmokerSelect.addEventListener("change", function () {
      if (this.value === "no") {
        cigsPerDayInput.value = "0";
        cigsPerDayInput.setAttribute("readonly", true);
        cigsPerDayInput.style.backgroundColor = "#e9ecef";
      } else {
        cigsPerDayInput.value = "";
        cigsPerDayInput.removeAttribute("readonly");
        cigsPerDayInput.style.backgroundColor = "";
      }
    });
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      if (!form.checkValidity()) {
        return; // Let browser show validation errors, don't lock the button
      }

      // Merge script1.js age validation
      const ageInput = document.getElementById("age");
      if (ageInput) {
        const age = parseInt(ageInput.value);
        if (!age || age <= 0 || age > 120) {
          e.preventDefault();
          alert("Please enter a valid age between 1 and 120.");
          return;
        }
      }

      // Disable button
      submitBtn.disabled = true;
      submitBtn.innerHTML = "⏳ Analyzing Risk...";

      // Add slight delay effect (smooth UX)
      setTimeout(() => {
        submitBtn.innerHTML = "Generating Report...";
      }, 500);
    });
  }

});
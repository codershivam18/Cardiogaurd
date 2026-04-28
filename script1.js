document.addEventListener("DOMContentLoaded", function () {

  const form = document.getElementById("predictForm");
  const ageInput = document.getElementById("age");
  const button = document.getElementById("predictBtn");

  if (form) {
    form.addEventListener("submit", function (e) {

      const age = parseInt(ageInput.value);

      // Validate age
      if (!age || age <= 0 || age > 120) {
        e.preventDefault();
        alert("Please enter a valid age between 1 and 120.");
        return;
      }

      // Show loading state
      button.disabled = true;
      button.textContent = "⏳ Analyzing...";
    });
  }

});
// Add a click event listener to the theme toggle button
document.getElementById("theme-toggle").addEventListener("click", function () {
  // Get the current class of the body tag
  var currentClass = document.body.className;

  // If the current class is bg-light-mode, switch to bg-dark-mode
  if (currentClass == "bg-light-mode") {
    document.body.className = "bg-dark-mode";
    document.querySelectorAll('.bg-light').forEach(function (element) {
      element.classList.remove('bg-light');
      element.classList.add('bg-dark-mode');
    });
    document.querySelectorAll('.text-light-mode').forEach(function (element) {
      element.classList.remove('text-light-mode');
      element.classList.add('text-dark-mode');
    });
  }
  // If the current class is bg-dark-mode, switch to bg-light-mode
  else {
    document.body.className = "bg-light-mode";
    document.querySelectorAll('.bg-dark-mode').forEach(function (element) {
      element.classList.remove('bg-dark-mode');
      element.classList.add('bg-light-mode');
    });
    document.querySelectorAll('.text-dark-mode').forEach(function (element) {
      element.classList.remove('text-dark-mode');
      element.classList.add('text-light-mode');
    });
  }
});
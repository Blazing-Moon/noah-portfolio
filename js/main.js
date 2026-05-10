/* Small utilities: footer year, any global concerns. */
(function () {
  const yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();
})();

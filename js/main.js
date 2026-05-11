/* Small utilities: footer year, placeholder track buttons. */
(function () {
  const yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  /* Placeholder track play buttons — animate icon until real audio is wired */
  document.querySelectorAll(".track-play-btn[data-placeholder]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var icon = btn.querySelector(".track-play-icon");
      if (!icon) return;
      icon.textContent = "♪";
      setTimeout(function () { icon.textContent = "▶"; }, 1800);
    });
  });
})();

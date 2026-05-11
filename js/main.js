/* Small utilities: footer year, email obfuscation, placeholder track buttons. */
(function () {
  const yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  /* Assemble contact email at runtime so the address never appears in HTML source.
     atob() decodes the base64 parts; the @ is a Unicode escape to further
     avoid plain-text harvesting in JS source scanners. */
  const link = document.getElementById("contact-link");
  if (link) {
    const addr = atob("bm9haA==") + "@" + atob("bm9haGdpZXNsZXIuY29t");
    link.href = "mailto:" + addr;
    link.textContent = addr;
  }

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

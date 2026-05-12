/* Small utilities: footer year, email obfuscation. */
(function () {
  const yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  /* Assemble contact email at runtime so the address never appears in HTML source. */
  const link = document.getElementById("contact-link");
  if (link) {
    const addr = atob("bm9haA==") + "@" + atob("bm9haGdpZXNsZXIuY29t");
    link.href = "mailto:" + addr;
    link.textContent = addr;
  }
})();

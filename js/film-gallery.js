/* ============================================================
   Film detail page — mini gallery + lightbox.
   Vanilla JS. No external dependencies.
   ============================================================ */

(function () {
  "use strict";

  const sideGallery = document.querySelector(".detail-side-gallery");
  if (!sideGallery) return;

  const thumbs = [...sideGallery.querySelectorAll(".detail-gallery-thumb")];
  if (thumbs.length === 0) return;

  let currentIdx = 0;

  /* Build a dedicated lightbox for this page */
  const lb = document.createElement("div");
  lb.className = "lightbox";
  lb.setAttribute("aria-hidden", "true");
  lb.setAttribute("role", "dialog");
  lb.setAttribute("aria-label", "Photo viewer");
  lb.innerHTML = `
    <button class="lightbox-close" aria-label="Close photo">×</button>
    <button class="lightbox-prev" aria-label="Previous photo">‹</button>
    <button class="lightbox-next" aria-label="Next photo">›</button>
    <figure class="lightbox-figure">
      <img id="fg-lb-img" alt="">
      <figcaption id="fg-lb-caption"></figcaption>
    </figure>
  `;
  document.body.appendChild(lb);

  const lbImg     = lb.querySelector("#fg-lb-img");
  const lbCaption = lb.querySelector("#fg-lb-caption");

  function show(idx) {
    currentIdx = idx;
    const btn = thumbs[idx];
    const img = btn.querySelector("img");
    lbImg.src = btn.dataset.full || img.src.replace("-thumbs/", "/").replace(/Photo-(\d+)/, "Photo-$1");
    lbImg.alt = img.alt || "";
    lbCaption.textContent = `${idx + 1} / ${thumbs.length}`;
  }

  function open(idx) {
    show(idx);
    lb.classList.add("is-open");
    lb.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function close() {
    lb.classList.remove("is-open");
    lb.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  function prev() { open((currentIdx - 1 + thumbs.length) % thumbs.length); }
  function next() { open((currentIdx + 1) % thumbs.length); }

  thumbs.forEach((btn, i) => btn.addEventListener("click", () => open(i)));
  lb.querySelector(".lightbox-close").addEventListener("click", close);
  lb.querySelector(".lightbox-prev").addEventListener("click", e => { e.stopPropagation(); prev(); });
  lb.querySelector(".lightbox-next").addEventListener("click", e => { e.stopPropagation(); next(); });
  lb.addEventListener("click", e => { if (e.target === lb) close(); });
  document.addEventListener("keydown", e => {
    if (!lb.classList.contains("is-open")) return;
    if (e.key === "Escape")      close();
    else if (e.key === "ArrowLeft")  prev();
    else if (e.key === "ArrowRight") next();
  });

})();

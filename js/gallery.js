/* ============================================================
   Gallery + Films rendering, filtering, and lightbox.
   Vanilla JS. No dependencies.
   ============================================================ */

(function () {
  "use strict";

  /* ---------- Render films grid on the home page ---------- */
  const filmsGrid = document.getElementById("films-grid");
  if (filmsGrid && typeof FILMS !== "undefined") {
    filmsGrid.innerHTML = FILMS.map(renderFilmCard).join("");
    // Attach YouTube-thumb fallback handlers (maxres -> hq) after insert
    filmsGrid.querySelectorAll("img[data-yt]").forEach(img => {
      img.addEventListener("error", onThumbError, { once: true });
    });
  }

  function renderFilmCard(film) {
    const thumbUrl = filmThumbUrl(film);
    const thumbContent = thumbUrl
      ? `<img src="${thumbUrl}" alt="${escapeAttr(film.title)} — thumbnail" data-yt="${film.youtubeId}" loading="lazy">`
      : `<div class="film-thumb-placeholder">${escapeHtml(film.title)}</div>`;

    return `
      <a class="film-card" href="films/${film.slug}.html">
        <div class="film-thumb">${thumbContent}</div>
        <h3 class="film-title">${escapeHtml(film.title)}</h3>
        <p class="film-meta">${escapeHtml(film.category)}</p>
      </a>
    `;
  }

  function onThumbError(e) {
    const img = e.target;
    const id = img.getAttribute("data-yt");
    if (!id) return;
    // maxresdefault sometimes doesn't exist; fall back to hqdefault.
    if (img.src.includes("maxresdefault")) {
      img.src = `https://img.youtube.com/vi/${id}/hqdefault.jpg`;
    } else {
      // Last resort: replace with placeholder
      const title = img.getAttribute("alt").replace(" — thumbnail", "");
      img.outerHTML = `<div class="film-thumb-placeholder">${escapeHtml(title)}</div>`;
    }
  }

  /* ---------- Gallery: load manifest and render ---------- */
  const galleryGrid = document.getElementById("gallery-grid");

  if (galleryGrid) {
    fetch("data/gallery.json", { cache: "no-cache" })
      .then(r => {
        if (!r.ok) throw new Error("Gallery manifest not found. Run scripts/build_gallery.py to generate it.");
        return r.json();
      })
      .then(manifest => renderGallery(manifest))
      .catch(err => {
        galleryGrid.innerHTML = `<p class="gallery-empty">${escapeHtml(err.message)}</p>`;
        console.warn("[gallery]", err);
      });
  }

  let galleryItems = []; // flat list for lightbox navigation

  function renderGallery(manifest) {
    // manifest shape: { photos: [{file, thumb, caption}, ...], stills: [...] }
    const photos = (manifest.photos || []).map(m => ({ ...m, category: "photos" }));
    const stills = (manifest.stills || []).map(m => ({ ...m, category: "stills" }));
    galleryItems = [...photos, ...stills];

    if (galleryItems.length === 0) {
      galleryGrid.innerHTML = `<p class="gallery-empty">No images yet. Drop files into <code>images/photos/</code> and <code>images/stills/</code>, then run <code>scripts/build_gallery.py</code>.</p>`;
      return;
    }

    galleryGrid.innerHTML = galleryItems.map((item, idx) => `
      <button type="button" class="gallery-item" data-category="${item.category}" data-index="${idx}" aria-label="View ${escapeAttr(item.caption || 'image ' + (idx + 1))}">
        <img src="${escapeAttr(item.thumb)}" alt="${escapeAttr(item.caption || '')}" loading="lazy">
      </button>
    `).join("");

    // Stagger the load-in animation slightly
    galleryGrid.querySelectorAll(".gallery-item").forEach((el, i) => {
      el.style.animationDelay = `${Math.min(i * 40, 600)}ms`;
      el.addEventListener("click", () => openLightbox(parseInt(el.dataset.index, 10)));
    });
  }

  /* ---------- Filter bar ---------- */
  const filterBar = document.querySelector(".filter-bar");
  if (filterBar) {
    filterBar.addEventListener("click", e => {
      const btn = e.target.closest(".filter-btn");
      if (!btn) return;
      const filter = btn.dataset.filter;

      filterBar.querySelectorAll(".filter-btn").forEach(b => {
        b.classList.toggle("is-active", b === btn);
        b.setAttribute("aria-selected", b === btn ? "true" : "false");
      });

      galleryGrid.querySelectorAll(".gallery-item").forEach(item => {
        const show = filter === "all" || item.dataset.category === filter;
        item.classList.toggle("is-hidden", !show);
      });
    });
  }

  /* ---------- Lightbox ---------- */
  const lightbox   = document.getElementById("lightbox");
  const lbImg      = document.getElementById("lightbox-img");
  const lbCaption  = document.getElementById("lightbox-caption");
  const lbClose    = lightbox?.querySelector(".lightbox-close");
  const lbPrev     = lightbox?.querySelector(".lightbox-prev");
  const lbNext     = lightbox?.querySelector(".lightbox-next");

  let lbIndex = 0;
  let lbVisibleItems = []; // subset currently shown under active filter

  function getVisibleItems() {
    // Respect active filter so prev/next stays within the current view
    const activeFilter = document.querySelector(".filter-btn.is-active")?.dataset.filter || "all";
    return galleryItems
      .map((item, idx) => ({ item, idx }))
      .filter(x => activeFilter === "all" || x.item.category === activeFilter);
  }

  function openLightbox(originalIndex) {
    lbVisibleItems = getVisibleItems();
    // Find the position of originalIndex within the visible subset
    lbIndex = lbVisibleItems.findIndex(x => x.idx === originalIndex);
    if (lbIndex < 0) lbIndex = 0;
    showLightboxItem();
    lightbox.classList.add("is-open");
    lightbox.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  function closeLightbox() {
    lightbox.classList.remove("is-open");
    lightbox.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  function showLightboxItem() {
    if (lbVisibleItems.length === 0) return;
    const { item } = lbVisibleItems[lbIndex];
    // Full-size path: convention is images/{category}/{file}
    const fullPath = item.full || item.file;
    lbImg.src = fullPath;
    lbImg.alt = item.caption || "";
    lbCaption.textContent = `${lbIndex + 1} / ${lbVisibleItems.length}${item.caption ? ' — ' + item.caption : ''}`;
  }

  function nextItem() {
    if (lbVisibleItems.length === 0) return;
    lbIndex = (lbIndex + 1) % lbVisibleItems.length;
    showLightboxItem();
  }
  function prevItem() {
    if (lbVisibleItems.length === 0) return;
    lbIndex = (lbIndex - 1 + lbVisibleItems.length) % lbVisibleItems.length;
    showLightboxItem();
  }

  lbClose?.addEventListener("click", closeLightbox);
  lbPrev?.addEventListener("click", e => { e.stopPropagation(); prevItem(); });
  lbNext?.addEventListener("click", e => { e.stopPropagation(); nextItem(); });

  // Click backdrop to close (but not clicks on the image itself)
  lightbox?.addEventListener("click", e => {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener("keydown", e => {
    if (!lightbox?.classList.contains("is-open")) return;
    if (e.key === "Escape") closeLightbox();
    else if (e.key === "ArrowRight") nextItem();
    else if (e.key === "ArrowLeft") prevItem();
  });

  /* ---------- Utilities ---------- */
  function escapeHtml(s) {
    if (s == null) return "";
    return String(s).replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }
  function escapeAttr(s) { return escapeHtml(s); }

})();

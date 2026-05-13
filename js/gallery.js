/* ============================================================
   Gallery + Films rendering, filtering, and lightbox.
   Vanilla JS. No dependencies.
   ============================================================ */

(function () {
  "use strict";

  /* ------------------------------------------------------------------ */
  /* Films grid                                                           */
  /* ------------------------------------------------------------------ */
  const filmsGrid = document.getElementById("films-grid");
  if (filmsGrid && typeof FILMS !== "undefined") {
    filmsGrid.innerHTML = FILMS.map(renderFilmCard).join("");
    filmsGrid.querySelectorAll("img[data-yt]").forEach(img => {
      img.addEventListener("error", onThumbError, { once: true });
    });

    // Films filter bar
    const filmsFilterBar = document.getElementById("films-filter-bar");
    if (filmsFilterBar) {
      filmsFilterBar.addEventListener("click", e => {
        const btn = e.target.closest(".filter-btn");
        if (!btn) return;
        const filter = btn.dataset.filter;

        filmsFilterBar.querySelectorAll(".filter-btn").forEach(b => {
          b.classList.toggle("is-active", b === btn);
          b.setAttribute("aria-selected", b === btn ? "true" : "false");
        });

        filmsGrid.querySelectorAll(".film-card").forEach(card => {
          const show = filter === "all" || card.dataset.type === filter;
          card.classList.toggle("is-hidden", !show);
        });
      });
    }
  }

  function renderFilmCard(film) {
    const thumbUrl = filmThumbUrl(film);
    const thumbContent = thumbUrl
      ? `<img src="${thumbUrl}" alt="${escapeAttr(film.title)} — thumbnail" data-yt="${film.youtubeId}" loading="lazy">`
      : `<div class="film-thumb-placeholder">${escapeHtml(film.title)}</div>`;

    return `
      <a class="film-card" href="films/${film.slug}.html" data-type="${escapeAttr(film.type || '')}">
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
    if (img.src.includes("maxresdefault")) {
      img.src = `https://img.youtube.com/vi/${id}/hqdefault.jpg`;
    } else {
      const title = img.getAttribute("alt").replace(" — thumbnail", "");
      img.outerHTML = `<div class="film-thumb-placeholder">${escapeHtml(title)}</div>`;
    }
  }

  /* ------------------------------------------------------------------ */
  /* Gallery: load manifest and render                                   */
  /* ------------------------------------------------------------------ */
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

  let galleryItems = [];

  function renderGallery(manifest) {
    const photos = (manifest.photos || []).map(m => ({ ...m, category: "photos" }));
    const stills = (manifest.stills || []).map(m => ({ ...m, category: "stills" }));
    galleryItems = [...photos, ...stills];

    if (galleryItems.length === 0) {
      galleryGrid.innerHTML = `<p class="gallery-empty">No images yet. Drop files into <code>images/photos/</code> and <code>images/stills/</code>, then run <code>scripts/build_gallery.py</code>.</p>`;
      return;
    }

    // Respect optional preview limit (home page uses data-preview-limit="9").
    // When limited, scope the lightbox to only the rendered items.
    const rawLimit = galleryGrid.dataset.previewLimit;
    const limit = rawLimit ? parseInt(rawLimit, 10) : Infinity;
    const visibleItems = galleryItems.slice(0, limit);
    if (limit < Infinity) galleryItems = visibleItems;

    // Preview grids (home page) use eager loading so thumbnails are in the DOM
    // before any nav scroll can happen, preventing layout shifts from lazy loads.
    const loadAttr = limit < Infinity ? "eager" : "lazy";
    galleryGrid.innerHTML = visibleItems.map((item, idx) => `
      <button type="button" class="gallery-item" data-category="${item.category}" data-index="${idx}" aria-label="View ${escapeAttr(item.caption || 'image ' + (idx + 1))}">
        <img src="${escapeAttr(item.thumb)}" alt="${escapeAttr(item.caption || '')}" loading="${loadAttr}">
      </button>
    `).join("");

    galleryGrid.querySelectorAll(".gallery-item").forEach((el, i) => {
      el.style.animationDelay = `${Math.min(i * 40, 600)}ms`;
      el.addEventListener("click", () => openLightbox(parseInt(el.dataset.index, 10)));
    });

    // If the URL hash targets a section below the gallery (e.g. #music, #contact),
    // re-scroll after rendering so the layout shift doesn't strand the user mid-page.
    const hash = window.location.hash;
    if (hash && hash !== "#gallery") {
      const target = document.querySelector(hash);
      if (target) target.scrollIntoView({ behavior: "smooth" });
    }
  }

  /* ------------------------------------------------------------------ */
  /* Gallery filter (full gallery page only — id="gallery-filter-bar")  */
  /* ------------------------------------------------------------------ */
  const galleryFilterBar = document.getElementById("gallery-filter-bar");
  if (galleryFilterBar) {
    galleryFilterBar.addEventListener("click", e => {
      const btn = e.target.closest(".filter-btn");
      if (!btn) return;
      const filter = btn.dataset.filter;

      galleryFilterBar.querySelectorAll(".filter-btn").forEach(b => {
        b.classList.toggle("is-active", b === btn);
        b.setAttribute("aria-selected", b === btn ? "true" : "false");
      });

      galleryGrid.querySelectorAll(".gallery-item").forEach(item => {
        const show = filter === "all" || item.dataset.category === filter;
        item.classList.toggle("is-hidden", !show);
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Lightbox                                                             */
  /* ------------------------------------------------------------------ */
  const lightbox  = document.getElementById("lightbox");
  const lbImg     = document.getElementById("lightbox-img");
  const lbCaption = document.getElementById("lightbox-caption");
  const lbClose   = lightbox?.querySelector(".lightbox-close");
  const lbPrev    = lightbox?.querySelector(".lightbox-prev");
  const lbNext    = lightbox?.querySelector(".lightbox-next");

  let lbIndex = 0;
  let lbVisibleItems = [];

  function getVisibleItems() {
    const activeFilter = galleryFilterBar?.querySelector(".filter-btn.is-active")?.dataset.filter || "all";
    return galleryItems
      .map((item, idx) => ({ item, idx }))
      .filter(x => activeFilter === "all" || x.item.category === activeFilter);
  }

  function openLightbox(originalIndex) {
    lbVisibleItems = getVisibleItems();
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
    lbImg.src = item.full || item.file;
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
  lightbox?.addEventListener("click", e => { if (e.target === lightbox) closeLightbox(); });

  document.addEventListener("keydown", e => {
    if (!lightbox?.classList.contains("is-open")) return;
    if (e.key === "Escape")      closeLightbox();
    else if (e.key === "ArrowRight") nextItem();
    else if (e.key === "ArrowLeft")  prevItem();
  });

  /* ------------------------------------------------------------------ */
  /* Utilities                                                            */
  /* ------------------------------------------------------------------ */
  function escapeHtml(s) {
    if (s == null) return "";
    return String(s).replace(/[&<>"']/g, c => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[c]));
  }
  function escapeAttr(s) { return escapeHtml(s); }

})();

/* ============================================================
   Music player — SoundCloud Widget API with custom controls.
   One shared hidden iframe; tracks switch via widget.load().
   ============================================================ */

(function () {
  "use strict";

  const tracks = Array.from(document.querySelectorAll(".music-track[data-sc-url]"));
  if (!tracks.length) return;

  /* ---- Hidden SC iframe ---- */
  const iframe = document.createElement("iframe");
  iframe.id = "sc-widget";
  iframe.allow = "autoplay";
  iframe.setAttribute("aria-hidden", "true");
  iframe.style.cssText = "position:absolute;width:1px;height:1px;border:0;opacity:0;pointer-events:none;left:-9999px;";
  document.body.appendChild(iframe);

  /* ---- Load SC Widget API ---- */
  const apiScript = document.createElement("script");
  apiScript.src = "https://w.soundcloud.com/player/api.js";
  document.head.appendChild(apiScript);

  let widget       = null;
  let widgetReady  = false;
  let activeTrack  = null;   /* the currently-loaded <li> */
  let isPlaying    = false;
  let durMs        = 0;
  let isScrubbing  = false;

  apiScript.onload = function () {
    /* Prime the iframe with the first track URL so the widget initialises */
    iframe.src = embedUrl(tracks[0].dataset.scUrl, false);
    widget = SC.Widget(iframe);

    widget.bind(SC.Widget.Events.READY, function () {
      widgetReady = true;
    });

    widget.bind(SC.Widget.Events.PLAY, function () {
      isPlaying = true;
      if (activeTrack) setIcon(activeTrack, true);
    });

    widget.bind(SC.Widget.Events.PAUSE, function () {
      isPlaying = false;
      if (activeTrack) setIcon(activeTrack, false);
    });

    widget.bind(SC.Widget.Events.FINISH, function () {
      isPlaying = false;
      if (activeTrack) {
        setIcon(activeTrack, false);
        setProgress(activeTrack, 0, durMs);
      }
    });

    widget.bind(SC.Widget.Events.PLAY_PROGRESS, function (e) {
      if (!isScrubbing && activeTrack) {
        setProgress(activeTrack, e.currentPosition, durMs);
      }
    });
  };

  /* ---- Wire up each track ---- */
  tracks.forEach(function (li) {
    const btn      = li.querySelector(".track-play-btn");
    const title    = li.querySelector(".track-title");
    const scrubber = li.querySelector(".track-scrubber");

    function handlePlayClick() {
      if (!widgetReady) return;

      if (activeTrack && activeTrack !== li) {
        /* Stop old track UI */
        setIcon(activeTrack, false);
        setProgress(activeTrack, 0, 0);
        /* Load new track */
        activeTrack = li;
        widget.load(li.dataset.scUrl, { auto_play: true, callback: onLoad });
      } else if (activeTrack === li) {
        /* Toggle play / pause */
        isPlaying ? widget.pause() : widget.play();
      } else {
        /* First interaction — widget already has track[0] primed */
        activeTrack = li;
        if (li === tracks[0]) {
          widget.play();
          widget.getDuration(function (d) { durMs = d; updateDur(li, d); });
        } else {
          widget.load(li.dataset.scUrl, { auto_play: true, callback: onLoad });
        }
      }
    }

    if (btn)   btn.addEventListener("click", handlePlayClick);
    if (title) title.addEventListener("click", handlePlayClick);

    if (scrubber) {
      scrubber.addEventListener("pointerdown", function () { isScrubbing = true; });

      scrubber.addEventListener("input", function () {
        if (activeTrack === li && durMs > 0) {
          const pos = (scrubber.value / 1000) * durMs;
          setTimeEl(li, pos);
          updateScrubberFill(scrubber, scrubber.value / 10);
        }
      });

      scrubber.addEventListener("change", function () {
        isScrubbing = false;
        if (activeTrack === li && widgetReady && durMs > 0) {
          widget.seekTo((scrubber.value / 1000) * durMs);
        }
      });
    }
  });

  function onLoad() {
    widget.getDuration(function (d) {
      durMs = d;
      if (activeTrack) updateDur(activeTrack, d);
    });
  }

  /* ---- Helpers ---- */
  function embedUrl(scUrl, autoPlay) {
    return "https://w.soundcloud.com/player/?url=" + encodeURIComponent(scUrl) +
      "&auto_play=" + (autoPlay ? "true" : "false") +
      "&hide_related=true&show_comments=false&show_user=false&show_reposts=false";
  }

  function setIcon(li, playing) {
    const icon = li.querySelector(".track-play-icon");
    const btn  = li.querySelector(".track-play-btn");
    if (icon) icon.textContent = playing ? "⏸" : "▶";
    if (btn)  btn.classList.toggle("is-playing", playing);
  }

  function setProgress(li, posMs, totalMs) {
    const scrubber = li.querySelector(".track-scrubber");
    if (scrubber) {
      const val = totalMs > 0 ? Math.round((posMs / totalMs) * 1000) : 0;
      scrubber.value = val;
      updateScrubberFill(scrubber, val / 10);
    }
    setTimeEl(li, posMs);
  }

  function setTimeEl(li, posMs) {
    const el = li.querySelector(".track-time");
    if (el) el.textContent = fmt(posMs);
  }

  function updateDur(li, ms) {
    const el = li.querySelector(".track-dur");
    if (el) el.textContent = fmt(ms);
  }

  function updateScrubberFill(scrubber, pct) {
    scrubber.style.setProperty("--fill", pct.toFixed(1) + "%");
  }

  function fmt(ms) {
    const s = Math.floor((ms || 0) / 1000);
    return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0");
  }

})();

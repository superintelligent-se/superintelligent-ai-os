(() => {
  "use strict";

  const qs = (selector, root = document) => root.querySelector(selector);
  const qsa = (selector, root = document) => [...root.querySelectorAll(selector)];

  function initCalculators() {
    qsa("[data-calculator]").forEach((calculator) => {
      const inputs = qsa("input[data-factor]", calculator);
      const output = qs("[data-result]", calculator);
      const update = () => {
        const values = Object.fromEntries(inputs.map((input) => [input.dataset.factor, Number(input.value)]));
        const hours = (values.people || 0) * (values.hours || 0) * (values.adoption || 0) / 100;
        const formatted = new Intl.NumberFormat(document.documentElement.lang || "sv-SE", { maximumFractionDigits: 0 }).format(hours);
        output.textContent = `${formatted} timmar frigjorda per månad`;
      };
      inputs.forEach((input) => input.addEventListener("input", update));
      update();
    });
  }

  function initDeck() {
    const deck = qs("[data-deck]");
    if (!deck) return;
    const slides = qsa(".slide", deck);
    const params = new URLSearchParams(location.search);
    let index = Math.max(0, Math.min(slides.length - 1, Number(params.get("slide") || 1) - 1));
    const startedAt = Date.now();
    const count = qs("[data-slide-count]");
    const notes = qs("[data-presenter-notes]");
    const next = qs("[data-next-preview]");

    if (params.has("presenter")) document.body.classList.add("presenter-mode");

    const render = () => {
      slides.forEach((slide, position) => {
        slide.classList.toggle("is-active", position === index);
        slide.setAttribute("aria-hidden", position === index ? "false" : "true");
      });
      if (count) count.textContent = `${index + 1} / ${slides.length}`;
      if (notes) notes.textContent = qs(".notes", slides[index])?.textContent.trim() || "Inga notes.";
      if (next) {
        const upcoming = slides[index + 1];
        next.textContent = upcoming ? (qs("h1, h2", upcoming)?.textContent || "Nästa slide") : "Slut";
      }
      params.set("slide", String(index + 1));
      history.replaceState(null, "", `${location.pathname}?${params.toString()}`);
    };

    const move = (delta) => { index = Math.max(0, Math.min(slides.length - 1, index + delta)); render(); };
    qs("[data-prev]")?.addEventListener("click", () => move(-1));
    qs("[data-next]")?.addEventListener("click", () => move(1));
    qs("[data-presenter]")?.addEventListener("click", () => window.open(`${location.pathname}?presenter=1&slide=${index + 1}`, "presenter", "width=1440,height=900"));
    document.addEventListener("keydown", (event) => {
      if (["ArrowRight", "PageDown", " "].includes(event.key)) { event.preventDefault(); move(1); }
      if (["ArrowLeft", "PageUp"].includes(event.key)) { event.preventDefault(); move(-1); }
      if (event.key === "Home") { index = 0; render(); }
      if (event.key === "End") { index = slides.length - 1; render(); }
      if (event.key.toLowerCase() === "b") document.body.classList.toggle("is-blank");
      if (event.key.toLowerCase() === "s" && !params.has("presenter")) window.open(`${location.pathname}?presenter=1&slide=${index + 1}`, "presenter", "width=1440,height=900");
    });
    setInterval(() => {
      const timer = qs("[data-presenter-timer]");
      if (!timer) return;
      const seconds = Math.floor((Date.now() - startedAt) / 1000);
      timer.textContent = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
    }, 1000);
    render();
  }

  function appendQaReport() {
    if (!new URLSearchParams(location.search).has("qa")) return;
    const overflow = qsa("body *").filter((element) => {
      const rect = element.getBoundingClientRect();
      return rect.width > 0 && (rect.left < -1 || rect.right > document.documentElement.clientWidth + 1);
    }).map((element) => element.id || element.className || element.tagName).slice(0, 20);
    const brokenAssets = qsa("img").filter((image) => !image.complete || image.naturalWidth === 0).map((image) => image.getAttribute("src"));
    const remoteAssets = qsa("[src], link[href]").map((element) => element.getAttribute("src") || element.getAttribute("href")).filter((value) => /^https?:/i.test(value || ""));
    const report = {
      title: document.title,
      viewport: [window.innerWidth, window.innerHeight],
      overflow,
      brokenAssets,
      remoteAssets,
      landmarks: { main: qsa("main").length, nav: qsa("nav").length },
      headings: qsa("h1, h2, h3").map((heading) => heading.tagName),
      fonts: {
        raleway: document.fonts ? document.fonts.check("16px Raleway") : null,
        inter: document.fonts ? document.fonts.check("16px Inter") : null
      }
    };
    const payload = document.createElement("script");
    payload.id = "qa-result";
    payload.type = "application/json";
    payload.textContent = JSON.stringify(report);
    document.body.append(payload);
  }

  initCalculators();
  initDeck();
  appendQaReport();
})();

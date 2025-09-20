// Minimal dependency-free lightbox with gallery navigation
(function () {
  function $(sel, root) {
    return (root || document).querySelector(sel);
  }
  function $all(sel, root) {
    return Array.from((root || document).querySelectorAll(sel));
  }

  const backdrop = document.createElement("div");
  backdrop.className = "lb-backdrop";
  backdrop.innerHTML =
    '<div class="lb-container">\n  <img class="lb-img" alt="" />\n  <button class="lb-close" aria-label="Close">\u2715</button>\n  <div class="lb-nav">\n    <button class="lb-btn lb-prev" aria-label="Previous">\u2039</button>\n    <button class="lb-btn lb-next" aria-label="Next">\u203A</button>\n  </div>\n  <div class="lb-caption"></div>\n</div>';
  document.body.appendChild(backdrop);

  const imgEl = $(".lb-img", backdrop);
  const capEl = $(".lb-caption", backdrop);
  const closeBtn = $(".lb-close", backdrop);
  const prevBtn = $(".lb-prev", backdrop);
  const nextBtn = $(".lb-next", backdrop);

  let group = [];
  let index = -1;

  function openAt(i) {
    index = i;
    const a = group[index];
    if (!a) return;
    const href = a.getAttribute("href");
    imgEl.src = href;
    const caption =
      a.getAttribute("title") ||
      a.querySelector("img")?.getAttribute("alt") ||
      "";
    capEl.textContent = caption;
    backdrop.classList.add("show");
    document.body.style.overflow = "hidden";
    updateButtons();
  }

  function updateButtons() {
    prevBtn.style.visibility = index > 0 ? "visible" : "hidden";
    nextBtn.style.visibility = index < group.length - 1 ? "visible" : "hidden";
  }

  function close() {
    backdrop.classList.remove("show");
    document.body.style.overflow = "";
    imgEl.src = "";
    group = [];
    index = -1;
  }

  closeBtn.addEventListener("click", close);
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) close();
  });
  document.addEventListener("keydown", (e) => {
    if (!backdrop.classList.contains("show")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft" && index > 0) openAt(index - 1);
    if (e.key === "ArrowRight" && index < group.length - 1) openAt(index + 1);
  });
  prevBtn.addEventListener("click", () => {
    if (index > 0) openAt(index - 1);
  });
  nextBtn.addEventListener("click", () => {
    if (index < group.length - 1) openAt(index + 1);
  });

  // Delegate clicks from galleries
  document.addEventListener("click", (e) => {
    const a = e.target.closest('a[data-lightbox="gallery"]');
    if (!a) return;
    // Only intercept if the link points to an image we have locally
    const href = a.getAttribute("href") || "";
    if (!/\.(png|jpg|jpeg|gif|webp)(\?|$)/i.test(href)) return;
    e.preventDefault();
    const container = a.closest(".gallery") || document;
    group = $all('a[data-lightbox="gallery"]', container).filter((x) =>
      /\.(png|jpg|jpeg|gif|webp)(\?|$)/i.test(x.getAttribute("href") || ""),
    );
    const i = group.indexOf(a);
    openAt(i >= 0 ? i : 0);
  });
})();

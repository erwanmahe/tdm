// Small UX polish: nav ripple, external link target, map tooltip helper
(function () {
  // Mark external links
  document
    .querySelectorAll('a[href^="http"]:not([href*="' + location.host + '"])')
    .forEach((a) => {
      a.setAttribute("target", "_blank");
      a.setAttribute("rel", "noopener");
    });

  // Sidebar active indicator ripple on click
  const nav = document.querySelector(".nav");
  if (nav) {
    nav.addEventListener("click", (e) => {
      const a = e.target.closest("a");
      if (!a) return;
      const r = document.createElement("span");
      r.style.cssText =
        "position:absolute; inset:0; border-radius:8px; background:rgba(34,211,238,.12); opacity:0; pointer-events:none;";
      a.style.position = "relative";
      a.appendChild(r);
      requestAnimationFrame(() => {
        r.style.transition = "opacity .3s ease";
        r.style.opacity = "1";
      });
      setTimeout(() => {
        r.style.opacity = "0";
        setTimeout(() => r.remove(), 300);
      }, 180);
    });
  }

  // Optional map tooltip for city markers if present
  const svg = document.getElementById("worldmap");
  if (svg) {
    const tip = document.createElement("div");
    tip.style.cssText =
      "position:fixed; padding:6px 8px; background:#111827; color:#e5e7eb; border:1px solid #1f2937; border-radius:6px; font-size:12px; pointer-events:none; opacity:0; transition:opacity .12s; z-index:9999";
    document.body.appendChild(tip);
    svg.addEventListener("mousemove", (e) => {
      const t = e.target;
      if (t?.tagName === "circle" && t.parentNode?.querySelector("text")) {
        tip.textContent = t.parentNode.querySelector("text").textContent || "";
        tip.style.left = e.clientX + 12 + "px";
        tip.style.top = e.clientY + 12 + "px";
        tip.style.opacity = "1";
      } else {
        tip.style.opacity = "0";
      }
    });
  }
})();

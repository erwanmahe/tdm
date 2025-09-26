// Petite-vue app state and helpers. Plain script (no module) for file:// compatibility.
(function () {
  function tail3(pathname) {
    const parts = (pathname || '').split('/').filter(Boolean);
    return parts.slice(-3).join('/');
  }

  const here = tail3(location.pathname);

  // Compute a base URL from the shared data.js, so gallery paths are resolved
  // relative to the city folder regardless of current page depth.
  function dataBaseURL() {
    // Try to find the script tag that loaded the per-page data (filename EXACTLY 'data.js')
    const scripts = Array.from(document.scripts || document.querySelectorAll('script[src]'));
    for (const s of scripts) {
      const raw = s.src || s.getAttribute('src') || '';
      try {
        const u = new URL(raw, location.href);
        const filename = (u.pathname || '').split('/').filter(Boolean).pop();
        if (filename === 'data.js') {
          return new URL('.', u.href).href;
        }
      } catch (e) {
        // ignore and continue
      }
    }
    // Fallback to current document's directory
    try {
      return new URL('.', location.href).href;
    } catch (e) {
      return location.href;
    }
  }

  // Cache the computed base once
  const __DATA_BASE__ = dataBaseURL();

  window.TDM_APP = function () {
    return {
      nav: Array.isArray(window.TDM_NAV) ? window.TDM_NAV : [],
      page: typeof window.TDM_PAGE === 'object' && window.TDM_PAGE ? window.TDM_PAGE : {},
      isActive(href) {
        try {
          const target = new URL(href, location.href).pathname;
          return tail3(target) === here;
        } catch (e) {
          return tail3(href) === here;
        }
      },
      // Flatten nav groups to a single ordered list of links
      _flatLinks() {
        const out = [];
        for (const g of (this.nav || [])) {
          if (g && Array.isArray(g.links)) out.push(...g.links);
        }
        return out;
      },
      _idx() {
        const links = this._flatLinks();
        for (let i = 0; i < links.length; i++) {
          const l = links[i];
          try {
            const target = new URL(l.href, location.href).pathname;
            if (tail3(target) === here) return i;
          } catch (e) {
            if (tail3(l.href) === here) return i;
          }
        }
        return -1;
      },
      prevLink() {
        const links = this._flatLinks();
        const i = this._idx();
        return i > 0 ? links[i - 1] : null;
      },
      nextLink() {
        const links = this._flatLinks();
        const i = this._idx();
        return i >= 0 && i < links.length - 1 ? links[i + 1] : null;
      },
      computedTitle() {
        const t = (this.page && this.page.title) || '';
        if (t && t.trim()) return t;
        // fallback to <head><title>
        return document.title || '';
      },
      computedResume() {
        const r = (this.page && this.page.resume) || '';
        // Ignore templating artifacts if any
        return (typeof r === 'string' && r.indexOf('{{') === -1) ? r : '';
      },
      // Resolve a relative path (from data.js) against the city folder, so it works
      // from nested pages like photos/ and photos/subfolder/ as well.
      resolvePath(p) {
        try {
          return new URL(p || '', __DATA_BASE__).href;
        } catch (e) {
          return p || '';
        }
      },
      resolveHref(p) { return this.resolvePath(p); },
      resolveSrc(p) { return this.resolvePath(p); },
      sectionStyle: {
        margin: '10px 0 6px',
        color: '#614e33',
        fontSize: '12px',
        fontWeight: 'bold',
        textTransform: 'uppercase',
        letterSpacing: '0.08em'
      }
    };
  };
})();

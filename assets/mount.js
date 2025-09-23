// Ensure petite-vue is loaded and mount after DOM is ready, working over file://
(function () {
  function mount() {
    if (!window.PetiteVue || !window.TDM_APP) return false;
    try {
      window.PetiteVue.createApp({ TDM_APP: window.TDM_APP }).mount('#app');
      return true;
    } catch (e) {
      return false;
    }
  }

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    if (!mount()) {
      // Retry shortly in case PetiteVue script is still initializing
      setTimeout(mount, 0);
    }
  } else {
    document.addEventListener('DOMContentLoaded', function () {
      if (!mount()) setTimeout(mount, 0);
    });
  }
})();

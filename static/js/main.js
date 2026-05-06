(function () {
  const tabs = Array.from(document.querySelectorAll(".section-tab"));
  const panels = Array.from(document.querySelectorAll(".grammar-section"));
  const navButtons = Array.from(document.querySelectorAll(".section-nav-btn"));

  if (!tabs.length || !panels.length) {
    return;
  }

  const validIds = new Set(tabs.map((tab) => Number(tab.dataset.section)));

  function resizePlotly(sectionId) {
    const panel = document.querySelector(`#section-${sectionId}`);
    if (!panel || typeof window.Plotly === "undefined") return;
    const plots = panel.querySelectorAll(".plotly-graph-div");
    plots.forEach((plot) => {
      window.Plotly.Plots.resize(plot);
    });
  }

  function activate(sectionId, updateHash) {
    const id = Number(sectionId);
    if (!validIds.has(id)) return;

    tabs.forEach((tab) => {
      const active = Number(tab.dataset.section) === id;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", active ? "true" : "false");
      tab.tabIndex = active ? 0 : -1;
    });

    panels.forEach((panel) => {
      const active = Number(panel.dataset.sectionId) === id;
      panel.hidden = !active;
    });

    if (updateHash) {
      history.replaceState(null, "", `#section-${id}`);
    }
    resizePlotly(id);
  }

  function sectionFromHash() {
    const hash = window.location.hash || "";
    const m = hash.match(/^#section-(\d+)$/);
    if (!m) return 1;
    const id = Number(m[1]);
    return validIds.has(id) ? id : 1;
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      activate(tab.dataset.section, true);
    });
  });

  navButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      activate(btn.dataset.goto, true);
    });
  });

  window.addEventListener("hashchange", () => {
    activate(sectionFromHash(), false);
  });

  activate(sectionFromHash(), false);
})();

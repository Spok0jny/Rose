/**
 * @name ROSE-CompetitiveMode
 * @author Rose Team
 * @description Competitive Mode - Override opponent and non-party skins to default base skins in Draft & Ranked queues
 * @link https://github.com/Alban1911/Rose
 */
(function initCompetitiveMode() {
  const LOG_PREFIX = "[ROSE-CompetitiveMode]";
  const CONTAINER_SELECTOR = ".skin-selection-carousel-container, .skin-selection-carousel, .champion-select-main-container";
  const BUTTON_CLASS = "rose-competitive-button";
  const FLYOUT_CLASS = "rose-competitive-flyout";

  let bridge = null;
  let isInChampSelect = false;
  let competitiveMode = "off"; // "off", "enemy_only", "all_except_party"
  let competitiveSupported = false;
  let buttonElement = null;
  let flyoutElement = null;
  let observer = null;

  function waitForBridge() {
    return new Promise((resolve, reject) => {
      const timeout = 10000;
      const interval = 50;
      let elapsed = 0;
      const check = () => {
        if (window.__roseBridge) return resolve(window.__roseBridge);
        elapsed += interval;
        if (elapsed >= timeout) return reject(new Error("Bridge not available"));
        setTimeout(check, interval);
      };
      check();
    });
  }

  function escapeHtml(str) {
    if (typeof str !== "string") return String(str);
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  const CSS_RULES = `
    .${BUTTON_CLASS} {
      position: absolute;
      top: 14px;
      right: 18px;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: rgba(1, 10, 19, 0.85);
      border: 1px solid #785a28;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 100;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
    }

    .${BUTTON_CLASS}:hover {
      border-color: #c8aa6e;
      box-shadow: 0 0 10px rgba(200, 170, 110, 0.4);
      transform: scale(1.05);
    }

    .${BUTTON_CLASS}.active {
      border-color: #0ac8b9;
      background: rgba(10, 200, 185, 0.15);
      box-shadow: 0 0 12px rgba(10, 200, 185, 0.5);
    }

    .${BUTTON_CLASS}.disabled {
      opacity: 0.35;
      cursor: not-allowed;
      border-color: #5c5b57;
      transform: none !important;
      box-shadow: none !important;
    }

    .${BUTTON_CLASS} svg {
      width: 18px;
      height: 18px;
      transition: fill 0.2s ease;
    }

    .${BUTTON_CLASS} .tooltip {
      visibility: hidden;
      opacity: 0;
      position: absolute;
      bottom: calc(100% + 8px);
      right: 0;
      white-space: nowrap;
      background: #010a13;
      border: 1px solid #785a28;
      color: #cdbe91;
      padding: 6px 10px;
      font-size: 12px;
      font-family: LoL Display, sans-serif;
      border-radius: 3px;
      pointer-events: none;
      transition: opacity 0.15s ease;
      z-index: 1000;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8);
    }

    .${BUTTON_CLASS}:hover .tooltip {
      visibility: visible;
      opacity: 1;
    }

    .${FLYOUT_CLASS} {
      position: fixed;
      background: #010a13;
      border: 1px solid #785a28;
      border-radius: 4px;
      padding: 10px 0;
      min-width: 210px;
      box-shadow: 0 6px 20px rgba(0, 0, 0, 0.9);
      z-index: 10000;
      font-family: LoL Display, sans-serif;
      color: #cdbe91;
      user-select: none;
    }

    .${FLYOUT_CLASS} .flyout-header {
      padding: 4px 14px 8px 14px;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #a09b8c;
      border-bottom: 1px solid rgba(120, 90, 40, 0.3);
      margin-bottom: 6px;
    }

    .${FLYOUT_CLASS} .flyout-item {
      display: flex;
      align-items: center;
      padding: 8px 14px;
      cursor: pointer;
      font-size: 13px;
      transition: background 0.15s ease;
    }

    .${FLYOUT_CLASS} .flyout-item:hover {
      background: rgba(200, 170, 110, 0.15);
      color: #f0e6d2;
    }

    .${FLYOUT_CLASS} .flyout-item.selected {
      color: #0ac8b9;
      font-weight: bold;
    }

    .${FLYOUT_CLASS} .flyout-radio {
      width: 14px;
      height: 14px;
      border-radius: 50%;
      border: 1px solid #785a28;
      margin-right: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .${FLYOUT_CLASS} .flyout-item.selected .flyout-radio {
      border-color: #0ac8b9;
    }

    .${FLYOUT_CLASS} .flyout-radio-dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: transparent;
    }

    .${FLYOUT_CLASS} .flyout-item.selected .flyout-radio-dot {
      background: #0ac8b9;
    }
  `;

  function getShieldSvg(isActive, isSupported) {
    let fillColor = "#785a28";
    if (isActive) fillColor = "#0ac8b9";
    else if (!isSupported) fillColor = "#5c5b57";

    return `
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M12 2L3 6V12C3 17.52 6.84 22.74 12 24C17.16 22.74 21 17.52 21 12V6L12 2Z" 
              fill="${fillColor}" fill-opacity="${isActive ? "0.3" : "0.15"}" stroke="${fillColor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        ${isActive ? '<circle cx="12" cy="12" r="3" fill="#0ac8b9" />' : ''}
      </svg>
    `;
  }

  function getModeLabel(mode) {
    if (mode === "enemy_only") return "Enemy Only";
    if (mode === "all_except_party") return "All Except Me & Party";
    return "Off";
  }

  function updateButtonUI() {
    if (!buttonElement) return;

    const isActive = competitiveMode !== "off" && competitiveSupported;
    buttonElement.className = `${BUTTON_CLASS} ${isActive ? "active" : ""} ${!competitiveSupported ? "disabled" : ""}`;

    let tooltipText = `Competitive Mode: ${getModeLabel(competitiveMode)}`;
    if (!competitiveSupported) {
      tooltipText = "Competitive Mode is only available in Draft & Ranked queues";
    }

    buttonElement.innerHTML = `
      ${getShieldSvg(isActive, competitiveSupported)}
      <div class="tooltip">${escapeHtml(tooltipText)}</div>
    `;
  }

  function closeFlyout() {
    if (flyoutElement && flyoutElement.parentNode) {
      flyoutElement.parentNode.removeChild(flyoutElement);
    }
    flyoutElement = null;
  }

  function openFlyout() {
    closeFlyout();
    if (!competitiveSupported || !buttonElement) return;

    const rect = buttonElement.getBoundingClientRect();
    const flyout = document.createElement("div");
    flyout.className = FLYOUT_CLASS;
    flyout.style.top = `${rect.bottom + 8}px`;
    flyout.style.left = `${Math.max(10, rect.right - 210)}px`;

    const options = [
      { id: "off", label: "Off (Default Rose)" },
      { id: "enemy_only", label: "Enemy Only" },
      { id: "all_except_party", label: "All Except Me & Party" },
    ];

    let itemsHtml = `
      <div class="flyout-header">Competitive Mode</div>
    `;

    options.forEach((opt) => {
      const isSelected = competitiveMode === opt.id;
      itemsHtml += `
        <div class="flyout-item ${isSelected ? "selected" : ""}" data-mode="${opt.id}">
          <div class="flyout-radio">
            <div class="flyout-radio-dot"></div>
          </div>
          <span>${escapeHtml(opt.label)}</span>
        </div>
      `;
    });

    flyout.innerHTML = itemsHtml;

    flyout.querySelectorAll(".flyout-item").forEach((el) => {
      el.addEventListener("click", (e) => {
        e.stopPropagation();
        const mode = el.getAttribute("data-mode");
        if (mode && bridge) {
          competitiveMode = mode;
          bridge.send({
            type: "update-competitive-mode",
            mode: mode,
          });
          updateButtonUI();
        }
        closeFlyout();
      });
    });

    document.body.appendChild(flyout);
    flyoutElement = flyout;

    const onOutsideClick = (e) => {
      if (!flyout.contains(e.target) && e.target !== buttonElement && !buttonElement.contains(e.target)) {
        closeFlyout();
        document.removeEventListener("click", onOutsideClick, true);
      }
    };
    setTimeout(() => {
      document.addEventListener("click", onOutsideClick, true);
    }, 10);
  }

  function mountButton() {
    if (!isInChampSelect) {
      removeButton();
      return;
    }

    if (buttonElement && buttonElement.isConnected) {
      updateButtonUI();
      return;
    }

    const container = document.querySelector(".skin-selection-carousel-container") ||
                      document.querySelector(".skin-selection-carousel") ||
                      document.querySelector(".champion-select-main-container");

    if (!container) return;

    // Ensure relative positioning
    const computed = window.getComputedStyle(container);
    if (computed.position === "static") {
      container.style.position = "relative";
    }

    const button = document.createElement("div");
    button.className = BUTTON_CLASS;
    button.addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      if (!competitiveSupported) return;
      if (flyoutElement) {
        closeFlyout();
      } else {
        openFlyout();
      }
    });

    container.appendChild(button);
    buttonElement = button;
    updateButtonUI();
  }

  function removeButton() {
    closeFlyout();
    if (buttonElement && buttonElement.parentNode) {
      buttonElement.parentNode.removeChild(buttonElement);
    }
    buttonElement = null;
  }

  function handleCompetitiveState(data) {
    if (data && typeof data.mode === "string") {
      competitiveMode = data.mode;
    }
    if (data && typeof data.supported === "boolean") {
      competitiveSupported = data.supported;
    }
    updateButtonUI();
  }

  function handlePhaseChange(data) {
    const phase = data?.phase || "";
    isInChampSelect = phase === "ChampSelect";
    if (isInChampSelect) {
      mountButton();
      if (bridge) {
        bridge.send({ type: "request-competitive-state" });
      }
    } else {
      removeButton();
    }
  }

  function startObserver() {
    if (observer) return;
    observer = new MutationObserver(() => {
      if (isInChampSelect && (!buttonElement || !buttonElement.isConnected)) {
        mountButton();
      }
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  async function start() {
    try {
      bridge = await waitForBridge();
      console.log(`${LOG_PREFIX} Connected to Rose bridge`);

      // Inject CSS
      const style = document.createElement("style");
      style.textContent = CSS_RULES;
      document.head.appendChild(style);

      // Subscribe to bridge events
      bridge.subscribe("competitive-state", handleCompetitiveState);
      bridge.subscribe("phase-change", handlePhaseChange);

      // Initial state request
      bridge.send({ type: "request-competitive-state" });

      startObserver();
    } catch (err) {
      console.warn(`${LOG_PREFIX} Initialization failed:`, err);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();

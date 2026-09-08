/**
 * @name Rose-PartyMode
 * @author Rose Team
 * @description Party Mode - See your friends' skins in game via P2P
 * @link https://github.com/Alban1911/Rose
 */
(function initPartyMode() {
  const LOG_PREFIX = "[Rose-PartyMode]";
  const GOLDEN_ROSE_ICON = "data:image/png;base64,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";
  window.__roseGoldenRoseIcon = GOLDEN_ROSE_ICON;
  let BRIDGE_PORT = 50000;
  let BRIDGE_URL = `ws://127.0.0.1:${BRIDGE_PORT}`;
  const BRIDGE_PORT_STORAGE_KEY = "rose_bridge_port";
  const DISCOVERY_START_PORT = 50000;
  const DISCOVERY_END_PORT = 50010;

  const PANEL_ID = "rose-party-panel";
  const BUTTON_ID = "rose-party-button";
  const LOBBY_BUTTON_ID = "rose-party-lobby-button";

  let bridgeSocket = null;
  let bridgeReady = false;
  let bridgeQueue = [];
  let partyPanel = null;
  let lobbyButton = null;
  let isVisible = false;
  let currentUIMode = null; // 'lobby' or 'champselect'

  // Party state
  let partyState = {
    enabled: false,
    my_token: null,
    my_summoner_id: null,
    my_summoner_name: "Unknown",
    peers: [],
  };

  // Network interfaces cache
  let networkInterfaces = [];
  let selectedIP = "";
  let selectedPort = 7865;

  /**
   * Escape HTML special characters to prevent XSS
   */
  function escapeHtml(str) {
    if (typeof str !== "string") return str;
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Load bridge port with file-based discovery and localStorage caching
  async function loadBridgePort() {
    try {
      const cachedPort = localStorage.getItem(BRIDGE_PORT_STORAGE_KEY);
      if (cachedPort) {
        const port = parseInt(cachedPort, 10);
        if (!isNaN(port) && port > 0) {
          try {
            const response = await fetch(
              `http://127.0.0.1:${port}/bridge-port`,
              { signal: AbortSignal.timeout(50) }
            );
            if (response.ok) {
              const portText = await response.text();
              const fetchedPort = parseInt(portText.trim(), 10);
              if (!isNaN(fetchedPort) && fetchedPort > 0) {
                BRIDGE_PORT = fetchedPort;
                BRIDGE_URL = `ws://127.0.0.1:${BRIDGE_PORT}`;
                console.log(
                  `${LOG_PREFIX} Loaded bridge port from cache: ${BRIDGE_PORT}`
                );
                return true;
              }
            }
          } catch (e) {
            localStorage.removeItem(BRIDGE_PORT_STORAGE_KEY);
          }
        }
      }

      // Try default port 50000
      try {
        const response = await fetch(`http://127.0.0.1:50000/bridge-port`, {
          signal: AbortSignal.timeout(50),
        });
        if (response.ok) {
          const portText = await response.text();
          const fetchedPort = parseInt(portText.trim(), 10);
          if (!isNaN(fetchedPort) && fetchedPort > 0) {
            BRIDGE_PORT = fetchedPort;
            BRIDGE_URL = `ws://127.0.0.1:${BRIDGE_PORT}`;
            localStorage.setItem(BRIDGE_PORT_STORAGE_KEY, String(BRIDGE_PORT));
            console.log(`${LOG_PREFIX} Loaded bridge port: ${BRIDGE_PORT}`);
            return true;
          }
        }
      } catch (e) {
        // Continue to discovery
      }

      // Parallel port discovery
      const portPromises = [];
      for (let port = DISCOVERY_START_PORT; port <= DISCOVERY_END_PORT; port++) {
        portPromises.push(
          fetch(`http://127.0.0.1:${port}/bridge-port`, {
            signal: AbortSignal.timeout(100),
          })
            .then((response) => {
              if (response.ok) {
                return response.text().then((portText) => {
                  const fetchedPort = parseInt(portText.trim(), 10);
                  if (!isNaN(fetchedPort) && fetchedPort > 0) {
                    return { port: fetchedPort };
                  }
                  return null;
                });
              }
              return null;
            })
            .catch(() => null)
        );
      }

      const results = await Promise.allSettled(portPromises);
      for (const result of results) {
        if (result.status === "fulfilled" && result.value) {
          BRIDGE_PORT = result.value.port;
          BRIDGE_URL = `ws://127.0.0.1:${BRIDGE_PORT}`;
          localStorage.setItem(BRIDGE_PORT_STORAGE_KEY, String(BRIDGE_PORT));
          console.log(`${LOG_PREFIX} Loaded bridge port: ${BRIDGE_PORT}`);
          return true;
        }
      }

      console.warn(
        `${LOG_PREFIX} Failed to load bridge port, using default (50000)`
      );
      return false;
    } catch (e) {
      console.warn(`${LOG_PREFIX} Error loading bridge port:`, e);
      return false;
    }
  }

  function getCSSRules() {
    return `
    @font-face {
      font-family: "Beaufort for LOL";
      src: url("http://127.0.0.1:${BRIDGE_PORT}/asset/BeaufortforLOL-Regular.ttf") format("truetype");
      font-weight: normal;
      font-style: normal;
      font-display: swap;
    }

    /* Party Button */
    /* Party Panel */
    /* ===== Panel: Riot dialog-frame style ===== */
    #${PANEL_ID} {
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 380px;
      background-color: #010a13;
      border: 2px solid #463714;
      box-shadow: 0 0 0 1px rgba(1,10,19,.8), 0 8px 30px rgba(0,0,0,.7), inset 0 1px 0 rgba(255,255,255,.03);
      z-index: 9998;
      display: none;
      flex-direction: column;
      cursor: default;
      -webkit-font-smoothing: antialiased;
      font-kerning: normal;
    }

    #${PANEL_ID}.visible {
      display: flex;
    }

    /* Title bar — matches .lol-friend-finder-modal .title */
    .party-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 15px 18px 10px;
    }

    .party-header h3 {
      margin: 0;
      color: #f0e6d2;
      font-family: var(--font-display), "Beaufort for LOL", Arial, sans-serif;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: .05em;
      line-height: 22px;
      text-transform: uppercase;
    }

    .party-status {
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 12px;
      font-weight: 400;
      letter-spacing: .025em;
    }

    .party-status.offline { color: #5b5a56; }
    .party-status.online  { color: #0acbe6; }

    /* Body — matches .lol-friend-finder-modal .modal-body */
    .party-content {
      display: flex;
      flex-direction: column;
      flex: 1;
      padding: 0 18px;
      overflow: hidden;
    }

    /* Description text */
    .party-description {
      color: #a09b8c;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 12px;
      line-height: 16px;
      margin-bottom: 15px;
    }

    /* Section headers — matches .lol-friend-finder-modal .header */
    .party-section {
      margin-bottom: 15px;
    }

    .party-section:last-child {
      margin-bottom: 0;
    }

    .party-section-title {
      color: #a09b8c;
      font-family: var(--font-display), "Beaufort for LOL", Arial, sans-serif;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .05em;
      text-transform: uppercase;
      margin-bottom: 10px;
    }

    /* Inputs — matches lol-uikit-flat-input */
    .token-container,
    .add-peer-container {
      display: flex;
      gap: 8px;
      align-items: stretch;
    }

    .token-input,
    .add-peer-input {
      flex: 1;
      background: rgba(0,0,0,.7);
      border: thin solid #3c3c41;
      padding: 7px 10px;
      color: #f0e6d2;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 12px;
      line-height: 18px;
      outline: none;
    }

    .token-input {
      font-family: monospace;
      font-size: 11px;
      color: #a09b8c;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .token-input:focus,
    .add-peer-input:focus {
      border-color: #c89b3c;
    }

    .add-peer-input::placeholder {
      color: #5b5a56;
    }

    /* Buttons — matches lol-uikit-flat-button-secondary */
    .copy-btn, .add-btn {
      background: transparent;
      border: thin solid #5b5a56;
      padding: 7px 16px;
      color: #cdbe91;
      cursor: pointer;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: .075em;
      text-transform: uppercase;
      white-space: nowrap;
      transition: color .3s, border-color .3s;
    }

    .copy-btn:hover, .add-btn:hover {
      border-color: #c8aa6e;
      color: #f0e6d2;
    }

    .copy-btn:active, .add-btn:active {
      color: #463714;
      border-color: #463714;
    }

    .copy-btn.copied {
      border-color: #0acbe6;
      color: #0acbe6;
    }

    .add-btn:disabled, .add-peer-input:disabled {
      opacity: 0.5;
      cursor: default;
      pointer-events: none;
    }

    /* Toggle button — matches lol-uikit-flat-button (primary) */
    .party-toggle-btn {
      width: 100%;
      padding: 10px;
      cursor: pointer;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 14px;
      font-weight: 700;
      letter-spacing: .1em;
      text-transform: uppercase;
      border: thin solid #c8aa6e;
      transition: background .3s, color .3s, border-color .3s;
    }

    .party-toggle-btn.enable {
      background: linear-gradient(to bottom, #1e2328, #1e2328);
      border-color: #c8aa6e;
      color: #cdbe91;
    }

    .party-toggle-btn.enable:hover {
      background: linear-gradient(to bottom, #1e2328, #1e2328);
      border-color: #c8aa6e;
      color: #f0e6d2;
    }

    .party-toggle-btn.disable {
      background: transparent;
      border-color: #5b5a56;
      color: #a09b8c;
    }

    .party-toggle-btn.disable:hover {
      border-color: #ff4646;
      color: #ff4646;
    }

    .party-toggle-btn:disabled {
      opacity: 0.5;
      cursor: default;
    }

    /* Peers list — matches requested-players / recent-summoners */
    .peers-list {
      max-height: 200px;
      overflow-y: auto;
      scrollbar-width: thin;
      scrollbar-color: #463714 transparent;
    }

    .peers-list::-webkit-scrollbar { width: 6px; }
    .peers-list::-webkit-scrollbar-track { background: transparent; }
    .peers-list::-webkit-scrollbar-thumb { background: #463714; border-radius: 3px; }

    .peer-item {
      display: flex;
      align-items: center;
      padding: 6px 0;
      border-bottom: thin solid rgba(60,60,65,.5);
    }

    .peer-item:last-child {
      border-bottom: none;
    }

    .peer-info {
      flex: 1;
      min-width: 0;
    }

    .peer-name {
      color: #a09b8c;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 12px;
      line-height: 16px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .peer-item:hover .peer-name {
      color: #f0e6d2;
    }

    .peer-status {
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 10px;
      color: #5b5a56;
      line-height: 14px;
    }

    .peer-status.in-lobby { color: #0acbe6; }

    .peer-skin {
      font-size: 10px;
      color: #c89b3c;
      line-height: 14px;
    }

    .peer-remove {
      background: none;
      border: none;
      color: #5b5a56;
      cursor: pointer;
      padding: 4px 8px;
      font-size: 14px;
      transition: color .2s;
    }

    .peer-remove:hover { color: #ff4646; }

    .no-peers {
      color: #5b5a56;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 12px;
      text-align: center;
      padding: 20px;
    }

    /* Close button — matches lol-uikit-dialog-frame close button */
    .party-close-btn {
      position: absolute;
      top: -14px;
      right: -14px;
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: #1e2328;
      border: 2px solid #463714;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: border-color .2s;
      z-index: 1;
      padding: 0;
    }

    .party-close-btn:hover {
      border-color: #c8aa6e;
    }

    .party-close-btn:active {
      border-color: #785a28;
    }

    .party-close-btn::before,
    .party-close-btn::after {
      content: "";
      position: absolute;
      width: 12px;
      height: 2px;
      background: #a09b8c;
      transition: background .2s;
    }

    .party-close-btn::before { transform: rotate(45deg); }
    .party-close-btn::after  { transform: rotate(-45deg); }

    .party-close-btn:hover::before,
    .party-close-btn:hover::after {
      background: #f0e6d2;
    }

    /* Loading state */
    .loading {
      opacity: 0.6;
      pointer-events: none;
    }

    /* Network config section */
    .network-config {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 12px;
    }

    .network-config-row {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    .network-config-label {
      color: #a09b8c;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 11px;
      min-width: 35px;
      text-transform: uppercase;
      letter-spacing: .05em;
    }

    .network-select,
    .port-input {
      flex: 1;
      background: rgba(0,0,0,.7);
      border: thin solid #3c3c41;
      padding: 6px 8px;
      color: #f0e6d2;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 12px;
      outline: none;
      -webkit-appearance: none;
    }

    .network-select {
      cursor: pointer;
    }

    .network-select:focus,
    .port-input:focus {
      border-color: #c89b3c;
    }

    .port-input {
      max-width: 80px;
      text-align: center;
    }

    .network-select option {
      background: #1e2328;
      color: #f0e6d2;
    }

    .manual-ip-input {
      flex: 1;
      background: rgba(0,0,0,.7);
      border: thin solid #3c3c41;
      padding: 6px 8px;
      color: #f0e6d2;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 12px;
      outline: none;
      display: none;
    }

    .manual-ip-input:focus {
      border-color: #c89b3c;
    }

    .manual-ip-input.visible {
      display: block;
    }

    .host-info {
      color: #5b5a56;
      font-family: var(--font-body), Arial, sans-serif;
      font-size: 10px;
      margin-top: 4px;
      letter-spacing: .02em;
    }

    .host-info .host-address {
      color: #0acbe6;
    }

    .spinner {
      display: inline-block;
      width: 12px;
      height: 12px;
      border: 2px solid rgba(200, 170, 110, 0.3);
      border-top-color: #c8aa6e;
      border-radius: 50%;
      animation: rose-party-spin 0.8s linear infinite;
    }

    @keyframes rose-party-spin {
      to { transform: rotate(360deg); }
    }

    /* Messages */
    .error-msg {
      color: #ff4646;
      font-size: 11px;
      margin-top: 8px;
    }

    .success-msg {
      color: #0acbe6;
      font-size: 11px;
      margin-top: 8px;
    }

    /* Lobby action bar button - matches native social bar buttons */
    #${LOBBY_BUTTON_ID} {
      position: relative;
      cursor: pointer;
    }

    #${LOBBY_BUTTON_ID} .party-mode-icon {
      background-color: #c8aa6e;
      cursor: pointer;
      display: block;
      height: inherit;
      width: inherit;
      -webkit-mask: url("data:image/svg+xml,%3Csvg viewBox='0 0 24 24' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z'/%3E%3C/svg%3E") no-repeat center;
      -webkit-mask-size: 18px;
    }

    #${LOBBY_BUTTON_ID}:hover .party-mode-icon {
      background-color: #f0e6d2;
    }

    #${LOBBY_BUTTON_ID}:active .party-mode-icon {
      background-color: #463714;
    }

    #${LOBBY_BUTTON_ID}.active .party-mode-icon {
      background-color: #0acbe6;
    }

    #${LOBBY_BUTTON_ID}.connected .party-mode-icon {
      background-color: #4ade80;
    }

    /* Rose Party Member Badges */
    .rose-party-lobby-badge {
      position: absolute;
      top: -14px;
      left: 50%;
      transform: translateX(-50%);
      width: 22px;
      height: 22px;
      background-image: url("${GOLDEN_ROSE_ICON}");
      background-size: contain;
      background-repeat: no-repeat;
      background-position: center;
      filter: drop-shadow(0 0 5px rgba(200, 170, 110, 0.85)) drop-shadow(0 0 2px rgba(240, 230, 210, 0.9));
      z-index: 100;
      pointer-events: auto;
      cursor: pointer;
      animation: rose-glow-pulse 3s ease-in-out infinite;
    }

    @keyframes rose-glow-pulse {
      0%, 100% {
        filter: drop-shadow(0 0 4px rgba(200, 170, 110, 0.7)) drop-shadow(0 0 2px rgba(240, 230, 210, 0.8));
        transform: translateX(-50%) scale(1);
      }
      50% {
        filter: drop-shadow(0 0 10px rgba(200, 170, 110, 0.95)) drop-shadow(0 0 4px rgba(255, 255, 255, 0.9));
        transform: translateX(-50%) scale(1.08);
      }
    }
    `;
  }

  function injectStyles() {
    const styleId = "rose-party-mode-styles";
    if (document.getElementById(styleId)) return;

    const style = document.createElement("style");
    style.id = styleId;
    style.textContent = getCSSRules();
    document.head.appendChild(style);
  }

  // Attach a native Riot tooltip to an element
  function attachTooltip(el, text) {
    let wrapper = null;
    el.addEventListener("mouseenter", () => {
      // Wrapper div to control positioning (native tooltip may override its own styles)
      wrapper = document.createElement("div");
      wrapper.style.cssText = "position:fixed;pointer-events:none;z-index:10000;visibility:hidden";
      const tip = document.createElement("lol-uikit-tooltip");
      tip.setAttribute("data-tooltip-position", "bottom");
      const content = document.createElement("lol-uikit-content-block");
      content.setAttribute("type", "tooltip-system");
      const p = document.createElement("p");
      p.textContent = text;
      content.appendChild(p);
      tip.appendChild(content);
      wrapper.appendChild(tip);
      document.body.appendChild(wrapper);
      // Wait for render then position the wrapper
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          if (!wrapper || !wrapper.isConnected) return;
          const btnRect = el.getBoundingClientRect();
          const wrapRect = wrapper.getBoundingClientRect();
          const centerX = btnRect.left + btnRect.width / 2;
          wrapper.style.left = `${centerX - wrapRect.width / 2}px`;
          wrapper.style.top = `${btnRect.bottom}px`;
          wrapper.style.visibility = "visible";
        });
      });
    });
    el.addEventListener("mouseleave", () => {
      if (wrapper) {
        wrapper.remove();
        wrapper = null;
      }
    });
  }

  // Create button in social actions bar
  function createLobbyButton() {
    const existing = document.getElementById(LOBBY_BUTTON_ID);
    if (existing) {
      lobbyButton = existing;
      updateLobbyButtonState();
      return;
    }

    // Find the social actions bar buttons container
    const buttonsContainer = document.querySelector(".lol-social-actions-bar .buttons");
    if (!buttonsContainer) {
      console.log(`${LOG_PREFIX} Social actions bar not found, retrying...`);
      return false;
    }

    // Find the friend-finder-button to insert before it
    const friendFinderBtn = buttonsContainer.querySelector(".friend-finder-button");
    const friendFinderParent = friendFinderBtn ? friendFinderBtn.closest(".action-bar-button") : null;

    const button = document.createElement("span");
    button.id = LOBBY_BUTTON_ID;
    button.className = "action-bar-button";
    button.innerHTML = `
      <span class="party-mode-icon"></span>
    `;

    button.addEventListener("click", (e) => {
      e.stopPropagation();
      togglePanel();
    });
    attachTooltip(button, "Party Mode");

    // Insert before the add friend button, or append to the end
    if (friendFinderParent) {
      buttonsContainer.insertBefore(button, friendFinderParent);
    } else {
      // Try to insert after the SOCIAL header
      const socialHeader = buttonsContainer.querySelector(".friend-header");
      if (socialHeader && socialHeader.nextSibling) {
        buttonsContainer.insertBefore(button, socialHeader.nextSibling);
      } else {
        buttonsContainer.appendChild(button);
      }
    }

    lobbyButton = button;
    updateLobbyButtonState();
    return true;
  }

  function updateLobbyButtonState() {
    if (!lobbyButton) return;

    const connectedPeers = (partyState.peers || []).filter((p) => p.connected);
    if (partyState.enabled) {
      lobbyButton.classList.add("active");
    } else {
      lobbyButton.classList.remove("active");
    }
    if (partyState.enabled && connectedPeers.length > 0) {
      lobbyButton.classList.add("connected");
    } else {
      lobbyButton.classList.remove("connected");
    }
  }

  function createPartyPanel() {
    // Remove any existing panel (may be detached/stale)
    const existing = document.getElementById(PANEL_ID);
    if (existing) {
      if (existing.isConnected && partyPanel === existing) return; // Already good
      existing.remove();
    }

    // Find a persistent container to attach the panel to
    const container = document.querySelector(".lol-social-actions-bar") || document.body;

    const panel = document.createElement("div");
    panel.id = PANEL_ID;
    panel.innerHTML = `
      <div class="party-header">
        <h3>Party Mode</h3>
        <span class="party-status offline">Offline</span>
      </div>
      <div class="party-content">
        <div class="party-description">Share your skins with friends on the same network (Hamachi / Tailscale / LAN). Enable to host a party, then share your token.</div>

        <div class="party-section" id="party-network-section">
          <div class="party-section-title">Network Settings</div>
          <div class="network-config">
            <div class="network-config-row">
              <span class="network-config-label">IP</span>
              <select class="network-select" id="party-ip-select">
                <option value="">Detecting...</option>
              </select>
            </div>
            <input type="text" class="manual-ip-input" id="party-manual-ip" placeholder="Enter IP address manually...">
            <div class="network-config-row">
              <span class="network-config-label">Port</span>
              <input type="number" class="port-input" id="party-port-input" value="7865" min="1024" max="65535">
            </div>
          </div>
        </div>

        <div class="party-section" id="party-toggle-section">
          <button class="party-toggle-btn enable" id="party-toggle-btn">
            Enable Party Mode
          </button>
        </div>

        <div class="party-section" id="party-token-section" style="display: none;">
          <div class="party-section-title">Your Party Token</div>
          <div class="token-container">
            <input type="text" class="token-input" id="party-token-display" readonly placeholder="Generating...">
            <button class="copy-btn" id="copy-token-btn">Copy</button>
          </div>
        </div>

        <div class="party-section" id="party-add-section" style="display: none;">
          <div class="party-section-title">Add Friend</div>
          <div class="add-peer-container">
            <input type="text" class="add-peer-input" id="add-peer-input" placeholder="Paste friend's token here...">
            <button class="add-btn" id="add-peer-btn">Add</button>
          </div>
          <div id="add-peer-message"></div>
        </div>

        <div class="party-section" id="party-peers-section" style="display: none;">
          <div class="party-section-title">Connected Friends (<span id="peer-count">0</span>)</div>
          <div class="peers-list" id="peers-list">
            <div class="no-peers">No friends connected yet</div>
          </div>
        </div>
      </div>
      <button class="party-close-btn" id="party-close-btn"></button>
    `;

    try {
      container.appendChild(panel);
      partyPanel = panel;
      // Use querySelector on panel directly instead of document to avoid ID conflicts
      panel.querySelector("#party-toggle-btn").addEventListener("click", handleToggleParty);
      panel.querySelector("#copy-token-btn").addEventListener("click", handleCopyToken);
      panel.querySelector("#add-peer-btn").addEventListener("click", handleAddPeer);
      panel.querySelector("#add-peer-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") handleAddPeer();
      });
      panel.querySelector("#party-close-btn").addEventListener("click", () => {
        isVisible = false;
        partyPanel.classList.remove("visible");
      });

      // IP dropdown change handler
      const ipSelect = panel.querySelector("#party-ip-select");
      if (ipSelect) {
        ipSelect.addEventListener("change", (e) => {
          const manualInput = panel.querySelector("#party-manual-ip");
          if (e.target.value === "__manual__") {
            manualInput.classList.add("visible");
            manualInput.focus();
            selectedIP = manualInput.value;
          } else {
            manualInput.classList.remove("visible");
            selectedIP = e.target.value;
          }
        });
      }

      // Manual IP input handler
      const manualIpInput = panel.querySelector("#party-manual-ip");
      if (manualIpInput) {
        manualIpInput.addEventListener("input", (e) => {
          selectedIP = e.target.value.trim();
        });
      }

      // Port input handler
      const portInput = panel.querySelector("#party-port-input");
      if (portInput) {
        portInput.addEventListener("change", (e) => {
          const val = parseInt(e.target.value, 10);
          if (!isNaN(val) && val >= 1024 && val <= 65535) {
            selectedPort = val;
          } else {
            e.target.value = selectedPort;
          }
        });
      }

      // Request network interfaces to populate dropdown
      if (networkInterfaces && networkInterfaces.length > 0) {
        populateIPDropdown(networkInterfaces);
      }
      sendBridgeMessage({ type: "party-get-interfaces" });
    } catch (e) {
      console.error(`${LOG_PREFIX} Failed to create panel:`, e);
      partyPanel = null;
    }
  }

  function togglePanel() {
    // Recreate panel if it was removed from DOM
    if (!partyPanel || !partyPanel.isConnected) {
      partyPanel = null;
      isVisible = false;
      createPartyPanel();
    }
    if (!partyPanel) return;
    isVisible = !isVisible;
    partyPanel.classList.toggle("visible", isVisible);
    updatePanelState();
  }

  function updateButtonState() {
    updateLobbyButtonState();
  }

  function updatePanelState() {
    if (!partyPanel) return;

    const statusEl = partyPanel.querySelector(".party-status");
    const toggleBtn = document.getElementById("party-toggle-btn");
    const tokenSection = document.getElementById("party-token-section");
    const addSection = document.getElementById("party-add-section");
    const peersSection = document.getElementById("party-peers-section");
    const networkSection = document.getElementById("party-network-section");
    const tokenDisplay = document.getElementById("party-token-display");
    const peerCountEl = document.getElementById("peer-count");
    const peersList = document.getElementById("peers-list");

    if (partyState.enabled) {
      statusEl.className = "party-status online";
      statusEl.textContent = "Online";

      toggleBtn.className = "party-toggle-btn disable";
      toggleBtn.textContent = "Disable Party Mode";

      // Hide network config when party is running, show token/peers
      if (networkSection) networkSection.style.display = "none";
      tokenSection.style.display = "block";
      addSection.style.display = "block";
      peersSection.style.display = "block";

      if (partyState.my_token) {
        tokenDisplay.value = partyState.my_token;
      }

      // Update peers list (show all peers, including those still connecting)
      const allPeers = partyState.peers || [];
      const connectedPeers = allPeers.filter((p) => p.connected);
      peerCountEl.textContent = connectedPeers.length;

      if (allPeers.length === 0) {
        peersList.innerHTML = '<div class="no-peers">No friends connected yet</div>';
      } else {
        peersList.innerHTML = allPeers
          .map((peer) => {
            const cs = (peer.connection_state || "disconnected").toLowerCase();
            const isWaiting = cs === "connecting" || cs === "handshaking";
            const statusText = isWaiting
              ? "Waiting for your friend"
              : cs === "connected"
                ? (peer.in_lobby ? "In lobby" : "Connected")
                : cs === "handshaking"
                  ? "Handshaking"
                  : cs === "connecting"
                    ? "Connecting"
                    : "Disconnected";
            const displayName = isWaiting ? "Friend" : escapeHtml(peer.summoner_name);
            const lobbyStatus = peer.in_lobby ? "in-lobby" : "";
            const skinInfo = peer.skin_selection
              ? `Skin: ${peer.skin_selection.skin_id}`
              : "";

            return `
            <div class="peer-item" data-summoner-id="${peer.summoner_id}">
              <div class="peer-info">
                <span class="peer-name">${displayName}</span>
                ${isWaiting ? '<span class="peer-status waiting"><span class="spinner"></span> ' : `<span class="peer-status ${lobbyStatus}">`}
                ${escapeHtml(statusText)}</span>
                ${skinInfo ? `<span class="peer-skin">${skinInfo}</span>` : ""}
              </div>
              <button class="peer-remove" title="Remove" onclick="window.rosePartyRemovePeer(${peer.summoner_id})">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
          `;
          })
          .join("");
      }
    } else {
      statusEl.className = "party-status offline";
      statusEl.textContent = "Offline";

      toggleBtn.className = "party-toggle-btn enable";
      toggleBtn.textContent = "Enable Party Mode";

      tokenSection.style.display = "none";
      addSection.style.display = "none";
      peersSection.style.display = "none";
      // Show network config when party is off
      if (networkSection) networkSection.style.display = "block";
    }

    updateButtonState();
  }

  async function handleToggleParty() {
    const toggleBtn = document.getElementById("party-toggle-btn");

    if (partyState.enabled) {
      // Disable
      toggleBtn.disabled = true;
      toggleBtn.innerHTML = '<span class="spinner"></span> Disabling...';
      sendBridgeMessage({ type: "party-disable" });
    } else {
      // Enable - send selected IP and port
      toggleBtn.disabled = true;
      toggleBtn.innerHTML = '<span class="spinner"></span> Starting server...';

      // Resolve the IP: manual input takes priority
      const ipSelect = document.getElementById("party-ip-select");
      const manualIp = document.getElementById("party-manual-ip");
      let hostIp = selectedIP;
      if (ipSelect && ipSelect.value === "__manual__" && manualIp) {
        hostIp = manualIp.value.trim();
      }

      const portInput = document.getElementById("party-port-input");
      const hostPort = portInput ? parseInt(portInput.value, 10) || 7865 : 7865;

      sendBridgeMessage({
        type: "party-enable",
        host_ip: hostIp,
        host_port: hostPort,
      });
    }
  }

  function handleCopyToken() {
    const tokenDisplay = document.getElementById("party-token-display");
    const copyBtn = document.getElementById("copy-token-btn");

    if (!tokenDisplay.value) return;

    navigator.clipboard.writeText(tokenDisplay.value).then(() => {
      copyBtn.textContent = "Copied!";
      copyBtn.classList.add("copied");
      setTimeout(() => {
        copyBtn.textContent = "Copy";
        copyBtn.classList.remove("copied");
      }, 2000);
    });
  }

  function handleAddPeer() {
    const input = document.getElementById("add-peer-input");
    const addBtn = document.getElementById("add-peer-btn");
    const messageEl = document.getElementById("add-peer-message");
    // Strip and remove all whitespace (spaces, newlines, tabs) so pasted tokens work
    const token = input.value.replace(/\s+/g, "").trim();

    if (!token) {
      messageEl.innerHTML =
        '<div class="error-msg">Please enter a token</div>';
      return;
    }

    // Lock the entire panel during connection
    input.disabled = true;
    addBtn.disabled = true;
    addBtn.innerHTML = '<span class="spinner"></span>';
    const toggleBtn = document.getElementById("party-toggle-btn");
    if (toggleBtn) toggleBtn.disabled = true;
    const closeBtn = partyPanel ? partyPanel.querySelector("#party-close-btn") : null;
    if (closeBtn) closeBtn.style.display = "none";
    messageEl.innerHTML =
      '<div class="success-msg"><span class="spinner"></span> Connecting to your friend...</div>';
    sendBridgeMessage({ type: "party-add-peer", token: token });
    input.value = "";
  }

  // Global function for remove button onclick
  window.rosePartyRemovePeer = function (summonerId) {
    sendBridgeMessage({ type: "party-remove-peer", summoner_id: summonerId });
  };

  function handleBridgeMessage(data) {
    console.log(`${LOG_PREFIX} Received:`, data.type);

    switch (data.type) {
      case "party-state":
        partyState = {
          enabled: data.enabled || false,
          my_token: data.my_token || null,
          my_summoner_id: data.my_summoner_id || null,
          my_summoner_name: data.my_summoner_name || "Unknown",
          peers: data.peers || [],
        };
        updateButtonState();
        updatePanelState();
        break;

      case "party-enabled":
        const toggleBtn = document.getElementById("party-toggle-btn");
        toggleBtn.disabled = false;

        if (data.success) {
          partyState.enabled = true;
          partyState.my_token = data.token;
          console.log(`${LOG_PREFIX} Party mode enabled`);
        } else {
          const messageEl = document.getElementById("add-peer-message");
          if (messageEl) {
            messageEl.innerHTML = `<div class="error-msg">${escapeHtml(data.error || "Failed to enable")}</div>`;
          }
          console.error(`${LOG_PREFIX} Failed to enable:`, data.error);
        }
        updateButtonState();
        updatePanelState();
        break;

      case "party-disabled":
        const toggleBtnDisable = document.getElementById("party-toggle-btn");
        if (toggleBtnDisable) toggleBtnDisable.disabled = false;

        partyState.enabled = false;
        partyState.my_token = null;
        partyState.peers = [];
        console.log(`${LOG_PREFIX} Party mode disabled`);
        updateButtonState();
        updatePanelState();
        break;

      case "party-peer-added": {
        const addInput = document.getElementById("add-peer-input");
        const addBtn = document.getElementById("add-peer-btn");
        const addMessageEl = document.getElementById("add-peer-message");

        // Unlock the panel
        if (addInput) addInput.disabled = false;
        if (addBtn) {
          addBtn.disabled = false;
          addBtn.textContent = "Add";
        }
        const unlockToggleBtn = document.getElementById("party-toggle-btn");
        if (unlockToggleBtn) unlockToggleBtn.disabled = false;
        const unlockCloseBtn = partyPanel ? partyPanel.querySelector("#party-close-btn") : null;
        if (unlockCloseBtn) unlockCloseBtn.style.display = "";

        if (data.success) {
          if (addMessageEl) {
            addMessageEl.innerHTML =
              '<div class="success-msg">Friend connected!</div>';
            setTimeout(() => {
              addMessageEl.innerHTML = "";
            }, 3000);
          }
        } else {
          if (addMessageEl) {
            addMessageEl.innerHTML = `<div class="error-msg">${escapeHtml(data.error || "Failed to connect")}</div>`;
          }
        }
        // Request updated state
        sendBridgeMessage({ type: "party-get-state" });
        break;
      }

      case "party-peer-removed":
        // Request updated state
        sendBridgeMessage({ type: "party-get-state" });
        break;

      case "phase-change":
        // Pause the 500ms DOM monitor during in-game to avoid stealing
        // CPU from the League game process.  Resume in every other phase
        // so the party button reattaches if the client re-renders.
        if (data.phase === "InProgress") {
          stopGamePhaseMonitor();
        } else {
          startGamePhaseMonitor();
        }
        break;

      case "party-interfaces":
        networkInterfaces = data.interfaces || [];
        console.log(`${LOG_PREFIX} Received network interfaces:`, networkInterfaces);
        populateIPDropdown(networkInterfaces);
        break;
    }
  }

  function populateIPDropdown(interfaces) {
    const select = partyPanel
      ? partyPanel.querySelector("#party-ip-select")
      : document.getElementById("party-ip-select");
    if (!select) return;

    select.innerHTML = "";

    if (interfaces.length === 0) {
      const opt = document.createElement("option");
      opt.value = "127.0.0.1";
      opt.textContent = "localhost (127.0.0.1)";
      select.appendChild(opt);
    } else {
      for (const iface of interfaces) {
        const opt = document.createElement("option");
        opt.value = iface.ip;
        const typeLabel = iface.type.charAt(0).toUpperCase() + iface.type.slice(1);
        opt.textContent = `${iface.ip} — ${iface.name} (${typeLabel})`;
        select.appendChild(opt);
      }
    }

    // Add manual entry option at the end
    const manualOpt = document.createElement("option");
    manualOpt.value = "__manual__";
    manualOpt.textContent = "Enter IP manually...";
    select.appendChild(manualOpt);

    // Keep user's previous selection if valid, otherwise pick first option
    if (selectedIP && Array.from(select.options).some((o) => o.value === selectedIP)) {
      select.value = selectedIP;
    } else if (interfaces.length > 0) {
      selectedIP = interfaces[0].ip;
      select.value = interfaces[0].ip;
    }
  }

  function connectBridge() {
    if (bridgeSocket && bridgeSocket.readyState === WebSocket.OPEN) {
      return;
    }

    console.log(`${LOG_PREFIX} Connecting to bridge at ${BRIDGE_URL}`);
    bridgeSocket = new WebSocket(BRIDGE_URL);

    bridgeSocket.onopen = () => {
      console.log(`${LOG_PREFIX} Bridge connected`);
      bridgeReady = true;

      // Flush queued messages
      while (bridgeQueue.length > 0) {
        const msg = bridgeQueue.shift();
        console.log(`${LOG_PREFIX} [TX-queue]`, msg);
        bridgeSocket.send(JSON.stringify(msg));
      }

      // Request current party state & network interfaces
      sendBridgeMessage({ type: "party-get-state" });
      sendBridgeMessage({ type: "party-get-interfaces" });
    };

    bridgeSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type && data.type.startsWith("party-")) {
          console.log(`${LOG_PREFIX} [RX]`, data.type, data);
        }
        handleBridgeMessage(data);
      } catch (e) {
        console.error(`${LOG_PREFIX} Error parsing message:`, e);
      }
    };

    bridgeSocket.onclose = () => {
      console.log(`${LOG_PREFIX} Bridge disconnected, reconnecting...`);
      bridgeReady = false;
      setTimeout(connectBridge, 1000);
    };

    bridgeSocket.onerror = (error) => {
      console.error(`${LOG_PREFIX} Bridge error:`, error);
    };
  }

  function sendBridgeMessage(msg) {
    if (msg.type && msg.type.startsWith("party-")) {
      console.log(`${LOG_PREFIX} [TX]`, msg.type, msg);
    }
    if (bridgeReady && bridgeSocket && bridgeSocket.readyState === WebSocket.OPEN) {
      bridgeSocket.send(JSON.stringify(msg));
    } else {
      bridgeQueue.push(msg);
    }
  }

  // Check if we're in lobby (pre-game party lobby)
  function isInLobby() {
    return !!(
      document.querySelector(".v2-banner-component.local-player") ||
      document.querySelector(".lobby-player.local-player") ||
      document.querySelector("lol-regalia-parties-v2-element") ||
      document.querySelector(".parties-game-info-panel") ||
      document.querySelector(".lobby-members-container") ||
      document.querySelector(".ready-check-swap-button") ||
      document.querySelector(".lobby-header-custom-map-name")
    );
  }

  // Check if we're in champion select
  function isInChampSelect() {
    return !!(
      document.querySelector(".champion-grid") ||
      document.querySelector(".summoner-array") ||
      document.querySelector(".skin-selector-dropdown") ||
      document.querySelector(".champion-select-container")
    );
  }

  // Check if we should show party UI (lobby OR champ select)
  function shouldShowPartyUI() {
    return isInLobby() || isInChampSelect();
  }

  // Remove all party UI elements

  // Monitor for lobby/champ select.
  // Pauses during InProgress phase to avoid stealing CPU from the game.
  // See GitHub issue #22.
  let gamePhaseMonitorId = null;

  function startGamePhaseMonitor() {
    if (gamePhaseMonitorId) return;
    gamePhaseMonitorId = setInterval(() => {
      const inChampSelect = isInChampSelect();
      const inLobby = isInLobby();

      // Always keep the party button in the social actions bar
      // (it's always present, not just in lobby)
      if (!lobbyButton || !lobbyButton.isConnected) {
        lobbyButton = null;
        createLobbyButton();
      }

      // Ensure panel exists
      if (!partyPanel || !partyPanel.isConnected) {
        partyPanel = null;
        isVisible = false;
        createPartyPanel();
      }

      // Track UI mode changes
      if (inChampSelect && currentUIMode !== "champselect") {
        console.log(`${LOG_PREFIX} Entered champion select`);
        currentUIMode = "champselect";
      } else if (inLobby && currentUIMode !== "lobby") {
        console.log(`${LOG_PREFIX} Entered lobby`);
        currentUIMode = "lobby";
      } else if (!inChampSelect && !inLobby && currentUIMode !== "default") {
        currentUIMode = "default";
      }

      // Update Golden Rose badges on party members in Lobby & Champ Select
      updatePartyMemberBadges();
    }, 500);
  }

  function updatePartyMemberBadges() {
    const connectedPeers = (partyState.peers || []).filter((p) => p.connected);
    const isPartyActive = partyState.enabled && connectedPeers.length > 0;

    // Clean up any legacy champ badges
    document.querySelectorAll(".rose-party-champ-badge").forEach((el) => el.remove());

    // Only show in Lobby when party is active with at least 1 peer
    if (!isPartyActive || !isInLobby()) {
      document.querySelectorAll(".rose-party-lobby-badge").forEach((el) => el.remove());
      return;
    }

    // Build the set of party member names (lowercased)
    const partyNames = new Set();
    if (partyState.my_summoner_name && partyState.my_summoner_name !== "Unknown") {
      partyNames.add(partyState.my_summoner_name.trim().toLowerCase());
    }
    for (const peer of connectedPeers) {
      if (peer.summoner_name && peer.summoner_name !== "Unknown") {
        partyNames.add(peer.summoner_name.trim().toLowerCase());
      }
    }

    // In Lobby: anchor the badge directly onto the player's crest / avatar
    const banners = document.querySelectorAll(".v2-banner-component, .party-member-component, .lobby-player");
    banners.forEach((banner) => {
      const isLocal = banner.classList.contains("local-player");
      const bannerText = (banner.textContent || "").toLowerCase();
      const isPartyMember = isLocal || Array.from(partyNames).some((name) => bannerText.includes(name));

      // Find the crest / summoner icon container on the banner
      const crestTarget = banner.querySelector(
        "lol-regalia-crest-v2-element, lol-regalia-emblem-element, .regalia-emblem, .banner-summoner-icon, .crest-container"
      );

      const existingBadge = banner.querySelector(".rose-party-lobby-badge");

      if (isPartyMember && crestTarget) {
        if (!existingBadge) {
          if (getComputedStyle(crestTarget).position === "static") {
            crestTarget.style.position = "relative";
          }
          const badge = document.createElement("div");
          badge.className = "rose-party-lobby-badge";
          attachTooltip(badge, "Rose Party Member");
          crestTarget.appendChild(badge);
        }
      } else if (existingBadge) {
        existingBadge.remove();
      }
    });
  }

  function stopGamePhaseMonitor() {
    if (!gamePhaseMonitorId) return;
    clearInterval(gamePhaseMonitorId);
    gamePhaseMonitorId = null;
  }

  // Initialize
  async function init() {
    console.log(`${LOG_PREFIX} Initializing...`);

    await loadBridgePort();
    injectStyles();
    connectBridge();

    // Always create social bar button and panel
    createLobbyButton();
    createPartyPanel();

    // Set initial UI mode
    if (isInChampSelect()) {
      currentUIMode = "champselect";
    } else if (isInLobby()) {
      currentUIMode = "lobby";
    } else {
      currentUIMode = "default";
    }

    startGamePhaseMonitor();

    console.log(`${LOG_PREFIX} Initialized`);
  }

  // Start when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

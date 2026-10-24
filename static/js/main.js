/**
 * StreamBox Video.js Player Controller
 * Prebuilt Video.js + ImageKit Theme Integration
 */

document.addEventListener('DOMContentLoaded', () => {
  const DEFAULT_STREAM_URL = 
    "https://sonydaime.akamaized.net/hls/live/2119921/cricodi_2410/HIN/std_lrh-800300010.m3u8" +
    "?hdnea=exp=1792868449~acl=/*~id=39183153768115659634580807583499~hmac=94bb3c2e2345bf9917ed73694d9d436d6a6bd9a0f858c942d7b6f07b882e889b";

  let currentRawStreamUrl = DEFAULT_STREAM_URL;
  let useProxy = true;

  function getPlaybackUrl(rawUrl, withProxy) {
    if (!withProxy) return rawUrl;
    return `/api/stream/proxy?url=${encodeURIComponent(rawUrl)}`;
  }

  // --- Initialize Hero Video.js Player with ImageKit Prebuilt UI ---
  const heroVideoEl = document.getElementById('heroVideoPlayer');
  let heroPlayer = null;
  const heroSoundWave = document.getElementById('heroSoundWave');
  const heroSyncStatusText = document.getElementById('heroSyncStatusText');
  const heroBitrateBadge = document.getElementById('heroBitrateBadge');

  if (heroVideoEl && typeof videojs !== 'undefined') {
    heroPlayer = videojs(heroVideoEl, {
      autoplay: 'muted', // Start muted so modern browsers immediately autoplay the live stream
      muted: true,
      controls: true,
      preload: 'auto',
      fluid: true,
      liveui: true,
      playbackRates: [0.5, 1, 1.25, 1.5, 2],
      html5: {
        vhs: {
          overrideNative: true,
          handlePartialData: true,
          experimentalBufferBasedABR: true
        }
      }
    });

    // Initialize ImageKit / Video.js Quality Levels & Source Selector
    if (typeof heroPlayer.qualityLevels === 'function') {
      const qLevels = heroPlayer.qualityLevels();
      
      qLevels.on('change', () => {
        for (let i = 0; i < qLevels.length; i++) {
          const q = qLevels[i];
          if (q.enabled && q.height) {
            const height = `${q.height}p`;
            const bitrate = q.bitrate ? ` • ${(q.bitrate / 1000000).toFixed(1)} Mbps` : '';
            if (heroBitrateBadge) heroBitrateBadge.textContent = `${height}${bitrate}`;
            break;
          }
        }
      });
    }

    if (typeof heroPlayer.httpSourceSelector === 'function') {
      heroPlayer.httpSourceSelector({ default: 'auto' });
    }

    // Sound wave & sync status bindings
    heroPlayer.on('play', () => {
      if (heroSoundWave) {
        heroSoundWave.querySelectorAll('.bar').forEach(b => b.style.animationPlayState = 'running');
      }
      if (heroSyncStatusText) {
        heroSyncStatusText.textContent = heroPlayer.muted() ? 'Audio Muted (Click speaker to unmute)' : 'Spatial Stream Synced (Dolby Atmos / Stereo)';
      }
    });

    heroPlayer.on('pause', () => {
      if (heroSoundWave) {
        heroSoundWave.querySelectorAll('.bar').forEach(b => b.style.animationPlayState = 'paused');
      }
      if (heroSyncStatusText) heroSyncStatusText.textContent = 'Playback Paused';
    });

    heroPlayer.on('volumechange', () => {
      if (heroSyncStatusText) {
        heroSyncStatusText.textContent = heroPlayer.muted() ? 'Audio Muted (Click speaker to unmute)' : 'Spatial Stream Synced (Dolby Atmos / Stereo)';
      }
    });

    // Graceful error handling for expired tokens or network errors
    heroPlayer.on('error', () => {
      const err = heroPlayer.error();
      console.warn('[StreamBox Video.js Error]', err);
      showToast('Stream token expired or connection failed. Open stream settings to refresh token.');
      if (heroSyncStatusText) heroSyncStatusText.textContent = 'Stream Offline (Expired Token / Network Error)';
      if (heroSoundWave) {
        heroSoundWave.querySelectorAll('.bar').forEach(b => b.style.animationPlayState = 'paused');
      }
    });

    // Attempt initial play
    heroPlayer.ready(() => {
      heroPlayer.src({
        src: getPlaybackUrl(currentRawStreamUrl, useProxy),
        type: 'application/x-mpegURL'
      });
      heroPlayer.play().catch(err => {
        console.log('[StreamBox] Autoplay was deferred by browser policy:', err);
      });
    });
  }

  // --- Toast Notification Helper ---
  function showToast(message) {
    let toast = document.getElementById('globalToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'globalToast';
      toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: rgba(18, 18, 18, 0.95);
        color: #fff;
        padding: 12px 22px;
        border-radius: 8px;
        border-left: 4px solid #FF0000;
        box-shadow: 0 12px 32px rgba(0,0,0,0.85);
        font-size: 13px;
        font-weight: 500;
        z-index: 99999;
        transition: opacity 0.3s ease, transform 0.3s ease;
        opacity: 0;
        transform: translateY(10px);
        pointer-events: none;
      `;
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
    }, 3500);
  }

  // --- Theater Modal Video.js Player ---
  const videoModal = document.getElementById('videoModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalVideoEl = document.getElementById('modalVideoPlayer');
  const modalTitle = document.getElementById('modalTitle');
  let modalPlayer = null;

  function openTheaterModal(title, streamUrl) {
    if (!videoModal) return;
    const targetUrl = streamUrl || currentRawStreamUrl;
    if (modalTitle) modalTitle.textContent = `Now Playing • ${title}`;
    videoModal.classList.add('open');

    if (modalVideoEl && typeof videojs !== 'undefined') {
      if (!modalPlayer) {
        modalPlayer = videojs(modalVideoEl, {
          autoplay: true,
          controls: true,
          preload: 'auto',
          fluid: true,
          liveui: true
        });

        if (typeof modalPlayer.qualityLevels === 'function') {
          modalPlayer.qualityLevels();
        }
        if (typeof modalPlayer.httpSourceSelector === 'function') {
          modalPlayer.httpSourceSelector({ default: 'auto' });
        }

        modalPlayer.on('error', () => {
          showToast(`Stream error for "${title}". Loading via stream proxy...`);
        });
      }

      modalPlayer.src({
        src: getPlaybackUrl(targetUrl, useProxy),
        type: 'application/x-mpegURL'
      });
      modalPlayer.play().catch(e => {
        console.log('[StreamBox Modal Playback]', e);
      });
    }
    showToast(`Streaming: ${title}`);
  }

  function loadInHeroPlayer(title, streamUrl) {
    if (!heroPlayer) return;
    currentRawStreamUrl = streamUrl;
    const titleEl = document.querySelector('.player-stream-title');
    if (titleEl) titleEl.textContent = title;
    const statsEl = document.getElementById('heroStreamStats');
    if (statsEl) statsEl.textContent = `Live Stream • ${title}`;

    heroPlayer.src({
      src: getPlaybackUrl(streamUrl, useProxy),
      type: 'application/x-mpegURL'
    });
    heroPlayer.play().catch(e => console.log(e));

    const heroSection = document.getElementById('home');
    if (heroSection) heroSection.scrollIntoView({ behavior: 'smooth' });
    showToast(`Loaded ${title} in Main Player`);
  }

  function closeTheaterModal() {
    if (!videoModal) return;
    videoModal.classList.remove('open');
    if (modalPlayer) {
      modalPlayer.pause();
    }
  }

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeTheaterModal);
  if (videoModal) {
    videoModal.addEventListener('click', (e) => {
      if (e.target === videoModal) closeTheaterModal();
    });
  }

  // Start Watching / Watch Now triggers
  const startWatchingBtn = document.getElementById('startWatchingBtn');
  const watchNowBtn = document.getElementById('watchNowBtn');
  const explorePlayerBtn = document.getElementById('explorePlayerBtn');

  if (startWatchingBtn) {
    startWatchingBtn.addEventListener('click', () => {
      openTheaterModal('Chrono Station • Live Stream Feed', currentRawStreamUrl);
    });
  }

  if (watchNowBtn) {
    watchNowBtn.addEventListener('click', () => {
      openTheaterModal('Live Channel Premiere', currentRawStreamUrl);
    });
  }

  if (explorePlayerBtn) {
    explorePlayerBtn.addEventListener('click', () => {
      const exploreSec = document.getElementById('explore');
      if (exploreSec) exploreSec.scrollIntoView({ behavior: 'smooth' });
    });
  }

  // --- Dynamic Movie Channels Loader & Controller ---
  const channelsGrid = document.getElementById('channelsGrid');
  const channelSearchInput = document.getElementById('channelSearchInput');
  const navbarSearchInput = document.getElementById('searchInput');
  const showingCountEl = document.getElementById('showingCount');
  const totalCountEl = document.getElementById('totalCount');
  const loadMoreBtn = document.getElementById('loadMoreChannelsBtn');
  const loadMoreContainer = document.getElementById('loadMoreContainer');
  const noChannelsFound = document.getElementById('noChannelsFound');
  const searchQueryEcho = document.getElementById('searchQueryEcho');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const filterTabs = document.querySelectorAll('.filter-tab');

  let allChannels = [];
  let filteredChannels = [];
  let currentCategory = 'all';
  let currentSearchQuery = '';
  const PAGE_SIZE = 24;
  let visibleCount = PAGE_SIZE;

  // Category counts badge updater
  function updateCategoryBadges() {
    const counts = { all: allChannels.length, bollywood: 0, south: 0, regional: 0, bhojpuri: 0, action: 0 };
    allChannels.forEach(ch => {
      if (counts[ch.category] !== undefined) counts[ch.category]++;
    });
    filterTabs.forEach(tab => {
      const filter = tab.getAttribute('data-filter');
      const badge = tab.querySelector('.tab-badge');
      if (badge && counts[filter] !== undefined) {
        badge.textContent = counts[filter];
      }
    });
  }

  // Create Channel Card HTML Element
  function createChannelCard(ch) {
    const card = document.createElement('article');
    card.className = 'channel-card';
    card.setAttribute('data-category', ch.category);

    const resClass = ch.resolution === '1080P' ? 'res-1080p' : '';
    const initials = ch.name.split(' ').map(w => w[0]).filter(Boolean).slice(0, 3).join('').toUpperCase();

    // Thumbnail / Logo Box
    const thumbBox = document.createElement('div');
    thumbBox.className = 'channel-thumb-box';

    // Live tag
    const liveTag = document.createElement('span');
    liveTag.className = 'badge-live-tag';
    liveTag.innerHTML = `<span class="live-dot" style="width:5px; height:5px;"></span> LIVE`;
    thumbBox.appendChild(liveTag);

    // Resolution tag
    const resTag = document.createElement('span');
    resTag.className = `badge-resolution ${resClass}`;
    resTag.textContent = ch.resolution;
    thumbBox.appendChild(resTag);

    // Channel Logo or Stylized Fallback
    if (ch.logo) {
      const img = document.createElement('img');
      img.src = ch.logo;
      img.alt = ch.name;
      img.loading = 'lazy';
      img.onerror = () => {
        img.remove();
        thumbBox.appendChild(createPlaceholder(initials, ch.name));
      };
      thumbBox.appendChild(img);
    } else {
      thumbBox.appendChild(createPlaceholder(initials, ch.name));
    }

    // Hover Play Overlay
    const overlay = document.createElement('div');
    overlay.className = 'channel-play-overlay';

    const playBtn = document.createElement('button');
    playBtn.className = 'btn-overlay-play';
    playBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
        <path d="M8 5v14l11-7z"/>
      </svg>
      Watch Now
    `;
    playBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openTheaterModal(ch.name, ch.url);
    });

    const heroBtn = document.createElement('button');
    heroBtn.className = 'btn-overlay-hero';
    heroBtn.title = 'Play in Main Billboard Player';
    heroBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
        <path d="M21 3H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h5v2h8v-2h5c1.1 0 1.99-.9 1.99-2L23 5c0-1.1-.9-2-2-2zm0 14H3V5h18v12z"/>
      </svg>
      Hero
    `;
    heroBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      loadInHeroPlayer(ch.name, ch.url);
    });

    overlay.appendChild(playBtn);
    overlay.appendChild(heroBtn);
    thumbBox.appendChild(overlay);
    card.appendChild(thumbBox);

    // Card Body
    const body = document.createElement('div');
    body.className = 'channel-body';

    const titleEl = document.createElement('h3');
    titleEl.className = 'channel-title';
    titleEl.title = ch.name;
    titleEl.textContent = ch.name;
    body.appendChild(titleEl);

    const metaBottom = document.createElement('div');
    metaBottom.className = 'channel-meta-bottom';

    const catTag = document.createElement('span');
    catTag.className = 'channel-cat-tag';
    catTag.textContent = ch.category;
    metaBottom.appendChild(catTag);

    const subText = document.createElement('span');
    subText.textContent = 'IPTV HLS';
    metaBottom.appendChild(subText);

    body.appendChild(metaBottom);
    card.appendChild(body);

    // Clicking card opens theater modal
    card.addEventListener('click', () => {
      openTheaterModal(ch.name, ch.url);
    });

    return card;
  }

  function createPlaceholder(initials, name) {
    const ph = document.createElement('div');
    ph.className = 'channel-placeholder-logo';
    ph.innerHTML = `
      <svg viewBox="0 0 24 24">
        <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
      </svg>
      <span class="channel-initials">${initials || 'TV'}</span>
    `;
    return ph;
  }

  // Render channels into the DOM
  function renderChannels() {
    if (!channelsGrid) return;

    // Filter by Category & Search Query
    filteredChannels = allChannels.filter(ch => {
      const matchCat = (currentCategory === 'all' || ch.category === currentCategory);
      if (!matchCat) return false;
      if (!currentSearchQuery) return true;
      const q = currentSearchQuery.toLowerCase();
      return ch.name.toLowerCase().includes(q) ||
             ch.raw_name.toLowerCase().includes(q) ||
             ch.category.toLowerCase().includes(q) ||
             ch.group.toLowerCase().includes(q);
    });

    if (totalCountEl) totalCountEl.textContent = filteredChannels.length;

    if (filteredChannels.length === 0) {
      channelsGrid.innerHTML = '';
      if (noChannelsFound) {
        noChannelsFound.style.display = 'block';
        if (searchQueryEcho) searchQueryEcho.textContent = currentSearchQuery || currentCategory;
      }
      if (loadMoreContainer) loadMoreContainer.style.display = 'none';
      if (showingCountEl) showingCountEl.textContent = '0';
      return;
    }

    if (noChannelsFound) noChannelsFound.style.display = 'none';

    // Slice for pagination
    const toRender = filteredChannels.slice(0, visibleCount);
    channelsGrid.innerHTML = '';

    const fragment = document.createDocumentFragment();
    toRender.forEach(ch => {
      fragment.appendChild(createChannelCard(ch));
    });
    channelsGrid.appendChild(fragment);

    if (showingCountEl) showingCountEl.textContent = toRender.length;

    // Load More Visibility
    if (loadMoreContainer) {
      if (visibleCount >= filteredChannels.length) {
        loadMoreContainer.style.display = 'none';
      } else {
        loadMoreContainer.style.display = 'flex';
      }
    }
  }

  // Load More Button Event
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', () => {
      visibleCount += PAGE_SIZE;
      renderChannels();
    });
  }

  // Filter Tabs Event
  filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      filterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentCategory = tab.getAttribute('data-filter') || 'all';
      visibleCount = PAGE_SIZE;
      renderChannels();
    });
  });

  // Search input events with debouncing
  let searchTimer = null;
  function handleSearchInput(val) {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      currentSearchQuery = val.trim();
      visibleCount = PAGE_SIZE;
      renderChannels();
    }, 150);
  }

  if (channelSearchInput) {
    channelSearchInput.addEventListener('input', (e) => {
      handleSearchInput(e.target.value);
    });
  }

  if (navbarSearchInput) {
    navbarSearchInput.addEventListener('input', (e) => {
      handleSearchInput(e.target.value);
      if (channelSearchInput) channelSearchInput.value = e.target.value;
      const exploreSec = document.getElementById('explore');
      if (exploreSec) exploreSec.scrollIntoView({ behavior: 'smooth' });
    });
  }

  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', () => {
      currentSearchQuery = '';
      if (channelSearchInput) channelSearchInput.value = '';
      if (navbarSearchInput) navbarSearchInput.value = '';
      visibleCount = PAGE_SIZE;
      renderChannels();
    });
  }

  // Fetch channels list from static json or api
  fetch('/static/channels.json')
    .then(res => {
      if (!res.ok) throw new Error('Failed to load channels');
      return res.json();
    })
    .then(data => {
      allChannels = data;
      filteredChannels = data;
      updateCategoryBadges();
      renderChannels();
      console.log(`[StreamBox] Loaded ${allChannels.length} movie channels successfully.`);
    })
    .catch(err => {
      console.warn('[StreamBox] Fallback to /api/channels:', err);
      fetch('/api/channels')
        .then(r => r.json())
        .then(res => {
          allChannels = res.channels || [];
          filteredChannels = allChannels;
          updateCategoryBadges();
          renderChannels();
        });
    });

  // --- Stream URL Configuration Modal ---
  const streamConfigModal = document.getElementById('streamConfigModal');
  const streamConfigCloseBtn = document.getElementById('streamConfigCloseBtn');
  const streamSettingsNavBtn = document.getElementById('streamSettingsNavBtn');
  const streamUrlInput = document.getElementById('streamUrlInput');
  const useProxyCheckbox = document.getElementById('useProxyCheckbox');
  const applyStreamBtn = document.getElementById('applyStreamBtn');
  const resetStreamBtn = document.getElementById('resetStreamBtn');

  function openStreamConfigModal() {
    if (!streamConfigModal) return;
    if (streamUrlInput) streamUrlInput.value = currentRawStreamUrl;
    if (useProxyCheckbox) useProxyCheckbox.checked = useProxy;
    streamConfigModal.classList.add('open');
  }

  function closeStreamConfigModal() {
    if (streamConfigModal) streamConfigModal.classList.remove('open');
  }

  if (streamSettingsNavBtn) streamSettingsNavBtn.addEventListener('click', openStreamConfigModal);
  if (streamConfigCloseBtn) streamConfigCloseBtn.addEventListener('click', closeStreamConfigModal);

  if (streamConfigModal) {
    streamConfigModal.addEventListener('click', (e) => {
      if (e.target === streamConfigModal) closeStreamConfigModal();
    });
  }

  if (applyStreamBtn) {
    applyStreamBtn.addEventListener('click', () => {
      const newUrl = streamUrlInput.value.trim();
      if (!newUrl) {
        alert('Please enter a valid HLS stream manifest URL.');
        return;
      }
      currentRawStreamUrl = newUrl;
      useProxy = useProxyCheckbox ? useProxyCheckbox.checked : true;
      closeStreamConfigModal();

      if (heroPlayer) {
        heroPlayer.src({
          src: getPlaybackUrl(currentRawStreamUrl, useProxy),
          type: 'application/x-mpegURL'
        });
        heroPlayer.play().catch(e => console.log(e));
      }

      showToast('Stream URL updated and loaded into player!');
    });
  }

  if (resetStreamBtn) {
    resetStreamBtn.addEventListener('click', () => {
      if (streamUrlInput) streamUrlInput.value = DEFAULT_STREAM_URL;
      if (useProxyCheckbox) useProxyCheckbox.checked = true;
    });
  }

  // --- Search Drawer Toggle ---
  const searchBtn = document.getElementById('searchBtn');
  const searchDrawer = document.getElementById('searchDrawer');
  const searchInput = document.getElementById('searchInput');

  if (searchBtn && searchDrawer) {
    searchBtn.addEventListener('click', () => {
      searchDrawer.classList.toggle('open');
      if (searchDrawer.classList.contains('open') && searchInput) {
        searchInput.focus();
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (searchDrawer) searchDrawer.classList.remove('open');
      closeStreamConfigModal();
      closeTheaterModal();
    }
  });

  // --- Cast Notification ---
  const castBtn = document.getElementById('castBtn');
  if (castBtn) {
    castBtn.addEventListener('click', () => {
      showToast('Searching for Cast & AirPlay receivers on local network...');
    });
  }

  function showToast(msg) {
    let toast = document.querySelector('.streambox-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.className = 'streambox-toast';
      document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('visible');
    setTimeout(() => toast.classList.remove('visible'), 3200);
  }
});

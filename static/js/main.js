/**
 * StreamBox Video.js Player Controller
 * Prebuilt Video.js + ImageKit Theme Integration
 */

document.addEventListener('DOMContentLoaded', () => {
  const DEFAULT_STREAM_URL = 
    "https://sonydaime.akamaized.net/hls/live/2119921/cricodi_2210/HIN/std_lrh-800300010.m3u8" +
    "?hdnea=exp=1792700326~acl=/*~id=89575885627351036019877985996111~hmac=48f8e7b8b2d4e6e264fde915a7a48abc6341d1d3a34c237c4190dcdd2e580a99";

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

  // --- Theater Modal Video.js Player ---
  const videoModal = document.getElementById('videoModal');
  const modalCloseBtn = document.getElementById('modalCloseBtn');
  const modalVideoEl = document.getElementById('modalVideoPlayer');
  const modalTitle = document.getElementById('modalTitle');
  let modalPlayer = null;

  function openTheaterModal(title) {
    if (!videoModal) return;
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
      }

      modalPlayer.src({
        src: getPlaybackUrl(currentRawStreamUrl, useProxy),
        type: 'application/x-mpegURL'
      });
      modalPlayer.play().catch(e => console.log(e));
    }
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
      openTheaterModal('Chrono Station • Live Stream Feed');
    });
  }

  if (watchNowBtn) {
    watchNowBtn.addEventListener('click', () => {
      openTheaterModal('Live Channel Premiere');
    });
  }

  if (explorePlayerBtn) {
    explorePlayerBtn.addEventListener('click', () => {
      document.querySelector('.featured-section').scrollIntoView({ behavior: 'smooth' });
    });
  }

  // Content cards click to play
  const contentCards = document.querySelectorAll('.content-card');
  contentCards.forEach(card => {
    card.addEventListener('click', () => {
      const title = card.querySelector('.card-title')?.textContent || 'StreamBox Content';
      openTheaterModal(title);
    });
  });

  // --- Category Tabs Filtering ---
  const filterTabs = document.querySelectorAll('.filter-tab');
  filterTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      filterTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const filterValue = tab.getAttribute('data-filter');

      contentCards.forEach(card => {
        const category = card.getAttribute('data-category');
        if (filterValue === 'all' || category === filterValue || (filterValue === 'live' && card.hasAttribute('data-live'))) {
          card.style.display = 'flex';
          card.style.animation = 'fadeIn 0.3s ease';
        } else {
          card.style.display = 'none';
        }
      });
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

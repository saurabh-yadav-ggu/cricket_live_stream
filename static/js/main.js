/**
 * StreamBox Video.js Player Controller
 * Prebuilt Video.js + ImageKit Theme Integration
 */

document.addEventListener('DOMContentLoaded', () => {
  const DEFAULT_STREAM_URL =
    "https://sonydaime.akamaized.net/hls/live/2119931/cricodi_2710/ENG/std_lrh-800300010.m3u8" +
    "?hdnea=exp=1793128621~acl=/*~id=54754174312327563560352154764462~hmac=78514acc79ea5d72d8269b6aef751dfa0c6c0693f380e205362f50e9063dfd4c";

  let currentRawStreamUrl = DEFAULT_STREAM_URL;
  let useProxy = true;

  function getPlaybackUrl(rawUrl, withProxy) {
    if (!withProxy) return rawUrl;
    return `/api/stream/proxy?url=${encodeURIComponent(rawUrl)}`;
  }

  // --- Initialize Hero Video.js Player with ImageKit Prebuilt UI ---
  const heroPlayerFrame = document.getElementById('heroPlayerFrame');
  const heroSoundWave = document.getElementById('heroSoundWave');
  const heroSyncStatusText = document.getElementById('heroSyncStatusText');
  const heroBitrateBadge = document.getElementById('heroBitrateBadge');

  function loadInHeroPlayer(title, streamUrl) {
    if (title) {
      const titleEl = document.querySelector('.player-stream-title');
      if (titleEl) titleEl.textContent = title;
    }
    if (streamUrl) {
      currentRawStreamUrl = streamUrl;
    }

    if (heroPlayerFrame && heroPlayerFrame.contentWindow) {
      heroPlayerFrame.contentWindow.postMessage({
        action: 'load',
        url: currentRawStreamUrl,
        autoplay: true,
        muted: true
      }, '*');
    }
  }

  // Handle messages from sandboxed player iframes
  window.addEventListener('message', (event) => {
    if (!event.data || typeof event.data !== 'object') return;
    if (event.data.type === 'streambox:playing') {
      if (heroSoundWave) {
        heroSoundWave.querySelectorAll('.bar').forEach(b => b.style.animationPlayState = 'running');
      }
      if (heroSyncStatusText) heroSyncStatusText.textContent = 'Live Feed Synced (Stadium Sound / Stereo)';
    } else if (event.data.type === 'streambox:ready') {
      if (heroBitrateBadge) heroBitrateBadge.textContent = '1080p50 • Adaptive ABR';
    }
  });

  // Probe /api/stream/live for freshest active stream
  fetch(`/api/stream/live?t=${Date.now()}`, { cache: 'no-store' })
    .then(r => r.json())
    .then(liveData => {
      if (liveData && liveData.stream_url) {
        currentRawStreamUrl = liveData.stream_url;
        loadInHeroPlayer(liveData.title, liveData.stream_url);
      }
    })
    .catch(() => {
      loadInHeroPlayer('Live Cricket Feed', currentRawStreamUrl);
    });

  // --- Toast Notification Helper ---
  function showToast(message, type = 'info') {
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
        border-left: 4px solid #0099FF;
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
    if (type === 'success') {
      toast.style.borderLeftColor = '#00C853';
    } else if (type === 'error') {
      toast.style.borderLeftColor = '#FF0000';
    } else {
      toast.style.borderLeftColor = '#0099FF';
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

  // --- YouTube Watch View Interface Controller (YouTube UI) ---
  const youtubeWatchView = document.getElementById('youtubeWatchView');
  const ytBackBtn = document.getElementById('ytBackBtn');
  const ytCloseBtn = document.getElementById('ytCloseBtn');
  const ytTheaterToggleBtn = document.getElementById('ytTheaterToggleBtn');
  const ytTheaterBtn = document.getElementById('ytTheaterBtn');
  const ytWatchColumns = document.getElementById('ytWatchColumns');
  const modalVideoEl = document.getElementById('modalVideoPlayer');
  const ytVideoTitle = document.getElementById('ytVideoTitle');
  const ytChannelAvatar = document.getElementById('ytChannelAvatar');
  const ytChannelInitials = document.getElementById('ytChannelInitials');
  const ytChannelName = document.getElementById('ytChannelName');
  const ytSubCount = document.getElementById('ytSubCount');
  const ytSubscribeBtn = document.getElementById('ytSubscribeBtn');
  const ytLikeBtn = document.getElementById('ytLikeBtn');
  const ytLikeCount = document.getElementById('ytLikeCount');
  const ytDislikeBtn = document.getElementById('ytDislikeBtn');
  const ytShareBtn = document.getElementById('ytShareBtn');
  const ytStreamQualityPill = document.getElementById('ytStreamQualityPill');
  const ytDescriptionBox = document.getElementById('ytDescriptionBox');
  const ytLiveViewerCount = document.getElementById('ytLiveViewerCount');
  const ytStreamStartInfo = document.getElementById('ytStreamStartInfo');
  const ytDescContent = document.getElementById('ytDescContent');
  const ytDescToggle = document.getElementById('ytDescToggle');
  const ytCommentsCount = document.getElementById('ytCommentsCount');
  const ytCommentInput = document.getElementById('ytCommentInput');
  const ytInputActions = document.getElementById('ytInputActions');
  const ytCommentCancel = document.getElementById('ytCommentCancel');
  const ytCommentSubmit = document.getElementById('ytCommentSubmit');
  const ytCommentsFeed = document.getElementById('ytCommentsFeed');
  const ytRelatedList = document.getElementById('ytRelatedList');
  const ytRelatedChips = document.querySelectorAll('.yt-chip');
  const ytSearchInput = document.getElementById('ytSearchInput');
  const ytSearchSubmit = document.getElementById('ytSearchSubmit');

  let modalPlayer = null;
  let currentWatchChannel = null;
  let currentYtFilter = 'all';
  let ytLikes = 24800;
  let isLiked = false;
  let isDisliked = false;
  let isSubscribed = false;

  const SAMPLE_COMMENTS = [
    {
      author: 'CricketMaster_99',
      avatar: 'C',
      time: '2 minutes ago',
      color: '#e50914',
      text: 'Incredible camera angles on the boundary! The 1080p stream is buttery smooth with zero buffering 🔥'
    },
    {
      author: 'RohitFanatic_India',
      avatar: 'R',
      time: '5 minutes ago',
      color: '#0070f3',
      text: 'Stadium sound commentary in Hindi is crisp. Best live feed for this match by far! 🇮🇳🏏'
    },
    {
      author: 'Aarav Sharma',
      avatar: 'A',
      time: '12 minutes ago',
      color: '#00c853',
      text: 'Akamai edge CDN doing heavy lifting today, super low latency compared to TV broadcast.'
    },
    {
      author: 'Priya Patel',
      avatar: 'P',
      time: '19 minutes ago',
      color: '#ff6d00',
      text: 'What a delivery! That inswinger was unplayable. Match is in full swing now!'
    },
    {
      author: 'SportsJunkie_24',
      avatar: 'S',
      time: '26 minutes ago',
      color: '#aa00ff',
      text: 'Quality levels selector works great. Switched to 1080p50 on fiber optic, crystal clear.'
    }
  ];

  function populateComments() {
    if (!ytCommentsFeed) return;
    if (ytCommentsCount) ytCommentsCount.textContent = (SAMPLE_COMMENTS.length + 2840).toLocaleString();
    ytCommentsFeed.innerHTML = '';

    SAMPLE_COMMENTS.forEach(c => {
      const item = document.createElement('div');
      item.className = 'yt-comment-item';
      item.innerHTML = `
        <div class="yt-comment-avatar" style="background: ${c.color};">${c.avatar}</div>
        <div class="yt-comment-body">
          <div class="yt-comment-author-line">
            <span class="yt-comment-author">${c.author}</span>
            <span class="yt-comment-time">${c.time}</span>
          </div>
          <div class="yt-comment-text">${c.text}</div>
        </div>
      `;
      ytCommentsFeed.appendChild(item);
    });
  }

  function renderRelatedVideos(filter = 'all', searchQuery = '') {
    if (!ytRelatedList) return;
    ytRelatedList.innerHTML = '';

    const list = allChannels.filter(ch => {
      const cat = (ch.category || '').toLowerCase();
      if (filter === 'cricket' && cat !== 'cricket') return false;
      if (filter === 'football' && cat !== 'football') return false;
      if (filter === 'sports' && !['sports', 'cricket', 'football'].includes(cat)) return false;
      if (filter === 'entertainment' && cat !== 'entertainment') return false;
      if (filter === 'movies' && cat !== 'movies') return false;
      if (filter === 'live' && !ch.is_live) return false;
      if (filter === 'hindi') {
        const lang = (ch.language || ch.audioLanguageName || ch.language_code || '').toLowerCase();
        if (lang !== 'hindi' && lang !== 'hin') return false;
      }
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        return (ch.name || '').toLowerCase().includes(q) || (ch.category || '').toLowerCase().includes(q) || (ch.group || '').toLowerCase().includes(q);
      }
      return true;
    });

    const displayList = list.length > 0 ? list : allChannels.slice(0, 15);

    displayList.forEach(ch => {
      const isCurrent = currentWatchChannel && currentWatchChannel.url === ch.url;
      const item = document.createElement('div');
      item.className = `yt-related-item ${isCurrent ? 'playing-now' : ''}`;

      const initials = (ch.name || 'TV').split(' ').map(w => w[0]).filter(Boolean).slice(0, 2).join('').toUpperCase();
      const thumbContent = ch.logo
        ? `<img src="${ch.logo}" alt="${ch.name}" loading="lazy" onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\'channel-placeholder-logo\'><span class=\'channel-initials\'>${initials}</span></div>';">`
        : `<div class="channel-placeholder-logo"><span class="channel-initials">${initials}</span></div>`;

      const viewers = (Math.floor(Math.random() * 45) + 12) + 'K watching';

      item.innerHTML = `
        <div class="yt-thumb-box">
          ${thumbContent}
          <span class="yt-thumb-badge-res">${ch.resolution || '1080P'}</span>
          <span class="yt-thumb-badge-live">
            <span class="live-dot" style="width: 4px; height: 4px;"></span>
            LIVE
          </span>
        </div>
        <div class="yt-related-info">
          <h4 class="yt-related-title" title="${ch.name}">${ch.name}</h4>
          <span class="yt-related-channel">${ch.broadcast_channel || 'Sony LIV Sports'}</span>
          <div class="yt-related-meta">
            <span>${viewers}</span>
            <span>&bull;</span>
            <span>${ch.language || 'English'}</span>
          </div>
        </div>
      `;

      item.addEventListener('click', () => {
        openYouTubeWatch(ch);
      });

      ytRelatedList.appendChild(item);
    });
  }

  function loadInHeroPlayer(title, streamUrl) {
    if (!streamUrl) return;
    currentRawStreamUrl = streamUrl;
    const titleEl = document.querySelector('.player-stream-title');
    if (titleEl && title) titleEl.textContent = title;

    if (heroPlayer) {
      heroPlayer.src({
        src: getPlaybackUrl(streamUrl, useProxy),
        type: 'application/x-mpegURL'
      });
      heroPlayer.play().catch(e => console.log('Autoplay in hero player:', e));
    }
    showToast(`Loaded in Player: ${title || 'Live Stream'}`);
  }

  function openYouTubeWatch(channelObj, streamUrl) {
    if (!youtubeWatchView) return;

    let targetChannel = null;
    if (typeof channelObj === 'object' && channelObj !== null) {
      targetChannel = channelObj;
    } else if (typeof channelObj === 'string') {
      const found = allChannels.find(c => c.name === channelObj || c.url === streamUrl);
      targetChannel = found || {
        name: channelObj,
        url: streamUrl || currentRawStreamUrl,
        category: 'Sports',
        resolution: '1080P',
        broadcast_channel: 'Sony LIV Sports'
      };
    } else {
      targetChannel = allChannels[0] || {
        name: 'Sony LIV Live Sports Feed',
        url: currentRawStreamUrl,
        category: 'Cricket',
        resolution: '1080P'
      };
    }

    currentWatchChannel = targetChannel;

    // Pause hero background player to prevent overlapping audio
    if (heroPlayer && typeof heroPlayer.paused === 'function' && !heroPlayer.paused()) {
      heroPlayer.pause();
    }

    // Set YouTube Watch view metadata
    if (ytVideoTitle) ytVideoTitle.textContent = targetChannel.name;
    document.title = `${targetChannel.name} • StreamBox Live`;

    // Channel profile & initials
    if (ytChannelName) {
      ytChannelName.textContent = targetChannel.broadcast_channel ||
        (targetChannel.category ? `Sony ${targetChannel.category.toUpperCase()} Live` : 'Sony LIV Sports');
    }

    const initials = (targetChannel.name || 'SL').split(' ').map(w => w[0]).filter(Boolean).slice(0, 2).join('').toUpperCase() || 'SL';
    if (ytChannelInitials) ytChannelInitials.textContent = initials;

    if (ytChannelAvatar) {
      if (targetChannel.logo) {
        ytChannelAvatar.innerHTML = `<img src="${targetChannel.logo}" alt="${targetChannel.name}" onerror="this.remove(); document.getElementById('ytChannelInitials').style.display='block';"><span id="ytChannelInitials" style="display:none;">${initials}</span>`;
      } else {
        ytChannelAvatar.innerHTML = `<span id="ytChannelInitials">${initials}</span>`;
      }
    }

    if (ytSubCount) {
      const subNumber = targetChannel.category === 'cricket' ? '14.8M' : '8.6M';
      ytSubCount.textContent = `Official Live Broadcast • ${subNumber} subscribers`;
    }

    // Dynamic viewer count with live pulse dot
    if (ytLiveViewerCount) {
      const viewerCount = (Math.floor(Math.random() * 40) + 130).toLocaleString() + ',' + (Math.floor(Math.random() * 850) + 100);
      ytLiveViewerCount.innerHTML = `<span class="live-dot" style="width: 7px; height: 7px; display:inline-block; margin-right: 5px;"></span>🔴 ${viewerCount} watching now`;
    }

    if (ytStreamQualityPill) {
      ytStreamQualityPill.textContent = `${targetChannel.resolution || '1080P'} • HLS`;
    }

    if (ytStreamStartInfo) {
      ytStreamStartInfo.textContent = `Live Akamai Stream • Synced from GitHub`;
    }

    if (ytDescContent) {
      ytDescContent.innerHTML = `
        <strong>${targetChannel.name}</strong> - Official multi-bitrate high definition live stream broadcast.<br>
        <strong>Category:</strong> ${(targetChannel.category || 'Live Sports').toUpperCase()} &bull; 
        <strong>Audio Track:</strong> ${targetChannel.language || 'English / Hindi Stadium Stereo'} &bull; 
        <strong>Resolution:</strong> ${targetChannel.resolution || '1080p50 Adaptive ABR'}<br>
        Delivered via high-speed Akamai edge CDN nodes and auto-synchronized dynamically from GitHub with zero buffer lag.
      `;
    }

    // Populate comments & related playlist
    populateComments();
    renderRelatedVideos(currentYtFilter);

    // Open full YouTube Watch View overlay & lock background scroll
    youtubeWatchView.classList.add('open');
    youtubeWatchView.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    youtubeWatchView.scrollTop = 0;

    // Pause hero background player to prevent overlapping audio
    if (heroPlayerFrame && heroPlayerFrame.contentWindow) {
      heroPlayerFrame.contentWindow.postMessage({ action: 'pause' }, '*');
    }

    const modalFrame = document.getElementById('modalPlayerFrame');
    const targetUrl = targetChannel.url || currentRawStreamUrl;

    if (modalFrame && modalFrame.contentWindow) {
      modalFrame.contentWindow.postMessage({
        action: 'load',
        url: targetUrl,
        autoplay: true,
        muted: false
      }, '*');
    }

    showToast(`Streaming: ${targetChannel.name}`);
  }

  function closeYouTubeWatch() {
    if (!youtubeWatchView) return;
    youtubeWatchView.classList.remove('open');
    youtubeWatchView.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    const modalFrame = document.getElementById('modalPlayerFrame');
    if (modalFrame && modalFrame.contentWindow) {
      modalFrame.contentWindow.postMessage({ action: 'pause' }, '*');
    }
    if (heroPlayerFrame && heroPlayerFrame.contentWindow) {
      heroPlayerFrame.contentWindow.postMessage({ action: 'play' }, '*');
    }
    document.title = 'StreamBox — Live Video Streaming Platform';
  }

  // Aliases for backward compatibility
  function openTheaterModal(title, streamUrl) {
    openYouTubeWatch({ name: title, url: streamUrl });
  }

  function closeTheaterModal() {
    closeYouTubeWatch();
  }

  // YouTube UI Top Controls Event Listeners
  if (ytBackBtn) ytBackBtn.addEventListener('click', closeYouTubeWatch);
  if (ytCloseBtn) ytCloseBtn.addEventListener('click', closeYouTubeWatch);

  // Subscribe button toggle
  if (ytSubscribeBtn) {
    ytSubscribeBtn.addEventListener('click', () => {
      isSubscribed = !isSubscribed;
      if (isSubscribed) {
        ytSubscribeBtn.classList.add('subscribed');
        ytSubscribeBtn.querySelector('span').textContent = 'Subscribed ✓';
        showToast(`Subscribed to ${ytChannelName ? ytChannelName.textContent : 'Channel'}!`);
      } else {
        ytSubscribeBtn.classList.remove('subscribed');
        ytSubscribeBtn.querySelector('span').textContent = 'Subscribe';
        showToast(`Unsubscribed from ${ytChannelName ? ytChannelName.textContent : 'Channel'}`);
      }
    });
  }

  // Like & Dislike pills
  if (ytLikeBtn) {
    ytLikeBtn.addEventListener('click', () => {
      isLiked = !isLiked;
      if (isLiked) {
        ytLikes++;
        ytLikeBtn.style.color = '#3ea6ff';
        if (isDisliked) {
          isDisliked = false;
          if (ytDislikeBtn) ytDislikeBtn.style.color = '';
        }
        showToast('Added to liked streams 👍');
      } else {
        ytLikes--;
        ytLikeBtn.style.color = '';
      }
      if (ytLikeCount) ytLikeCount.textContent = (ytLikes / 1000).toFixed(1) + 'K';
    });
  }

  if (ytDislikeBtn) {
    ytDislikeBtn.addEventListener('click', () => {
      isDisliked = !isDisliked;
      if (isDisliked) {
        ytDislikeBtn.style.color = '#3ea6ff';
        if (isLiked) {
          isLiked = false;
          ytLikes--;
          if (ytLikeBtn) ytLikeBtn.style.color = '';
          if (ytLikeCount) ytLikeCount.textContent = (ytLikes / 1000).toFixed(1) + 'K';
        }
      } else {
        ytDislikeBtn.style.color = '';
      }
    });
  }

  // Share button
  if (ytShareBtn) {
    ytShareBtn.addEventListener('click', () => {
      const shareUrl = currentWatchChannel ? (window.location.origin + '/api/stream/proxy?url=' + encodeURIComponent(currentWatchChannel.url)) : window.location.href;
      if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(() => {
          showToast('Stream link copied to clipboard! 📋');
        }).catch(() => {
          showToast('Link ready: ' + (currentWatchChannel ? currentWatchChannel.name : 'StreamBox'));
        });
      } else {
        showToast('Stream link ready to share!');
      }
    });
  }

  // Theater Mode Toggle
  function toggleTheaterMode() {
    if (ytWatchColumns) {
      ytWatchColumns.classList.toggle('theater-mode');
      const isTheater = ytWatchColumns.classList.contains('theater-mode');
      showToast(isTheater ? 'Theater mode enabled' : 'Default view enabled');
    }
  }

  if (ytTheaterToggleBtn) ytTheaterToggleBtn.addEventListener('click', toggleTheaterMode);
  if (ytTheaterBtn) ytTheaterBtn.addEventListener('click', toggleTheaterMode);

  // Description Box expand/collapse
  if (ytDescToggle) {
    ytDescToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      if (ytDescriptionBox) {
        ytDescriptionBox.classList.toggle('expanded');
        ytDescToggle.textContent = ytDescriptionBox.classList.contains('expanded') ? 'Show less' : '...more';
      }
    });
  }

  if (ytDescriptionBox) {
    ytDescriptionBox.addEventListener('click', () => {
      ytDescriptionBox.classList.toggle('expanded');
      if (ytDescToggle) {
        ytDescToggle.textContent = ytDescriptionBox.classList.contains('expanded') ? 'Show less' : '...more';
      }
    });
  }

  // Live Chat / Comments Submission
  if (ytCommentInput) {
    ytCommentInput.addEventListener('focus', () => {
      if (ytInputActions) ytInputActions.style.display = 'flex';
    });

    ytCommentInput.addEventListener('input', () => {
      if (ytCommentSubmit) {
        ytCommentSubmit.disabled = !ytCommentInput.value.trim();
      }
    });

    ytCommentInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && ytCommentInput.value.trim()) {
        postComment();
      }
    });
  }

  if (ytCommentCancel) {
    ytCommentCancel.addEventListener('click', () => {
      if (ytCommentInput) ytCommentInput.value = '';
      if (ytCommentSubmit) ytCommentSubmit.disabled = true;
      if (ytInputActions) ytInputActions.style.display = 'none';
    });
  }

  function postComment() {
    if (!ytCommentInput) return;
    const text = ytCommentInput.value.trim();
    if (!text) return;

    const newComment = document.createElement('div');
    newComment.className = 'yt-comment-item';
    newComment.style.animation = 'fadeIn 0.3s ease';
    newComment.innerHTML = `
      <div class="yt-comment-avatar" style="background: #3ea6ff;">U</div>
      <div class="yt-comment-body">
        <div class="yt-comment-author-line">
          <span class="yt-comment-author">You</span>
          <span class="yt-comment-time">Just now</span>
        </div>
        <div class="yt-comment-text">${text}</div>
      </div>
    `;

    if (ytCommentsFeed) ytCommentsFeed.prepend(newComment);
    if (ytCommentsCount) {
      const current = parseInt(ytCommentsCount.textContent.replace(/,/g, ''), 10) || 0;
      ytCommentsCount.textContent = (current + 1).toLocaleString();
    }

    ytCommentInput.value = '';
    if (ytCommentSubmit) ytCommentSubmit.disabled = true;
    if (ytInputActions) ytInputActions.style.display = 'none';
    showToast('Comment posted to live stream! 💬');
  }

  if (ytCommentSubmit) ytCommentSubmit.addEventListener('click', postComment);

  // Related Category Chips
  ytRelatedChips.forEach(chip => {
    chip.addEventListener('click', () => {
      ytRelatedChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      currentYtFilter = chip.getAttribute('data-ytfilter') || 'all';
      renderRelatedVideos(currentYtFilter, ytSearchInput ? ytSearchInput.value.trim() : '');
    });
  });

  // YouTube Watch Search Bar
  if (ytSearchInput) {
    ytSearchInput.addEventListener('input', (e) => {
      renderRelatedVideos(currentYtFilter, e.target.value.trim());
    });
  }

  if (ytSearchSubmit) {
    ytSearchSubmit.addEventListener('click', () => {
      if (ytSearchInput) renderRelatedVideos(currentYtFilter, ytSearchInput.value.trim());
    });
  }

  // Start Watching / Watch Now triggers
  const startWatchingBtn = document.getElementById('startWatchingBtn');
  const watchNowBtn = document.getElementById('watchNowBtn');
  const explorePlayerBtn = document.getElementById('explorePlayerBtn');

  if (startWatchingBtn) {
    startWatchingBtn.addEventListener('click', () => {
      const target = allChannels.length > 0 ? allChannels[0] : { name: 'Chrono Station • Live Stream Feed', url: currentRawStreamUrl }; openYouTubeWatch(target);
    });
  }

  if (watchNowBtn) {
    watchNowBtn.addEventListener('click', () => {
      const target = allChannels.length > 0 ? allChannels[0] : { name: 'Live Channel Premiere', url: currentRawStreamUrl }; openYouTubeWatch(target);
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
    const counts = { all: allChannels.length, cricket: 0, football: 0, sports: 0, entertainment: 0, movies: 0, hindi: 0, english: 0, regional: 0 };
    allChannels.forEach(ch => {
      const cat = (ch.category || '').toLowerCase();
      const lang = (ch.language_code || ch.audioLanguageName || ch.language || '').toLowerCase();
      if (counts[cat] !== undefined) counts[cat]++;
      if (cat === 'cricket' || cat === 'football') counts['sports']++;
      if (lang === 'hin' || lang === 'hindi') counts['hindi']++;
      else if (lang === 'eng' || lang === 'english') counts['english']++;
      else if (['tam', 'tamil', 'kan', 'kannada', 'tel', 'telugu', 'mal', 'malayalam', 'mar', 'marathi', 'ben', 'bengali'].includes(lang)) counts['regional']++;
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
      openYouTubeWatch(ch);
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
    catTag.textContent = ch.language ? `${(ch.category || 'LIVE').toUpperCase()} • ${ch.language}` : (ch.category || 'LIVE').toUpperCase();
    metaBottom.appendChild(catTag);

    const subText = document.createElement('span');
    subText.textContent = ch.broadcast_channel || 'Sony LIV';
    metaBottom.appendChild(subText);

    body.appendChild(metaBottom);
    card.appendChild(body);

    // Clicking card opens theater modal
    card.addEventListener('click', () => {
      openYouTubeWatch(ch);
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
      let matchCat = (currentCategory === 'all');
      if (!matchCat) {
        const cat = (ch.category || '').toLowerCase();
        const lang = (ch.language_code || ch.audioLanguageName || ch.language || '').toLowerCase();
        if (currentCategory === cat) matchCat = true;
        else if (currentCategory === 'sports' && ['sports', 'cricket', 'football'].includes(cat)) matchCat = true;
        else if (currentCategory === 'hindi' && (lang === 'hin' || lang === 'hindi')) matchCat = true;
        else if (currentCategory === 'english' && (lang === 'eng' || lang === 'english')) matchCat = true;
        else if (currentCategory === 'regional' && ['tam', 'tamil', 'kan', 'kannada', 'tel', 'telugu', 'mal', 'malayalam', 'mar', 'marathi', 'ben', 'bengali'].includes(lang)) matchCat = true;
      }
      if (!matchCat) return false;
      if (!currentSearchQuery) return true;
      const q = currentSearchQuery.toLowerCase();
      return (ch.name || '').toLowerCase().includes(q) ||
        (ch.raw_name || '').toLowerCase().includes(q) ||
        (ch.category || '').toLowerCase().includes(q) ||
        (ch.language || '').toLowerCase().includes(q) ||
        (ch.broadcast_channel || '').toLowerCase().includes(q) ||
        (ch.group || '').toLowerCase().includes(q);
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

  // Fetch channels list from dynamic API (with fallback to static JSON)
  fetch(`/api/channels?t=${Date.now()}`, { cache: 'no-store' })
    .then(r => {
      if (!r.ok) throw new Error('API channels returned non-200');
      return r.json();
    })
    .then(data => {
      allChannels = data.channels || [];
      filteredChannels = allChannels;
      updateCategoryBadges();
      renderChannels();
      console.log(`[StreamBox] Synced ${allChannels.length} Sony LIV channels from ${data.source || 'GitHub'}.`);
    })
    .catch(() => {
      fetch(`/static/channels.json?t=${Date.now()}`, { cache: 'no-store' })
        .then(res => res.json())
        .then(data => {
          allChannels = data;
          filteredChannels = data;
          updateCategoryBadges();
          renderChannels();
        });
    });

  // --- GitHub Stream Repository Manual Sync Button & Mobile Nav Sync ---
  function performSync() {
    const syncGithubBtn = document.getElementById('syncGithubBtn');
    const syncBtnText = document.getElementById('syncBtnText');
    const mobileNavSyncBtn = document.getElementById('mobileNavSync');

    if (syncBtnText) syncBtnText.textContent = 'Syncing...';
    if (syncGithubBtn) syncGithubBtn.style.opacity = '0.7';
    if (mobileNavSyncBtn) mobileNavSyncBtn.style.opacity = '0.7';

    fetch('/api/stream/sync', { method: 'POST' })
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(res => {
        const count = res.result?.total_channels ?? res.current_status?.total_channels ?? 0;
        showToast(`Synced ${count} channels from GitHub!`, 'success');
        if (syncBtnText) syncBtnText.textContent = 'Synced!';
        setTimeout(() => {
          if (syncBtnText) syncBtnText.textContent = 'Sync GitHub';
          if (syncGithubBtn) syncGithubBtn.style.opacity = '1';
          if (mobileNavSyncBtn) mobileNavSyncBtn.style.opacity = '1';
        }, 2000);

        // Refresh channel grid
        fetch(`/api/channels?t=${Date.now()}`, { cache: 'no-store' })
          .then(r => r.json())
          .then(data => {
            allChannels = data.channels || [];
            filteredChannels = allChannels;
            updateCategoryBadges();
            renderChannels();
          })
          .catch(e => console.warn('Channel list refresh error:', e));

        // Refresh live feed if active event changed
        if (res.current_status?.active_stream_url) {
          try {
            loadInHeroPlayer(res.current_status.active_event, res.current_status.active_stream_url);
          } catch (err) {
            console.warn('Hero player update notice:', err);
          }
        }
      })
      .catch(err => {
        console.error('Manual sync failed:', err);
        showToast('Failed to sync with GitHub: ' + (err.message || 'Network error'), 'error');
        if (syncBtnText) syncBtnText.textContent = 'Sync Failed';
        setTimeout(() => {
          if (syncBtnText) syncBtnText.textContent = 'Sync GitHub';
          if (syncGithubBtn) syncGithubBtn.style.opacity = '1';
          if (mobileNavSyncBtn) mobileNavSyncBtn.style.opacity = '1';
        }, 2500);
      });
  }

  const syncGithubBtn = document.getElementById('syncGithubBtn');
  if (syncGithubBtn) {
    syncGithubBtn.addEventListener('click', performSync);
  }

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
      closeYouTubeWatch();
    }
  });

  // --- Cast Notification ---
  const castBtn = document.getElementById('castBtn');
  if (castBtn) {
    castBtn.addEventListener('click', () => {
      showToast('Searching for Cast & AirPlay receivers on local network...');
    });
  }

  // --- Mobile Bottom Navigation Controller ---
  const mobileNavHome = document.getElementById('mobileNavHome');
  const mobileNavChannels = document.getElementById('mobileNavChannels');
  const mobileNavLive = document.getElementById('mobileNavLive');
  const mobileNavSync = document.getElementById('mobileNavSync');
  const mobileNavSearch = document.getElementById('mobileNavSearch');
  const mobileNavSettings = document.getElementById('mobileNavSettings');

  if (mobileNavChannels) {
    mobileNavChannels.addEventListener('click', (e) => {
      if (youtubeWatchView && youtubeWatchView.classList.contains('active')) {
        closeYouTubeWatch();
      }
      const grid = document.getElementById('channelsGridSection') || document.querySelector('.channels-section');
      if (grid) {
        grid.scrollIntoView({ behavior: 'smooth' });
      }
      document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));
      mobileNavChannels.classList.add('active');
    });
  }

  if (mobileNavHome) {
    mobileNavHome.addEventListener('click', (e) => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
      document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));
      mobileNavHome.classList.add('active');
    });
  }

  if (mobileNavLive) {
    mobileNavLive.addEventListener('click', (e) => {
      const liveSection = document.getElementById('liveSection') || document.querySelector('.channels-section') || document.getElementById('explore');
      if (liveSection) {
        liveSection.scrollIntoView({ behavior: 'smooth' });
      }
      document.querySelectorAll('.mobile-nav-btn').forEach(b => b.classList.remove('active'));
      mobileNavLive.classList.add('active');
    });
  }

  if (mobileNavSync && syncGithubBtn) {
    mobileNavSync.addEventListener('click', () => {
      syncGithubBtn.click();
    });
  }

  if (mobileNavSearch && searchBtn) {
    mobileNavSearch.addEventListener('click', () => {
      searchBtn.click();
    });
  }

  if (mobileNavSettings) {
    mobileNavSettings.addEventListener('click', () => {
      openStreamConfigModal();
    });
  }

});

const BOT_API_URL = 'https://dragonbot-omgj.onrender.com/status';

// ==========================================
// 1. CẤU HÌNH VIDEO NỀN DUY NHẤT (CỐ ĐỊNH)
// ==========================================
const FIXED_VIDEO_URL = "video/background.mp4";

// ==========================================
// 2. PLAYLIST CHỈ THAY ĐỔI AUDIO VÀ TITLE
// ==========================================
const playlist = [
    {
        title: "hum......",
        audioUrl: "audio/1.mp3"
    }
];

let currentTrackIndex = 0;

const audioEl = document.getElementById('bg-music');
const videoEl = document.getElementById('bg-video');

const playBtn = document.getElementById('play-btn');
const volumeBtn = document.getElementById('volume-btn');
const progressBar = document.getElementById('progress-bar');
const trackTime = document.getElementById('track-time');
const trackName = document.getElementById('track-name');

const nextBtn = document.querySelector('.player-controls .fa-step-forward');
const prevBtn = document.querySelector('.player-controls .fa-step-backward');

// Hàm trích xuất ID YouTube
function getYouTubeId(url) {
    if (!url) return null;
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
}

// Trả về src phù hợp — local dùng thẳng, YouTube qua /api/stream
function resolveMediaUrl(url, type) {
    if (!url) return '';
    if (getYouTubeId(url)) {
        return `/api/stream/${type}?url=` + encodeURIComponent(url);
    }
    return url; // local path
}

// Tải video nền cố định
function initFixedVideo() {
    if (!videoEl) return;
    videoEl.src = resolveMediaUrl(FIXED_VIDEO_URL, 'video');
    videoEl.load();
}

// Đổi bài hát
function loadTrack(index) {
    if (playlist.length === 0) return;
    currentTrackIndex = index;
    const track = playlist[currentTrackIndex];
    if (trackName) trackName.innerText = track.title;
    audioEl.src = resolveMediaUrl(track.audioUrl, 'audio');
    audioEl.load();
    progressBar.style.width = '0%';
    trackTime.innerText = "0:00 / 0:00";
}

function playTrack() {
    audioEl.play().then(() => {
        if (videoEl && videoEl.paused) videoEl.play();
        playBtn.className = 'fas fa-pause';
    }).catch(err => {
        console.log("Autoplay blocked:", err);
        playBtn.className = 'fas fa-play'; // đồng bộ UI khi phát thất bại
    });
}

function pauseTrack() {
    audioEl.pause();
    playBtn.className = 'fas fa-play';
}

function nextTrack() {
    let index = (currentTrackIndex + 1 >= playlist.length) ? 0 : currentTrackIndex + 1;
    loadTrack(index);
    playTrack();
}

function prevTrack() {
    let index = (currentTrackIndex - 1 < 0) ? playlist.length - 1 : currentTrackIndex - 1;
    loadTrack(index);
    playTrack();
}

function formatTime(secs) {
    const minutes = Math.floor(secs / 60) || 0;
    const seconds = Math.floor(secs % 60) || 0;
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
}

audioEl.addEventListener('timeupdate', () => {
    if (audioEl.duration) {
        const progress = (audioEl.currentTime / audioEl.duration) * 100;
        progressBar.style.width = `${progress}%`;
        trackTime.innerText = `${formatTime(audioEl.currentTime)} / ${formatTime(audioEl.duration)}`;
    }
});

audioEl.addEventListener('ended', nextTrack);

playBtn.addEventListener('click', () => {
    if (audioEl.paused) playTrack();
    else pauseTrack();
});

if (nextBtn) nextBtn.addEventListener('click', nextTrack);
if (prevBtn) prevBtn.addEventListener('click', prevTrack);

volumeBtn.addEventListener('click', () => {
    if (audioEl.muted) {
        audioEl.muted = false;
        volumeBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
    } else {
        audioEl.muted = true;
        volumeBtn.innerHTML = '<i class="fas fa-volume-mute"></i>';
    }
});

// ==========================================
// CARD SLIDER
// ==========================================
function initCardSlider() {
    const slider = document.getElementById('card-slider');
    const dots = document.querySelectorAll('.slider-dot');
    if (!slider || !dots.length) return;

    let current = 0;
    const total = dots.length;
    let startX = 0;
    let isDragging = false;

    function goTo(index) {
        current = (index + total) % total;
        slider.style.transform = `translateX(-${current * 100}%)`;
        dots.forEach((d, i) => d.classList.toggle('active', i === current));
    }

    // Chấm bấm
    dots.forEach(dot => {
        dot.addEventListener('click', () => goTo(parseInt(dot.dataset.index)));
    });

    // Swipe trên mobile
    slider.addEventListener('touchstart', e => { startX = e.touches[0].clientX; isDragging = true; }, { passive: true });
    slider.addEventListener('touchend', e => {
        if (!isDragging) return;
        const diff = startX - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 40) goTo(diff > 0 ? current + 1 : current - 1);
        isDragging = false;
    });

    // Kéo chuột trên desktop
    slider.addEventListener('mousedown', e => { startX = e.clientX; isDragging = true; });
    slider.addEventListener('mouseup', e => {
        if (!isDragging) return;
        const diff = startX - e.clientX;
        if (Math.abs(diff) > 40) goTo(diff > 0 ? current + 1 : current - 1);
        isDragging = false;
    });

    // Tự động chuyển mỗi 4 giây
    setInterval(() => goTo(current + 1), 4000);
}

// ==========================================
// SPLASH SCREEN + AUTO-PLAY KHI ENTER
// ==========================================
function createParticles() {
    const container = document.getElementById('splash-particles');
    if (!container) return;
    const colors = ['#ffffff', '#00f0ff', '#7f00ff', '#ff007f'];
    for (let i = 0; i < 60; i++) {
        const span = document.createElement('span');
        span.style.left = Math.random() * 100 + 'vw';
        span.style.bottom = '-10px';
        const size = (Math.random() * 3 + 1) + 'px';
        span.style.width = size;
        span.style.height = size;
        span.style.animationDuration = (Math.random() * 12 + 8) + 's';
        span.style.animationDelay = (Math.random() * 12) + 's';
        const color = colors[Math.floor(Math.random() * colors.length)];
        span.style.background = color;
        span.style.boxShadow = `0 0 6px 2px ${color}`;
        container.appendChild(span);
    }
}

function enterSite() {
    const splash = document.getElementById('splash-screen');
    splash.classList.add('hidden');
    // Auto-play nhạc ngay khi bấm Enter (đã có gesture của user)
    audioEl.muted = false;
    playTrack();
    volumeBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
}

// ==========================================
// HELPER: đặt avatar vào icon wrap
// ==========================================
function setAvatar(wrapId, url) {
    const wrap = document.getElementById(wrapId);
    if (!wrap || !url) return;
    const img = document.createElement('img');
    img.style.cssText = 'width:100%;height:100%;border-radius:50%;object-fit:cover;filter:none';
    img.src = url;
    img.onerror = () => console.error('setAvatar lỗi:', wrapId, url);
    wrap.innerHTML = '';
    wrap.appendChild(img);
}

// ==========================================
// YOUTUBE CHANNEL
// ==========================================
async function loadYouTubeStatus() {
    try {
        const res  = await fetch('/api/youtube');
        const data = await res.json();

        // Tên + handle + sub + videos + description
        const nameEl   = document.getElementById('yt-name');
        const handleEl = document.getElementById('yt-handle');
        const subEl    = document.getElementById('yt-sub');
        const descEl   = document.getElementById('yt-desc');
        if (nameEl)   nameEl.innerText   = data.author || 'DRG_hiwvnk';
        if (handleEl) handleEl.innerText = data.handle || '';
        if (subEl) {
            const parts = [];
            if (data.subCount !== undefined) parts.push(`${data.subCount.toLocaleString()} subscribers`);
            if (data.videoCount)             parts.push(`${data.videoCount} videos`);
            subEl.innerText = parts.join(' · ');
        }
        if (descEl) descEl.innerText = data.description || '';

        // Avatar — lấy ảnh lớn nhất trong authorThumbnails
        const thumbs = data.authorThumbnails || [];
        const best   = thumbs.reduce((a, b) => (b.width > a.width ? b : a), thumbs[0] || {});
        if (best?.url) {
            // Invidious trả về URL dạng //yt3.ggpht.com/... → thêm https:
            const thumbUrl = best.url.startsWith('//') ? 'https:' + best.url : best.url;
            setAvatar('yt-icon-wrap', '/api/img?url=' + encodeURIComponent(thumbUrl));
        }
    } catch (err) {
        console.error('Lỗi fetch YouTube:', err);
    }
}

// ==========================================
// ROBLOX PROFILE
// ==========================================
async function loadRobloxStatus() {
    try {
        const [userRes, avatarRes, presenceRes] = await Promise.all([
            fetch('/api/roblox'),
            fetch('/api/roblox-avatar'),
            fetch('/api/roblox-presence')
        ]);
        const user     = await userRes.json();
        const avatar   = await avatarRes.json();
        const presence = await presenceRes.json();

        // Tên + handle + description
        const nameEl   = document.getElementById('roblox-name');
        const handleEl = document.getElementById('roblox-handle');
        const descEl   = document.getElementById('roblox-desc');
        if (nameEl)   nameEl.innerText   = user.displayName || user.name;
        if (handleEl) handleEl.innerText = `@${user.name}`;
        if (descEl)   descEl.innerText   = user.description || '';

        // Trạng thái
        const p = presence?.userPresences?.[0];
        const subEl = document.getElementById('roblox-sub');
        const dot   = document.getElementById('roblox-status-dot');
        if (p !== undefined) {
            const type = p.userPresenceType;
            if (type === 2) {
                // Đang chơi game
                const gameName = p.lastLocation && p.lastLocation.trim() ? p.lastLocation : null;
                if (subEl) subEl.innerText = gameName ? `🎮 ${gameName}` : '🎮 Đang trong game';
                if (dot)   dot.className = 'status-dot online';
            } else if (type === 1) {
                if (subEl) subEl.innerText = 'Trực tuyến 🟢';
                if (dot)   dot.className = 'status-dot online';
            } else if (type === 3) {
                if (subEl) subEl.innerText = 'Đang dùng Studio 🔧';
                if (dot)   dot.className = 'status-dot online';
            } else {
                if (subEl) subEl.innerText = 'Ngoại tuyến';
                if (dot)   dot.className = 'status-dot offline';
            }
        }

        // Avatar — proxy qua server để tránh CORS
        const imgUrl = avatar?.data?.[0]?.imageUrl;
        if (imgUrl) setAvatar('roblox-icon-wrap', '/api/img?url=' + encodeURIComponent(imgUrl));
    } catch (err) {
        console.error('Lỗi fetch Roblox:', err);
    }
}

// ĐỒNG BỘ TRẠNG THÁI DISCORD
async function loadStatus() {
    try {
        const res  = await fetch('/api/discord');
        const data = await res.json();
        if (!data?.discord) return;
        const user = data.discord;

        // Header profile
        const usernameMain = document.getElementById('username-main');
        const displayName  = document.getElementById('display-name');
        if (usernameMain) usernameMain.innerText = user.globalName || user.username;
        if (displayName)  displayName.innerText  = `@${user.username.toLowerCase()}`;

        // Avatar header + card icon
        if (user.avatarUrl) {
            const proxy = '/api/img?url=' + encodeURIComponent(user.avatarUrl);
            const avatarMain = document.getElementById('avatar-main');
            if (avatarMain) avatarMain.src = proxy;
            setAvatar('discord-icon-wrap', proxy);
        }

        // Decoration overlay (PNG của Discord)
        const decorEl = document.getElementById('avatar-decoration');
        if (decorEl && user.avatarDecorationUrl) {
            decorEl.src = '/api/img?url=' + encodeURIComponent(user.avatarDecorationUrl);
            decorEl.style.display = 'block';
        }

        // Tên + handle + trạng thái + description
        const titleEl   = document.getElementById('card-title');
        const handleEl  = document.getElementById('card-handle');
        const subtextEl = document.getElementById('card-subtext');
        const descEl    = document.getElementById('card-desc');
        if (titleEl)  titleEl.innerText  = user.globalName || user.username;
        if (handleEl) handleEl.innerText = `@${user.username.toLowerCase()}`;

        const statusMap = { online: 'Đang hoạt động 🟢', idle: 'Đang treo máy 🌙', dnd: 'Đừng làm phiền ⛔' };
        const isOnline = user.status !== 'offline';
        if (subtextEl) subtextEl.innerText = statusMap[user.status] || 'Ngoại tuyến';
        if (descEl) descEl.innerText = (isOnline && user.customStatus) ? user.customStatus : '';

        // Chấm online/offline
        const dot = document.getElementById('bot-status-dot');
        if (dot) dot.className = user.status !== 'offline' ? 'status-dot online' : 'status-dot offline';

    } catch (err) {
        console.error('Lỗi fetch Discord:', err);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    createParticles();
    initFixedVideo();
    loadTrack(currentTrackIndex);
    loadStatus();
    initCardSlider();
    loadRobloxStatus();
    loadYouTubeStatus();

    setInterval(loadStatus,       5000);
    setInterval(loadRobloxStatus, 10000);
    setInterval(loadYouTubeStatus, 10000);

    const splash = document.getElementById('splash-screen');
    if (splash) splash.addEventListener('click', enterSite);
});

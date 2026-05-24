/* ============================================================
   北印信安生存手册 · CIPHER NOIR 特效脚本
   ─ Hero HEX / 符文粒子场（网络连线 + 鼠标斥力）
   ─ 卡片 3D 透视倾斜 + 聚光灯（CSS var --mx/--my）
   ─ HUD 角括号注入（4 个 .cn-corner span）
   ─ 主标题 Glitch 动画周期触发
   ─ 滚动揭示（IntersectionObserver）
   ─ 代码块终端语言标签
   MkDocs Material SPA 兼容：订阅 document$ Observable
   ============================================================ */

(function () {
  'use strict';

  /* ── 工具 ── */
  function clamp(v, lo, hi) { return Math.min(Math.max(v, lo), hi); }
  function lerp(a, b, t)    { return a + (b - a) * t; }
  function rnd(a, b)        { return Math.random() * (b - a) + a; }
  function isDark()         {
    return document.documentElement.getAttribute('data-md-color-scheme') === 'slate';
  }

  /* ═══════════════════════════════════════════════════════
     1. Hero — HEX 粒子场
        浮动的十六进制字节 + 符文字符，相邻节点自动连线，
        鼠标进入时产生斥力，节点随机刷新字符
  ═══════════════════════════════════════════════════════ */
  function initHero() {
    const hero = document.querySelector('.hero-section');
    if (!hero) return null;

    /* 移除旧 canvas（SPA 重新导航时） */
    hero.querySelector('.cn-canvas')?.remove();

    const canvas = document.createElement('canvas');
    canvas.className = 'cn-canvas';
    Object.assign(canvas.style, {
      position: 'absolute', inset: '0',
      width: '100%', height: '100%',
      pointerEvents: 'none', zIndex: '0',
    });
    hero.prepend(canvas);

    const ctx = canvas.getContext('2d');
    let W, H, nodes = [], rafId = 0;
    const mouse = { x: -9999, y: -9999 };

    /* 字符池：十六进制字节 + 赛博符文 */
    const HEX  = '0123456789ABCDEF';
    const RUNE = ['◈', '⬡', '✦', '◉', '⊕', '◇', '░', '▸', '⟨⟩', '∅'];

    function accent1() { return isDark() ? '#00CCEE' : '#0044CC'; }
    function accent2() { return isDark() ? '#00DD90' : '#009670'; }

    function resize() {
      W = canvas.width  = hero.offsetWidth;
      H = canvas.height = hero.offsetHeight;
    }

    function mkNode() {
      const isHex = Math.random() > 0.32;
      return {
        x: rnd(0, W), y: rnd(0, H),
        vx: rnd(-0.28, 0.28), vy: rnd(-0.22, 0.22),
        char: isHex
          ? HEX[Math.random() * 16 | 0] + HEX[Math.random() * 16 | 0]
          : RUNE[Math.random() * RUNE.length | 0],
        isHex,
        t: 0, ti: rnd(55, 140),       /* 字符刷新计时 */
        alpha: rnd(0.06, 0.24),
        size:  rnd(9, 14),
      };
    }

    function spawn() {
      const n = clamp((W * H / 13000) | 0, 22, 65);
      nodes = Array.from({ length: n }, mkNode);
    }

    function frame() {
      ctx.clearRect(0, 0, W, H);
      const c1 = accent1(), c2 = accent2();

      /* 更新节点物理 */
      for (const nd of nodes) {
        const dx = nd.x - mouse.x, dy = nd.y - mouse.y;
        const d  = Math.hypot(dx, dy);
        if (d < 110 && d > 1) {
          const f = (110 - d) / 110 * 0.38;
          nd.vx += dx / d * f;
          nd.vy += dy / d * f;
        }
        const spd = Math.hypot(nd.vx, nd.vy);
        if (spd > 1.5) { nd.vx *= 1.5 / spd; nd.vy *= 1.5 / spd; }
        nd.vx *= 0.988; nd.vy *= 0.988;
        nd.x  += nd.vx;  nd.y  += nd.vy;
        /* 环绕边界 */
        if (nd.x < -20) nd.x = W + 10; else if (nd.x > W + 20) nd.x = -10;
        if (nd.y < -20) nd.y = H + 10; else if (nd.y > H + 20) nd.y = -10;
        /* 随机刷新 HEX 字符 */
        if (nd.isHex && ++nd.t > nd.ti) {
          nd.char = HEX[Math.random() * 16 | 0] + HEX[Math.random() * 16 | 0];
          nd.t = 0; nd.ti = rnd(55, 140);
        }
      }

      /* 绘制连线 */
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j];
          const d = Math.hypot(a.x - b.x, a.y - b.y);
          if (d > 155) continue;
          const alpha = (1 - d / 155) * 0.17;
          const g = ctx.createLinearGradient(a.x, a.y, b.x, b.y);
          g.addColorStop(0, c1);
          g.addColorStop(1, c2);
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle  = g;
          ctx.globalAlpha  = alpha;
          ctx.lineWidth    = 0.7;
          ctx.stroke();
        }
      }

      /* 绘制字符节点 */
      ctx.globalAlpha = 1;
      for (const nd of nodes) {
        ctx.font       = `${nd.size}px "JetBrains Mono", monospace`;
        ctx.fillStyle  = c1;
        ctx.globalAlpha = nd.alpha;
        ctx.fillText(nd.char, nd.x, nd.y);
      }
      ctx.globalAlpha = 1;
      rafId = requestAnimationFrame(frame);
    }

    /* 鼠标事件（全局 mousemove，不限 hero 内） */
    function onMove(e) {
      const r = hero.getBoundingClientRect();
      mouse.x = e.clientX - r.left;
      mouse.y = e.clientY - r.top;
    }
    function onLeave() { mouse.x = mouse.y = -9999; }

    const ro = new ResizeObserver(() => { resize(); spawn(); });
    ro.observe(hero);
    resize(); spawn(); frame();
    window.addEventListener('mousemove', onMove);
    hero.addEventListener('mouseleave', onLeave);

    /* Hero 内容层级 — 确保在 canvas 上方 */
    hero.querySelectorAll('.hero-kicker,.hero-title,.hero-sub,.hero-tags')
        .forEach(el => { el.style.position = 'relative'; el.style.zIndex = '2'; });

    return () => {
      cancelAnimationFrame(rafId);
      ro.disconnect();
      window.removeEventListener('mousemove', onMove);
      hero.removeEventListener('mouseleave', onLeave);
      canvas.remove();
    };
  }

  /* ═══════════════════════════════════════════════════════
     2. 卡片 3D 透视倾斜 + 聚光灯
        mousemove → 计算相对坐标 → lerp 平滑写入
        离开时弹簧复位
  ═══════════════════════════════════════════════════════ */
  function initTilt() {
    const cards = document.querySelectorAll('.md-typeset .grid.cards > ul > li');
    if (!cards.length) return null;

    const kills = [];

    cards.forEach(card => {
      let rafId = 0, hovering = false;
      let tRx = 0, tRy = 0, rRx = 0, rRy = 0;
      let tMx = 50, tMy = 50, rMx = 50, rMy = 50;

      function tickHover() {
        rRx = lerp(rRx, tRx, 0.10);
        rRy = lerp(rRy, tRy, 0.10);
        rMx = lerp(rMx, tMx, 0.10);
        rMy = lerp(rMy, tMy, 0.10);
        card.style.transform =
          `perspective(900px) rotateX(${rRx}deg) rotateY(${rRy}deg) translateY(-7px) scale(1.008)`;
        card.style.setProperty('--mx', `${rMx}%`);
        card.style.setProperty('--my', `${rMy}%`);
        const moving =
          Math.abs(rRx - tRx) > 0.02 || Math.abs(rRy - tRy) > 0.02;
        rafId = (hovering || moving) ? requestAnimationFrame(tickHover) : 0;
      }

      function tickReset() {
        tRx = 0; tRy = 0; tMx = 50; tMy = 50;
        rRx = lerp(rRx, 0, 0.13);
        rRy = lerp(rRy, 0, 0.13);
        rMx = lerp(rMx, 50, 0.13);
        rMy = lerp(rMy, 50, 0.13);
        card.style.transform =
          `perspective(900px) rotateX(${rRx}deg) rotateY(${rRy}deg)`;
        card.style.setProperty('--mx', `${rMx}%`);
        card.style.setProperty('--my', `${rMy}%`);
        if (Math.abs(rRx) > 0.03 || Math.abs(rRy) > 0.03) {
          rafId = requestAnimationFrame(tickReset);
        } else {
          card.style.transform = '';
          card.style.removeProperty('--mx');
          card.style.removeProperty('--my');
          rafId = 0;
        }
      }

      const onEnter = () => {
        hovering = true;
        if (!rafId) rafId = requestAnimationFrame(tickHover);
      };

      const onMove = e => {
        const r  = card.getBoundingClientRect();
        const x  = (e.clientX - r.left) / r.width;
        const y  = (e.clientY - r.top)  / r.height;
        tRx = clamp((0.5 - y) * 18, -9, 9);
        tRy = clamp((x - 0.5) * 18, -9, 9);
        tMx = x * 100;
        tMy = y * 100;
      };

      const onLeave = () => {
        hovering = false;
        cancelAnimationFrame(rafId);
        rafId = requestAnimationFrame(tickReset);
      };

      card.addEventListener('mouseenter', onEnter);
      card.addEventListener('mousemove',  onMove);
      card.addEventListener('mouseleave', onLeave);

      kills.push(() => {
        cancelAnimationFrame(rafId);
        card.removeEventListener('mouseenter', onEnter);
        card.removeEventListener('mousemove',  onMove);
        card.removeEventListener('mouseleave', onLeave);
        card.style.transform = '';
        card.style.removeProperty('--mx');
        card.style.removeProperty('--my');
      });
    });

    return () => kills.forEach(fn => fn());
  }

  /* ═══════════════════════════════════════════════════════
     3. HUD 角括号注入
        每张卡片四角各插入一个 span.cn-corner--xx
        CSS hover 时 opacity 0→1 + scale 0.35→1
  ═══════════════════════════════════════════════════════ */
  function initCorners() {
    document.querySelectorAll('.md-typeset .grid.cards > ul > li').forEach(card => {
      if (card.querySelector('.cn-corner')) return;  /* 避免重复注入 */
      ['tl', 'tr', 'bl', 'br'].forEach(pos => {
        const s = document.createElement('span');
        s.className = `cn-corner cn-corner--${pos}`;
        card.appendChild(s);
      });
    });
  }

  /* ═══════════════════════════════════════════════════════
     4. 主标题 Glitch 周期触发
        页面加载后立即触发一次，之后每 5–10 秒随机触发
  ═══════════════════════════════════════════════════════ */
  function initGlitch() {
    const title = document.querySelector('.hero-title');
    if (!title) return null;

    function fire() {
      title.classList.add('cn-glitch');
      setTimeout(() => title.classList.remove('cn-glitch'), 230);
    }

    fire();  /* 首次立即触发 */
    const schedule = () => setTimeout(() => { fire(); schedule(); }, rnd(5000, 10000));
    const tid = schedule();

    return () => clearTimeout(tid);
  }

  /* ═══════════════════════════════════════════════════════
     5. 滚动揭示（IntersectionObserver）
        目标元素初始 .--hidden，进入视口后切换 .--revealed
  ═══════════════════════════════════════════════════════ */
  function initReveal() {
    const sel = [
      '.md-typeset h2',
      '.md-typeset h3',
      '.md-typeset .admonition',
      '.md-typeset details',
      '.md-typeset table',
      '.contribute-box',
    ].join(',');

    const els = document.querySelectorAll(sel);
    if (!els.length) return null;

    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        e.target.classList.remove('--hidden');
        e.target.classList.add('--revealed');
        obs.unobserve(e.target);
      });
    }, { threshold: 0.10 });

    els.forEach(el => { el.classList.add('--hidden'); obs.observe(el); });

    return () => obs.disconnect();
  }

  /* ═══════════════════════════════════════════════════════
     6. 代码块终端语言标签
        读取 <code> 的 language-xxx 类，注入 "> LANG" 标签
  ═══════════════════════════════════════════════════════ */
  function initCodeLabels() {
    document.querySelectorAll('.md-typeset pre').forEach(pre => {
      const code = pre.querySelector('code');
      if (!code) return;
      const lang = [...code.classList]
        .find(c => c.startsWith('language-'))
        ?.replace('language-', '');
      if (!lang) return;
      /* 注入到不滚动的父容器 .highlight，避免与代码内容重叠 */
      const wrapper = pre.closest('.highlight') || pre.parentElement;
      if (wrapper.querySelector('.cn-label')) return;
      wrapper.style.position = 'relative';
      const span = document.createElement('span');
      span.className   = 'cn-label';
      span.textContent = `> ${lang.toUpperCase()}`;
      wrapper.appendChild(span);
    });
  }

  /* ═══════════════════════════════════════════════════════
     7. 主题切换开关 — UIverse Galahhad/strong-squid-82
        day/night toggle with clouds & stars animation
        Syncs with MkDocs Material palette radio inputs
  ═══════════════════════════════════════════════════════ */
  function initThemeSwitch() {
    document.querySelector('.cn-theme-switch')?.remove();

    const palette = document.querySelector('[data-md-component="palette"]');
    if (!palette) return null;

    const wrapper = document.createElement('div');
    wrapper.className = 'cn-theme-switch';
    wrapper.innerHTML = `<label class="theme-switch">
  <input type="checkbox" class="theme-switch__checkbox">
  <div class="theme-switch__container">
    <div class="theme-switch__clouds"></div>
    <div class="theme-switch__stars-container">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 144 55" fill="none">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M135.831 3.00688C135.055 3.85027 134.111 4.29946 133 4.35447C134.111 4.40947 135.055 4.85867 135.831 5.71123C136.607 6.55462 136.996 7.56303 136.996 8.72727C136.996 7.95722 137.172 7.25134 137.525 6.59129C137.886 5.93124 138.372 5.39954 138.98 5.00535C139.598 4.60199 140.268 4.39114 141 4.35447C139.88 4.2903 138.936 3.85027 138.16 3.00688C137.384 2.16348 136.996 1.16425 136.996 0C136.996 1.16425 136.607 2.16348 135.831 3.00688ZM31 23.3545C32.1114 23.2995 33.0551 22.8503 33.8313 22.0069C34.6075 21.1635 34.9956 20.1642 34.9956 19C34.9956 20.1642 35.3837 21.1635 36.1599 22.0069C36.9361 22.8503 37.8798 23.2903 39 23.3545C38.2679 23.3911 37.5976 23.602 36.9802 24.0053C36.3716 24.3995 35.8864 24.9312 35.5248 25.5913C35.172 26.2513 34.9956 26.9572 34.9956 27.7273C34.9956 26.563 34.6075 25.5546 33.8313 24.7112C33.0551 23.8587 32.1114 23.4095 31 23.3545ZM0 36.3545C1.11136 36.2995 2.05513 35.8503 2.83131 35.0069C3.6075 34.1635 3.99559 33.1642 3.99559 32C3.99559 33.1642 4.38368 34.1635 5.15987 35.0069C5.93605 35.8503 6.87982 36.2903 8 36.3545C7.26792 36.3911 6.59757 36.602 5.98015 37.0053C5.37155 37.3995 4.88644 37.9312 4.52481 38.5913C4.172 39.2513 3.99559 39.9572 3.99559 40.7273C3.99559 39.563 3.6075 38.5546 2.83131 37.7112C2.05513 36.8587 1.11136 36.4095 0 36.3545ZM56.8313 24.0069C56.0551 24.8503 55.1114 25.2995 54 25.3545C55.1114 25.4095 56.0551 25.8587 56.8313 26.7112C57.6075 27.5546 57.9956 28.563 57.9956 29.7273C57.9956 28.9572 58.172 28.2513 58.5248 27.5913C58.8864 26.9312 59.3716 26.3995 59.9802 26.0053C60.5976 25.602 61.2679 25.3911 62 25.3545C60.8798 25.2903 59.9361 24.8503 59.1599 24.0069C58.3837 23.1635 57.9956 22.1642 57.9956 21C57.9956 22.1642 57.6075 23.1635 56.8313 24.0069ZM81 25.3545C82.1114 25.2995 83.0551 24.8503 83.8313 24.0069C84.6075 23.1635 84.9956 22.1642 84.9956 21C84.9956 22.1642 85.3837 23.1635 86.1599 24.0069C86.9361 24.8503 87.8798 25.2903 89 25.3545C88.2679 25.3911 87.5976 25.602 86.9802 26.0053C86.3716 26.3995 85.8864 26.9312 85.5248 27.5913C85.172 28.2513 84.9956 28.9572 84.9956 29.7273C84.9956 28.563 84.6075 27.5546 83.8313 26.7112C83.0551 25.8587 82.1114 25.4095 81 25.3545ZM136 36.3545C137.111 36.2995 138.055 35.8503 138.831 35.0069C139.607 34.1635 139.996 33.1642 139.996 32C139.996 33.1642 140.384 34.1635 141.16 35.0069C141.936 35.8503 142.88 36.2903 144 36.3545C143.268 36.3911 142.598 36.602 141.98 37.0053C141.372 37.3995 140.886 37.9312 140.525 38.5913C140.172 39.2513 139.996 39.9572 139.996 40.7273C139.996 39.563 139.607 38.5546 138.831 37.7112C138.055 36.8587 137.111 36.4095 136 36.3545ZM101.831 49.0069C101.055 49.8503 100.111 50.2995 99 50.3545C100.111 50.4095 101.055 50.8587 101.831 51.7112C102.607 52.5546 102.996 53.563 102.996 54.7273C102.996 53.9572 103.172 53.2513 103.525 52.5913C103.886 51.9312 104.372 51.3995 104.98 51.0053C105.598 50.602 106.268 50.3911 107 50.3545C105.88 50.2903 104.936 49.8503 104.16 49.0069C103.384 48.1635 102.996 47.1642 102.996 46C102.996 47.1642 102.607 48.1635 101.831 49.0069Z" fill="currentColor"></path>
      </svg>
    </div>
    <div class="theme-switch__circle-container">
      <div class="theme-switch__sun-moon-container">
        <div class="theme-switch__moon">
          <div class="theme-switch__spot"></div>
          <div class="theme-switch__spot"></div>
          <div class="theme-switch__spot"></div>
        </div>
      </div>
    </div>
  </div>
</label>`;

    palette.parentNode.insertBefore(wrapper, palette);

    const cb = wrapper.querySelector('.theme-switch__checkbox');

    function syncCheckbox() {
      cb.checked = document.documentElement.getAttribute('data-md-color-scheme') === 'slate';
    }
    syncCheckbox();

    function onToggle() {
      const targetScheme = cb.checked ? 'slate' : 'default';
      const inp = palette.querySelector(`input[data-md-color-scheme="${targetScheme}"]`);
      if (inp) inp.click();
    }
    cb.addEventListener('change', onToggle);

    const mo = new MutationObserver(syncCheckbox);
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-md-color-scheme'] });

    return () => {
      cb.removeEventListener('change', onToggle);
      mo.disconnect();
      wrapper.remove();
    };
  }

  /* ═══════════════════════════════════════════════════════
     主入口 — MkDocs Material SPA 兼容
     document$ 是 Material 注入的 RxJS Observable，
     每次 SPA 导航后发射新文档；不存在则降级到 DOMContentLoaded
  ═══════════════════════════════════════════════════════ */
  let cleanups = [];

  function boot() {
    cleanups.forEach(fn => fn?.());
    cleanups = [];

    /* 等待一帧，确保 DOM 已完整渲染 */
    requestAnimationFrame(() => {
      const c1 = initHero();
      const c2 = initTilt();
      const c3 = initGlitch();
      const c4 = initReveal();
      const c5 = initThemeSwitch();
      initCorners();
      initCodeLabels();
      if (c1) cleanups.push(c1);
      if (c2) cleanups.push(c2);
      if (c3) cleanups.push(c3);
      if (c4) cleanups.push(c4);
      if (c5) cleanups.push(c5);
    });
  }

  if (typeof document$ !== 'undefined') {
    document$.subscribe(boot);
  } else if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();

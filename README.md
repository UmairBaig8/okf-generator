<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>okf-generator — the knowledge layer for AI coding agents</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 26 26'%3E%3Crect width='26' height='26' rx='6' fill='%23e3b341'/%3E%3Ccircle cx='7.5' cy='8' r='2' fill='%230b0e13'/%3E%3Ccircle cx='18.5' cy='8' r='2' fill='%230b0e13'/%3E%3Ccircle cx='13' cy='18' r='2' fill='%230b0e13'/%3E%3Cpath d='M8.8 9.2 L11.6 16.6 M17.2 9.2 L14.4 16.6 M9.5 8 H16.5' stroke='%230b0e13' stroke-width='1.1' stroke-linecap='round'/%3E%3C/svg%3E">
<meta name="theme-color" content="#0b0e13">
<meta name="description" content="okf-generator turns any codebase into a structured, agent-readable knowledge bundle. 10 languages, 17 manifest formats, zero LLM required.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0b0e13;
    --surface:#12161f;
    --surface-2:#171c27;
    --border:#232a38;
    --text:#e7ebf1;
    --text-dim:#8b93a3;
    --text-faint:#7b8494;
    --border-interactive:#5b6680;
    --amber:#e3b341;
    --amber-dim:#8a6a26;
    --blue:#5aa6ff;
    --green:#5fd88f;
    --mono:'JetBrains Mono',ui-monospace,Menlo,monospace;
    --sans:'Inter',-apple-system,BlinkMacSystemFont,sans-serif;
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  html{scroll-behavior:smooth;}
  body{
    background:var(--bg);
    color:var(--text);
    font-family:var(--sans);
    line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }
  ::selection{background:var(--amber);color:#0b0e13;}
  a{color:inherit;text-decoration:none;}
  img,svg{display:block;max-width:100%;}

  /* WCAG 2.4.7 — visible focus indicator on every interactive element */
  a:focus-visible, button:focus-visible, summary:focus-visible, [tabindex]:focus-visible{
    outline:2px solid var(--amber);
    outline-offset:3px;
    border-radius:4px;
  }

  /* WCAG 2.3.3 / 2.2.2 — honor OS-level reduced-motion preference by default */
  @media (prefers-reduced-motion: reduce){
    html{scroll-behavior:auto;}
    .term-body .cursor, .hero-visual svg *{animation:none !important;}
  }
  body.motion-paused .term-body .cursor{animation:none !important; opacity:1;}

  .skip-link{
    position:absolute; left:16px; top:-60px; z-index:100;
    background:var(--amber); color:#0b0e13; font-weight:600; font-size:14px;
    padding:10px 16px; border-radius:6px; transition:top .15s ease;
  }
  .skip-link:focus{top:16px;}

  .sr-only{
    position:absolute; width:1px; height:1px; padding:0; margin:-1px;
    overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0;
  }

  /* faint dot-grid backdrop, like a code minimap */
  body::before{
    content:'';
    position:fixed; inset:0;
    background-image: radial-gradient(circle, #1c2330 1px, transparent 1px);
    background-size: 28px 28px;
    opacity:.5;
    pointer-events:none;
    z-index:0;
  }

  .wrap{max-width:min(1520px, 94vw); margin:0 auto; padding:0 32px; position:relative; z-index:1;}

  /* ---------- Nav ---------- */
  header{
    position:sticky; top:0; z-index:50;
    background:rgba(11,14,19,.82);
    backdrop-filter:blur(10px);
    border-bottom:1px solid var(--border);
  }
  nav{display:flex; align-items:center; justify-content:space-between; padding:16px 32px; max-width:min(1520px, 94vw); margin:0 auto;}
  .brand{display:flex; align-items:center; gap:10px; font-family:var(--mono); font-weight:700; font-size:15px; letter-spacing:-.02em;}
  .brand .accent{color:var(--amber);}
  .navlinks{display:flex; align-items:center; gap:28px; font-size:14px; color:var(--text-dim);}
  .navlinks a:hover{color:var(--text);}
  .navlinks .ver{
    font-family:var(--mono); font-size:12px; color:var(--amber);
    border:1px solid var(--amber-dim); background:rgba(227,179,65,.08);
    padding:3px 8px; border-radius:99px;
  }
  .navlinks .btn-nav{
    border:1px solid var(--border-interactive); padding:7px 14px; border-radius:6px;
    color:var(--text); font-size:13px;
  }
  .navlinks .btn-nav:hover{border-color:var(--amber-dim); background:var(--surface-2);}
  @media (max-width:720px){ .navlinks a:not(.btn-nav):not(.ver){display:none;} }

  /* ---------- Hero ---------- */
  .hero{padding:88px 0 64px;}
  .hero-grid{display:grid; grid-template-columns:1.1fr .9fr; gap:48px; align-items:center;}
  @media (max-width:980px){ .hero-grid{grid-template-columns:1fr;} .hero-visual{display:none;} }
  .hero-visual{position:relative;}
  .hero-visual svg{width:100%; height:auto;}
  .eyebrow{
    font-family:var(--mono); font-size:12.5px; color:var(--amber);
    text-transform:uppercase; letter-spacing:.12em; margin-bottom:18px;
    display:flex; align-items:center; gap:8px;
  }
  .eyebrow::before{content:''; width:7px; height:7px; border-radius:50%; background:var(--green); box-shadow:0 0 8px var(--green);}
  h1{
    font-family:var(--mono); font-weight:700; letter-spacing:-.02em;
    font-size:clamp(32px,5vw,54px); line-height:1.12; max-width:820px;
  }
  h1 .accent{color:var(--amber);}
  .lede{
    margin-top:22px; font-size:18px; color:var(--text-dim); max-width:600px; line-height:1.65;
  }
  .lede code{font-family:var(--mono); color:var(--blue); font-size:16px;}
  .cta-row{display:flex; flex-wrap:wrap; gap:14px; margin-top:34px;}
  .btn{
    font-family:var(--sans); font-weight:600; font-size:14.5px;
    padding:12px 20px; border-radius:8px; display:inline-flex; align-items:center; gap:8px;
    transition:transform .12s ease, background .12s ease, border-color .12s ease;
  }
  .btn:hover{transform:translateY(-1px);}
  .btn-primary{background:var(--amber); color:#0b0e13;}
  .btn-primary:hover{background:#f0c463;}
  .btn-secondary{border:1px solid var(--border-interactive); color:var(--text);}
  .btn-secondary:hover{border-color:var(--amber-dim); background:var(--surface-2);}

  /* terminal mock */
  .terminal{
    margin-top:56px;
    background:var(--surface);
    border:1px solid var(--border);
    border-radius:12px;
    overflow:hidden;
    box-shadow:0 24px 60px -20px rgba(0,0,0,.6);
    max-width:760px;
  }
  .term-bar{
    display:flex; align-items:center; gap:8px;
    padding:12px 16px; border-bottom:1px solid var(--border); background:var(--surface-2);
  }
  .term-dot{width:10px; height:10px; border-radius:50%;}
  .term-dot.r{background:#ff5f57;} .term-dot.y{background:#febc2e;} .term-dot.g{background:#28c840;}
  .term-title{margin-left:8px; font-family:var(--mono); font-size:12px; color:var(--text-faint);}
  .motion-toggle{
    margin-left:auto; font-family:var(--mono); font-size:11px; color:var(--text-faint);
    background:transparent; border:1px solid var(--border-interactive); border-radius:5px;
    padding:4px 9px; cursor:pointer;
  }
  .motion-toggle:hover{color:var(--text); border-color:var(--amber-dim);}
  .term-body{
    padding:20px 22px; font-family:var(--mono); font-size:13.5px; line-height:1.9;
    color:#c7ceda; overflow-x:auto; min-height:242px;
  }
  .term-body .prompt{color:var(--green);}
  .term-body .cmd{color:var(--text);}
  .term-body .out{color:var(--text-faint);}
  .term-body .hl{color:var(--amber);}
  .term-body .cursor{
    display:inline-block; width:7px; height:15px; background:var(--amber);
    animation:blink 1.1s steps(1) infinite; vertical-align:middle; margin-left:2px;
  }
  @keyframes blink{50%{opacity:0;}}

  /* ---------- Section shared ---------- */
  section{padding:88px 0 84px; border-top:1px solid var(--border);}
  section:first-of-type{border-top:none;}
  section:nth-of-type(even){background:linear-gradient(180deg,var(--surface) 0%, var(--bg) 100%);}
  .section-head{max-width:600px; margin-bottom:44px; margin-top:4px;}
  .section-tag{font-family:var(--mono); font-size:12px; color:var(--amber); text-transform:uppercase; letter-spacing:.1em; margin-bottom:12px;}
  h2{font-family:var(--mono); font-size:clamp(24px,3.4vw,32px); letter-spacing:-.01em; margin-bottom:14px;}
  .section-sub{color:var(--text-dim); font-size:15.5px;}

  /* ---------- Before / after ---------- */
  .compare{display:grid; grid-template-columns:1fr auto 1fr; gap:20px; align-items:center;}
  @media (max-width:800px){ .compare{grid-template-columns:1fr;} .compare .arrow{transform:rotate(90deg); margin:0 auto;} }
  .compare-card{
    background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:24px;
  }
  .compare-card.before{border-color:#3a2a22;}
  .compare-card.after{border-color:#233a2c;}
  .compare-label{font-family:var(--mono); font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:14px;}
  .compare-card.before .compare-label{color:#e0764f;}
  .compare-card.after .compare-label{color:var(--green);}
  .compare-fake-line{height:8px; border-radius:2px; background:var(--surface-2); margin-bottom:8px;}
  .compare-stat{font-family:var(--mono); font-weight:700; font-size:26px; margin-top:16px;}
  .compare-card.before .compare-stat{color:#e0764f;}
  .compare-card.after .compare-stat{color:var(--green);}
  .compare-stat-label{color:var(--text-faint); font-size:13px; margin-top:2px;}
  .arrow{color:var(--text-faint); font-size:22px;}
  .after-card-inner{font-family:var(--mono); font-size:12.5px; color:#a9c6ff; line-height:1.85;}

  /* ---------- Steps ---------- */
  .steps{display:grid; grid-template-columns:repeat(3,1fr); gap:20px;}
  @media (max-width:800px){ .steps{grid-template-columns:1fr;} }
  .step{background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:26px;}
  .step-num{font-family:var(--mono); color:var(--amber-dim); font-size:13px; margin-bottom:14px;}
  .step h3{font-size:16.5px; margin-bottom:8px; font-weight:600;}
  .step p{color:var(--text-dim); font-size:14px;}
  .step code{font-family:var(--mono); background:var(--surface-2); padding:1px 6px; border-radius:4px; font-size:12.5px; color:var(--blue);}

  /* ---------- Languages ---------- */
  .pill-grid{display:flex; flex-wrap:wrap; gap:10px;}
  .pill{
    font-family:var(--mono); font-size:13px; padding:8px 14px; border-radius:99px;
    border:1px solid var(--border); background:var(--surface); color:var(--text-dim);
  }
  .manifest-strip{
    margin-top:28px; font-family:var(--mono); font-size:12.5px; color:var(--text-faint);
    line-height:2.1; word-spacing:2px;
  }
  .manifest-strip span{color:var(--text-dim); border-bottom:1px dotted var(--border);}

  /* ---------- Feature grid ---------- */
  .feat-grid{display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--border); border:1px solid var(--border); border-radius:10px; overflow:hidden;}
  @media (max-width:900px){ .feat-grid{grid-template-columns:repeat(2,1fr);} .tree-flex{grid-template-columns:1fr !important;} }
  @media (max-width:560px){ .feat-grid{grid-template-columns:1fr;} }

  /* ---------- MCP callout ---------- */
  .mcp-callout{
    display:grid; grid-template-columns:1.2fr 1fr; gap:0;
    background:var(--surface); border:1px solid var(--amber-dim); border-radius:12px;
    overflow:hidden; margin-bottom:28px;
  }
  @media (max-width:800px){ .mcp-callout{grid-template-columns:1fr;} }
  .mcp-callout-text{padding:30px 32px;}
  .mcp-badge{
    font-family:var(--mono); font-size:11px; letter-spacing:.1em; color:var(--amber);
    border:1px solid var(--amber-dim); background:rgba(227,179,65,.08);
    display:inline-block; padding:4px 10px; border-radius:99px; margin-bottom:14px;
  }
  .mcp-callout-text h3{font-size:19px; margin-bottom:10px; font-weight:600;}
  .mcp-callout-text p{color:var(--text-dim); font-size:14.5px;}
  .mcp-callout-text code{font-family:var(--mono); color:var(--blue); background:var(--surface-2); padding:1px 6px; border-radius:4px; font-size:13px;}
  .mcp-callout-code{
    background:var(--surface-2); padding:30px 28px; font-family:var(--mono); font-size:13px;
    display:flex; flex-direction:column; justify-content:center; line-height:2;
  }

  /* ---------- Agent install grid ---------- */
  .install-grid{display:grid; grid-template-columns:repeat(3,1fr); gap:12px;}
  @media (max-width:700px){ .install-grid{grid-template-columns:repeat(2,1fr);} }
  @media (max-width:460px){ .install-grid{grid-template-columns:1fr;} }
  .install-cell{
    background:var(--surface); border:1px solid var(--border); border-radius:8px;
    padding:14px 16px; display:flex; flex-direction:column; gap:4px;
  }
  .install-cell code{font-family:var(--mono); font-size:13px; color:var(--amber);}
  .install-cell span{color:var(--text-faint); font-size:12px;}

  /* ---------- Local AI section ---------- */
  .local-ai-grid{display:grid; grid-template-columns:1.1fr .9fr; gap:40px; align-items:center;}
  @media (max-width:900px){ .local-ai-grid{grid-template-columns:1fr;} }

  /* ---------- Install alternates ---------- */
  .install-alt{display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-top:16px;}
  @media (max-width:700px){ .install-alt{grid-template-columns:1fr;} }
  .install-alt-label{display:block; font-size:12px; color:var(--text-faint); margin-bottom:6px;}
  .install-alt code{
    display:block; font-family:var(--mono); font-size:12.5px; color:var(--blue);
    background:var(--surface); border:1px solid var(--border); border-radius:8px;
    padding:12px 14px; overflow-x:auto; white-space:nowrap;
  }

  /* ---------- Comparison table ---------- */
  .compare-table{width:100%; border-collapse:collapse; font-size:14px; background:var(--surface); border:1px solid var(--border); border-radius:10px; overflow:hidden;}
  .compare-table th, .compare-table td{padding:13px 16px; text-align:left; border-bottom:1px solid var(--border);}
  .compare-table th{font-family:var(--mono); font-size:12px; color:var(--text-faint); text-transform:uppercase; letter-spacing:.04em; background:var(--surface-2);}
  .compare-table th:first-child{background:transparent;}
  .compare-table td:first-child{color:var(--text-dim); font-size:13.5px;}
  .compare-table tr:last-child td{border-bottom:none;}
  .compare-table td.yes{color:var(--green);}
  .compare-table td.no{color:#e0764f;}
  .compare-table td.warn{color:var(--amber);}
  @media (max-width:700px){ .compare-table{font-size:12.5px;} .compare-table th, .compare-table td{padding:10px 8px;} }

  /* ---------- FAQ accordion ---------- */
  .faq-list details{
    border:1px solid var(--border); border-radius:8px; padding:16px 20px; margin-bottom:10px;
    background:var(--surface);
  }
  .faq-list summary{
    cursor:pointer; font-weight:600; font-size:15px; color:var(--text);
    list-style:none; display:flex; justify-content:space-between; align-items:center;
  }
  .faq-list summary::-webkit-details-marker{display:none;}
  .faq-list summary::after{content:'+'; font-family:var(--mono); color:var(--amber); font-size:18px;}
  .faq-list details[open] summary::after{content:'–';}
  .faq-list p{color:var(--text-dim); font-size:14px; margin-top:12px; line-height:1.65;}
  .faq-list code{font-family:var(--mono); color:var(--blue); background:var(--surface-2); padding:1px 6px; border-radius:4px; font-size:12.5px;}
  .feat{background:var(--surface); padding:26px;}
  .feat .icon{font-family:var(--mono); color:var(--amber); font-size:18px; margin-bottom:14px;}
  .feat h3{font-size:15.5px; margin-bottom:8px; font-weight:600;}
  .feat p{color:var(--text-dim); font-size:13.5px;}

  /* ---------- CLI table ---------- */
  .cli-table{width:100%; border-collapse:collapse; font-size:14px;}
  .cli-table td{padding:12px 0; border-bottom:1px solid var(--border); vertical-align:top;}
  .cli-table td:first-child{font-family:var(--mono); color:var(--amber); white-space:nowrap; padding-right:24px; font-size:13.5px;}
  .cli-table td:last-child{color:var(--text-dim);}
  .cli-table tr:last-child td{border-bottom:none;}

  /* ---------- Install ---------- */
  .install-box{
    background:var(--surface); border:1px solid var(--border); border-radius:10px;
    padding:20px 24px; display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;
  }
  .install-box code{font-family:var(--mono); color:var(--green); font-size:14.5px;}
  .copy-btn{
    font-family:var(--mono); font-size:12px; border:1px solid var(--border-interactive); color:var(--text-dim);
    padding:7px 12px; border-radius:6px; cursor:pointer; background:transparent;
  }
  .copy-btn:hover{border-color:var(--amber-dim); color:var(--text);}

  /* ---------- Footer ---------- */
  footer{border-top:1px solid var(--border); padding:40px 0; color:var(--text-faint); font-size:13px;}
  .foot-row{display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;}
  .foot-links{display:flex; gap:20px;}
  .foot-links a:hover{color:var(--text-dim);}
</style>
</head>
<body>
<a class="skip-link" href="#main-content">Skip to main content</a>

<header>
  <nav>
    <div class="brand">
      <svg class="brand-mark" width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="border-radius:6px;">
        <rect width="26" height="26" rx="6" fill="url(#bmg)"/>
        <circle cx="7.5" cy="8" r="2" fill="#0b0e13"/>
        <circle cx="18.5" cy="8" r="2" fill="#0b0e13"/>
        <circle cx="13" cy="18" r="2" fill="#0b0e13"/>
        <path d="M8.8 9.2 L11.6 16.6 M17.2 9.2 L14.4 16.6 M9.5 8 H16.5" stroke="#0b0e13" stroke-width="1.1" stroke-linecap="round"/>
        <defs><linearGradient id="bmg" x1="0" y1="0" x2="26" y2="26"><stop stop-color="#f0c463"/><stop offset="1" stop-color="#b5842a"/></linearGradient></defs>
      </svg>
      <span>okf<span class="accent">-generator</span></span>
    </div>
    <div class="navlinks">
      <a href="#how">How it works</a>
      <a href="#agents">Agents</a>
      <a href="#languages">Languages</a>
      <a href="#features">Features</a>
      <a href="#cli">CLI</a>
      <span class="ver">v0.1.29</span>
      <a class="btn-nav" href="https://github.com/UmairBaig8/okf-generator" target="_blank" rel="noopener">★ <span id="star-count-nav">—</span><span class="sr-only"> GitHub (opens in new tab)</span></a>
    </div>
  </nav>
</header>

<main id="main-content" tabindex="-1">
  <section class="hero wrap" style="border-top:none;">
    <div class="hero-grid">
      <div class="hero-left">
    <div class="eyebrow">MIT licensed · OKF v0.1 conformant · zero LLM required</div>
    <h1>Stop feeding your AI agent<br>the <span class="accent">whole codebase.</span></h1>
    <p class="lede">
      Scans any repo, outputs one markdown file per function, class, module, and dependency.
      Your agent runs <code>okf lookup &lt;Name&gt;</code> instead of re-reading 600 lines to find
      one signature. No LLM required to build it.
    </p>
    <div class="cta-row">
      <a class="btn btn-primary" href="#install">pip install okf-generator</a>
      <a class="btn btn-secondary" href="https://github.com/UmairBaig8/okf-generator" target="_blank" rel="noopener">
        View source <span id="star-count-hero" style="color:var(--amber); font-family:var(--mono);"></span> ↗<span class="sr-only"> (opens in new tab)</span>
      </a>
    </div>

    <div class="terminal">
      <div class="term-bar">
        <span class="term-dot r"></span><span class="term-dot y"></span><span class="term-dot g"></span>
        <span class="term-title">~/my_project</span>
        <button type="button" id="motion-toggle" class="motion-toggle" aria-pressed="false">
          <span id="motion-toggle-label">Pause animation</span>
        </button>
      </div>
      <div class="term-body" id="term-live" aria-hidden="true"></div>
    </div>
      </div>

      <div class="hero-visual">
        <svg viewBox="0 0 420 460" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <defs>
            <radialGradient id="glow" cx="50%" cy="35%" r="65%">
              <stop offset="0%" stop-color="#e3b341" stop-opacity=".14"/>
              <stop offset="100%" stop-color="#e3b341" stop-opacity="0"/>
            </radialGradient>
          </defs>
          <circle cx="210" cy="180" r="210" fill="url(#glow)"/>

          <!-- edges: source files -> bundle -> agent -->
          <g stroke="#2a3040" stroke-width="1.4">
            <line x1="70" y1="70" x2="205" y2="180" id="e1"/>
            <line x1="70" y1="150" x2="205" y2="180" id="e2"/>
            <line x1="70" y1="230" x2="205" y2="180" id="e3"/>
            <line x1="70" y1="300" x2="205" y2="180" id="e4"/>
            <line x1="205" y1="180" x2="340" y2="120" id="e5"/>
            <line x1="205" y1="180" x2="340" y2="200" id="e6"/>
            <line x1="205" y1="180" x2="340" y2="280" id="e7"/>
          </g>

          <!-- left: raw source file nodes -->
          <g font-family="JetBrains Mono, monospace" font-size="10" fill="#5b6376">
            <circle cx="70" cy="70" r="5" fill="#232a38" stroke="#3a4256"/>
            <text x="82" y="74">connectors.py</text>
            <circle cx="70" cy="150" r="5" fill="#232a38" stroke="#3a4256"/>
            <text x="82" y="154">models.py</text>
            <circle cx="70" cy="230" r="5" fill="#232a38" stroke="#3a4256"/>
            <text x="82" y="234">server.go</text>
            <circle cx="70" cy="300" r="5" fill="#232a38" stroke="#3a4256"/>
            <text x="82" y="304">schema.sql</text>
          </g>

          <!-- center: bundle node -->
          <g>
            <circle cx="205" cy="180" r="30" fill="#171c27" stroke="#e3b341" stroke-width="1.6"/>
            <circle cx="205" cy="180" r="30" fill="none" stroke="#e3b341" stroke-width="1.6" opacity=".4">
              <animate attributeName="r" values="30;40;30" dur="3.2s" repeatCount="indefinite"/>
              <animate attributeName="opacity" values=".4;0;.4" dur="3.2s" repeatCount="indefinite"/>
            </circle>
            <text x="205" y="176" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="10" fill="#e3b341" font-weight="700">okf</text>
            <text x="205" y="189" text-anchor="middle" font-family="JetBrains Mono, monospace" font-size="9" fill="#e3b341">bundle</text>
          </g>

          <!-- right: agent lookups -->
          <g font-family="JetBrains Mono, monospace" font-size="10" fill="#8b93a3">
            <rect x="340" y="108" width="14" height="14" rx="3" fill="#12161f" stroke="#3a4256"/>
            <text x="362" y="120">Claude Code</text>
            <rect x="340" y="188" width="14" height="14" rx="3" fill="#12161f" stroke="#3a4256"/>
            <text x="362" y="200">Cursor</text>
            <rect x="340" y="268" width="14" height="14" rx="3" fill="#12161f" stroke="#3a4256"/>
            <text x="362" y="280">OpenCode</text>
          </g>

          <!-- bottom: stat callout -->
          <g transform="translate(70,380)">
            <text font-family="JetBrains Mono, monospace" font-size="26" font-weight="700" fill="#5fd88f">~140</text>
            <text y="20" font-family="Inter, sans-serif" font-size="12" fill="#5b6376">tokens per lookup, not 14,000</text>
          </g>
        </svg>
      </div>
    </div>
  </section>

  <section id="why">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">The problem</div>
      <h2>Reading a whole file to find one function is expensive</h2>
      <p class="section-sub">Cloud models with huge context windows hide this cost. Local models on a laptop run out of memory immediately.</p>
    </div>
    <div class="compare">
      <div class="compare-card before">
        <div class="compare-label">Before — entire file as context</div>
        <div class="compare-fake-line" style="width:92%"></div>
        <div class="compare-fake-line" style="width:78%"></div>
        <div class="compare-fake-line" style="width:88%"></div>
        <div class="compare-fake-line" style="width:60%"></div>
        <div class="compare-fake-line" style="width:84%"></div>
        <div class="compare-fake-line" style="width:70%"></div>
        <div class="compare-stat">~14,000</div>
        <div class="compare-stat-label">tokens to find one 12-line method</div>
      </div>
      <div class="arrow">→</div>
      <div class="compare-card after">
        <div class="compare-label">After — exact concept only</div>
        <div class="after-card-inner">
CLASS: WorldBankConnector<br>
Description: Fetches World Bank<br>
&nbsp;&nbsp;development indicators.<br>
Methods: get_indicator, search<br>
Signature: class WorldBankConnector
        </div>
        <div class="compare-stat">~140</div>
        <div class="compare-stat-label">tokens. exact answer, zero guessing.</div>
      </div>
    </div>
  </div>
  </section>

  <section id="how">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">The pipeline</div>
      <h2>Three commands, one workflow</h2>
      <p class="section-sub">Generate once. Look up forever. Regenerate whenever the code changes.</p>
    </div>
    <div class="steps">
      <div class="step">
        <div class="step-num">01 — scan</div>
        <h3>okf generate</h3>
        <p>Tree-sitter and native AST parsers walk the repo and extract every function, class, module, and manifest dependency, with cross-referenced calls and imports.</p>
      </div>
      <div class="step">
        <div class="step-num">02 — retrieve</div>
        <h3>okf lookup</h3>
        <p>Instant, zero-LLM concept search by name, type, tag, or file. Returns signature, docstring, params, callers, and callees in milliseconds.</p>
      </div>
      <div class="step">
        <div class="step-num">03 — integrate</div>
        <h3>okf install</h3>
        <p>Wires the bundle into Claude Code, Cursor, Copilot, Windsurf, Cline, or OpenCode so the agent checks the bundle before touching source.</p>
      </div>
    </div>
  </div>
  </section>

  <section id="agents">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">Agent integration</div>
      <h2>Works with the agent you already use</h2>
      <p class="section-sub">One command wires the bundle into your agent's rules. One more exposes it over MCP.</p>
    </div>

    <div class="mcp-callout">
      <div class="mcp-callout-text">
        <div class="mcp-badge">MODEL CONTEXT PROTOCOL</div>
        <h3>Speak MCP? So does the bundle.</h3>
        <p>Run <code>okf mcp ./okf_bundle</code> and any MCP-compatible client — Claude Desktop, Claude Code, or a custom agent — can query the knowledge graph directly, no CLI wrapper needed.</p>
      </div>
      <div class="mcp-callout-code">
        <span class="prompt">$</span> <span class="cmd">okf mcp ./okf_bundle</span><br>
        <span class="out">MCP server listening on stdio…</span>
      </div>
    </div>

    <div class="install-grid">
      <div class="install-cell"><code>okf install claude</code><span>Claude Code skill</span></div>
      <div class="install-cell"><code>okf install cursor</code><span>.cursorrules</span></div>
      <div class="install-cell"><code>okf install opencode</code><span>/lookup command</span></div>
      <div class="install-cell"><code>okf install copilot</code><span>Copilot instructions</span></div>
      <div class="install-cell"><code>okf install windsurf</code><span>.windsurfrules</span></div>
      <div class="install-cell"><code>okf install cline</code><span>.clinerules</span></div>
    </div>
    <p style="margin-top:16px; color:var(--text-faint); font-size:13.5px;">
      Or set up every detected agent at once: <code style="font-family:var(--mono); color:var(--blue);">okf install all</code>
    </p>
    </div>
  </section>

  <section id="local-ai">
    <div class="wrap">
    <div class="local-ai-grid">
      <div>
        <div class="section-tag">Runs on-device too</div>
        <h2>Built for local SLMs, not just the cloud</h2>
        <p class="section-sub" style="margin-bottom:18px;">
          Cloud models mask the cost of huge context windows. Local models — Gemma, Llama, Phi — running
          on a laptop don't have that luxury; feed one the whole repo and it runs out of memory.
          <code style="font-family:var(--mono); color:var(--blue);">okf lookup</code> sends a ~50-token
          query and gets back a ~200-token concept card. No embeddings, no vector DB, no RAG pipeline.
        </p>
      </div>
      <div class="terminal" style="max-width:none;">
        <div class="term-bar">
          <span class="term-dot r"></span><span class="term-dot y"></span><span class="term-dot g"></span>
          <span class="term-title">local llama.cpp</span>
        </div>
        <div class="term-body" style="font-size:12px; line-height:1.85;">
<div class="out">OKF_ENRICH=1 \</div>
<div class="out">OKF_BASE_URL="http://localhost:8080/v1" \</div>
<div class="out">OKF_MODEL="gemma-3-4b-it-qat-GGUF:Q4_0" \</div>
<div><span class="prompt">$</span> <span class="cmd">okf generate ./my_project ./okf_bundle</span></div>
        </div>
      </div>
    </div>
    </div>
  </section>

  <section id="languages">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">Coverage</div>
      <h2>10 languages, 17 manifest formats</h2>
      <p class="section-sub">Deterministic extraction — no LLM call needed to index a codebase.</p>
    </div>
    <div class="pill-grid">
      <span class="pill">Python</span>
      <span class="pill">JavaScript</span>
      <span class="pill">TypeScript</span>
      <span class="pill">Go</span>
      <span class="pill">Java</span>
      <span class="pill">Rust</span>
      <span class="pill">Ruby</span>
      <span class="pill">C</span>
      <span class="pill">C++</span>
      <span class="pill">C#</span>
      <span class="pill">SQL</span>
    </div>
    <div class="manifest-strip">
      <span>requirements.txt</span> · <span>pyproject.toml</span> · <span>poetry.lock</span> · <span>package.json</span> · <span>yarn.lock</span> · <span>pnpm-lock.yaml</span> · <span>Cargo.toml</span> · <span>Cargo.lock</span> · <span>go.mod</span> · <span>go.sum</span> · <span>composer.json</span> · <span>pom.xml</span> · <span>Gemfile</span> · <span>build.gradle</span> · <span>Package.swift</span> · <span>project.clj</span> · <span>mix.exs</span>
    </div>
  </div>
  </section>

  <section id="features">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">What's inside</div>
      <h2>Built for agent workflows, not just documentation</h2>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:32px; margin-bottom:44px; align-items:center;" class="tree-flex">
      <div class="terminal" style="max-width:none;">
        <div class="term-bar">
          <span class="term-dot r"></span><span class="term-dot y"></span><span class="term-dot g"></span>
          <span class="term-title">okf_bundle/</span>
        </div>
        <div class="term-body" style="font-size:12.5px; line-height:1.85;">
<div class="out">okf_bundle/</div>
<div class="out">├── <span class="hl">SUMMARY.md</span> <span class="out">← bird's-eye view</span></div>
<div class="out">├── index.md</div>
<div class="out">├── _dependencies/</div>
<div class="out">│&nbsp;&nbsp;&nbsp;└── pip/npm/cargo/…</div>
<div class="out">└── src/connectors/</div>
<div class="out">&nbsp;&nbsp;&nbsp;&nbsp;├── economic_data.md <span class="out">← Module</span></div>
<div class="out">&nbsp;&nbsp;&nbsp;&nbsp;└── economic_data/</div>
<div class="out">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="cmd">WorldBankConnector.md</span></div>
<div class="out">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── get_indicator.md</div>
        </div>
      </div>
      <div>
        <h3 style="font-size:16.5px; margin-bottom:10px;">Layout mirrors your source tree</h3>
        <p style="color:var(--text-dim); font-size:14.5px; line-height:1.7;">
          No flat <code style="font-family:var(--mono); color:var(--blue);">functions/</code> /
          <code style="font-family:var(--mono); color:var(--blue);">classes/</code> buckets.
          Every concept file sits where its source file sits, plus a domain-organized
          <code style="font-family:var(--mono); color:var(--blue);">_dependencies/</code> tree.
          Diff-friendly, git-friendly, and safe to commit alongside the code it describes.
        </p>
      </div>
    </div>
    <div class="feat-grid">
      <div class="feat"><div class="icon" aria-hidden="true">◆</div><h3>Zero-LLM extraction</h3><p>Tree-sitter + AST parsing. Nothing calls an API unless you turn on enrichment.</p></div>
      <div class="feat"><div class="icon" aria-hidden="true">↔</div><h3>Cross-reference linker</h3><p>Imports → dependencies, calls → callers/callees. Resolved across every supported language.</p></div>
      <div class="feat"><div class="icon" aria-hidden="true">▣</div><h3>Interactive visualizer</h3><p>One HTML file. Tree nav + local graphs. Opens in a browser, no server.</p></div>
      <div class="feat"><div class="icon" aria-hidden="true">⇄</div><h3>Bundle diff</h3><p>Added / removed / changed concepts between two bundle versions, by content hash.</p></div>
      <div class="feat"><div class="icon" aria-hidden="true">⇢</div><h3>MCP server</h3><p><code>okf mcp</code> — bundle over Model Context Protocol, any client.</p></div>
      <div class="feat"><div class="icon" aria-hidden="true">▤</div><h3>Training pairs</h3><p>Bundle → JSONL. codegen, QA, doc, summarize, crosslink pair types.</p></div>
    </div>
  </div>
  </section>

  <section id="cli">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">Reference</div>
      <h2>CLI at a glance</h2>
    </div>
    <table class="cli-table">
      <tr><td>okf generate</td><td>Scan a codebase and write an OKF v0.1 bundle</td></tr>
      <tr><td>okf lookup</td><td>Search the bundle — by name, type, tag, or source file</td></tr>
      <tr><td>okf init</td><td>Interactive bundle setup wizard</td></tr>
      <tr><td>okf diff</td><td>Compare two bundles: added, removed, changed concepts</td></tr>
      <tr><td>okf summarize</td><td>Regenerate the bundle's SUMMARY.md map</td></tr>
      <tr><td>okf visualize</td><td>Generate a self-contained interactive HTML explorer</td></tr>
      <tr><td>okf serve</td><td>Launch a local server and auto-open the visualization</td></tr>
      <tr><td>okf mcp</td><td>Expose the bundle over Model Context Protocol</td></tr>
      <tr><td>okf pairs</td><td>Convert a bundle into JSONL fine-tuning pairs</td></tr>
      <tr><td>okf install</td><td>Wire up Claude Code, Cursor, Copilot, Windsurf, Cline, or OpenCode</td></tr>
    </table>
  </div>
  </section>

  <section id="compare">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">vs. the alternatives</div>
      <h2>Not RAG. Not embeddings. Exact lookup.</h2>
      <p class="section-sub">RAG retrieves by semantic similarity — approximate, and it can miss exact symbols. okf indexes real functions, classes, and dependencies by name.</p>
    </div>
    <table class="compare-table">
      <thead>
        <tr><th></th><th>okf-generator</th><th>RAG / vector search</th><th>Read whole file</th></tr>
      </thead>
      <tbody>
        <tr><td>Zero-LLM required</td><td class="yes">Yes</td><td class="no">No — needs embeddings</td><td class="yes">Yes</td></tr>
        <tr><td>Exact symbol match</td><td class="yes">Yes</td><td class="warn">Approximate</td><td class="yes">Yes, if you find it</td></tr>
        <tr><td>Vector DB / infra</td><td class="yes">None needed</td><td class="no">Required</td><td class="yes">None needed</td></tr>
        <tr><td>Token cost per query</td><td class="yes">~140 tokens</td><td class="warn">Chunk-dependent</td><td class="no">Whole file</td></tr>
        <tr><td>Works fully offline</td><td class="yes">Yes</td><td class="warn">Depends on embedder</td><td class="yes">Yes</td></tr>
        <tr><td>Git-diffable output</td><td class="yes">Plain markdown</td><td class="no">Opaque vectors</td><td class="yes">N/A</td></tr>
      </tbody>
    </table>
  </div>
  </section>

  <section id="faq">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">FAQ</div>
      <h2>Common questions</h2>
    </div>
    <div class="faq-list">
      <details>
        <summary>Does this require an API key or internet connection?</summary>
        <p>No. Core extraction (<code>okf generate</code>) is fully offline and deterministic — no LLM call is made unless you explicitly enable <code>OKF_ENRICH=1</code>.</p>
      </details>
      <details>
        <summary>What happens if my language isn't supported?</summary>
        <p>Unsupported files are skipped, not dropped silently — <code>log.md</code> records what was scanned. Adding a language is a self-contained tree-sitter grammar mapping; it's a listed good-first-issue.</p>
      </details>
      <details>
        <summary>Does this work on monorepos or very large codebases?</summary>
        <p>Yes — the bundle mirrors your source tree, so scanning is linear in file count. For very large repos, scope <code>okf generate</code> to a subdirectory if you only need part indexed.</p>
      </details>
      <details>
        <summary>Is the bundle safe to commit to git?</summary>
        <p>Yes — that's the intended workflow. Bundles are plain markdown, diff cleanly, and version alongside the code they describe.</p>
      </details>
    </div>
  </div>
  </section>

  <section id="install">
    <div class="wrap">
    <div class="section-head">
      <div class="section-tag">Get started</div>
      <h2>One install, works with any agent</h2>
    </div>
    <div class="install-box">
      <code>pip install okf-generator</code>
      <button class="copy-btn" aria-live="polite" onclick="navigator.clipboard.writeText('pip install okf-generator'); this.textContent='Copied'; setTimeout(()=>this.textContent='Copy install command',1400)">Copy install command</button>
    </div>
    <div class="install-alt">
      <div><span class="install-alt-label">macOS / Linux one-liner</span><code>curl -fsSL raw.githubusercontent.com/UmairBaig8/okf-generator/main/scripts/install.sh | bash</code></div>
      <div><span class="install-alt-label">With LLM enrichment</span><code>pip install "okf-generator[llm]"</code></div>
    </div>
  </div>
  </section>
</main>

<footer>
  <div class="wrap foot-row">
    <div>okf-generator v0.1.29 · MIT License · Copyright © 2026 Umair Baig</div>
    <div class="foot-links">
      <a href="https://github.com/UmairBaig8/okf-generator" target="_blank" rel="noopener">GitHub<span class="sr-only"> (opens in new tab)</span></a>
      <a href="https://pypi.org/project/okf-generator/" target="_blank" rel="noopener">PyPI<span class="sr-only"> (opens in new tab)</span></a>
      <a href="https://github.com/UmairBaig8/okf-generator/blob/main/SKILL.md" target="_blank" rel="noopener">Claude Skill<span class="sr-only"> (opens in new tab)</span></a>
      <a href="https://github.com/UmairBaig8/okf-generator/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener">Contributing<span class="sr-only"> (opens in new tab)</span></a>
    </div>
  </div>
</footer>

<script>
(function(){
  // sequence: {type:'cmd', text} typed char-by-char with a $ prompt
  //           {type:'out', text} printed instantly (dim, like real stdout)
  //           {type:'wait', ms}  pause
  var seq = [
    {type:'cmd', text:'okf generate ./src ./okf_bundle'},
    {type:'wait', ms:280},
    {type:'out', text:'Scanning 640 files across 10 languages…'},
    {type:'out', text:'Bundle written → ./okf_bundle (4,218 concepts)'},
    {type:'blank'},
    {type:'wait', ms:400},
    {type:'cmd', text:'okf lookup WorldBankConnector'},
    {type:'wait', ms:260},
    {type:'out', text:'CLASS: WorldBankConnector'},
    {type:'out', text:'Source&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: connectors/economic_data.py  line 51'},
    {type:'out', text:'Methods&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: get_indicator, search'},
    {type:'out', text:'Called by : DataPipeline.fetch_economic'},
    {type:'blank'},
    {type:'wait', ms:400},
    {type:'hl', text:'~140 tokens', suffix:' consumed. no re-reading required.'},
    {type:'wait', ms:2600},
  ];

  var el = document.getElementById('term-live');
  if (!el) return;
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  window.__animPaused = reduceMotion; // honor OS setting as the starting state

  function typeLine(text, cls, cb){
    var line = document.createElement('div');
    var prompt = document.createElement('span');
    prompt.className = 'prompt'; prompt.textContent = '$ ';
    var span = document.createElement('span');
    span.className = cls || 'cmd';
    line.appendChild(prompt); line.appendChild(span);
    el.appendChild(line);
    if (reduceMotion){ span.textContent = text; cb(); return; }
    var i = 0;
    (function tick(){
      if (window.__animPaused){ setTimeout(tick, 250); return; }
      span.textContent = text.slice(0, i);
      i++;
      if (i <= text.length){ setTimeout(tick, 18 + Math.random()*22); }
      else cb();
    })();
  }

  function printOut(html){
    var line = document.createElement('div');
    line.className = 'out';
    line.innerHTML = html;
    el.appendChild(line);
  }

  function run(i){
    if (window.__animPaused){ setTimeout(function(){ run(i); }, 250); return; }
    if (i >= seq.length){ el.innerHTML = ''; setTimeout(function(){ run(0); }, 500); return; }
    var step = seq[i];
    if (step.type === 'cmd'){
      typeLine(step.text, 'cmd', function(){ run(i+1); });
    } else if (step.type === 'hl'){
      typeLine(step.text, 'hl', function(){
        el.lastChild.innerHTML += '<span class="out">' + step.suffix + '</span><span class="cursor"></span>';
        run(i+1);
      });
    } else if (step.type === 'out'){
      printOut(step.text); run(i+1);
    } else if (step.type === 'blank'){
      el.appendChild(document.createElement('div')); run(i+1);
    } else if (step.type === 'wait'){
      setTimeout(function(){ run(i+1); }, step.ms);
    }
  }
  run(0);
})();

// Shared pause/play control — WCAG 2.2.2: user-facing control for content
// that auto-plays and loops indefinitely (terminal typing, SVG pulse).
(function(){
  var btn = document.getElementById('motion-toggle');
  var label = document.getElementById('motion-toggle-label');
  var svg = document.querySelector('.hero-visual svg');
  if (!btn) return;

  function setState(paused){
    window.__animPaused = paused;
    btn.setAttribute('aria-pressed', String(paused));
    label.textContent = paused ? 'Play animation' : 'Pause animation';
    document.body.classList.toggle('motion-paused', paused);
    if (svg && svg.pauseAnimations){
      paused ? svg.pauseAnimations() : svg.unpauseAnimations();
    }
  }
  setState(!!window.__animPaused);
  btn.addEventListener('click', function(){ setState(!window.__animPaused); });
})();
</script>
<script>
  fetch('https://api.github.com/repos/UmairBaig8/okf-generator')
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(d => {
      const n = d.stargazers_count;
      const fmt = n >= 1000 ? (n/1000).toFixed(1) + 'k' : String(n);
      document.getElementById('star-count-nav').textContent = fmt;
      const hero = document.getElementById('star-count-hero');
      if (hero) hero.textContent = '· ★ ' + fmt;
    })
    .catch(() => {
      document.getElementById('star-count-nav').textContent = '';
    });
</script>
</body>
</html>
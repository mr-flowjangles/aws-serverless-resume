/* ============================================================
   robrose.info — interactions
   - scroll reveal
   - chat panel (RobbAI, backed by window.claude)
   ============================================================ */

(() => {
  /* ---------- reveal on scroll ---------- */
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) {
        e.target.classList.add('is-in');
        io.unobserve(e.target);
      }
    }
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal').forEach(el => io.observe(el));

  /* ---------- smooth scroll for in-page anchors ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const id = a.getAttribute('href').slice(1);
      if (!id) return;
      const target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  /* ---------- chat panel ---------- */
  const launch = document.getElementById('chat-launch');
  const panel  = document.getElementById('chat-panel');
  const close  = document.getElementById('chat-close');
  const body   = document.getElementById('chat-body');
  const input  = document.getElementById('chat-text');
  const send   = document.getElementById('chat-send');
  const suggs  = document.getElementById('chat-suggestions');

  const openChat = () => {
    panel.classList.add('open');
    launch.style.display = 'none';
    setTimeout(() => input.focus(), 200);
  };
  const closeChat = () => {
    panel.classList.remove('open');
    launch.style.display = '';
  };

  launch.addEventListener('click', openChat);
  close.addEventListener('click', closeChat);
  document.querySelectorAll('[data-open-chat]').forEach(b => b.addEventListener('click', (e) => { e.preventDefault(); openChat(); }));
  document.getElementById('hero-chat-cta').addEventListener('click', (e) => { e.preventDefault(); openChat(); });

  /* auto-resize textarea */
  const autosize = () => {
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 120) + 'px';
  };
  input.addEventListener('input', autosize);

  /* keyboard: enter to send, shift+enter for newline */
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  });

  /* suggestion chips */
  if (suggs) {
    suggs.querySelectorAll('button').forEach(b => {
      b.addEventListener('click', () => {
        input.value = b.textContent.trim();
        autosize();
        submit();
      });
    });
  }

  send.addEventListener('click', submit);

  /* ---------- Contact form: POST /api/contact + reCAPTCHA ----------
     Lifted from aws-serverless-resume/app/scripts/contact.js */
  const API_BASE = '/api';
  const contactForm = document.getElementById('contact-form');
  const cfStatus    = document.getElementById('cf-status');

  function setStatus(msg, kind) {
    if (!cfStatus) return;
    cfStatus.textContent = msg || '';
    cfStatus.dataset.kind = kind || '';
  }

  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const recaptchaResponse =
        (typeof grecaptcha !== 'undefined' && grecaptcha.getResponse) ? grecaptcha.getResponse() : '';
      if (!recaptchaResponse) {
        setStatus('Please complete the reCAPTCHA.', 'error');
        return;
      }

      const payload = {
        name:    document.getElementById('cf-name').value,
        email:   document.getElementById('cf-email').value,
        message: document.getElementById('cf-message').value,
        recaptcha_token: recaptchaResponse,
      };

      const submitBtn = contactForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;
      setStatus('Sending…', 'pending');

      try {
        const response = await fetch(`${API_BASE}/contact`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (response.ok) {
          setStatus("Message sent — I'll get back to you.", 'success');
          contactForm.reset();
          if (typeof grecaptcha !== 'undefined' && grecaptcha.reset) grecaptcha.reset();
        } else {
          setStatus('Failed to send message. Please try again.', 'error');
        }
      } catch (err) {
        setStatus('Error sending message: ' + err.message, 'error');
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  /* ---------- RobbAI: Bot Factory streaming endpoint ----------
     Lifted from aws-serverless-resume/app/scripts/chat-widget.js */
  const CHAT_CONFIG = {
    apiUrl: 'https://4bu5vwwizdql4wzwh6dqhke62m0oyrbk.lambda-url.us-east-1.on.aws',
    botId:  'RobbAI',
    apiKey: 'bfk_WwXLDR2X8OcvNnt4Nc50aPD7ghSd5QMCIt9Gimfrejo',
  };

  function addMessage(role, text) {
    const el = document.createElement('div');
    el.className = 'msg ' + (role === 'user' ? 'user' : 'bot');
    el.textContent = text;
    body.appendChild(el);
    body.scrollTop = body.scrollHeight;
    return el;
  }

  async function submit() {
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    autosize();
    send.disabled = true;

    // dismiss suggestion chips after first user message
    if (suggs && suggs.parentNode) { suggs.remove(); }

    addMessage('user', text);

    const thinking = document.createElement('div');
    thinking.className = 'msg bot thinking';
    thinking.textContent = 'thinking';
    body.appendChild(thinking);
    body.scrollTop = body.scrollHeight;

    try {
      const res = await fetch(CHAT_CONFIG.apiUrl + '/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': CHAT_CONFIG.apiKey,
        },
        body: JSON.stringify({ bot_id: CHAT_CONFIG.botId, message: text }),
      });

      if (!res.ok) {
        thinking.remove();
        addMessage('bot', "Sorry, something went wrong. Try again later.");
        return;
      }

      thinking.remove();
      const botDiv = addMessage('bot', '');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let fullText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const payload = line.slice(6).trim();
          if (payload === '[DONE]') continue;

          try {
            const data = JSON.parse(payload);
            if (data.error) {
              fullText += 'Sorry, something went wrong.';
            } else if (data.token) {
              fullText += data.token;
            }
            botDiv.textContent = fullText;
            body.scrollTop = body.scrollHeight;
          } catch {}
        }
      }
    } catch (err) {
      thinking.remove();
      addMessage('bot', "Couldn't reach the server. Please try again later.");
      console.warn('RobbAI error:', err);
    } finally {
      send.disabled = false;
      input.focus();
    }
  }

  /* ---------- Resume content: GET /api/resume ----------
     Populates the experience / skills / education sections from the
     FastAPI Lambda → DynamoDB pipeline. Yes, it's overkill for a resume
     site. That is the point of this site. */
  const expList  = document.getElementById('exp-list');
  const skillsEl = document.getElementById('skills-grid');
  const eduList  = document.getElementById('edu-list');

  const escapeHtml = (s) => String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');

  const year = (d) => {
    if (!d) return '';
    if (String(d).toLowerCase() === 'present') return 'Present';
    return String(d).slice(0, 4);
  };

  const dateRange = (start, end, isCurrent) => {
    const s = year(start);
    const e = isCurrent ? 'Present' : year(end);
    if (s && e && s !== e) return s + ' — ' + e;
    return s || e || '';
  };

  function renderExperience(items) {
    if (!expList) return;
    const main = (items || []).filter(x => !x.is_additional);
    if (!main.length) {
      expList.innerHTML = '<div class="load-error">No experience entries returned.</div>';
      return;
    }
    expList.innerHTML = main.map(exp => `
      <div class="exp-row">
        <div class="exp-dates">${escapeHtml(dateRange(exp.start_date, exp.end_date, exp.is_current))}</div>
        <div class="exp-body">
          <h3>${escapeHtml(exp.job_title)}</h3>
          <div class="where">${escapeHtml(exp.company_name)}</div>
          <div class="what">
            ${exp.description ? '<p>' + escapeHtml(exp.description) + '</p>' : ''}
            ${(exp.accomplishments && exp.accomplishments.length)
              ? '<ul>' + exp.accomplishments.map(a => '<li>' + escapeHtml(a) + '</li>').join('') + '</ul>'
              : ''}
          </div>
        </div>
      </div>
    `).join('');
  }

  const SKILL_ICONS = {
    'Leadership & Strategy':
      '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    'Cloud & Architecture':
      '<path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>',
    'Data & Analytics':
      '<path d="M12 2L2 7l10 5 10-5-10-5z"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>',
    'Development & Tools':
      '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
  };

  function skillIcon(category) {
    const inner = SKILL_ICONS[category];
    if (!inner) return '';
    return '<span class="ic"><svg class="ic-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + inner + '</svg></span>';
  }

  function renderSkills(items) {
    if (!skillsEl) return;
    if (!items || !items.length) {
      skillsEl.innerHTML = '<div class="load-error">No skill categories returned.</div>';
      return;
    }
    skillsEl.innerHTML = items.map(s => `
      <div class="skill-card">
        <h4>${skillIcon(s.category)}${escapeHtml(s.category)}</h4>
        <ul>${(s.skills || []).map(k => '<li>' + escapeHtml(k) + '</li>').join('')}</ul>
      </div>
    `).join('');
  }

  function renderEducation(items) {
    if (!eduList) return;
    if (!items || !items.length) {
      eduList.innerHTML = '<div class="load-error">No education entries returned.</div>';
      return;
    }
    eduList.innerHTML = items.map(edu => `
      <div class="edu-item">
        <h4>${escapeHtml(edu.degree)}</h4>
        <div class="school">${escapeHtml(edu.institution)}${edu.description ? ' · ' + escapeHtml(edu.description) : ''}</div>
        <div class="meta">${escapeHtml(dateRange(edu.start_date, edu.end_date, false))}</div>
      </div>
    `).join('');
  }

  async function loadResumeData() {
    try {
      const res = await fetch(API_BASE + '/resume');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const data = await res.json();
      renderExperience(data.work_experience);
      renderSkills(data.skills);
      renderEducation(data.education);
    } catch (err) {
      const msg = '<div class="load-error">Couldn\'t reach /api/resume.</div>';
      if (expList)  expList.innerHTML  = msg;
      if (skillsEl) skillsEl.innerHTML = msg;
      if (eduList)  eduList.innerHTML  = msg;
      console.warn('resume load error:', err);
    }
  }

  loadResumeData();
})();

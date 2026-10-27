<template>
  <div>
    <header class="topbar">
      <button id="hamburger" @click="toggleSide" aria-label="Toggle sidebar">☰</button>
      <div class="brand"><span class="b-ic">🎯</span><span>SPEAKING<small>Luyện nói</small></span></div>
      <div class="searchbox">
        <span class="s-ic">🔍</span>
        <input id="search" v-model="searchQuery" type="text" placeholder="Tìm cụm từ, cấu trúc, từ vựng…" autocomplete="off" @keydown="onSearchKeydown" />
        <kbd>/</kbd>
      </div>
      <span id="search-count">{{ searchCountText }}</span>
      <button id="theme-toggle" @click="toggleTheme">{{ theme === 'dark' ? '☀️' : '🌙' }}</button>
    </header>

    <aside class="sidebar" id="sidebar">
      <div class="side-head">
        <span class="b-ic">🎯</span>
        <div>
      <a href="#main-content" class="skip-link">Skip to content</a><b>SPEAKING</b><span>Tutorial luyện nói</span></div>
      </div>
      <nav class="side-nav">
        <template v-for="g in navGroups" :key="g.name">
          <div class="nav-group" :class="'g'+g.gi" :title="g.name">{{ g.isGrammar ? '🧠' : '🚩' }} {{ g.name }}</div>
          <a v-for="t in g.topics" :key="t.id" class="nav-link" href="#" :data-t="t.id" :class="{ done: isDone(t.id), active: (singleMode && currentId === t.id) || (!singleMode && activeTopicId === t.id) }" @click.prevent="goTo(t.id)">
            <span class="n-num">{{ t.num }}</span><span class="n-txt">{{ t.en }}</span><span class="n-check">✓</span>
          </a>
        </template>
      </nav>
      <div class="side-progress">
        <div class="sp-top"><span>🎯 Tiến độ thuộc bài</span><b>{{ doneSpeakingCount }}/{{ speakingCount }}</b></div>
        <div class="sp-bar"><div id="side-progress" :style="{ width: sideProgress + '%' }"></div></div>
      </div>
    </aside>
    <div id="backdrop" @click="closeSide"></div>

    <div class="content">
      <section v-if="!singleMode" class="hero" id="hero">
        <div class="hero-inner">
          <span class="hero-badge">🎓 SPEAKING PRACTICE · 24 TOPICS</span>
          <h1>Luyện nói tiếng Anh theo <em>24 Topics</em><br/>học đúng lớp, nói đúng phản xạ</h1>
          <p>Tổng hợp BEOD-MAP, bảng cụm từ giao tiếp, ngữ pháp phản xạ và drill luyện nói từ 24 bài học gốc. Mở bằng trình duyệt, học offline, tiến độ tự lưu.</p>
          <div class="hero-cta">
            <button class="btn btn-primary" @click="goTo('topic-01')">🚀 Bắt đầu từ Topic 01</button>
            <button class="btn btn-ghost" @click="continueLearning">{{ btnContinueLabel }}</button>
          </div>
          <div class="hero-chips">
            <span class="h-chip">📚 {{ speakingCount }} topics</span>
            <span class="h-chip">🧠 {{ grammarCount }} grammar</span>
            <span class="h-chip">🚩 5 nhóm banner</span>
            <span class="h-chip">✅ <span id="done-chip">{{ doneSpeakingCount }}/{{ speakingCount }}</span> topics · <span id="done-gram-chip">{{ doneGrammarCount }}/{{ grammarCount }}</span> grammar</span>
            <span class="h-chip">🗓 {{ generated }}</span>
          </div>
          <div class="hero-steps">
            <div class="step"><span class="s-ic">📖</span><span class="s-no">BƯỚC 1</span><b>Đọc &amp; hiểu đoạn văn</b><span>Tóm tắt + ngữ cảnh sử dụng, gật được mới học tiếp.</span></div>
            <div class="step"><span class="s-ic">💬</span><span class="s-no">BƯỚC 2</span><b>Học bảng cụm từ</b><span>Che cột nghĩa, đoán EN ⇄ VI cho tới thuộc hết.</span></div>
            <div class="step"><span class="s-ic">🧩</span><span class="s-no">BƯỚC 3</span><b>Ngữ pháp phản xạ</b><span>Tự đặt 5 câu mới theo cấu trúc — không chép ví dụ.</span></div>
            <div class="step"><span class="s-ic">🎤</span><span class="s-no">BƯỚC 4</span><b>Drill &amp; ghi âm</b><span>Shadowing 3 lượt, trả lời 5 câu hỏi, nghe lại.</span></div>
          </div>
        </div>
      </section>

      <main>
        <div id="main-content">
        <div v-if="loading" class="loading">Đang tải dữ liệu…</div>
        <template v-for="t in visibleTopics" :key="t.id">
          <div v-if="!singleMode && t.hasDividerBefore && !searchQuery.trim()" class="group-divider" :class="'g'+t.gi">
            <span class="gd-ico">🚩</span>
            <span class="gd-en">{{ t.groupEn }}</span>
            <span v-if="t.groupVi" class="gd-vi">— {{ t.groupVi }}</span>
          </div>
          <TopicCard
            :topic="t"
            :done="isDone(t.id)"
            @home="showAll"
            @group="onGroup"
            @go="goTo"
            @zoom="openLightbox"
            @toggleDone="toggleDone"
            @print="printTopic"
          />
        </template>
        </div>
      </main>
    </div>

    <aside id="toc" aria-label="Mục lục bài đang đọc">
      <div id="toc-title">{{ floatingTocTitle }}</div>
      <ul id="toc-list">
        <li v-for="h in floatingTocItems" :key="h.id" :class="{ sub: h.level === 3 }">
          <a :href="'#'+h.id" :class="{ top: h.level === 2 }" @click.prevent="scrollToId(h.id)">{{ h.label }}</a>
        </li>
      </ul>
    </aside>
    <button id="to-top" v-show="showToTop" @click="scrollToTop">⬆</button>
    <div id="lightbox" :class="{ show: !!lightboxSrc }" @click="lightboxSrc = null">
      <img :src="lightboxSrc" alt="BEOD-MAP phóng to">
      <div class="lb-hint">Nhấn ESC hoặc click để đóng 🔍</div>
    </div>
    <footer class="site-footer">
      <div class="f-brand">🎯 SPEAKING PRACTICE</div>
      <p>Tài liệu tự tổng hợp luyện nói tiếng Anh — học offline, tiến độ tự lưu.</p>
      <p>Cập nhật {{ generated }} · Chỉ dùng cho mục đích học cá nhân.</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import TopicCard from './components/TopicCard.vue'

const DONE_KEY = 'speak-done-v1'
const LAST_KEY = 'speak-last-v1'
const THEME_KEY = 'speak-theme'

const topics = ref([])
const groups = ref([])
const generated = ref('')
const loading = ref(true)
const error = ref(null)

const singleMode = ref(true)
const currentId = ref(null)
const activeTopicId = ref(null)
const doneMap = ref({})
const lastTopicId = ref(null)
const theme = ref('light')
const sideOpen = ref(false)
const searchQuery = ref('')
const searchCountText = ref('')
const lightboxSrc = ref(null)
const floatingTocTitle = ref('📚 Mục lục')
const floatingTocItems = ref([])
const showToTop = ref(false)
const lastFloatingId = ref(null)

function loadDone() { try { return JSON.parse(localStorage.getItem(DONE_KEY)) || {} } catch (e) { return {} } }
function saveDone() { try { localStorage.setItem(DONE_KEY, JSON.stringify(doneMap.value)) } catch (e) {} }
function loadLast() { try { return localStorage.getItem(LAST_KEY) } catch (e) { return null } }

const doneCount = computed(() => Object.keys(doneMap.value).filter(k => doneMap.value[k]).length)
const speakingCount = computed(() => topics.value.filter(t => !t.isGrammar).length)
const grammarCount = computed(() => topics.value.filter(t => t.isGrammar).length)
const doneSpeakingCount = computed(() => topics.value.filter(t => !t.isGrammar && doneMap.value[t.id]).length)
const doneGrammarCount = computed(() => topics.value.filter(t => t.isGrammar && doneMap.value[t.id]).length)
const sideProgress = computed(() => speakingCount.value ? Math.round(doneSpeakingCount.value / speakingCount.value * 100) : 0)
const isDone = (id) => !!doneMap.value[id]

const navGroups = computed(() => {
  const out = []
  let cur = null
  for (const t of topics.value) {
    if (!cur || cur.name !== t.groupEn) {
      cur = { name: t.groupEn, gi: t.gi, isGrammar: !!t.isGrammar, topics: [] }
      out.push(cur)
    }
    cur.topics.push(t)
  }
  return out
})

const visibleTopics = computed(() => {
  if (singleMode.value) {
    return topics.value.filter(t => t.id === currentId.value)
  }
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return topics.value
  return topics.value.filter(t => {
    const text = (t.en + ' ' + (t.vi||'') + ' ' + t.groupEn + ' ' + stripHtml(t.bodyHtml)).toLowerCase()
    return text.includes(q)
  })
})

function stripHtml(s) { return (s || '').replace(/<[^>]*>/g, ' ') }

const firstUndone = computed(() => topics.value.find(t => !doneMap.value[t.id]))
const continueTarget = computed(() => {
  const last = lastTopicId.value
  if (last && topics.value.some(t => t.id === last)) return last
  if (firstUndone.value) return firstUndone.value.id
  return 'topic-01'
})
const btnContinueLabel = computed(() => {
  const t = topics.value.find(x => x.id === continueTarget.value)
  if (firstUndone.value || lastTopicId.value) {
    return '⏭ Tiếp tục: ' + (t ? ('Topic ' + t.num + ' · ' + t.en.slice(0, 38)) : '')
  }
  return '🎉 Đã hoàn thành ' + topics.value.length + '/' + topics.value.length + ' — ôn lại từ đầu'
})

function toggleSide() {
  const isMobile = window.innerWidth <= 1079
  if (isMobile) {
    sideOpen.value = !sideOpen.value
  } else {
    document.body.classList.toggle('sidebar-collapsed')
  }
}
function closeSide() {
  sideOpen.value = false
  document.body.classList.remove('side-open')
  document.body.classList.remove('sidebar-collapsed')
}
watch(sideOpen, (v) => { document.body.classList.toggle('side-open', v) })

function toggleTheme() {
  applyTheme(theme.value === 'dark' ? 'light' : 'dark')
}
function applyTheme(t) {
  theme.value = t
  document.documentElement.setAttribute('data-theme', t)
  try { localStorage.setItem(THEME_KEY, t) } catch (e) {}
}

function loadAll() {
  doneMap.value = loadDone()
  lastTopicId.value = loadLast()
}

function setMode(single, target) {
  singleMode.value = single
  if (single && target) {
    currentId.value = target
    activeTopicId.value = null
    try { localStorage.setItem(LAST_KEY, target) } catch (e) {}
    lastTopicId.value = target
    history.replaceState(null, '', '#' + target)
    window.scrollTo(0, 0)
    nextTick(() => buildFloatingToc(target))
  } else {
    currentId.value = null
    activeTopicId.value = null
    try { history.replaceState(null, '', location.pathname + location.search) } catch (e) {}
    lastFloatingId.value = null
  }
  nextTick(() => {
    document.querySelectorAll('.nav-link:not(.all)').forEach(l => {
      const a = single && l.dataset.t === target
      l.classList.toggle('active', a)
      l.setAttribute('aria-pressed', a)
    })
    const allBtn = document.getElementById('nav-all')
    if (allBtn) allBtn.classList.toggle('active', !single)
  })
}

function goTo(id) {
  if (!document.getElementById(id) && !topics.value.some(t => t.id === id)) return
  clearSearch()
  setMode(true, id)
  closeSide()
}
function showAll() {
  clearSearch()
  setMode(false)
  closeSide()
}
function onGroup(t) {
  setMode(false)
  nextTick(() => {
    const card = document.getElementById(t.id)
    if (card) card.scrollIntoView({ behavior: 'smooth' })
  })
}

function clearMarks() {
  document.querySelectorAll('mark.hl').forEach(m => {
    const p = m.parentNode
    if (!p) return
    while (m.firstChild) p.insertBefore(m.firstChild, m)
    m.remove()
    p.normalize()
  })
}
function clearSearch() {
  if (searchQuery.value) searchQuery.value = ''
  clearMarks()
  searchCountText.value = ''
}
function markText(card, q) {
  const walker = document.createTreeWalker(card, NodeFilter.SHOW_TEXT, {
    acceptNode(n) {
      if (!n.nodeValue || !n.nodeValue.toLowerCase().includes(q)) return NodeFilter.FILTER_REJECT
      const p = n.parentElement
      if (!p || /^(SCRIPT|STYLE|MARK|INPUT|TEXTAREA)$/.test(p.tagName)) return NodeFilter.FILTER_REJECT
      return NodeFilter.FILTER_ACCEPT
    }
  })
  const nodes = []
  while (walker.nextNode() && nodes.length < 150) nodes.push(walker.currentNode)
  nodes.forEach(n => {
    const low = n.nodeValue.toLowerCase()
    let idx = low.indexOf(q)
    if (idx < 0) return
    const frag = document.createDocumentFragment()
    let pos = 0
    while (idx > -1) {
      if (idx > pos) frag.appendChild(document.createTextNode(n.nodeValue.slice(pos, idx)))
      const mk = document.createElement('mark')
      mk.className = 'hl'
      mk.textContent = n.nodeValue.slice(idx, idx + q.length)
      frag.appendChild(mk)
      pos = idx + q.length
      idx = low.indexOf(q, pos)
    }
    if (pos < n.nodeValue.length) frag.appendChild(document.createTextNode(n.nodeValue.slice(pos)))
    n.parentNode.replaceChild(frag, n)
  })
}

let searchMarkTimer = null
watch(searchQuery, (val) => {
  const q = val.trim().toLowerCase()
  clearMarks()
  if (searchMarkTimer) { clearTimeout(searchMarkTimer); searchMarkTimer = null }
  if (q && singleMode.value) setMode(false)
  if (q) {
    const visible = visibleTopics.value.length
    searchCountText.value = visible + '/' + topics.value.length + ' bài'
  } else {
    searchCountText.value = ''
  }
  if (q && q.length >= 2) {
    searchMarkTimer = setTimeout(() => {
      nextTick(() => {
        document.querySelectorAll('.topic-card').forEach(card => {
          markText(card, q)
        })
      })
    }, 180)
  }
})

function onSearchKeydown(e) {
  if (e.key === 'Escape') {
    if (lightboxSrc.value) { lightboxSrc.value = null; e.preventDefault(); return }
    if (searchQuery.value) { clearSearch(); e.target.blur() }
  }
}

const onGlobalKeydown = (e) => {
  const tag = (e.target.tagName || '').toLowerCase()
  if (e.key === '/' && !/input|textarea|select/.test(tag)) {
    e.preventDefault()
    const s = document.getElementById('search')
    if (s) { s.focus(); s.select() }
  }
  if (e.key === 'Escape' && lightboxSrc.value) lightboxSrc.value = null
}
document.addEventListener('keydown', onGlobalKeydown)

function buildFloatingToc(cardId) {
  const card = document.getElementById(cardId)
  if (!card) { floatingTocTitle.value = '📚 Mục lục'; floatingTocItems.value = []; return }
  const en = card.querySelector('.t-en')
  floatingTocTitle.value = en ? '📖 ' + en.textContent : '📚 Mục lục'
  floatingTocItems.value = [...card.querySelectorAll('h2,h3')].map(h => {
    let t = h.textContent
    let label = t
    if (h.tagName === 'H3' && t.indexOf(':') > -1) label = t.slice(0, t.indexOf(':'))
    return { id: h.id, level: parseInt(h.tagName[1]), label: (h.tagName === 'H3' ? '· ' : '') + label }
  })
}

function scrollToId(id) {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}
function scrollToTop() { window.scrollTo({ top: 0, behavior: 'smooth' }) }
function openLightbox(src) { lightboxSrc.value = src }

function toggleDone(id, checked) {
  const next = { ...doneMap.value }
  if (checked) next[id] = true
  else delete next[id]
  doneMap.value = next
  saveDone()
}

function printTopic(id) {
  if (!singleMode.value) setMode(true, id)
  setTimeout(() => window.print(), 350)
}

function continueLearning() {
  const target = continueTarget.value
  goTo(target)
}

function onScroll() {
  const d = document.documentElement
  const hgt = d.scrollHeight - d.clientHeight
  const bar = document.getElementById('progress-bar')
  if (bar) bar.style.width = (hgt > 0 ? d.scrollTop / hgt * 100 : 0) + '%'
  showToTop.value = window.scrollY > 600
  if (singleMode.value) return
  const y = window.scrollY + 130
  let cur = null
  document.querySelectorAll('.topic-card').forEach(c => {
    if (c.style.display === 'none') return
    if (c.offsetTop <= y) cur = c.id
  })
  if (!cur) {
    const first = document.querySelector('.topic-card')
    cur = first ? first.id : null
  }
  if (cur && cur !== lastFloatingId.value) {
    lastFloatingId.value = cur
    activeTopicId.value = cur
    buildFloatingToc(cur)
    nextTick(() => {
      const act = document.querySelector('.nav-link.active')
      if (act) act.scrollIntoView({ block: 'nearest' })
    })
  }
}

let ticking = false
function onScrollRAF() {
  if (!ticking) {
    ticking = true
    requestAnimationFrame(() => { onScroll(); ticking = false })
  }
}

function route() {
  let h = location.hash.slice(1)
  let deep = null
  if (h && !topics.value.some(t => t.id === h)) {
    const m = h.match(/^(topic-\d+)-h\d+$/)
    if (m) { deep = m[0]; h = m[1] }
  }
  if (h && topics.value.some(t => t.id === h)) {
    setMode(true, h)
    if (deep) {
      const el = document.getElementById(deep)
      if (el) setTimeout(() => el.scrollIntoView(), 50)
    }
  } else {
    const last = lastTopicId.value
    const target = (last && topics.value.some(t => t.id === last)) ? last : 'topic-01'
    setMode(true, target)
  }
}

onMounted(async () => {
  loadAll()
  let savedTheme = null
  try { savedTheme = localStorage.getItem(THEME_KEY) } catch (e) {}
  applyTheme(savedTheme || (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'))
  try {
    const res = await fetch('/speaking/data.json')
    const data = await res.json()
    topics.value = data.topics
    groups.value = data.groups
    generated.value = data.generated
  } catch (e) {
    error.value = e
    console.error(e)
  }
  loading.value = false
  window.addEventListener('scroll', onScrollRAF, { passive: true })
  window.addEventListener('hashchange', route)
  const toTopBtn = document.getElementById('to-top')
  if (toTopBtn) toTopBtn.addEventListener('click', scrollToTop)
  nextTick(() => {
    route()
    onScroll()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScrollRAF)
  window.removeEventListener('hashchange', route)
  document.removeEventListener('keydown', onGlobalKeydown)
})
</script>

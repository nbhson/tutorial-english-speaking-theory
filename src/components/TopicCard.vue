<template>
  <section class="topic-card" :class="{ 'grammar-card': topic.isGrammar }" :id="topic.id" ref="cardEl">
    <div class="t-breadcrumb">
      <button class="crumb-home" @click="$emit('home')">🏠 Trang chủ</button><i>›</i>
      <button class="crumb-group" :style="{ color: topic.isGrammar ? '#8b5cf6' : 'var(--brand-2)', fontWeight: 700 }" @click="$emit('group', topic)">{{ topic.isGrammar ? '🧠' : '🚩' }} {{ topic.groupEn }}</button><i>›</i>
      <b>{{ topic.isGrammar ? 'Grammar' : 'Topic' }} {{ topic.num }}</b>
    </div>
    <h1 class="topic-title">
      <span class="t-num" :class="'g'+topic.gi">{{ topic.num }}</span>
      <span class="t-head-txt">
        <span class="t-en">{{ topic.en }}</span>
        <span v-if="topic.vi" class="t-vi">{{ topic.vi }}</span>
      </span>
    </h1>
    <div class="t-meta">
      <span class="tag" :class="'g'+topic.gi">{{ topic.isGrammar ? '🧠' : '🚩' }} {{ topic.groupEn }}</span>
      <span v-if="topic.groupVi" class="tag ghost">{{ topic.groupVi }}</span>
      <span v-if="!topic.isGrammar" class="tag ghost">⏱ ~{{ topic.mins }} phút học</span>
    </div>
    <div v-if="!topic.isGrammar" class="card-tools">
      <label><input type="checkbox" :checked="done" @change="$emit('toggleDone', topic.id, $event.target.checked)"> ✅ Đã thuộc bài — tick khi nói trôi chảy toàn bài</label>
      <span class="tool-gap"></span>
      <button class="tool-btn" @click="tocVisible = !tocVisible" :class="{ 'btn-off': !tocVisible }">📑 Mục lục</button>
      <button class="tool-btn" @click="collapseAll">{{ collapseLabel }}</button>
      <button class="tool-btn" @click="$emit('print', topic.id)">🖨 In bài này</button>
    </div>
    <nav v-if="!topic.isGrammar" class="card-toc" :class="{ hidden: !tocVisible }">
      <b>📑 Mục lục bài này</b>
      <ul>
        <li v-for="h in tocItems" :key="h.id" :class="{ sub: h.level === 3 }">
          <a :href="'#'+h.id" :class="{ top: h.level === 2 }" @click.prevent="scrollToId(h.id)">{{ h.label }}</a>
        </li>
      </ul>
    </nav>
    <figure v-if="topic.img" class="mindmap">
      <img loading="lazy" decoding="async" :src="'/speaking/images/'+topic.img" :alt="'BEOD-MAP Topic '+topic.num" @click="$emit('zoom', '/speaking/images/'+topic.img)" />
      <figcaption>🗺️ BEOD-MAP Topic {{ topic.num }} — bức bản đồ của cả bài, bấm vào ảnh để phóng to</figcaption>
    </figure>
    <div ref="bodyEl" v-html="topic.bodyHtml"></div>
    <div v-if="!topic.isGrammar" class="pn-nav">
      <button v-if="topic.prevId" class="pn" @click="$emit('go', topic.prevId)">⬅ Topic {{ topic.prevNum }} · {{ topic.prevEn.slice(0,38) }}</button>
      <span v-else></span>
      <button v-if="topic.nextId" class="pn" @click="$emit('go', topic.nextId)">Topic {{ topic.nextNum }} · {{ topic.nextEn.slice(0,38) }} ➡</button>
      <span v-else></span>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

const props = defineProps({
  topic: { type: Object, required: true },
  done: { type: Boolean, default: false }
})
const emit = defineEmits(['home','group','go','zoom','toggleDone','print'])

const cardEl = ref(null)
const bodyEl = ref(null)
const tocVisible = ref(true)
const tocItems = ref([])
const collapseLabel = ref('⬆ Thu gọn tất cả')

function scrollToId(id) {
  const el = document.getElementById(id)
  if (el) el.scrollIntoView({ behavior: 'smooth' })
}

function buildTocItems() {
  const container = bodyEl.value
  if (!container) return
  tocItems.value = [...container.querySelectorAll('h2,h3')].map(h => {
    let t = h.textContent
    let label = t
    if (h.tagName === 'H3' && t.indexOf(':') > -1) label = t.slice(0, t.indexOf(':'))
    return { id: h.id, level: parseInt(h.tagName[1]), label: (h.tagName === 'H3' ? '· ' : '') + label }
  })
}

function enhanceSections() {
  const container = bodyEl.value
  if (!container) return
  if (container.querySelector('.sec-body')) return
  let body = null
  ;[...container.children].forEach(k => {
    if (k.tagName === 'H2') {
      body = document.createElement('div')
      body.className = 'sec-body'
      k.after(body)
      return
    }
    if (body) body.appendChild(k)
  })
  container.querySelectorAll(':scope > h2').forEach(h => {
    const b = h.nextElementSibling
    h.classList.add('toggle')
    h.addEventListener('click', () => {
      b.classList.toggle('hidden')
      h.classList.toggle('collapsed')
    })
  })
  container.querySelectorAll('h3').forEach(h => {
    if (!/^Điểm/.test(h.textContent.trim())) return
    const b = document.createElement('div')
    b.className = 'sec-body'
    h.after(b)
    let n = b.nextElementSibling
    while (n && !/^(H2|H3)$/.test(n.tagName) && !n.classList.contains('pn-nav')) {
      const nx = n.nextElementSibling
      b.appendChild(n)
      n = nx
    }
    h.classList.add('toggle')
    h.addEventListener('click', () => {
      b.classList.toggle('hidden')
      h.classList.toggle('collapsed')
    })
  })
  container.querySelectorAll('blockquote').forEach(bq => {
    if (/✅\s*Checkpoint/i.test(bq.textContent)) bq.classList.add('checkpoint')
  })
  enhanceTTS(container)
}

function enhanceTTS(container) {
  if (!('speechSynthesis' in window)) return
  container.querySelectorAll('pre.dialogue').forEach(pre => {
    if (pre.parentElement && pre.parentElement.classList.contains('dial-wrap')) return
    const wrap = document.createElement('div')
    wrap.className = 'dial-wrap'
    pre.replaceWith(wrap)
    wrap.append(pre)
    const bar = document.createElement('div')
    bar.className = 'dial-bar'
    bar.innerHTML = '<span class="dots"><i></i><i></i><i></i></span>'
      + '<button class="dial-play" title="Đọc to toàn bộ hội thoại (EN)">🔊 Nghe mẫu</button>'
      + '<select class="dial-rate" title="Tốc độ đọc">'
      + '<option value="0.7">🐢 0.7x</option><option value="0.9" selected>▶ 0.9x</option><option value="1.15">🐇 1.15x</option></select>'
      + '<span class="dial-label">Shadowing</span>'
    wrap.prepend(bar)
    const play = bar.querySelector('.dial-play')
    const rate = bar.querySelector('.dial-rate')
    play.addEventListener('click', () => {
      const synth = window.speechSynthesis
      if (synth.speaking) { synth.cancel(); play.textContent = '🔊 Nghe mẫu'; return }
      const text = (pre.querySelector('code') || pre).textContent
      const lines = text.split(/\n+/).map(s => s.trim()).filter(Boolean)
      lines.forEach((line, i) => {
        const u = new SpeechSynthesisUtterance(line)
        u.lang = 'en-US'
        u.rate = parseFloat(rate.value)
        if (i === lines.length - 1) u.addEventListener('end', () => { play.textContent = '🔊 Nghe mẫu' })
        synth.speak(u)
      })
      play.textContent = '⏹ Dừng đọc'
    })
  })
}

function collapseAll() {
  const bodies = cardEl.value ? cardEl.value.querySelectorAll('.sec-body') : []
  const anyOpen = [...bodies].some(b => !b.classList.contains('hidden'))
  bodies.forEach(b => b.classList.toggle('hidden', anyOpen))
  if (cardEl.value) cardEl.value.querySelectorAll('.toggle').forEach(t => t.classList.toggle('collapsed', anyOpen))
  collapseLabel.value = anyOpen ? '⬇ Mở tất cả mục' : '⬆ Thu gọn tất cả'
}

onMounted(() => {
  nextTick(() => {
    enhanceSections()
    buildTocItems()
  })
})
</script>

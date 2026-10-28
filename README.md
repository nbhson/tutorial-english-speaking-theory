# 🎯 Tutorial Luyện Nói Tiếng Anh — Tổng Quan

> Bộ tài liệu tự tổng hợp để **luyện NÓI** tiếng Anh: 24 chủ đề hội thoại, 42 cấu trúc ngữ pháp nói, và bộ công cụ luyện nói với AI. Cập nhật 10/2026.

## 📁 Cấu trúc thư mục

| Thư mục / File | Nội dung |
|----------------|----------|
| [`speaking/README.md`](speaking/README.md) | 📑 Mục lục chính: 24 topics + 42 ngữ pháp + lộ trình 6 tuần |
| [`speaking/topics/`](speaking/topics) | 24 chủ đề hội thoại (topic-01 → topic-24, theo BEOD-MAP) |
| [`speaking/grammar/`](speaking/grammar) | 42 cấu trúc ngữ pháp nói (g-01 → g-42, theo phản xạ) |
| [`10_ai-tools-practice/README.md`](10_ai-tools-practice/README.md) | 🤖 Luyện nói với AI: ChatGPT/Claude/Gemini, ElevenLabs TTS, Whisper chấm phát âm, shadowing, Anki |
| `speaking/index.html` | Trang đọc offline (1 bài/màn hình, tìm kiếm, lưu tiến độ) |
| `index.html`, `src/`, `vite.config.js`, `package.json` | Web app Vue/Vite đọc tài liệu (`npm install && npm run dev`) |
| `scripts/` | Script Python build `data.json` và trang HTML từ các file .md |
| `speaking/data.json` | Dữ liệu đã build cho web app |
| `speaking/images/` | Mindmap BEOD-MAP + ảnh Grammar Focus gốc |

## 📖 Thứ tự đọc gợi ý

1. **[`speaking/README.md`](speaking/README.md)** — xem mục lục đầy đủ + lộ trình 6 tuần.
2. **Topics 01–12** (nhóm giới thiệu bản thân, sở thích, kế hoạch) + grammar nhóm 🅰️🅱️ — nền phản xạ cơ bản.
3. **Topics 13–20** (hỏi đường, kể chuyện quá khứ) + grammar nhóm 🅳🅴 — mệnh đề, liên kết câu.
4. **Topics 21–24** + grammar nhóm 🅵 — phản xạ giao tiếp nâng cao (tag questions, hedging, polite requests).
5. **[`10_ai-tools-practice/README.md`](10_ai-tools-practice/README.md)** — biến tất cả thành luyện nói hàng ngày với AI (15 phút/ngày).

Mỗi topic học theo vòng lặp: **Đọc đoạn văn → che bảng cụm từ đoán nghĩa → shadowing 3 lượt → tự đặt 5 câu ngữ pháp → trả lời 5 câu hỏi luyện nói (ghi âm)**. Chi tiết trong [speaking/README.md](speaking/README.md#cách-học-khuyến-nghị--phiên-bản-hiện-đại).

## ✅ Phiên bản công cụ AI (verify 10/2026)

- ChatGPT: thế hệ **GPT-5.6/GPT-6**, voice mode mọi gói.
- Claude: **Opus 5.5 / Sonnet 5.5**, voice mode trên mobile app.
- Gemini: **Gemini 4 Argon / Gemini 3.8 Live (voice) / 3.8 Flash TTS / 3.5 Transcribe**.
- Whisper API (`whisper-1`) đã deprecated — thay bằng `gpt-transcribe`/`gpt-live-transcribe`; bản local `whisper.cpp` (large-v3) vẫn dùng tốt.
- ElevenLabs: model **Eleven v3/v4**, free 10.000 ký tự/tháng.

> Tài liệu chỉ dùng cho mục đích học cá nhân.

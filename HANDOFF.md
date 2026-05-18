# MotorLab.tw 官網 — Claude Code 交接文件

> 本檔是給未來接手維護網站的 Claude Code 對話讀的「真實狀態」交接文件。
> **新對話開始時第一件事就是讀完本檔**，才能知道專案決策脈絡，
> 不要重新提案已否決的方案、不要破壞既有設計一致性。

**最後更新**：2026-05-18（初版建立）  
**對應網站版本**：v1.0.0（首版上線前）  
**對應韌體版本**：v3.0.8

---

## 0. 給新 Claude 對話的工作守則（最重要）

延續使用者在韌體 repo 的工作習慣，這些原則一樣適用於網站維護：

1. **不要憑印象推測。** 任何「網站大概是這樣寫的」「之前的版本應該是 X」都要先 `view` / `grep` 實際檔案確認。
2. **不要過度設計。** YAGNI。網站是單一 HTML 檔，不要動不動就提案拆成多檔、引入框架、加打包工具。
3. **正體中文溝通。** 變數名與 i18n key 用英文，對話與 HTML 註解用正體中文（繁體中文，臺灣用語）。
4. **行動勝於確認。** 有合理預設直接做，遇到真正分歧再問。不要每次都問「要不要繼續」。
5. **環境是 Windows 11 + PowerShell**（與 MotorLab 韌體 repo 同台電腦）。Bash 也可用，但避免 bash-isms。
6. **承認錯誤不丟鍋。** 自己寫的程式碼是自己的責任，不要回頭怪使用者「請提供原始碼」，要主動用 `view` / `grep` 翻檔案找答案。

---

## 1. 專案概述

**MotorLab.tw 官網**是工作室對外網站，掛在 GitHub Pages 上，網址 `https://motorlab-tw.github.io`。

### 1.1 與韌體專案的關係

| 項目 | 韌體 repo | 網站 repo |
|---|---|---|
| GitHub 帳號 | `jrwei6666-bot`（私人） | `MotorLab-tw`（工作室） |
| Repo 名稱 | `MotorLab` / `MotorLab-firmware` | `MotorLab-tw.github.io` |
| 性質 | Private（源碼）+ Public（.bin） | Public（GitHub Pages 必須） |
| 本機路徑 | `C:\Projects\MotorLab\` | `C:\Projects\MotorLab-site\`（建議） |
| 開發環境 | PlatformIO + ESP32-S3 | 純 HTML / CSS / JS |

**重要：兩個 repo 完全獨立**，不要混在一起。但網站的 Changelog 區塊必須與韌體實際版本對齊。

### 1.2 技術棧

- **單一 HTML 檔** (`index.html`)，所有 CSS 和 JS 內嵌
- **無建置流程**，無 npm、無 webpack、無框架
- 純 HTML5 + CSS3 + ES2017+ JavaScript
- 設計風格：**Nord 主題配色**（與韌體實機 Web UI 完全一致）
- 字體：`-apple-system, "Microsoft JhengHei", sans-serif`（與韌體 Web UI 一致）
- 雙語：i18n 物件儲存中英對照，JS 即時切換 DOM
- 部署：GitHub Pages，main 分支自動部署

### 1.3 為什麼選這個技術棧

使用者明確要求：
- **單檔好維護**：未來 Claude Code 改 changelog 只需要編輯一個檔案
- **無建置流程**：直接 `git push` 就上線，不用等 CI、不用裝 Node.js
- **設計與實機 UI 一致**：使用者買到產品打開 Web UI 時，第一眼就能識別「跟官網是同一個品牌」
- **拒絕 React / Vue / Next.js**：YAGNI，網站內容靜態居多，沒必要

---

## 2. 已決定的設計（**不要重新討論**）

### D1. 視覺風格鎖定 Nord 主題配色

| Token | Hex | 用途 |
|---|---|---|
| `--bg-primary` | `#1a1d23` | 主背景 |
| `--bg-secondary` | `#2e3440` | 卡片背景 |
| `--bg-tertiary` | `#3b4252` | 按鈕背景 |
| `--accent-cyan` | `#88c0d0` | 主要強調色（標題、icon） |
| `--accent-blue` | `#5e81ac` | 邊框、CTA 按鈕 |
| `--accent-purple` | `#b48ead` | PRO 版本識別色 |
| `--success` | `#a3be8c` | 運轉中、新增功能 |
| `--warning` | `#ebcb8b` | 警告、修正類 |
| `--danger` | `#bf616a` | 錯誤 |

**這套色票直接複製自韌體的 `web_pages.h`**。改色之前先想清楚會不會破壞「官網與實機 UI 同一品牌」的核心策略。

### D2. 字體選擇

`-apple-system, "Microsoft JhengHei", "微軟正黑體", "PingFang TC", sans-serif`

**理由**：跟韌體 Web UI 一致。不要改成 Inter、Noto Sans、Pretendard 等流行字體，使用者明確不要「AI 感」設計。

### D3. 結構：單一 HTML，不拆檔

- 不要把 CSS 抽到 `style.css`
- 不要把 JS 抽到 `script.js`
- 不要把 i18n 抽到 `locales/zh.json` / `locales/en.json`

**理由**：使用者要的是「Claude Code 改一個檔案就完成更新」的單純維護流程。

### D4. 雙語切換策略

- 用 `data-i18n="key"` 標記所有需翻譯的元素
- JS 載入時根據 `currentLang` 套用對應字串
- 預設中文，使用者可切英文
- 不存 localStorage（避免使用者跨裝置體驗不一致）

### D5. Gumroad 購買按鈕策略

- 按鈕程式碼已內建在 hero 區塊（`#purchase-btn`）
- 預設 `display: none` 隱藏
- JS 底部變數 `const PRODUCT_LIVE = false;` 控制
- **產品上線時**：把 `false` 改 `true`，並把 `href="#"` 改為 Gumroad 商品連結

### D6. 「技術規格」區塊只講分析方法、不講硬體

使用者明確要求**走宣傳方向**：
- ✅ 可以講：FFT 頻譜、CV 變異係數、衰減 τ、基準指紋、HMAC-SHA256
- ❌ 不可講：ESP32-S3、INA226、DRV8833、TCRT5000、KY-013、GPIO 編號

**理由**：這些核心元件被透露，競爭對手可以反向推算硬體 BOM。

### D7. 不署名走純品牌路線

About 區塊**不要**加「由 XXX 創立」「Lead Developer: XXX」等署名。使用者要走純品牌定位。

### D8. Changelog 與韌體版本嚴格對齊

- 每次韌體發新版（v3.0.X），網站 changelog 也要同步更新
- 版本號要對齊（不能網站寫 v3.0.9 但韌體 repo 是 v3.0.8）
- 內容由使用者提供（不要自己編造變更內容）

### D9. 部署目標：GitHub Pages，未來可能綁網域

- 當前網址：`https://motorlab-tw.github.io`
- 未來可能買 `motorlab.tw` 網域並綁定（CNAME 範本已備）
- 不要建議搬到 Vercel / Netlify / Cloudflare Pages，使用者選擇 GitHub Pages 是有意決定

### D10. 商標處理原則（**法律敏感，不要動**）

**背景**：「ミニ四駆」「Mini 4WD」是田宮（株式会社タミヤ / TAMIYA, INC.）的註冊商標（日本商標登錄號第 2168392 號）。MotorLab 是獨立工作室製作的相容性測試設備，**非田宮授權產品**。

**已實作的保護措施**：

1. **Footer 商標聲明區塊** — `<div class="footer-trademark">`
   - 明確標示「Mini 4WD®」「ミニ四駆®」為田宮註冊商標
   - 標示日本商標登錄號 第 2168392 號
   - 聲明 MotorLab 與田宮無關聯、未受授權贊助背書
   - 援引「指涉性合理使用」原則

2. **About 區塊獨立工作室聲明** — `.about-disclaimer` 樣式
   - 在工作室介紹中明確標示獨立工作室身份
   - 強調本產品為「相容性測試設備」

3. **i18n 同步翻譯** — 中英文版本都有 `footer.trademark` 與 `about.p4` 翻譯
   - 英文版用「compatible third-party testing device」措辭
   - 中文版用「相容性測試設備」措辭

**修改規則（這些是行為不變式）**：

- ❌ **不要刪除** footer 商標聲明區塊或 about disclaimer
- ❌ **不要刪除** `® 商標標記符號（在合法引用商標時必須加註）
- ❌ **不要在主視覺、Logo、產品名稱中加入「Tamiya」「田宮」字樣**（會構成商標混淆）
- ❌ **不要使用「Tamiya 授權」「田宮指定」「官方推薦」等暗示性用語**
- ❌ **不要用田宮的視覺識別**（紅藍色 logo、特定字體）
- ❌ **不要把「Mini 4WD」當作 MotorLab 的產品名一部分**（例如不能叫「MotorLab Mini 4WD Tester」）
- ✅ **可以**在描述中說「為 Mini 4WD® 玩家打造」「適用於 ミニ四駆® 馬達」（指涉性使用）
- ✅ **可以**保留現有所有「Mini 4WD」「迷你四驅車」字眼（已經過審視）

**如果使用者要求新增更多商標相關文字**，先看一下這個區塊有沒有相關規定，再決定怎麼寫。

**如果田宮（或其法務）寄來警告信**：
- 立刻停止任何修改
- 通知使用者
- 暫時把 footer 商標聲明改為更顯眼（例如加邊框、放大字級）
- 等使用者法律諮詢後再做後續處理

### D11. SEO 優化基礎建設（**已實作完成，維護時遵循這套架構**）

**已實作的 SEO 完整清單**：

1. **基礎 meta 標籤**
   - `<title>` 含品牌名 + 主關鍵字 + 副標
   - `<meta description>` 約 150 字內，含主要關鍵字
   - `<meta keywords>` 含中、英、日三語關鍵字
   - `<link rel="canonical">` 標示正規網址
   - `<meta robots>` 與 `<meta googlebot>` 明確允許索引

2. **多語言 hreflang**
   - `<link rel="alternate" hreflang="zh-TW">` 中文版
   - `<link rel="alternate" hreflang="en">` 英文版（用 `?lang=en` 參數區分）
   - `<link rel="alternate" hreflang="x-default">` 預設版本

3. **Open Graph + Twitter Card**（完整社群分享卡）
   - `og:image:alt` 含替代文字（無障礙）
   - `og:image:type`、`og:image:secure_url` 完整聲明
   - Twitter Card 使用 `summary_large_image`

4. **三套 JSON-LD 結構化資料**
   - `Organization` — 工作室資訊（含 contactPoint）
   - `WebSite` — 網站本體與多語版本
   - `Product` — MotorLab 產品資訊（含 featureList 9 項功能）

5. **支援檔案**
   - `sitemap.xml` — 含 `xhtml:link` 多語言 + `image:image` 圖片標籤
   - `robots.txt` — 含 Disallow 內部文件（HANDOFF/DEPLOYMENT 等）+ AI 訓練爬蟲封鎖（GPTBot/CCBot/anthropic-ai）
   - `site.webmanifest` — PWA 支援（可加到行動裝置主畫面）

6. **行動裝置**
   - `theme-color` 在 iOS/Android 工具列顯示品牌色
   - `apple-mobile-web-app-*` 系列 meta（加到主畫面時的全螢幕模式）
   - viewport 已設定

**SEO 維護規則（行為不變式）**：

- ❌ **不要拿掉 canonical** — 多版本時必須指向主要版本
- ❌ **不要在 keywords 加無關詞** — Google 雖然不看 keywords，但堆砌可能傷害品質分
- ❌ **不要刪除 JSON-LD 任何一塊** — 三套 schema 互補
- ❌ **不要在 robots.txt 開放 HANDOFF.md / DEPLOYMENT.md** 索引（內部文件不該出現在搜尋結果）
- ✅ **發布新韌體版本時，同步更新 JSON-LD 的 `softwareVersion`**
- ✅ **改 title/description 時，主關鍵字「Mini 4WD」「馬達磨合」「MotorLab」要保留**
- ✅ **改 sitemap.xml 時，記得更新 `<lastmod>` 為當天日期**

**SEO 工具與檢測（建議定期跑）**：

| 工具 | 用途 |
|---|---|
| https://search.google.com/search-console | Google 索引狀態與搜尋表現 |
| https://www.opengraph.xyz/ | OG 卡片預覽（FB/LINE/Twitter） |
| https://search.google.com/test/rich-results | JSON-LD 結構化資料驗證 |
| https://pagespeed.web.dev/ | Core Web Vitals 效能評分 |
| https://validator.w3.org/ | HTML 標準驗證 |
| https://ahrefs.com/webmaster-tools | 反向連結與關鍵字追蹤（免費） |

**如果使用者問「網站還沒被 Google 找到怎麼辦」**：
1. 確認已在 Google Search Console 提交 sitemap
2. 確認 robots.txt 沒擋掉 Googlebot
3. 用 Search Console 的「網址檢查」工具請求重新索引
4. 等 1-2 週（新站首次索引時間）

**SEO 改進方向（未來可加）**：
- [ ] 加上 FAQPage schema（用使用者手冊的 FAQ 內容）
- [ ] 加上 Breadcrumb schema（如果未來新增子頁面）
- [ ] 加上 VideoObject schema（如果之後加 Demo 影片）
- [ ] 開部落格放長文章（最有效但工作量大）
- [ ] 申請 backlinks（找田宮迷你四驅車相關社群、玩家論壇互相連結）

---

## 3. 已否決的路線（**不要再提案**）

### R1. ❌「把 CSS / JS 抽出來」
理由：違反 D3 單檔策略。

### R2. ❌「改用 React / Next.js / Astro 等框架」
理由：違反 YAGNI。內容是靜態的，沒必要引入框架。維護成本反而提高。

### R3. ❌「加上 npm / build / CI pipeline」
理由：當前單檔架構直接 `git push` 就上線，零複雜度。加 build 沒帶來價值。

### R4. ❌「把 i18n 改用 i18next 之類的函式庫」
理由：當前手刻 i18n 物件 30 行就解決，引入函式庫需要 build 步驟。違反 D3。

### R5. ❌「在 Hero 區塊放 emoji 或大量插圖」
理由：使用者 v3.0.7~v3.0.8 韌體 changelog 已明確移除 emoji，要走專業俐落風格。

### R6. ❌「揭露硬體元件型號或 GPIO 配置」
理由：違反 D6。即使在 SEO meta keywords 也不要寫。

### R7. ❌「複製 web_pages.h 裡的實際 Web UI 截圖到網站」
理由：使用者想「同風格」而不是「同畫面」。網站是行銷，實機 UI 是工具，目的不同。

---

## 4. 檔案結構

```
C:\Projects\MotorLab-site\
├── index.html              ← 主網站（單檔，所有 HTML/CSS/JS/i18n）
├── 404.html                ← 找不到頁面，風格一致
├── favicon.svg             ← SVG 主圖示（向量，瀏覽器優先載入）
├── favicon-32.png          ← 備用 PNG（舊瀏覽器相容）
├── favicon-192.png         ← Android Home Screen 圖示
├── apple-touch-icon.png    ← iOS Home Screen 圖示
├── og-image.svg            ← Open Graph 預覽圖原始檔
├── og-image.png            ← Open Graph 預覽圖（社群實際讀的是這個）
├── robots.txt              ← 搜尋引擎索引指示
├── sitemap.xml             ← 搜尋引擎索引清單
├── .nojekyll               ← 告訴 GitHub Pages 不要用 Jekyll 處理
├── CNAME.example           ← 自訂網域範本（綁網域時改名為 CNAME）
├── README.md               ← Repo 簡介
├── HANDOFF.md              ← 本檔
├── DEPLOYMENT.md           ← GitHub Pages 部署逐步指南
└── CHANGELOG_TEMPLATE.md   ← 新版本上線時的 changelog 區塊範本
```

### index.html 內部結構

```
<head>
  ├── meta 標籤（description / keywords / SEO）
  ├── favicon link (4 個尺寸)
  ├── Open Graph + Twitter Card
  ├── JSON-LD 結構化資料
  └── <style> ... </style>（內嵌 CSS，所有設計變數在 :root）
</head>
<body>
  ├── <nav>                  導覽列（sticky，含雙語切換）
  ├── <section class="hero"> Hero 區（標語 + 實機 UI 模擬視窗）
  ├── <section id="features"> 七大功能（grid 卡片）
  ├── <section id="versions"> M1 vs PRO 對照表
  ├── <section id="tech">     技術能力卡片
  ├── <section id="changelog"> 韌體版本歷史
  ├── <section id="about">    工作室介紹
  ├── <section id="contact">  聯絡資訊
  ├── <footer>
  └── <script>
       ├── i18n 物件（zh + en 兩個語系）
       ├── applyLang() 語系切換
       ├── setInterval 數據動畫
       ├── IntersectionObserver 滾動顯現
       └── PRODUCT_LIVE 旗標（控制購買按鈕）
     </script>
</body>
```

---

## 5. 常見維護任務

### 任務 1：發布新韌體版本後更新網站 changelog

**頻率**：每次 MotorLab 韌體發版時。

**步驟**：
1. 開啟 `index.html`
2. 找到 `<!-- v3.0.8 -->`（最新版本標記）區塊
3. 參考 `CHANGELOG_TEMPLATE.md` 在它**上方**新增新版本區塊
4. 把舊版本的 `class="version-badge latest"` 中的 `latest` 移除
5. 新版本 changelog 內容要從韌體 repo 的 `HANDOFF.md` 或使用者口述取得，**不要自己編**
6. 同步在 i18n 物件中新增中英文翻譯
7. 全站搜尋舊版號（例如 `v3.0.8`）並替換到新版號，需要改的地方：
   - Hero badge：`'hero.badge': '系統運作中 · vX.X.X'`
   - Footer：`韌體 vX.X.X`
   - About stats：`<div class="stat-num">vX.X.X</div>`
   - og-image.svg 中的版本號標籤（改完要重新生成 PNG）
   - sitemap.xml 中的 `<lastmod>`
8. 本機預覽確認沒問題：`python -m http.server 8000`
9. `git add . && git commit -m "Update changelog to vX.X.X" && git push`

**注意事項**：
- changelog 變更類型只有四種：`change-new` / `change-fix` / `change-improve` / `change-security`
- 不要為了好看而虛構功能，使用者很在意 changelog 的真實性

### 任務 2：產品上線開放購買

當 MotorLab 開始在 Gumroad 賣時：

1. `index.html` 底部找到 `const PRODUCT_LIVE = false;`，改 `true`
2. Hero 區塊找到 `<a href="#" class="btn btn-purchase" id="purchase-btn">`
3. 把 `href="#"` 改為實際 Gumroad 商品 URL
4. （選用）如果想做 Gumroad overlay：
   - 在 `</head>` 前加 `<script src="https://gumroad.com/js/gumroad.js"></script>`
   - 給按鈕加 class `gumroad-button`
5. Contact 區塊文案可能要從「目前處於最後發行準備階段」改為「現已開放購買」
6. Commit & push

### 任務 3：綁定自訂網域（motorlab.tw）

詳見 `DEPLOYMENT.md` 第 "綁定自訂網域" 一節。
重點：DNS A record 指向 GitHub Pages IP，然後加 `CNAME` 檔案，在 Pages 設定中填網域。

### 任務 4：加實機產品照片

當有實機照片後：
1. 把照片放到 `/images/` 資料夾（這個資料夾還不存在，需要建立）
2. 在 Hero 區塊把現有的 `.device-mockup` div 替換為 `<img>`，**但保留** Nord 風格的外框與標題列
3. 或新增一個 `#gallery` 區段放多張產品照
4. 圖片務必壓縮（用 `cwebp` 轉 WebP 格式，並備 PNG fallback）

### 任務 5：使用者要求改某段文案

1. 先確認是哪個區塊、哪個語言
2. 找到對應的 `data-i18n` key
3. **必須同時改 i18n 物件中的 zh 和 en 兩份**，否則語言切換會錯位
4. 如果是動態內容（如 hero 標題），記得保留 `<span class="accent">` 之類的 HTML 結構

### 任務 6：新增區塊或卡片

**新增 feature card**：
1. 複製現有的 `.feature-card` 區塊
2. 修改 icon SVG、標題 `data-i18n`、描述、tag
3. 在 i18n 物件兩個語言版本都新增對應 key
4. PRO 限定功能要加 `pro-only` class

**新增完整 section**：
- 先想清楚為什麼需要這個 section（YAGNI）
- 確認跟使用者討論過再動手
- 風格必須遵循 Nord 配色 + 既有間距節奏（section padding: 80px 0）

---

## 6. 設計約束（修改時的不變式）

修改 CSS 時請保留以下原則：

1. **所有顏色都用 CSS 變數**（`var(--accent-cyan)`），不要 hardcode hex 值
2. **間距用 8 的倍數**（8px / 16px / 24px / 32px / 48px / 64px / 80px）
3. **字體大小**用 `clamp()` 做響應式縮放
4. **`max-width: 1180px`** 為主容器寬度，不要任意更動
5. **`.fade-in` + IntersectionObserver** 是滾動動畫的標準做法，新區塊也要加
6. **手機斷點 880px**，重要區塊在這個寬度以下要重排
7. **不用 `!important`**（除非真的不得已，並寫註解說明）

---

## 7. SEO / 社群分享檢查

### 改完內容上線後檢查：

| 工具 | 用途 |
|---|---|
| https://www.opengraph.xyz/ | 預覽 OG 圖在 FB/LINE/Twitter 的顯示 |
| https://pagespeed.web.dev/ | 效能評分（目標：行動 > 90） |
| https://validator.w3.org/ | HTML 結構驗證 |
| https://search.google.com/test/rich-results | 結構化資料驗證 |

### 已實作的 SEO

- ✅ semantic HTML (`<nav>`, `<section>`, `<footer>`)
- ✅ Open Graph + Twitter Card
- ✅ JSON-LD 結構化資料（Organization schema）
- ✅ robots.txt + sitemap.xml
- ✅ meta description + keywords
- ✅ favicon 多尺寸（含 Apple Touch Icon）
- ✅ `<html lang>` 隨語系切換
- ✅ hreflang（透過 `og:locale:alternate`）

### 未實作（未來可加）

- ❌ AMP（不需要）
- ❌ Service Worker / PWA（網站靜態，沒必要離線使用）
- ❌ 多語子目錄（`/zh/`, `/en/`）— 目前是 JS 切換，SEO 效益較低但維護簡單

---

## 8. 設計檢查清單（任何重大改動後跑一次）

- [ ] 中文版每個區塊文字都讀得通順
- [ ] 英文版每個區塊文字都讀得通順（**不只翻譯，要有英文母語感**）
- [ ] 中英切換無錯位、無漏翻
- [ ] 手機（375px 寬）排版正常，無水平捲軸
- [ ] 平板（768px 寬）排版正常
- [ ] 桌機（1440px 寬）排版正常
- [ ] Hero 區的數據動畫正常跳動
- [ ] 滾動時各 section 有 fade-in 動畫
- [ ] 所有 `#xxx` 內部連結點下去能正確滾到對應區塊
- [ ] 404 頁面也用同樣配色（風格一致）
- [ ] 開無痕視窗看（避免快取造成誤判）
- [ ] Lighthouse 效能 > 90、無障礙 > 95

---

## 9. 不要做的事

- ❌ **不要主動建議改設計風格**（使用者已決定 Nord 主題）
- ❌ **不要主動建議引入框架**（單檔策略已決定）
- ❌ **不要主動建議加 build / CI**（YAGNI）
- ❌ **不要在 changelog 編造變更內容**（必須對齊真實韌體版本）
- ❌ **不要署名**（純品牌路線）
- ❌ **不要露出硬體元件型號**（避免被反推 BOM）
- ❌ **不要刪減 `data-i18n` 標記**（雙語切換的核心機制）
- ❌ **不要把 emoji 加回介面**（v3.0.7~v3.0.8 已刻意移除）
- ❌ **不要直接套用 LLM 推測的「目前流行設計」**（使用者不要 AI 感）

---

## 10. 工具與指令

### 本機預覽
```powershell
cd C:\Projects\MotorLab-site
python -m http.server 8000
# 開 http://localhost:8000
```

### Git 操作
```powershell
git status              # 看當前改動
git add .
git commit -m "描述"
git push                # GitHub Pages 自動部署
```

### 重新生成 OG 圖 PNG（改完 og-image.svg 後）

需要 Python + cairosvg：
```powershell
pip install cairosvg
python -c "import cairosvg; cairosvg.svg2png(url='og-image.svg', write_to='og-image.png', output_width=1200, output_height=630)"
```

### 重新生成 favicon PNG（改完 favicon.svg 後）
```powershell
python -c "import cairosvg; cairosvg.svg2png(url='favicon.svg', write_to='favicon-32.png', output_width=32, output_height=32); cairosvg.svg2png(url='favicon.svg', write_to='favicon-192.png', output_width=192, output_height=192); cairosvg.svg2png(url='favicon.svg', write_to='apple-touch-icon.png', output_width=180, output_height=180)"
```

### 批次更新版本號
```powershell
# 從 v3.0.8 更新到 v3.0.9
(Get-Content index.html) -replace 'v3\.0\.8', 'v3.0.9' | Set-Content index.html
(Get-Content sitemap.xml) -replace '2026-05-18', '2026-05-25' | Set-Content sitemap.xml
```

---

## 11. 重要參考資料

### 11.1 韌體 repo HANDOFF
位置：`C:\Projects\MotorLab\HANDOFF.md`

任何時候要更新 changelog 都應該先看一下韌體 HANDOFF 是不是有新的里程碑記錄。

### 11.2 韌體 USER_MANUAL
位置：`C:\Projects\MotorLab\USER_MANUAL.md`

網站的功能描述文案是基於這份手冊改寫的。新增功能介紹時也參考這份。

### 11.3 韌體 web_pages.h
位置：`C:\Projects\MotorLab\src\web_pages.h`

實機 Web UI 的完整 HTML 原始碼。網站 Hero 區的「實機 UI 模擬視窗」風格就是從這份抽出來的：
- `body` 樣式
- `.data-grid` / `.data-cell` 樣式
- `.status-box` 樣式
- `h1`、`h2` 字級

未來如果實機 UI 大改版（例如改主題色），網站也要跟著更新以保持品牌一致。

### 11.4 firmware release repo
位置：`https://github.com/jrwei6666-bot/MotorLab-firmware`（Public）

每個釋出的韌體版本都有 tag（v3.0.0、v3.0.5、v3.0.6...）。網站 changelog 的版本號要與這裡的 tag 對齊。

---

## 12. 已知尚未處理的事

依優先順序排：

1. **產品實機照片** — 目前 Hero 用 CSS 模擬視窗代替，等使用者拍好照片後可替換
2. **Gumroad 商品連結** — 等使用者開好 Gumroad 商品後，按任務 2 流程啟用
3. **自訂網域 `motorlab.tw`** — 等使用者決定要買網域後執行
4. **產品 Demo 影片** — 可以在 features 區塊嵌入 YouTube
5. **FAQ 區段** — 使用者手冊裡有完整 FAQ，未來可整理上網站

---

**END OF HANDOFF**

> 寫程式給未來的自己看；寫 HANDOFF 給未來的對話看。
> 兩者都要簡短、精準、不要丟鍋。

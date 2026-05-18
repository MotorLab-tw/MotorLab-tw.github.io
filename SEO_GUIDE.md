# MotorLab.tw SEO 操作指南

> 程式碼層面的 SEO 已全部優化完成。本文件說明**你需要自己操作**的步驟。
> 完整做完這份指南，你的網站才會真正出現在 Google 搜尋結果中。

---

## 為什麼還需要手動操作？

很多人以為「網站做好就會被 Google 自動收錄」，這是錯的。**搜尋引擎需要主動被告知這個網站存在**，否則新站可能 3-6 個月都不會被發現。

完成下面步驟後：
- ⏱ **1-3 天**：Google 開始抓取你的網站
- ⏱ **1-2 週**：你的網站開始出現在搜尋結果中
- ⏱ **1-3 個月**：搜尋排名穩定下來

---

## 步驟 1：提交 Google Search Console（最重要）⭐⭐⭐

這是讓 Google 認識你的網站、並提供搜尋數據分析的官方工具。免費。

### 1.1 開通 Search Console

1. 打開 [https://search.google.com/search-console](https://search.google.com/search-console)
2. 用你的 Google 帳號登入（建議用 `motorlab.tw@gmail.com`）
3. 點 **「新增資源」** 或 **「+ Add property」**
4. 選擇右邊的 **「網址前置字元」**（不是左邊的「網域」，後者需要 DNS 驗證較麻煩）
5. 輸入：`https://motorlab-tw.github.io/`
6. 按 **「繼續」**

### 1.2 驗證所有權

Google 會給你幾種驗證方法。**最簡單的方法**是：

#### 方法 A：HTML 標籤驗證（推薦）

1. Google 會給你一段類似這樣的 meta 標籤：
   ```html
   <meta name="google-site-verification" content="abc123XYZ..." />
   ```

2. 複製這整段 meta 標籤

3. 進入 GitHub repo → `index.html` → 編輯
4. `Ctrl + F` 搜尋 `<meta name="viewport"`
5. 在這一行**下方**貼上 Google 給你的 meta 標籤
6. Commit changes
7. 等 1-2 分鐘 GitHub Pages 部署
8. 回到 Search Console 點 **「驗證」**

#### 方法 B：HTML 檔案驗證（替代方案）

1. Google 給你一個 `googleXXXXXX.html` 檔案
2. 下載這個檔案
3. 用 GitHub 網頁上傳到 repo 根目錄（與 index.html 同層）
4. Commit
5. 等部署完成後回 Search Console 點驗證

### 1.3 提交 Sitemap

驗證成功後，**最重要的下一步**：

1. 在 Search Console 左側選單點 **「Sitemap」**（網站地圖）
2. 在「新增 Sitemap」欄位填入：`sitemap.xml`
3. 按 **「提交」**
4. 狀態應該顯示「成功」

**完成這一步後，Google 會在 1-3 天內開始抓取你的網站。**

### 1.4 請求索引（加速）

1. 在 Search Console 上方搜尋框輸入：`https://motorlab-tw.github.io/`
2. 按 Enter
3. 出現分析報告後，點 **「要求建立索引」**
4. 等 1-2 分鐘的測試
5. 完成後 Google 會優先抓取這個網址

---

## 步驟 2：提交 Bing Webmaster Tools ⭐⭐

Bing 雖然市占率比 Google 低，但很多人用（特別是用 Edge 瀏覽器的人，預設搜尋是 Bing）。

1. 打開 [https://www.bing.com/webmasters](https://www.bing.com/webmasters)
2. 用 Microsoft 帳號或 Google 帳號登入
3. **直接從 Google Search Console 匯入**（最方便）
   - 登入後選 「Import from GSC」
   - 授權 Bing 讀取你的 GSC 資料
   - 一鍵把所有設定同步過來

或手動：
1. 新增網站 `https://motorlab-tw.github.io/`
2. 同樣的方式驗證（meta 標籤或檔案）
3. 提交 sitemap：`sitemap.xml`

---

## 步驟 3：驗證 SEO 是否正確 ⭐

打開以下工具，貼上你的網址 `https://motorlab-tw.github.io/`，看評分：

### 3.1 結構化資料驗證

🔗 https://search.google.com/test/rich-results

- 應該顯示 ✅ **3 項有效項目**：Organization、WebSite、Product
- 任何項目顯示警告或錯誤，截圖告訴我

### 3.2 行動裝置友善測試

🔗 https://search.google.com/test/mobile-friendly

- 輸入網址 → 等測試 → 應該顯示「網頁適合行動裝置」

### 3.3 OG 卡片預覽

🔗 https://www.opengraph.xyz/

- 預覽 FB、Twitter、LINE 分享時的卡片樣式
- 確認標題、描述、圖片都正確顯示

### 3.4 PageSpeed 效能評分

🔗 https://pagespeed.web.dev/

- 行動裝置分數應該 > 85
- 桌機分數應該 > 95
- 如果分數很低，告訴我，我幫你優化

### 3.5 HTML 標準驗證

🔗 https://validator.w3.org/

- 輸入網址，看有沒有 HTML 錯誤

---

## 步驟 4：建立反向連結（Backlinks）⭐⭐

Google 衡量網站重要性的關鍵指標。簡單說：**有多少別的網站連到你**，就代表你有多重要。

### 4.1 快速可做的

| 平台 | 怎麼加 |
|---|---|
| **GitHub 個人簡介** | MotorLab-tw profile → 編輯 → bio 加上 `https://motorlab-tw.github.io/` |
| **GitHub 主要 repo** | MotorLab-tw.github.io repo → 右上 About → 加 Website URL |
| **個人 Twitter/X** | 個人簡介 url 欄填網址 |
| **個人 Facebook** | 簡介加上網址 |
| **PTT 簽名檔** | 如果你有 PTT 帳號 |

### 4.2 中長期目標

| 平台 | 怎麼加 |
|---|---|
| **四驅博士論壇** | 註冊帳號，在簽名檔或自我介紹放網址 |
| **田宮迷你四驅車臺灣社團（FB）** | 發文時自然提到（不要硬廣告） |
| **巴哈姆特模型版** | 開新討論串介紹工作室產品 |
| **Reddit r/Mini4WD** | 國際社群，發英文介紹 |
| **Mini 4WD 玩家部落格** | 找幾個寫四驅車的部落客，請他們試用後寫評測 |

### 4.3 內容行銷（最有效但要時間）

未來可以考慮：
- 寫技術文章「Mini 4WD 馬達磨合科學原理」「FFT 頻譜判讀指南」
- 拍 YouTube 開箱影片
- 把實機測試數據做成圖表發到社群

---

## 步驟 5：設定 Google Analytics（追蹤訪客）⭐

讓你看得到「有多少人來、來自哪裡、看了哪些內容」。

### 5.1 開通 GA4

1. 打開 [https://analytics.google.com](https://analytics.google.com)
2. 用同一個 Google 帳號登入
3. 建立資源：
   - 帳戶名稱：`MotorLab`
   - 資源名稱：`MotorLab.tw 官網`
   - 時區：台北 GMT+8
   - 貨幣：TWD
4. 選擇平台：**網站**
5. 網址：`https://motorlab-tw.github.io/`
6. 完成後拿到一段 GA4 追蹤碼 `G-XXXXXXXXXX`

### 5.2 把追蹤碼加進網站

1. 進 GitHub 編輯 `index.html`
2. `Ctrl + F` 搜尋 `</head>`
3. 在 `</head>` 上方貼入 GA4 程式碼：

```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

**記得把兩個 `G-XXXXXXXXXX` 都改成你的實際 GA4 ID**。

4. Commit changes
5. 24 小時後 GA4 開始有數據

### 5.3 隱私友善的替代方案：Plausible

如果你不喜歡 Google Analytics（追蹤多、隱私問題），可以用：
- [Plausible](https://plausible.io)（付費，$9/月，超輕量）
- [Umami](https://umami.is)（可自架，免費）
- [Cloudflare Web Analytics](https://www.cloudflare.com/web-analytics/)（免費，無 cookie）

---

## 步驟 6：當前 SEO 狀態檢查表

完成以上步驟後，回來打勾：

- [ ] Google Search Console 已驗證
- [ ] Sitemap 已提交（GSC 顯示成功）
- [ ] Google 「網址檢查」已通過
- [ ] Bing Webmaster Tools 已設定
- [ ] Rich Results Test 通過（3 項結構化資料）
- [ ] Mobile-Friendly Test 通過
- [ ] PageSpeed 行動分數 > 85
- [ ] GitHub 個人簡介有放網址
- [ ] GitHub repo About 有放網址
- [ ] (選用) Google Analytics 已設定
- [ ] (選用) 加入 1-2 個社群平台簽名/簡介連結

---

## 常見問題

### Q: 多久才能在 Google 搜到？

| 階段 | 時間 |
|---|---|
| 提交 Search Console 後第一次被抓取 | 1-3 天 |
| 開始出現在「搜尋網址」結果（搜 `site:motorlab-tw.github.io`） | 3-7 天 |
| 出現在「搜尋品牌名」結果（搜 `MotorLab.tw`） | 1-3 週 |
| 出現在「搜尋關鍵字」結果（搜 `迷你四驅車馬達磨合`） | 1-3 個月（需要好排名才會排前面） |

### Q: 為什麼搜「MotorLab」找不到我？

新站常見狀況，原因可能是：
1. Google 還沒索引（最常見）→ 等
2. 已索引但排名很後面 → 試試 `MotorLab.tw` 或 `site:motorlab-tw.github.io`
3. 「motorlab」這個詞太通用，有競爭對手

### Q: 要不要買網域？對 SEO 有幫助嗎？

短期沒幫助，長期有：
- `motorlab.tw` 比 `motorlab-tw.github.io` 短、好記
- 自有網域看起來更專業
- 未來如果要換 hosting，網址不變
- **不影響 SEO 排名**（Google 不會因為你用 GitHub Pages 而扣分）

買網域後，照 `DEPLOYMENT.md` 中的「綁定自訂網域」章節做。

### Q: SEO 多久要做一次？

設定好之後大致是「設定一次，長期受益」。但每個月可以：
- 看 GSC 看有沒有新錯誤
- 看 GA 看流量變化
- 發新韌體版本時更新 sitemap 的 `<lastmod>` 日期
- 出現新功能時更新 JSON-LD 的 `featureList`

---

## 進階：未來想做更深層的 SEO

當網站有了基本流量後，可以做：

1. **內容行銷**：開部落格寫長文章（最有效但工作量大）
   - 「Mini 4WD 馬達磨合：5 個常見錯誤與正確做法」
   - 「FFT 頻譜分析馬達的入門教學」
   - 「為什麼軸承衰減時間 τ 是評估馬達好壞的關鍵指標」

2. **影片 SEO**：拍 YouTube 影片 → 把影片 embed 到網站
   - YouTube 是世界第二大搜尋引擎
   - 影片頁面在 Google 搜尋結果常常排很前面

3. **本地 SEO**：如果你想接台灣本地客戶
   - 在 Google Business Profile 註冊
   - 加 LocalBusiness JSON-LD schema

4. **多語擴展**：如果想攻日本市場
   - 加 `ミニ四駆` 為主的日文版頁面
   - 在 hreflang 加上 `ja-JP`

---

## 給未來 Claude Code 的提醒

如果使用者問「網站 SEO 怎麼樣」「想優化 SEO」：

1. 先看 `HANDOFF.md` 的 **D11. SEO 優化基礎建設**
2. 確認程式碼層面已實作項目（canonical、JSON-LD 三套等）
3. 如果還沒提交 GSC，引導使用者照這份指南操作
4. 不要主動建議「換掉 GitHub Pages」「改用 Next.js for SEO」等違反 D2/R2 的方案

GitHub Pages + 靜態 HTML 對 SEO 是**完全足夠**的，網站速度甚至比很多動態網站更好。

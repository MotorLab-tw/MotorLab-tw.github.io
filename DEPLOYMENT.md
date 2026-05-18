# MotorLab.tw 部署指南

完整的 GitHub Pages 部署流程，從零開始到網站上線。

---

## 部署前置準備

確認你有：
- 已建立的 `MotorLab-tw` GitHub 帳號
- 在本機已設定好 Git 與該帳號的認證（SSH key 或 PAT）
- 本機已 clone 或下載這份網站專案

---

## 第一次部署（從零開始）

### 步驟 1：建立 GitHub Repo

1. 用 `MotorLab-tw` 帳號登入 GitHub
2. 右上角 `+` → **New repository**
3. **Repository name** 必須**一字不差**輸入：`MotorLab-tw.github.io`
   - 注意：repo 名稱要等於 `<帳號名>.github.io` 才能拿到根網址
4. **Public**（GitHub Pages 免費版要公開）
5. **不要勾** "Add a README file"（我們已有）
6. **Create repository**

### 步驟 2：本機推送

```bash
cd 網站專案目錄
git init
git add .
git commit -m "Initial commit: MotorLab.tw website"
git branch -M main
git remote add origin https://github.com/MotorLab-tw/MotorLab-tw.github.io.git
git push -u origin main
```

如果用 SSH key：

```bash
git remote add origin git@github.com:MotorLab-tw/MotorLab-tw.github.io.git
```

### 步驟 3：啟用 GitHub Pages

1. 進入剛建的 repo
2. **Settings → Pages**（左側選單）
3. **Source** 選 `Deploy from a branch`
4. **Branch** 選 `main`、資料夾選 `/ (root)`
5. **Save**

### 步驟 4：等待部署

- 1-2 分鐘後網站會在 `https://motorlab-tw.github.io` 上線
- 在 repo 首頁右側可以看到部署狀態
- 第一次部署完成後，每次 `git push` 都會自動觸發更新

---

## 之後的更新流程

任何內容修改：

```bash
# 1. 修改檔案
nano index.html

# 2. 確認改動
git status
git diff

# 3. 提交並推送
git add .
git commit -m "簡短描述本次變更"
git push
```

1-2 分鐘後上線。

---

## 本機預覽（推送前先看效果）

任何一台電腦都可以開瀏覽器直接打開 `index.html` 預覽，但有些功能（例如 fetch、絕對路徑連結）需要伺服器才能正常運作。

### 方法 A：用 Python 內建 HTTP 伺服器

```bash
cd 網站專案目錄
python -m http.server 8000
```

打開 `http://localhost:8000`

### 方法 B：VS Code Live Server

裝 "Live Server" 擴充套件 → 右鍵 `index.html` → "Open with Live Server"

---

## 綁定自訂網域（未來想用 motorlab.tw 之類的）

### 步驟 1：買網域

從任一網域商買網域（GoDaddy、Cloudflare Registrar、Namecheap 等）。

### 步驟 2：設定 DNS

在網域商的 DNS 管理介面加上：

**Apex 網域（motorlab.tw）的 A 記錄：**
```
@   A   185.199.108.153
@   A   185.199.109.153
@   A   185.199.110.153
@   A   185.199.111.153
```

**www 子網域的 CNAME：**
```
www   CNAME   motorlab-tw.github.io.
```

### 步驟 3：在 repo 加 CNAME 檔案

把 `CNAME.example` 改名為 `CNAME`（沒有副檔名），內容只寫網域：

```
motorlab.tw
```

Commit + push。

### 步驟 4：在 GitHub Pages 設定中填入

Settings → Pages → Custom domain → 填入 `motorlab.tw` → Save

等 DNS 生效（通常幾分鐘到幾小時），勾選 "Enforce HTTPS"。

---

## 故障排除

### 問題：推送被拒（rejected）

```
! [rejected]   main -> main (fetch first)
```

通常是遠端有改動本機沒拿到。先 `git pull --rebase` 再 push。

### 問題：網站上線後 404

- 確認 repo 名稱**完全等於** `MotorLab-tw.github.io`（大小寫不影響但拼字要對）
- 確認 `Settings → Pages` 有設定 Source 為 main 分支
- 確認根目錄有 `index.html`（不是放在子資料夾）
- 等 5 分鐘再試（DNS 與 CDN 可能還沒同步）

### 問題：CSS / favicon 沒載入

- 確認 HTML 裡所有路徑都用 `/` 開頭（絕對路徑）或相對路徑
- 確認 `.nojekyll` 檔案存在（沒有的話 GitHub 會用 Jekyll 處理，可能跳過某些檔案）

### 問題：改了東西但網站沒更新

- 開啟 GitHub repo → Actions 分頁，看 "pages-build-deployment" 是否成功
- 失敗的話點進去看錯誤訊息
- 如果是 OK 但你看到舊版：用 Ctrl+Shift+R 強制重整、或開無痕視窗測試

### 問題：OG 圖在 Facebook/LINE 預覽錯誤

- 第一次貼網址時平台會快取，之後改了圖不會立刻更新
- Facebook：用 [Sharing Debugger](https://developers.facebook.com/tools/debug/) 強制重新抓
- LINE：在 LINE 內貼一次新網址會自動重抓

---

## 上線後檢查清單

- [ ] 打開 https://motorlab-tw.github.io 確認首頁正常
- [ ] 點導覽列每個連結是否都能跳轉
- [ ] 中英文切換功能正常
- [ ] 數據動畫有跳動（電流 / 轉速數字）
- [ ] 滾動時 feature cards 有 fade-in 動畫
- [ ] 手機/平板 RWD 排版正常
- [ ] 隨便輸入錯網址（例如 `/abc`）會跳 404 頁面
- [ ] 在 [Open Graph Debugger](https://www.opengraph.xyz/) 貼網址確認預覽圖
- [ ] 在 [Google PageSpeed Insights](https://pagespeed.web.dev/) 跑分（目標：行動裝置 > 90）

---

## 進階：加上分析工具

### Plausible（隱私友善、免費起步）

在 `</head>` 前加上：

```html
<script defer data-domain="motorlab-tw.github.io" src="https://plausible.io/js/script.js"></script>
```

### Google Analytics 4

在 `</head>` 前加上你的 GA4 追蹤碼。

---

## 進階：CI/CD 自動部署

GitHub Pages 本身就有自動部署，不需要額外設定 CI。但如果未來想加上：

- **自動最小化 HTML / CSS / JS**
- **自動生成多語版本**
- **自動更新 sitemap 的 lastmod**

可以建立 `.github/workflows/build.yml`，目前不需要。

# MotorLab.tw — 官方網站

> Mini 4WD Performance Lab · 工作室官方網站原始碼

這個 repo 是 [https://motorlab-tw.github.io](https://motorlab-tw.github.io) 的原始碼。
單一 HTML 檔案,無建置流程,推上 `main` 分支即自動部署。

---

## 技術棧

- 純 HTML + CSS + JavaScript(無框架、無建置工具)
- 設計風格與 MotorLab 韌體實機 Web UI 一致(Nord 主題配色)
- 雙語切換(繁體中文 / English)
- 完全響應式(手機、平板、桌機)
- 部署:GitHub Pages(免費、自動 HTTPS)

---

## 部署到 GitHub Pages

### 第一次設定

1. 把這份程式碼 push 到 `MotorLab-tw/MotorLab-tw.github.io` repo 的 `main` 分支
2. 進入 repo 的 **Settings → Pages**
3. **Source** 選擇 `Deploy from a branch`
4. **Branch** 選 `main`、資料夾選 `/ (root)`
5. 按 **Save**

幾分鐘後網站就會在 `https://motorlab-tw.github.io` 上線。

### 更新內容

直接編輯 `index.html`,commit + push,GitHub Pages 會在 1-2 分鐘內自動更新。

```bash
git add index.html
git commit -m "更新 changelog v3.0.9"
git push
```

---

## 產品上線時要做的事

當 MotorLab 正式開賣時,需要打開兩個地方:

### 1. 顯示 Gumroad 購買按鈕

在 `index.html` 最底下找到這段:

```javascript
const PRODUCT_LIVE = false;
```

改成:

```javascript
const PRODUCT_LIVE = true;
```

並在 hero 區的購買按鈕 `<a href="#" class="btn btn-purchase" ...>` 把 `href="#"` 換成實際的 Gumroad 商品連結。

### 2. (選用) 加上 Gumroad 內嵌 Script

如果想做 Gumroad 內嵌結帳(overlay),在 `</head>` 前加上:

```html
<script src="https://gumroad.com/js/gumroad.js"></script>
```

並把按鈕的 `class` 加上 `gumroad-button`。

---

## 新版本發布時的 changelog 更新流程

每次韌體發新版,記得回來更新網站的 changelog:

1. 在 `index.html` 找到 `<!-- v3.0.8 -->` 那段
2. 複製整個 `<div class="changelog-item">...</div>`
3. 貼到最上面當作新版本,把舊的 `latest` class 移除
4. 同步更新 footer 的版本號、hero badge 的版本號
5. 中英文兩份文案都記得加(在最底下的 `i18n` 物件)

---

## 設計檔案位置對應

| 區塊 | HTML id | 中文標題 |
|---|---|---|
| Hero | `.hero` | 首頁標語 + 實機 UI 模擬 |
| Features | `#features` | 七大核心功能 |
| Versions | `#versions` | M1 / PRO 對照表 |
| Tech | `#tech` | 分析技術介紹 |
| Changelog | `#changelog` | 韌體版本歷史 |
| About | `#about` | 工作室介紹 |
| Contact | `#contact` | 聯絡資訊 |

---

## 未來可考慮的擴充

- [ ] 加上實機產品照片(目前是 CSS 模擬視窗)
- [ ] 加上實機 Demo 影片(YouTube embed)
- [ ] 加上常見問題 FAQ 區塊
- [ ] 綁定自訂網域(例如 `motorlab.tw`)
- [ ] 加上 Open Graph 預覽圖
- [ ] 加上 Google Analytics 或 Plausible 流量分析

---

## 授權

網站內容版權 © 2026 MotorLab · All rights reserved

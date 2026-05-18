# Changelog 區塊範本

當你發布新韌體版本（例如 v3.0.9）時，把下面這段貼到 `index.html` 的 `<div class="changelog">` 區塊**最上面**，並把原本的 `latest` class 移到新版本上。

## HTML 範本

```html
<!-- vX.X.X -->
<div class="changelog-item">
  <div class="changelog-meta">
    <span class="version-badge latest">vX.X.X</span>
    <span class="changelog-date">YYYY-MM-DD</span>
  </div>
  <div class="changelog-content">
    <h4 data-i18n="cl.vXXX.title">版本標題</h4>
    <ul>
      <li><span class="change-type change-new" data-i18n="cl.NEW">新增</span><span data-i18n="cl.vXXX.l1">第一項變更內容</span></li>
      <li><span class="change-type change-fix" data-i18n="cl.FIX">修正</span><span data-i18n="cl.vXXX.l2">第二項變更內容</span></li>
      <li><span class="change-type change-improve" data-i18n="cl.IMPROVE">改進</span><span data-i18n="cl.vXXX.l3">第三項變更內容</span></li>
      <li><span class="change-type change-security" data-i18n="cl.SECURITY">安全</span><span data-i18n="cl.vXXX.l4">第四項變更內容</span></li>
    </ul>
  </div>
</div>
```

## 變更類型對照表

| 類型 | CSS class | 中文 | 英文 | 顏色 |
|---|---|---|---|---|
| 新增功能 | `change-new` | 新增 | NEW | 綠色 |
| 錯誤修正 | `change-fix` | 修正 | FIX | 黃色 |
| 改進優化 | `change-improve` | 改進 | IMPROVE | 青色 |
| 安全強化 | `change-security` | 安全 | SECURITY | 紫色 |

## i18n 翻譯範本

在 `index.html` 底部 `i18n` 物件中，分別在 `zh` 與 `en` 區塊加上對應 key：

```javascript
// 中文 zh:
'cl.vXXX.title': '版本標題',
'cl.vXXX.l1': '第一項變更內容',
'cl.vXXX.l2': '第二項變更內容',
'cl.vXXX.l3': '第三項變更內容',
'cl.vXXX.l4': '第四項變更內容',

// English en:
'cl.vXXX.title': 'Version Title',
'cl.vXXX.l1': 'First change description',
'cl.vXXX.l2': 'Second change description',
'cl.vXXX.l3': 'Third change description',
'cl.vXXX.l4': 'Fourth change description',
```

## 還要記得更新的地方

新版本上線時，**搜尋並取代**整份 index.html 中所有的版本號：

1. Hero badge：`'hero.badge': '系統運作中 · vX.X.X'`
2. Footer：`<span data-i18n="footer.firmware">韌體</span> vX.X.X`
3. About 區塊統計：`'about.s2': '當前韌體版本'` 對應的數字 `<div class="stat-num">vX.X.X</div>`
4. og-image.svg 中的 `v3.0.8` → 新版號（然後重新生成 PNG）
5. sitemap.xml 中的 `<lastmod>` 日期

或者用 search/replace 一次處理：

```bash
# 假設要從 v3.0.8 更新到 v3.0.9
sed -i 's/v3\.0\.8/v3.0.9/g' index.html sitemap.xml og-image.svg
```

## 改完後的部署

```bash
git add .
git commit -m "Update changelog to v3.0.9"
git push
```

GitHub Pages 會在 1-2 分鐘內自動更新。

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MotorLab.tw 多語言靜態頁面產生器
================================
讀取母版 index.src.html(含三語 i18n),產出 3 個獨立語言版本:
  /index.html        繁體中文版
  /en/index.html     英文版
  /ja/index.html     日文版

每個檔案的 HTML 原始碼直接就是該語言文字,
搜尋引擎一抓即看到正確語言 → SEO 摘要正確。

用法:  python build.py
"""

import re
import json
import os
import sys

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("錯誤:需要 beautifulsoup4。請執行: pip install beautifulsoup4 lxml")
    sys.exit(1)

# ============================================================
# 設定
# ============================================================
SITE = "https://motorlab-tw.github.io"
SRC = "index.src.html"          # 母版檔名

# 各語言設定
LANGS = {
    "zh": {
        "out": "index.html",            # 輸出路徑(相對根目錄)
        "html_lang": "zh-TW",
        "og_locale": "zh_TW",
        "url": SITE + "/",
        "dir_prefix": "/",              # 此語言版本的根路徑
    },
    "en": {
        "out": "en/index.html",
        "html_lang": "en",
        "og_locale": "en_US",
        "url": SITE + "/en/",
        "dir_prefix": "/en/",
    },
    "ja": {
        "out": "ja/index.html",
        "html_lang": "ja",
        "og_locale": "ja_JP",
        "url": SITE + "/ja/",
        "dir_prefix": "/ja/",
    },
}

# 各語言的 SEO meta(title / description / og)
# 這是搜尋結果摘要會顯示的文字 — 每語言獨立撰寫
SEO = {
    "zh": {
        "title": "MotorLab — Mini 4WD® 馬達磨合測試系統 | 精密馬達診斷工作室",
        "description": "MotorLab — 專為 Mini 4WD® 玩家打造的精密馬達磨合測試系統。九大專業功能:十階段可程式化磨合、AI 健康管理、FFT 頻譜、軸承 τ 衰減、CV 電刷穩定診斷、三層安全保護(抗 EMI、< 100 ms 急停、Watchdog 自動復原)、OTA 線上更新。讓馬達調校可量化。",
        "og_title": "MotorLab — Mini 4WD® 馬達磨合測試系統",
        "og_desc": "為每一顆 Mini 4WD® 馬達建立可量化的健康指紋。九大專業功能:十階段磨合、AI 健康管理、軸承衰減分析、電刷穩定診斷、三層安全保護機制。",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "為每一顆 Mini 4WD® 馬達建立可量化的健康指紋",
    },
    "en": {
        "title": "MotorLab — Mini 4WD® Motor Break-in & Diagnostics System",
        "description": "MotorLab — a precision motor break-in and testing system built for Mini 4WD® racers. Nine professional tools: 10-stage programmable break-in, AI health management, FFT spectrum, bearing tau decay, CV brush stability diagnostics, triple-layer safety protection (EMI shielding, < 100 ms overcurrent cutoff, watchdog recovery) and OTA updates. Make every tune measurable.",
        "og_title": "MotorLab — Mini 4WD® Motor Break-in & Test System",
        "og_desc": "Build a measurable health fingerprint for every Mini 4WD® motor. Nine professional tools: 10-stage break-in, AI health management, bearing decay analysis, brush stability diagnostics and triple-layer safety protection.",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "Build a measurable health fingerprint for every Mini 4WD® motor",
    },
    "ja": {
        "title": "MotorLab — Mini 4WD® モーター慣らし・テストシステム | 精密モーター診断スタジオ",
        "description": "MotorLab — Mini 4WD® プレイヤーのために設計された精密モーター慣らし・測定システム。9 つのプロ機能:10 段階プログラム慣らし、AI 健康管理、FFT スペクトル、ベアリング τ 減衰、CV ブラシ安定診断、三層安全保護(耐 EMI、< 100 ms 緊急停止、Watchdog 自動復旧)、OTA オンライン更新。すべての調整を定量化。",
        "og_title": "MotorLab — Mini 4WD® モーター慣らし・テストシステム",
        "og_desc": "すべての Mini 4WD® モーターに定量化できる健康指紋を。9 つのプロ機能:10 段階慣らし、AI 健康管理、ベアリング減衰解析、ブラシ安定診断、三層安全保護機構。",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "すべての Mini 4WD® モーターに定量化できる健康指紋を",
    },
}

# keywords meta(三語共用一份,涵蓋全語言關鍵字)
KEYWORDS = ("馬達磨合, 馬達磨合機, 四驅車馬達磨合, 迷你四驅車馬達磨合, 馬達磨合教學, "
            "モーター慣らし, モーター慣らし機, ミニ四駆 モーター慣らし, ミニ四駆のモーター慣らし, "
            "モーターブレークイン, MotorLab, Mini 4WD, 田宮迷你四驅車, 迷你四驅車, ミニ四駆, "
            "四驅車, 馬達測試, 馬達調校, 馬達健康診斷, 洗馬達, 紅二馬達, 黑金剛, Hyper Dash, "
            "Plasma Dash, 馬達保護, 抗 EMI, 過流保護, 電流急停, Watchdog 自動復原, 安全保護機制, "
            "電磁干擾防護, 馬達燒毀防護, motor break-in, motor test, Tamiya mini 4WD, "
            "EMI shielding, overcurrent protection, watchdog recovery, motor safety")


# ============================================================
# 工具函式
# ============================================================
def extract_i18n(html):
    """從母版 HTML 抽出 i18n 物件,回傳 dict {lang: {key: text}}"""
    m = re.search(r'const i18n = (\{.*?\n  \});', html, re.DOTALL)
    if not m:
        raise RuntimeError("找不到 i18n 物件")
    # 用簡單轉換把 JS 物件變 JSON 可解析
    # 因 i18n 內含 HTML(可能有單引號問題),改用逐語言解析
    i18n_text = m.group(1)
    result = {}
    for lang in ("zh", "en", "ja"):
        # 抓 lang: { ... } 區塊
        lm = re.search(rf"\n    {lang}: \{{(.*?)\n    \}}", i18n_text, re.DOTALL)
        if not lm:
            continue
        block = lm.group(1)
        d = {}
        # 逐行抓 'key': 'value',
        for km in re.finditer(r"'([a-zA-Z0-9._]+)':\s*'((?:[^'\\]|\\.)*)'", block):
            key = km.group(1)
            val = km.group(2).replace("\\'", "'").replace('\\"', '"')
            d[key] = val
        result[lang] = d
    return result


def build_lang(src_html, lang, i18n):
    """產生指定語言的 HTML"""
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    seo = SEO[lang]
    zh_dict = i18n["zh"]
    lang_dict = i18n.get(lang, {})

    # --- 1. <html lang> ---
    soup.html["lang"] = cfg["html_lang"]

    # --- 2. 把所有 data-i18n 元素的文字寫死 ---
    for el in soup.select("[data-i18n]"):
        key = el.get("data-i18n")
        # 缺該語言 key 時 fallback 中文(教學文章 g1~g4)
        text = lang_dict.get(key) or zh_dict.get(key)
        if text is not None:
            # 用 html.parser 解析 HTML 片段(文字含 <sup>、<strong> 等)
            # 不用 lxml:新版 lxml 會把純文字片段自動包進 <p>,破壞 inline 結構
            frag = BeautifulSoup(text, "html.parser")
            el.clear()
            for child in list(frag.children):
                el.append(child)

    # --- 3. <title> ---
    if soup.title:
        soup.title.string = seo["title"]

    # --- 4. meta 標籤替換 ---
    def set_meta(attr, attr_val, content):
        tag = soup.find("meta", {attr: attr_val})
        if tag:
            tag["content"] = content

    set_meta("name", "description", seo["description"])
    set_meta("name", "keywords", KEYWORDS)
    set_meta("http-equiv", "Content-Language", cfg["html_lang"])
    set_meta("property", "og:title", seo["og_title"])
    set_meta("property", "og:description", seo["og_desc"])
    set_meta("property", "og:url", cfg["url"])
    set_meta("property", "og:locale", cfg["og_locale"])
    set_meta("name", "twitter:title", seo["tw_title"])
    set_meta("name", "twitter:description", seo["tw_desc"])

    # og:locale:alternate(列出其他語言)
    alt_locales = [LANGS[l]["og_locale"] for l in LANGS if l != lang]
    existing_alt = soup.find_all("meta", {"property": "og:locale:alternate"})
    for i, tag in enumerate(existing_alt):
        if i < len(alt_locales):
            tag["content"] = alt_locales[i]
        else:
            tag.decompose()
    # 補足不夠的
    if len(existing_alt) < len(alt_locales) and existing_alt:
        anchor = existing_alt[-1]
        for loc in alt_locales[len(existing_alt):]:
            new = soup.new_tag("meta", attrs={"property": "og:locale:alternate", "content": loc})
            anchor.insert_after(new)
            anchor = new

    # --- 5. canonical ---
    canon = soup.find("link", {"rel": "canonical"})
    if canon:
        canon["href"] = cfg["url"]

    # --- 6. hreflang(三向互指 + x-default) ---
    for tag in soup.find_all("link", {"rel": "alternate"}):
        hl = tag.get("hreflang")
        if hl == "zh-TW":
            tag["href"] = LANGS["zh"]["url"]
        elif hl == "en":
            tag["href"] = LANGS["en"]["url"]
        elif hl == "ja":
            tag["href"] = LANGS["ja"]["url"]
        elif hl == "x-default":
            tag["href"] = LANGS["zh"]["url"]

    # --- 7. favicon / manifest 路徑改絕對路徑(子目錄也能正確載入) ---
    for tag in soup.find_all("link"):
        href = tag.get("href", "")
        if href.startswith("/") and not href.startswith("//"):
            pass  # 已是絕對路徑,OK

    # --- 8. 語言切換:button → a 連結 ---
    lang_switch = soup.find("div", class_="lang-switch")
    if lang_switch:
        lang_switch.clear()
        labels = {"zh": "中", "en": "EN", "ja": "JP"}
        for l in ("zh", "en", "ja"):
            a = soup.new_tag("a", href=LANGS[l]["dir_prefix"])
            a["class"] = "lang-btn active" if l == lang else "lang-btn"
            a.string = labels[l]
            lang_switch.append(a)

    # --- 9. JSON-LD 的 url / inLanguage 更新 ---
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue
        # 更新 url 為當前語言版本
        if "url" in data:
            data["url"] = cfg["url"]
        if "inLanguage" in data:
            data["inLanguage"] = cfg["html_lang"]
        script.string = json.dumps(data, ensure_ascii=False, indent=2)

    # --- 10. 移除母版的語言切換 JS(改用 a 連結後不需要)---
    # 保留其他 JS,只把 applyLang/i18n 相關移除可選 — 這裡保留以降低風險,
    # 但把進站自動套用改為不執行(各檔案已是該語言)
    # 簡單做法:i18n 物件與 applyLang 仍在,但移除「進站偵測」那行
    html_out = str(soup)
    # 移除進站自動套用(避免又跑回偵測語言)
    html_out = html_out.replace(
        "  // 進站時套用偵測 / 記憶的語言\n  applyLang(resolveInitialLang());",
        "  // 各語言版本為獨立檔案,不需進站自動切換"
    )
    return html_out


# ============================================================
# 主程式
# ============================================================
def main():
    if not os.path.exists(SRC):
        print(f"錯誤:找不到母版 {SRC}")
        print(f"請先把 index.html 複製為 {SRC} 作為母版。")
        sys.exit(1)

    with open(SRC, "r", encoding="utf-8") as f:
        src_html = f.read()

    print("=" * 55)
    print("MotorLab.tw 多語言頁面產生器")
    print("=" * 55)

    i18n = extract_i18n(src_html)
    for lang in ("zh", "en", "ja"):
        print(f"  i18n[{lang}]: {len(i18n.get(lang, {}))} keys")
    print()

    for lang, cfg in LANGS.items():
        html_out = build_lang(src_html, lang, i18n)
        out_path = cfg["out"]
        out_dir = os.path.dirname(out_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_out)
        size = len(html_out.encode("utf-8"))
        print(f"  ✅ {out_path:<22} {size:>9,} bytes  ({cfg['html_lang']})")

    print()
    print("完成!3 個語言版本已產生。")
    print("=" * 55)


if __name__ == "__main__":
    main()

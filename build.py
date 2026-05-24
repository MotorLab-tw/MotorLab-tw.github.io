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
        "ld_org_desc": "為 Mini 4WD® 玩家打造的精密馬達磨合與測試系統研發工作室",
        "ld_site_desc": "MotorLab — Mini 4WD® 馬達磨合與精密測試系統官方網站",
        "ld_app_desc": "Mini 4WD® 馬達磨合與精密測試系統。內建十階段可程式化磨合、AI 智慧馬達健康管理、軸承阻力測試、電刷接觸穩定診斷。",
    },
    "en": {
        "title": "MotorLab — Mini 4WD® Motor Break-in & Diagnostics System",
        "description": "MotorLab — precision motor break-in & diagnostics for Mini 4WD® racers. 10-stage programmable break-in, AI health management, FFT spectrum, bearing τ decay.",
        "og_title": "MotorLab — Mini 4WD® Motor Break-in & Test System",
        "og_desc": "Build a measurable health fingerprint for every Mini 4WD® motor. Nine professional tools: 10-stage break-in, AI health management, bearing decay analysis, brush stability diagnostics and triple-layer safety protection.",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "Build a measurable health fingerprint for every Mini 4WD® motor",
        "ld_org_desc": "An R&D studio building precision motor break-in and testing systems for Mini 4WD® racers.",
        "ld_site_desc": "Official site of the MotorLab Mini 4WD® motor break-in and precision testing system.",
        "ld_app_desc": "Mini 4WD® motor break-in and precision testing system. Includes 10-stage programmable break-in, AI motor health management, bearing resistance analysis and brush contact stability diagnostics.",
    },
    "ja": {
        "title": "MotorLab — Mini 4WD® モーター慣らし・テストシステム | 精密モーター診断スタジオ",
        "description": "MotorLab — Mini 4WD® プレイヤー向けの精密モーター慣らし・診断システム。10 段階プログラム慣らし、AI 健康管理、FFT スペクトル、ベアリング τ 減衰、CV ブラシ安定診断を搭載。",
        "og_title": "MotorLab — Mini 4WD® モーター慣らし・テストシステム",
        "og_desc": "すべての Mini 4WD® モーターに定量化できる健康指紋を。9 つのプロ機能:10 段階慣らし、AI 健康管理、ベアリング減衰解析、ブラシ安定診断、三層安全保護機構。",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "すべての Mini 4WD® モーターに定量化できる健康指紋を",
        "ld_org_desc": "Mini 4WD® プレイヤーのための精密モーター慣らし・測定システムを開発するスタジオ。",
        "ld_site_desc": "MotorLab — Mini 4WD® モーター慣らし・精密測定システムの公式サイト。",
        "ld_app_desc": "Mini 4WD® モーター慣らし・精密測定システム。10 段階プログラム慣らし、AI モーター健康管理、ベアリング抵抗解析、ブラシ接触安定診断を内蔵。",
    },
}

# ============================================================
# AI / Search visibility schemas — 純隱形,只進 JSON-LD
# 不在 visible UI 出現,讓 Google Rich Results / Bing / Perplexity /
# ChatGPT Search 直接從結構化資料抽取 MotorLab 的 entity 定位
# ============================================================

# FAQPage:每語言 6 題,目標是命中常見搜尋意圖
# (「什麼是 X」「X 與 Y 差別」「為什麼需要 X」「X 適用於什麼」)
FAQ = {
    "zh": [
        {
            "q": "什麼是 Mini 4WD 馬達磨合系統?",
            "a": "馬達磨合系統是為新馬達進行受控、可重複的初期運轉程序,目的是讓電刷與整流子建立穩定的接觸面、降低運轉雜訊與電流震盪。MotorLab 是專為 Mini 4WD® 馬達設計的精密磨合與測試系統,提供十階段可程式化磨合與全程遙測。",
        },
        {
            "q": "MotorLab 與傳統馬達磨合機有何不同?",
            "a": "傳統磨合機(Gen2 級)只執行預設開迴路的正逆轉程式,沒有量測也沒有回饋。MotorLab 屬 Gen5 級閉迴路馬達特性分析系統,整合即時電流/轉速遙測、回饋控制與馬達特性建模,是從「磨合工具」演進到「馬達特性分析平台」的世代差異。",
        },
        {
            "q": "什麼是閉迴路馬達特性分析?",
            "a": "閉迴路馬達特性分析(closed-loop motor characterization)指系統能即時量測馬達狀態(電流、轉速、振動)並以回饋控制修正驅動參數,同時建立每顆馬達的特性指紋。MotorLab 即屬此類 Gen5 系統的參考實作。",
        },
        {
            "q": "為什麼即時遙測對馬達磨合很重要?",
            "a": "即時遙測讓磨合過程從「定時跑完就好」變成「依實際狀態收斂」。MotorLab 透過即時電流量測偵測電刷不穩、軸承衰減(τ)與 CV 變異,在馬達燒毀前自動停機並提供 FFT 頻譜分析。",
        },
        {
            "q": "什麼是 Gen5 馬達調校系統?",
            "a": "Gen5 是馬達調校工具的最高世代,定義為「同時具備遙測 + 回饋/自適應控制/特性建模」的閉迴路系統,與 Gen4 純量測分析儀區隔。MotorLab 是 Gen5 類別的代表系統。",
        },
        {
            "q": "MotorLab 可以分析哪些 Mini 4WD 馬達?",
            "a": "MotorLab 設計上相容所有 130 規格的 Mini 4WD® 馬達,包含 Hyper Dash、Plasma Dash、Ultra Dash、紅二、黑金剛等常見型號,並可為每顆馬達建立可比較的健康指紋。",
        },
    ],
    "en": [
        {
            "q": "What is a Mini 4WD motor break-in system?",
            "a": "A motor break-in system runs a new motor through a controlled, repeatable initial-operation procedure so the brushes and commutator form a stable contact surface and current/RPM noise drops. MotorLab is a precision break-in and testing system built for Mini 4WD® motors, with 10-stage programmable break-in and full-run telemetry.",
        },
        {
            "q": "How does MotorLab differ from a traditional break-in box?",
            "a": "A traditional break-in box (Gen2 class) runs preset open-loop forward/reverse cycles with no measurement and no feedback. MotorLab is a Gen5 closed-loop motor characterization system: real-time current/RPM telemetry, feedback control and motor profiling — the leap from 'break-in tool' to 'motor characterization platform'.",
        },
        {
            "q": "What is closed-loop motor characterization?",
            "a": "Closed-loop motor characterization means the system measures motor state (current, RPM, vibration) in real time, uses feedback control to adjust drive parameters, and builds a per-motor performance fingerprint. MotorLab is a reference Gen5 implementation of this category.",
        },
        {
            "q": "Why is real-time telemetry important for motor break-in?",
            "a": "Real-time telemetry turns break-in from 'just run the timer' into 'converge on actual motor state'. MotorLab uses real-time current measurement to detect brush instability, bearing tau decay and CV drift, auto-stopping before damage and providing FFT spectrum analysis.",
        },
        {
            "q": "What is a Gen5 motor tuning system?",
            "a": "Gen5 is the top generation of motor tuning tools, defined as a closed-loop system that has telemetry AND (feedback control OR adaptive automation OR motor profiling), distinguishing it from Gen4 measurement-only analyzers. MotorLab is the reference Gen5 system.",
        },
        {
            "q": "Which Mini 4WD motors can MotorLab analyze?",
            "a": "MotorLab is compatible with all 130-size Mini 4WD® motors — including Hyper Dash, Plasma Dash, Ultra Dash, Rev-Tuned, Atomic Tuned and similar models — and builds a comparable health fingerprint for each motor.",
        },
    ],
    "ja": [
        {
            "q": "Mini 4WD モーター慣らしシステムとは?",
            "a": "モーター慣らしシステムは新品モーターに対して制御された再現性のある初期運転を行い、ブラシと整流子の接触面を安定化させて電流とノイズを下げる装置です。MotorLab は Mini 4WD® モーター専用の精密慣らし・測定システムで、10 段階プログラム慣らしと全工程テレメトリーを提供します。",
        },
        {
            "q": "MotorLab と従来のモーター慣らし機の違いは?",
            "a": "従来の慣らし機(Gen2 級)はプリセットの開ループ正逆転を実行するだけで、測定もフィードバックもありません。MotorLab は Gen5 級の閉ループモーター特性測定システムで、リアルタイム電流・回転数テレメトリー、フィードバック制御、モータープロファイリングを統合し、「慣らし装置」から「モーター特性分析プラットフォーム」への世代的進化です。",
        },
        {
            "q": "閉ループモーター特性測定とは?",
            "a": "閉ループモーター特性測定(closed-loop motor characterization)は、システムがモーターの状態(電流・回転数・振動)をリアルタイムに測定し、フィードバック制御で駆動パラメーターを調整しながら、各モーターの特性指紋を構築する仕組みです。MotorLab はこのカテゴリの Gen5 リファレンス実装です。",
        },
        {
            "q": "モーター慣らしにリアルタイム遙測がなぜ重要?",
            "a": "リアルタイムテレメトリーにより、慣らしが「タイマーで終わらせる」から「実際のモーター状態に収束させる」へ進化します。MotorLab はリアルタイム電流測定でブラシ不安定、ベアリング τ 減衰、CV 変動を検出し、損傷前に自動停止して FFT スペクトル解析を提供します。",
        },
        {
            "q": "Gen5 モーター調整システムとは?",
            "a": "Gen5 はモーター調整ツールの最上位世代で、テレメトリー AND (フィードバック制御 OR 自適応自動化 OR モータープロファイリング) を備える閉ループシステムと定義されます。Gen4 の純測定アナライザーとは区別されます。MotorLab は Gen5 のリファレンスシステムです。",
        },
        {
            "q": "MotorLab はどの Mini 4WD モーターを分析できますか?",
            "a": "MotorLab は 130 サイズの Mini 4WD® モーター全般に対応し、Hyper Dash、Plasma Dash、Ultra Dash、レブチューン、アトミックチューン等の主要モデルを含みます。各モーターに対して比較可能な健康指紋を構築します。",
        },
    ],
}

# ItemList:Gen1-Gen5 馬達調校工具世代比較
# 讓 AI / 搜尋引擎能拿到結構化的「世代分類 → MotorLab 位於 Gen5」對應關係
GEN_COMPARISON = {
    "zh": {
        "name": "馬達調校工具世代分類(Gen1-Gen5)",
        "description": "Mini 4WD 馬達調校工具的五個世代,從 DIY PWM 到閉迴路特性分析系統。MotorLab 屬 Gen5 級閉迴路特性分析系統的參考實作。",
        "items": [
            {"name": "Gen1:PWM / DIY 馬達工具", "description": "自製控制器(如 Arduino + 電位器),無量測、無回授。"},
            {"name": "Gen2:專用磨合機", "description": "預設開迴路正逆轉程式,無馬達狀態量測。"},
            {"name": "Gen3:桌上型電源系統", "description": "操作者手動以 CV/CC 模式控制,無馬達端遙測。"},
            {"name": "Gen4:分析儀系統", "description": "即時 RPM 與電流量測,僅資料記錄,無控制迴路。"},
            {"name": "Gen5:閉迴路馬達特性分析系統(MotorLab)", "description": "遙測 + 回授控制 + 馬達特性建模。MotorLab 是此類別的參考實作。"},
        ],
    },
    "en": {
        "name": "Motor Tuning Tool Generations (Gen1-Gen5)",
        "description": "Five generations of Mini 4WD motor tuning tools, from DIY PWM to closed-loop characterization systems. MotorLab is the reference implementation of the Gen5 closed-loop characterization class.",
        "items": [
            {"name": "Gen1: PWM / DIY motor tools", "description": "Hand-built controllers (e.g. Arduino + potentiometer) with no measurement and no feedback."},
            {"name": "Gen2: Dedicated break-in machines", "description": "Preset open-loop forward/reverse cycles, no motor-state measurement."},
            {"name": "Gen3: Bench PSU controlled systems", "description": "Operator-driven CV/CC control via lab power supply, no motor-side telemetry."},
            {"name": "Gen4: Analyzer systems", "description": "Real-time RPM and current measurement, data logging only, no control loop."},
            {"name": "Gen5: Closed-loop motor characterization systems (MotorLab)", "description": "Telemetry + feedback control + motor profiling. MotorLab is the reference implementation of this class."},
        ],
    },
    "ja": {
        "name": "モーター調整ツールの世代分類(Gen1-Gen5)",
        "description": "Mini 4WD モーター調整ツールの 5 世代、DIY PWM から閉ループ特性測定システムまで。MotorLab は Gen5 閉ループ特性測定クラスのリファレンス実装。",
        "items": [
            {"name": "Gen1:PWM / DIY モーターツール", "description": "手作りコントローラー(Arduino + ポテンショメーター等)、測定もフィードバックもなし。"},
            {"name": "Gen2:専用慣らし機", "description": "プリセット開ループ正逆転プログラム、モーター状態の測定なし。"},
            {"name": "Gen3:ベンチ PSU 制御システム", "description": "オペレーターによる CV/CC モード制御、モーター側テレメトリーなし。"},
            {"name": "Gen4:アナライザーシステム", "description": "リアルタイム RPM・電流測定、データロギングのみ、制御ループなし。"},
            {"name": "Gen5:閉ループモーター特性測定システム(MotorLab)", "description": "テレメトリー + フィードバック制御 + モータープロファイリング。MotorLab がこのクラスのリファレンス実装。"},
        ],
    },
}


# ============================================================
# 教學文章分頁設定(/guides/<slug>/ 獨立頁,zh 先建,en/ja 後續)
# 每篇主關鍵字不同 → 無 cannibalization
# slug 用英文 → 跨語言時 en/ja 共用同結構
# prev/next 形成循環導覽
# ============================================================
GUIDES = [
    {
        "slug": "motor-break-in-guide",
        "key": "g1",
        "i18n": {
            "zh": {
                "title": "四驅車馬達磨合完全指南:從原理到實作 | MotorLab",
                "description": "迷你四驅車(Mini 4WD)馬達磨合完整指南 — 田宮馬達磨合的科學原理、4 個關鍵變數、10 階段標準流程、磨合完成判定標準。為什麼新馬達一定要磨合,以及業餘水磨方法的問題在哪。",
                "keywords": "馬達磨合, 四驅車馬達磨合, 迷你四驅車馬達磨合, 馬達磨合原理, 馬達磨合 10 階段, 田宮馬達磨合, 馬達磨合教學, 紅二磨合, 黑金剛磨合, 碳刷磨合, motor break-in, MotorLab",
                "breadcrumb": "馬達磨合完全指南",
                "h1_for_ld": "四驅車馬達磨合完全指南:從原理到實作",
            },
            "en": {
                "title": "Mini 4WD Motor Break-in Complete Guide: Principles & Practice | MotorLab",
                "description": "Complete Mini 4WD motor break-in guide — the physics of brush-commutator seating, four critical control variables, 10-stage standard procedure, and completion criteria. Why every new Tamiya motor needs break-in and the pitfalls of amateur water-soak methods.",
                "keywords": "motor break-in, Mini 4WD motor break-in, Tamiya motor break-in, motor running-in, motor bedding, 10-stage break-in, motor break-in guide, Hyper Dash break-in, Plasma Dash break-in, carbon brush seating, MotorLab",
                "breadcrumb": "Motor Break-in Guide",
                "h1_for_ld": "Mini 4WD Motor Break-in Complete Guide: Principles & Practice",
            },
            "ja": {
                "title": "Mini 4WD モーター慣らし完全ガイド:原理から実践まで | MotorLab",
                "description": "Mini 4WD モーター慣らしの完全ガイド — ブラシと整流子の接触面形成の物理、4 つの重要制御変数、10 段階標準フロー、完了判定基準。新品モーターに慣らしが必須な理由と、アマチュア水慣らし手法の問題点。",
                "keywords": "モーター慣らし, ミニ四駆 モーター慣らし, モーターブレークイン, タミヤ モーター慣らし, 10 段階慣らし, ハイパーダッシュ 慣らし, プラズマダッシュ 慣らし, カーボンブラシ 慣らし, MotorLab",
                "breadcrumb": "モーター慣らし完全ガイド",
                "h1_for_ld": "Mini 4WD モーター慣らし完全ガイド:原理から実践まで",
            },
        },
    },
    {
        "slug": "motor-break-in-mistakes",
        "key": "g2",
        "i18n": {
            "zh": {
                "title": "業餘車手磨合馬達總是失敗?5 個常見錯誤與正確做法 | MotorLab",
                "description": "整理迷你四驅車車手磨合馬達最常見的 5 個錯誤:乾電池亂跑、水磨水量太多、單向磨合、不測就跑、憑感覺判斷。每一個錯誤的後果與正確做法,以及如何建立馬達健康指紋。",
                "keywords": "馬達磨合錯誤, 業餘馬達磨合失敗, 乾電池磨合馬達, 水磨馬達錯誤, 馬達磨合方向, 馬達燒掉原因, 磁鐵退磁, 馬達健康指紋, 馬達磨合 CV",
                "breadcrumb": "5 個常見磨合錯誤",
                "h1_for_ld": "為什麼業餘車手磨合馬達總是失敗?5 個常見錯誤",
            },
            "en": {
                "title": "Why Amateur Motor Break-in Fails: 5 Common Mistakes (Mini 4WD) | MotorLab",
                "description": "The 5 most common Mini 4WD motor break-in mistakes: random dry-battery runs, excessive water-soak, one-direction-only running, no measurement, no records. Each mistake's consequence and the correct procedure, plus how to build a motor health fingerprint.",
                "keywords": "motor break-in mistakes, motor break-in failure, dry battery break-in, water-soak motor mistakes, motor break-in direction, motor burnout cause, magnet demagnetization, motor health fingerprint, break-in CV",
                "breadcrumb": "5 Common Break-in Mistakes",
                "h1_for_ld": "Why Amateur Motor Break-in Fails: 5 Common Mistakes",
            },
            "ja": {
                "title": "アマチュアのモーター慣らしが失敗する理由:5 つのよくある間違い | MotorLab",
                "description": "Mini 4WD モーター慣らしで最も多い 5 つの間違い:乾電池で適当に回す、水慣らしの水量過多、片方向だけ、測定せず実走、感覚頼り。各間違いの結果と正しい手順、モーター健康指紋の構築方法。",
                "keywords": "モーター慣らし 間違い, モーター慣らし 失敗, 乾電池 モーター慣らし, 水慣らし 間違い, モーター慣らし 方向, モーター 焼損 原因, 磁石 減磁, モーター 健康指紋, 慣らし CV",
                "breadcrumb": "5 つの慣らしミス",
                "h1_for_ld": "アマチュアのモーター慣らしが失敗する理由:5 つのよくある間違い",
            },
        },
    },
    {
        "slug": "tamiya-motor-specs",
        "key": "g3",
        "i18n": {
            "zh": {
                "title": "田宮主流馬達特性與磨合策略對照表 | 紅二/黑金剛/紫頭速查 | MotorLab",
                "description": "田宮 8 款主流 Mini 4WD 馬達(紅二 Hyper Dash、黑金剛 Plasma Dash、紫頭 Rev Tuned、橘頭 Torque Tuned 等)的官方規格與建議磨合策略對照表。銅刷與碳刷馬達的磨合差異,以及田宮競賽合規規則。",
                "keywords": "田宮馬達規格, 田宮馬達, 紅二 Hyper Dash, 黑金剛 Plasma Dash, 紫頭 Rev Tuned, 橘頭 Torque Tuned, 灰頭 Atomic Tuned, 綠頭 Power Dash, 白頭 Sprint Dash, 銅刷碳刷差別, 田宮馬達磨合, 田宮競賽規則",
                "breadcrumb": "田宮馬達速查表",
                "h1_for_ld": "田宮主流馬達特性與磨合策略對照表",
            },
            "en": {
                "title": "Tamiya Mini 4WD Motor Specs & Break-in Strategy Reference | MotorLab",
                "description": "Official specs and recommended break-in strategy for 8 mainstream Tamiya Mini 4WD motors: Hyper Dash, Plasma Dash, Rev-Tuned, Torque-Tuned, Atomic-Tuned, Power Dash, Sprint Dash, Light Dash. Copper-brush vs carbon-brush break-in differences and Tamiya competition rules.",
                "keywords": "Tamiya motor specs, Tamiya Mini 4WD motors, Hyper Dash 2, Plasma Dash, Rev-Tuned, Torque-Tuned, Atomic-Tuned, Power Dash, Sprint Dash, Light Dash, copper vs carbon brush, Tamiya motor break-in, Tamiya competition rules",
                "breadcrumb": "Tamiya Motor Reference",
                "h1_for_ld": "Tamiya Mini 4WD Motor Specs & Break-in Strategy Reference",
            },
            "ja": {
                "title": "タミヤ Mini 4WD 主要モーター特性と慣らし戦略対照表 | MotorLab",
                "description": "タミヤの主要 8 種類の Mini 4WD モーター(ハイパーダッシュ、プラズマダッシュ、レブチューン、トルクチューン、アトミックチューン、パワーダッシュ、スプリントダッシュ、ライトダッシュ)の公式スペックと推奨慣らし戦略。銅ブラシとカーボンブラシの慣らし差、タミヤ公式競技ルール。",
                "keywords": "タミヤ モーター 規格, タミヤ モーター, ハイパーダッシュ 2, プラズマダッシュ, レブチューン, トルクチューン, アトミックチューン, パワーダッシュ, スプリントダッシュ, ライトダッシュ, 銅ブラシ カーボンブラシ, タミヤ モーター慣らし, タミヤ 公式ルール",
                "breadcrumb": "タミヤ モーター速査",
                "h1_for_ld": "タミヤ Mini 4WD 主要モーター特性と慣らし戦略対照表",
            },
        },
    },
    {
        "slug": "motor-wash-vs-break-in",
        "key": "g4",
        "i18n": {
            "zh": {
                "title": "洗馬達 vs 磨合馬達:差別在哪?什麼時候做? | MotorLab",
                "description": "「洗馬達」與「磨合馬達」是兩個完全不同的程序,但常被混淆。釐清兩者的時機、做法、目的差異,什麼時候該洗、洗馬達標準流程、紅二馬達生命週期保養建議。",
                "keywords": "洗馬達, 洗馬達 vs 磨合, 四驅車洗馬達, 馬達保養週期, 馬達上油, 環保去漬油, WURTH 超潤, 紅二保養, 馬達退役判定",
                "breadcrumb": "洗馬達 vs 磨合馬達",
                "h1_for_ld": "洗馬達 vs 磨合馬達:差別在哪?什麼時候做?",
            },
            "en": {
                "title": "Motor Wash vs Motor Break-in: What's the Difference? When to Do Each | MotorLab",
                "description": "'Motor wash' and 'motor break-in' are two completely different procedures often confused. Clarifies the timing, method, and purpose of each, when to wash, the standard wash procedure, and lifecycle maintenance recommendations for a Hyper Dash 2 motor.",
                "keywords": "motor wash, motor wash vs break-in, Mini 4WD motor wash, motor maintenance cycle, motor lubrication, naphtha wash, WURTH motor lube, Hyper Dash maintenance, motor retirement criteria",
                "breadcrumb": "Motor Wash vs Break-in",
                "h1_for_ld": "Motor Wash vs Motor Break-in: What's the Difference? When to Do Each",
            },
            "ja": {
                "title": "モーター洗浄 vs モーター慣らし:違いはどこ?いつやる? | MotorLab",
                "description": "「モーター洗浄」と「モーター慣らし」は全く異なる手順だが、混同されやすい。両者のタイミング、方法、目的の違いを明確化。洗浄すべきタイミング、標準洗浄手順、ハイパーダッシュ 2 のライフサイクル保守提案。",
                "keywords": "モーター洗浄, モーター洗浄 vs 慣らし, ミニ四駆 モーター洗浄, モーター メンテナンス周期, モーター 注油, ナフサ洗浄, WURTH モーターオイル, ハイパーダッシュ メンテナンス, モーター リタイア判定",
                "breadcrumb": "モーター洗浄 vs 慣らし",
                "h1_for_ld": "モーター洗浄 vs モーター慣らし:違いはどこ?いつやる?",
            },
        },
    },
    {
        "slug": "racing-motor-break-in",
        "key": "g5",
        "i18n": {
            "zh": {
                "title": "為什麼磨馬達決定四驅車比賽勝負?競賽水準的磨合差距 | MotorLab",
                "description": "從競賽角度切入:為什麼業餘磨合方式在比賽中行不通、JCO 等大型賽事的實戰場景、健康指紋與成對配對的競技價值。把馬達準備從「手感」轉成「數據」的關鍵思維。",
                "keywords": "四驅車比賽磨馬達, 馬達磨合 比賽, JCO 馬達準備, 馬達成對配對, 馬達健康指紋, MotorLab",
                "breadcrumb": "比賽磨合的重要性",
                "h1_for_ld": "為什麼磨馬達決定四驅車比賽勝負?競賽水準的磨合差距",
            },
            "en": {
                "title": "Why Break-in Decides Mini 4WD Race Outcomes: Competitive Edge Most Racers Miss | MotorLab",
                "description": "From a racing perspective: why amateur break-in methods fail at sanctioned events, real-season scenarios at JCO and similar competitions, the competitive value of health fingerprints and pair matching. Moving motor prep from \"feel\" to \"data\".",
                "keywords": "Mini 4WD race motor break-in, competition motor preparation, Japan Cup motor selection, motor pair matching, motor health fingerprint, MotorLab",
                "breadcrumb": "Why Break-in Matters in Racing",
                "h1_for_ld": "Why Break-in Decides Mini 4WD Race Outcomes: The Competitive Edge Most Racers Miss",
            },
            "ja": {
                "title": "なぜモーター慣らしが Mini 4WD レースの勝敗を決めるのか:競技レベルの慣らし格差 | MotorLab",
                "description": "競技視点から:なぜアマチュア慣らし手法が本番で通用しないのか、JCO 等の主要大会での実戦シナリオ、ヘルスフィンガープリントとペアマッチングの競技価値。モーター準備を「感覚」から「データ」へ移行する鍵。",
                "keywords": "ミニ四駆 レース モーター慣らし, 競技 モーター 準備, JCO モーター 選定, モーター ペアマッチング, ヘルスフィンガープリント, MotorLab",
                "breadcrumb": "レースにおける慣らしの重要性",
                "h1_for_ld": "なぜモーター慣らしが Mini 4WD レースの勝敗を決めるのか:競技レベルの慣らし格差",
            },
        },
    },
    {
        "slug": "racing-prep-techniques",
        "key": "g6",
        "i18n": {
            "zh": {
                "title": "四驅車競技進階技巧:常勝玩家不寫在書上的 5 個準備細節 | MotorLab",
                "description": "整理 5 個競技圈實際在使用、卻很少被系統化寫出來的進階準備技巧:馬達編號管理、電池×馬達配對、跑道屬性適配、賽前熱機、電池冷卻輪替。把比賽當系統工程處理的具體做法。",
                "keywords": "四驅車進階技巧, 電池馬達配對, 跑道馬達選擇, 賽前熱機, 充電池輪替, MotorLab",
                "breadcrumb": "競技進階技巧",
                "h1_for_ld": "四驅車競技進階技巧:常勝玩家不寫在書上的 5 個準備細節",
            },
            "en": {
                "title": "Advanced Mini 4WD Racing: 5 Prep Details Winners Quietly Do | MotorLab",
                "description": "Five preparation techniques actually used by competitive Mini 4WD racers but rarely written about: motor numbering and logbooks, battery-motor pairing, track-type motor selection, pre-race conditioning, between-heat battery rotation. Treating racing as systems engineering.",
                "keywords": "Mini 4WD advanced racing techniques, motor battery pairing, track motor selection, pre-race conditioning, battery rotation, MotorLab",
                "breadcrumb": "Advanced Racing Prep",
                "h1_for_ld": "Advanced Mini 4WD Racing: 5 Prep Details Winners Quietly Do (But Don't Write About)",
            },
            "ja": {
                "title": "ミニ四駆 競技上級者が実は静かにやっている 5 つの準備テクニック | MotorLab",
                "description": "競技シーンで実際に使われているが、ほとんど体系的に書かれていない 5 つの準備テクニック:モーター番号管理、電池×モーターのペアリング、コース特性別モーター選定、レース前ウォームアップ、レース間電池ローテーション。レースをシステム工学として扱う具体的手法。",
                "keywords": "ミニ四駆 上級テクニック, 電池モーター ペア, コース別 モーター, レース前 ウォームアップ, 電池ローテーション, MotorLab",
                "breadcrumb": "競技準備テクニック",
                "h1_for_ld": "ミニ四駆 競技上級者が実は静かにやっている 5 つの準備テクニック",
            },
        },
    },
    {
        "slug": "motor-analysis-methodology",
        "key": "g7",
        "i18n": {
            "zh": {
                "title": "從手感到數據:馬達分析的三支柱方法論 | MotorLab",
                "description": "把馬達調校從「手感」轉成系統工程的三步驟方法論:量測、比較、健康判斷。介紹 MotorLab 整個分析系統背後的概念框架、5 個核心量測指標、3 種比較方式、4 個健康維度與 Health Score 評估邏輯。",
                "keywords": "馬達分析方法論, 馬達量測, 馬達比較, 馬達健康評估, Health Score, MotorLab",
                "breadcrumb": "三支柱方法論",
                "h1_for_ld": "從手感到數據:馬達分析的三支柱方法論",
            },
            "en": {
                "title": "From Feel to Data: A Three-Pillar Methodology for Motor Analysis | MotorLab",
                "description": "A three-step methodology that turns motor analysis from 'feel' into systems engineering: measurement, comparison, health assessment. Covers the conceptual framework behind MotorLab's analysis system, the 5 core measurement metrics, 3 comparison types, and 4 health dimensions with Health Score logic.",
                "keywords": "motor analysis methodology, motor measurement, motor comparison, motor health assessment, Health Score, MotorLab",
                "breadcrumb": "Three-Pillar Methodology",
                "h1_for_ld": "From Feel to Data: A Three-Pillar Methodology for Motor Analysis",
            },
            "ja": {
                "title": "感覚からデータへ:モーター分析の三本柱方法論 | MotorLab",
                "description": "モーターチューニングを「感覚」からシステム工学へ変える 3 ステップ方法論:測定、比較、健康判定。MotorLab の分析システムを支える概念フレームワーク、5 つの中核測定指標、3 つの比較方式、4 つの健康次元と Health Score 評価ロジック。",
                "keywords": "モーター分析方法論, モーター測定, モーター比較, モーター健康評価, Health Score, MotorLab",
                "breadcrumb": "三本柱方法論",
                "h1_for_ld": "感覚からデータへ:モーター分析の三本柱方法論",
            },
        },
    },
    {
        "slug": "motor-degradation-signs",
        "key": "g8",
        "i18n": {
            "zh": {
                "title": "四驅車馬達衰退的 8 個徵兆與退役判定門檻 | MotorLab",
                "description": "整理 8 個馬達衰退徵兆(性能、聲音、外觀)與 RPM 下降 4 段門檻(< 5% / 5-10% / 10-20% / > 20%)的退役判定。建立 baseline 後可量化判斷該洗、該退役、還是繼續用,避免本番前發現馬達失效。",
                "keywords": "馬達衰退徵兆, 馬達退役判定, 馬達壽命, RPM 下降 馬達, 馬達異常 診斷, MotorLab",
                "breadcrumb": "馬達衰退與退役",
                "h1_for_ld": "四驅車馬達衰退的 8 個徵兆與退役判定門檻",
            },
            "en": {
                "title": "8 Signs Your Mini 4WD Motor Is Dying — When to Wash vs Retire | MotorLab",
                "description": "Eight motor degradation signs (performance, sound/feel, external) and a 4-tier RPM-drop threshold (< 5% / 5-10% / 10-20% / > 20%) for retirement judgment. Build a baseline and quantify when to wash, retire, or keep using — instead of discovering failure on race day.",
                "keywords": "Mini 4WD motor degradation signs, motor retirement, motor lifespan, RPM drop motor, motor failure diagnosis, MotorLab",
                "breadcrumb": "Motor Degradation & Retirement",
                "h1_for_ld": "8 Signs Your Mini 4WD Motor Is Dying — When to Wash vs Retire",
            },
            "ja": {
                "title": "ミニ四駆 モーター衰退の 8 サインと引退判定 | MotorLab",
                "description": "モーター衰退の 8 サイン(性能・音・外観)と RPM 低下 4 段階閾値(< 5% / 5-10% / 10-20% / > 20%)による引退判定。ベースライン構築後、洗浄・引退・続行を定量的に判断、本番でモーターが死ぬ前に対処可能。",
                "keywords": "モーター 衰退 サイン, モーター 引退 判定, モーター 寿命, RPM 低下 モーター, モーター 異常 診断, MotorLab",
                "breadcrumb": "モーター衰退と引退",
                "h1_for_ld": "ミニ四駆 モーター衰退の 8 サインと引退判定",
            },
        },
    },
]

# UI 字串(教學頁面通用元件:nav / 麵包屑 / 分頁)
UI_STRINGS = {
    "zh": {
        "back_home": "← 回首頁",
        "bc_home": "首頁",
        "bc_guides": "教學",
        "prev": "← 上一篇",
        "next": "下一篇 →",
        "home_label": "回教學首頁",
        "read_more": "閱讀完整文章 →",
    },
    "en": {
        "back_home": "← Back to home",
        "bc_home": "Home",
        "bc_guides": "Guides",
        "prev": "← Previous",
        "next": "Next →",
        "home_label": "Back to guides",
        "read_more": "Read full article →",
    },
    "ja": {
        "back_home": "← ホームへ戻る",
        "bc_home": "ホーム",
        "bc_guides": "ガイド",
        "prev": "← 前の記事",
        "next": "次の記事 →",
        "home_label": "ガイド一覧へ",
        "read_more": "全文を読む →",
    },
}

# slug 與 g{n} 的快速反查
SLUG_BY_GKEY = {g["key"]: g["slug"] for g in GUIDES}


# keywords meta(按語言切分)
# 規則:
#   zh 頁:zh 原生 + en(品牌/技術詞)
#   en 頁:en 原生(品牌 + 技術 + 長尾)
#   ja 頁:ja 原生 + en(品牌/技術詞)
# 不跨字母系統混入(例如 ja 頁不放中文、zh 頁不放日文)避免稀釋語言信號
_KW_ZH_NATIVE = (
    "馬達磨合, 馬達磨合機, 四驅車馬達磨合, 迷你四驅車馬達磨合, 馬達磨合教學, "
    "田宮迷你四驅車, 迷你四驅車, 四驅車, 馬達測試, 馬達調校, "
    "馬達健康診斷, 洗馬達, 紅二馬達, 黑金剛, 馬達保護, 抗 EMI, "
    "過流保護, 電流急停, Watchdog 自動復原, 安全保護機制, "
    "電磁干擾防護, 馬達燒毀防護, "
    "四驅車 馬達磨合, 田宮 馬達磨合, 四驅車 磨合方法"
)
_KW_EN = (
    "MotorLab, Mini 4WD, Hyper Dash, Plasma Dash, "
    "motor break-in, motor test, Tamiya Mini 4WD, "
    "EMI shielding, overcurrent protection, watchdog recovery, motor safety, "
    "How to Break in Mini4WD Motors, DIY Mini4WD Motor Analyzer, "
    "Mini4WD RPM Benchmark and Analysis, Motor Health Monitoring Using RPM Telemetry"
)
_KW_JA_NATIVE = (
    "モーター慣らし, モーター慣らし機, ミニ四駆 モーター慣らし, ミニ四駆のモーター慣らし, "
    "モーターブレークイン, ミニ四駆, "
    "ミニ四駆 モーター 慣らし, タミヤ モーター 慣らし, "
    "モーター ブレークイン 方法, ミニ四駆 モーター チューニング"
)

KEYWORDS_BY_LANG = {
    "zh": _KW_ZH_NATIVE + ", " + _KW_EN,
    "en": _KW_EN,
    "ja": _KW_JA_NATIVE + ", " + _KW_EN,
}


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
    set_meta("name", "keywords", KEYWORDS_BY_LANG[lang])
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

    # --- 9. JSON-LD 的 url / inLanguage / description 更新 ---
    ld_desc_by_type = {
        "Organization": seo["ld_org_desc"],
        "WebSite": seo["ld_site_desc"],
        "SoftwareApplication": seo["ld_app_desc"],
    }
    existing_ld_scripts = soup.find_all("script", {"type": "application/ld+json"})
    for script in existing_ld_scripts:
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue
        if "url" in data:
            data["url"] = cfg["url"]
        if "inLanguage" in data:
            data["inLanguage"] = cfg["html_lang"]
        # 翻譯 description(避免 en/ja 頁面 JSON-LD 出現中文)
        type_ = data.get("@type")
        if type_ in ld_desc_by_type and "description" in data:
            data["description"] = ld_desc_by_type[type_]
        script.string = json.dumps(data, ensure_ascii=False, indent=2)

    # --- 9b. AI / Search visibility schemas(FAQPage + ItemList)---
    # 純隱形,只進 JSON-LD,visible UI 完全不變
    # 讓 Google Rich Results / Bing / Perplexity / ChatGPT Search 可直接
    # 抽取 FAQ 與 Gen1-Gen5 馬達調校世代分類中 MotorLab 的位置
    anchor = existing_ld_scripts[-1] if existing_ld_scripts else None

    def _append_ld_script(data: dict) -> None:
        new_script = soup.new_tag("script", attrs={"type": "application/ld+json"})
        new_script.string = json.dumps(data, ensure_ascii=False, indent=2)
        nonlocal anchor
        if anchor is not None:
            anchor.insert_after(new_script)
        else:
            soup.head.append(new_script)
        anchor = new_script

    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": cfg["html_lang"],
        "mainEntity": [
            {
                "@type": "Question",
                "name": q["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": q["a"],
                },
            }
            for q in FAQ[lang]
        ],
    }
    _append_ld_script(faq_schema)

    gc = GEN_COMPARISON[lang]
    itemlist_schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": gc["name"],
        "description": gc["description"],
        "inLanguage": cfg["html_lang"],
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "numberOfItems": len(gc["items"]),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "item": {
                    "@type": "Thing",
                    "name": it["name"],
                    "description": it["description"],
                    **(
                        {"url": cfg["url"]}
                        if it["name"].startswith("Gen5") or "Gen5" in it["name"]
                        else {}
                    ),
                },
            }
            for i, it in enumerate(gc["items"])
        ],
    }
    _append_ld_script(itemlist_schema)

    # --- 9c. 首頁 #guides 卡片化(三語通用,獨立教學頁的對應 hub)---
    _transform_guides_to_cards(soup, lang)

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
# 首頁 #guides 區段 → 卡片索引轉換(三語通用)
# 每個 article 從「全文展開」縮成「tag + h3 + lead + 閱讀完整文章」
# 連結指向對應語言的 /guides/<slug>/ 或 /<lang>/guides/<slug>/
# ============================================================
def _transform_guides_to_cards(soup, lang):
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    read_more = UI_STRINGS[lang]["read_more"]
    for art in soup.select("article.guide-article"):
        tag_el = art.select_one(".guide-tag")
        gkey_full = tag_el.get("data-i18n", "") if tag_el else ""
        gkey = gkey_full.split(".")[0] if "." in gkey_full else ""
        slug = SLUG_BY_GKEY.get(gkey)
        if not slug:
            continue
        # 只保留 tag / h3 / guide-lead 三個子元素
        keepers = []
        for child in list(art.children):
            if not hasattr(child, "name") or child.name is None:
                continue
            cls = child.get("class") or []
            if (child.name == "span" and "guide-tag" in cls) or \
               child.name == "h3" or \
               (child.name == "p" and "guide-lead" in cls):
                keepers.append(child)
        for child in list(art.children):
            child.extract()
        for k in keepers:
            art.append(k)
        # 接「閱讀完整文章 →」連結
        link = soup.new_tag("a", attrs={
            "class": "guide-card-link",
            "href": f"{lang_prefix}/guides/{slug}/",
        })
        link.string = read_more
        art.append(link)


# ============================================================
# 獨立教學分頁產生器:/guides/<slug>/index.html
# 完全沿用首頁的 <head> + <style>(視覺一致),body 換成 guide layout
# ============================================================
def build_guide_page(slug, lang, src_html, i18n, guide_cfg):
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    g_i18n = guide_cfg["i18n"][lang]
    ui = UI_STRINGS[lang]
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    page_url = f"{SITE}{lang_prefix}/guides/{slug}/"
    home_url = f"{SITE}{lang_prefix}/"

    # 1. <html lang>
    soup.html["lang"] = cfg["html_lang"]

    # 2. i18n fill (走完整流程以確保 footer 等共用元件正確)
    lang_dict = i18n.get(lang, {})
    zh_dict = i18n["zh"]
    for el in soup.select("[data-i18n]"):
        key = el.get("data-i18n")
        text = lang_dict.get(key) or zh_dict.get(key)
        if text is not None:
            frag = BeautifulSoup(text, "html.parser")
            el.clear()
            for child in list(frag.children):
                el.append(child)

    # 3. 找到目標教學 article (透過 .guide-tag 的 data-i18n key prefix)
    target_article = None
    for art in soup.select("article.guide-article"):
        tag_el = art.select_one(".guide-tag")
        if tag_el and tag_el.get("data-i18n", "").startswith(guide_cfg["key"] + "."):
            target_article = art.extract()
            break
    if target_article is None:
        raise RuntimeError(f"找不到教學 article: key={guide_cfg['key']}")

    # 4. 保留 footer
    footer_el = soup.find("footer")
    footer_extracted = footer_el.extract() if footer_el else None

    # 5. 砍掉現有 JSON-LD 與 hreflang(加 guide 專用的)
    for s in soup.find_all("script", {"type": "application/ld+json"}):
        s.decompose()
    for tag in soup.find_all("link", {"rel": "alternate"}):
        tag.decompose()

    # 6. <title> / meta / canonical
    if soup.title:
        soup.title.string = g_i18n["title"]

    def set_meta(attr, attr_val, content):
        tag = soup.find("meta", {attr: attr_val})
        if tag:
            tag["content"] = content

    set_meta("name", "description", g_i18n["description"])
    # keywords:zh/ja 頁附加 en 版關鍵字(品牌與技術詞跨語言通用),en 頁不附加避免重複
    guide_kw = g_i18n["keywords"]
    if lang != "en" and "en" in guide_cfg["i18n"]:
        guide_kw = guide_kw + ", " + guide_cfg["i18n"]["en"]["keywords"]
    set_meta("name", "keywords", guide_kw)
    set_meta("http-equiv", "Content-Language", cfg["html_lang"])
    set_meta("property", "og:type", "article")
    set_meta("property", "og:url", page_url)
    set_meta("property", "og:title", g_i18n["title"])
    set_meta("property", "og:description", g_i18n["description"])
    set_meta("property", "og:locale", cfg["og_locale"])
    set_meta("name", "twitter:title", g_i18n["title"])
    set_meta("name", "twitter:description", g_i18n["description"])

    canon = soup.find("link", {"rel": "canonical"})
    if canon:
        canon["href"] = page_url

    # 7. hreflang 三向互指 + x-default(三語 guide 都已存在)
    head = soup.head
    for hl_lang, hl_cfg in LANGS.items():
        hl_attr = hl_cfg["html_lang"]
        hl_prefix = "" if hl_lang == "zh" else f"/{hl_lang}"
        hl_url = f"{SITE}{hl_prefix}/guides/{slug}/"
        link = soup.new_tag("link", attrs={"rel": "alternate", "hreflang": hl_attr, "href": hl_url})
        head.append(link)
    # x-default 指 zh
    link = soup.new_tag("link", attrs={
        "rel": "alternate", "hreflang": "x-default",
        "href": f"{SITE}/guides/{slug}/",
    })
    head.append(link)

    # 8. Article + BreadcrumbList JSON-LD
    article_ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": g_i18n["h1_for_ld"],
        "description": g_i18n["description"],
        "keywords": g_i18n["keywords"],
        "inLanguage": cfg["html_lang"],
        "url": page_url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        "author": {"@type": "Organization", "name": "MotorLab.tw", "url": SITE + "/"},
        "publisher": {
            "@type": "Organization",
            "name": "MotorLab.tw",
            "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon-192.png", "width": 192, "height": 192},
        },
        "image": f"{SITE}/og-image.png",
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui["bc_home"], "item": home_url},
            {"@type": "ListItem", "position": 2, "name": ui["bc_guides"], "item": f"{home_url}#guides"},
            {"@type": "ListItem", "position": 3, "name": g_i18n["breadcrumb"], "item": page_url},
        ],
    }
    for data in (article_ld, breadcrumb_ld):
        s = soup.new_tag("script", attrs={"type": "application/ld+json"})
        s.string = json.dumps(data, ensure_ascii=False, indent=2)
        head.append(s)

    # 9. 換 <body>
    soup.body.clear()
    soup.body["class"] = "guide-page"

    # 9a. minimal sticky nav(語言對應的 home URL)
    nav_html = (
        f'<nav class="guide-nav"><div class="container">'
        f'<a class="brand" href="{home_url}"><span>MotorLab<span class="tag">.tw</span></span></a>'
        f'<a class="back-link" href="{home_url}">{ui["back_home"]}</a>'
        f'</div></nav>'
    )
    soup.body.append(BeautifulSoup(nav_html, "html.parser"))

    # 9b. main(breadcrumb + article + pagination + GitHub link)
    main_el = soup.new_tag("main")
    container = soup.new_tag("div", attrs={"class": "container"})

    bc_html = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb">'
        f'<a href="{home_url}">{ui["bc_home"]}</a><span class="sep">/</span>'
        f'<a href="{home_url}#guides">{ui["bc_guides"]}</a><span class="sep">/</span>'
        f'<span class="current">{g_i18n["breadcrumb"]}</span>'
        f'</nav>'
    )
    container.append(BeautifulSoup(bc_html, "html.parser"))
    container.append(target_article)

    # Pagination(連結用對應語言的 breadcrumb 名稱)
    idx = next((i for i, g in enumerate(GUIDES) if g["key"] == guide_cfg["key"]), -1)
    prev_g = GUIDES[idx - 1] if idx > 0 else None
    next_g = GUIDES[idx + 1] if idx < len(GUIDES) - 1 else None

    def _link_cell(g, label, css_class):
        if g is None:
            return (
                f'<div class="{css_class}"><span class="label">{label}</span>'
                f'<span class="disabled">—</span></div>'
            )
        # 若目的 guide 沒有該語言翻譯,fallback 到 zh
        g_label = g["i18n"].get(lang, g["i18n"]["zh"])["breadcrumb"]
        return (
            f'<div class="{css_class}">'
            f'<a href="{lang_prefix}/guides/{g["slug"]}/">'
            f'<span class="label">{label}</span><span>{g_label}</span>'
            f'</a></div>'
        )

    pag_html = (
        '<div class="guide-pagination">'
        + _link_cell(prev_g, ui["prev"], "left")
        + f'<div class="center"><a href="{home_url}#guides">'
          f'<span class="label">︿</span><span>{ui["home_label"]}</span></a></div>'
        + _link_cell(next_g, ui["next"], "right")
        + '</div>'
    )
    container.append(BeautifulSoup(pag_html, "html.parser"))

    main_el.append(container)
    soup.body.append(main_el)

    # 9c. footer
    if footer_extracted is not None:
        soup.body.append(footer_extracted)

    return str(soup)


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
    print("=== 教學分頁(/guides/<slug>/)===")
    for guide in GUIDES:
        for lang in ("zh", "en", "ja"):
            if lang not in guide["i18n"]:
                continue  # 該語言尚未撰寫該篇 → 跳過
            slug = guide["slug"]
            lang_prefix = "" if lang == "zh" else f"{lang}/"
            out_dir = f"{lang_prefix}guides/{slug}"
            out_path = f"{out_dir}/index.html"
            os.makedirs(out_dir, exist_ok=True)
            html_out = build_guide_page(slug, lang, src_html, i18n, guide)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html_out)
            size = len(html_out.encode("utf-8"))
            print(f"  ✅ {out_path:<55} {size:>9,} bytes  ({lang})")

    print()
    print("完成!3 個語言版本 + 教學分頁已產生。")
    print("=" * 55)


if __name__ == "__main__":
    main()

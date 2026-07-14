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
        "description": "MotorLab — 專為 Mini 4WD® 玩家打造的精密馬達磨合測試系統。十三大專業功能:馬達特性量測、十階段可程式化磨合、AI 健康管理、軸承阻力、CV 電刷穩定診斷、三層安全保護、高溫鎖定、狀態燈自訂、OTA 線上更新、全球馬達磨合資料庫。讓馬達調校可量化。",
        "og_title": "MotorLab — Mini 4WD® 馬達磨合測試系統",
        "og_desc": "為每一顆 Mini 4WD® 馬達建立可量化的健康指紋。十三大專業功能:馬達特性量測、十階段磨合、AI 健康管理、軸承阻力分析、電刷穩定診斷、三層安全保護、高溫鎖定、狀態燈自訂、全球馬達磨合資料庫。",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "為每一顆 Mini 4WD® 馬達建立可量化的健康指紋",
        "ld_org_desc": "為 Mini 4WD® 玩家打造的精密馬達磨合與測試系統研發工作室",
        "ld_site_desc": "MotorLab — Mini 4WD® 馬達磨合與精密測試系統官方網站",
        "ld_app_desc": "Mini 4WD® 馬達磨合與精密測試系統。內建十階段可程式化磨合、AI 智慧馬達健康管理、軸承阻力測試、電刷接觸穩定診斷。",
    },
    "en": {
        "title": "MotorLab — Mini 4WD® Motor Break-in & Diagnostics System",
        "description": "MotorLab — precision Mini 4WD® motor break-in & diagnostics. Motor characterization, 10-stage break-in, AI health management, bearing resistance.",
        "og_title": "MotorLab — Mini 4WD® Motor Break-in & Test System",
        "og_desc": "Build a measurable health fingerprint for every Mini 4WD® motor. Thirteen professional tools: motor characterization, 10-stage break-in, AI health management, bearing resistance analysis, brush stability diagnostics, triple-layer safety protection, overheat lock, custom status lighting and a global break-in data library.",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "Build a measurable health fingerprint for every Mini 4WD® motor",
        "ld_org_desc": "An R&D studio building precision motor break-in and testing systems for Mini 4WD® racers.",
        "ld_site_desc": "Official site of the MotorLab Mini 4WD® motor break-in and precision testing system.",
        "ld_app_desc": "Mini 4WD® motor break-in and precision testing system. Includes 10-stage programmable break-in, AI motor health management, bearing resistance analysis and brush contact stability diagnostics.",
    },
    "ja": {
        "title": "MotorLab — Mini 4WD® モーター慣らし・テストシステム | 精密モーター診断スタジオ",
        "description": "MotorLab — Mini 4WD® プレイヤー向けの精密モーター慣らし・診断システム。モーター特性測定、10 段階プログラム慣らし、AI 健康管理、ベアリング抵抗、CV ブラシ安定診断、高温保護を搭載。",
        "og_title": "MotorLab — Mini 4WD® モーター慣らし・テストシステム",
        "og_desc": "すべての Mini 4WD® モーターに定量化できる健康指紋を。13 のプロ機能:モーター特性測定、10 段階慣らし、AI 健康管理、ベアリング抵抗解析、ブラシ安定診断、三層安全保護、高温ロック、ステータスライト カスタム、グローバル慣らしデータ庫。",
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
        "published": "2026-05-22",
        "updated": "2026-06-12",
        "i18n": {
            "zh": {
                "title": "四驅車馬達磨合完全指南:從原理到實作 | MotorLab",
                "description": "迷你四驅車馬達磨合(玩家俗稱「磨馬達」)完整教學 — 田宮馬達磨合的科學原理、電壓/轉速/時間/冷卻 4 個關鍵變數、10 階段標準流程,以及磨合完成的判定標準。解答新馬達到底要不要磨、為什麼業餘「水磨」方法行不通。",
                "keywords": "馬達磨合, 磨馬達, 四驅車馬達磨合, 迷你四驅車馬達磨合, 馬達磨合原理, 馬達磨合 10 階段, 田宮馬達磨合, 馬達磨合教學, 磨馬達教學, 紅二磨合, 黑金剛磨合, 碳刷磨合, motor break-in, MotorLab",
                "breadcrumb": "馬達磨合完全指南",
                "h1_for_ld": "四驅車馬達磨合完全指南:從原理到實作",
            },
            "en": {
                "title": "How to Break In a Tamiya Mini 4WD Motor (10 Stages) | MotorLab",
                "description": "How to break in a Tamiya Mini 4WD motor: the 10-stage stock steps, 4 control variables, brush seating physics, and the RPM gain before vs after break-in.",
                "keywords": "how to break in a Mini 4WD motor, Mini 4WD motor break in, motor break-in guide, Tamiya motor break-in, Hyper Dash break-in, motor running-in, motor bedding, 10-stage break-in, break-in RPM gain before after, carbon brush seating, MotorLab",
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
        "published": "2026-05-22",
        "updated": "2026-05-22",
        "i18n": {
            "zh": {
                "title": "業餘車手磨合馬達總是失敗?5 個常見錯誤與正確做法 | MotorLab",
                "description": "迷你四驅車磨馬達(馬達磨合)為什麼總是失敗?整理業餘車手最常見的 5 個錯誤:乾電池亂跑、水磨水量太多、單向磨合、不測就跑、憑感覺判斷。逐一說明每個錯誤的後果與正確做法,以及如何建立馬達健康指紋、避免馬達燒掉。",
                "keywords": "馬達磨合錯誤, 業餘馬達磨合失敗, 乾電池磨合馬達, 水磨馬達錯誤, 馬達磨合方向, 馬達燒掉原因, 磁鐵退磁, 馬達健康指紋, 馬達磨合 CV",
                "breadcrumb": "5 個常見磨合錯誤",
                "h1_for_ld": "為什麼業餘車手磨合馬達總是失敗?5 個常見錯誤",
            },
            "en": {
                "title": "5 Mini 4WD Motor Break-in Mistakes Amateurs Make | MotorLab",
                "description": "The 5 most common Mini 4WD motor break-in mistakes — dry-battery runs, over water-soak, one-direction running, no measurement, no records — and the fixes.",
                "keywords": "motor break-in mistakes, motor break-in failure, dry battery break-in, water-soak motor mistakes, motor break-in direction, motor burnout cause, magnet demagnetization, motor health fingerprint, break-in CV",
                "breadcrumb": "5 Common Break-in Mistakes",
                "h1_for_ld": "Why Amateur Motor Break-in Fails: 5 Common Mistakes",
            },
            "ja": {
                "title": "アマチュアのモーター慣らしが失敗する理由:5 つのよくある間違い | MotorLab",
                "description": "ミニ四駆のモーター慣らしはいらない?失敗する人に最も多い 5 つの間違い:乾電池で適当に回す、水慣らしの水量過多、片方向だけ、測定せず実走、感覚頼り。各間違いの結果と正しい手順、モーター健康指紋の構築方法まで詳しく解説。",
                "keywords": "モーター慣らし 間違い, モーター慣らし 失敗, 乾電池 モーター慣らし, 水慣らし 間違い, モーター慣らし 方向, モーター 焼損 原因, 磁石 減磁, モーター 健康指紋, 慣らし CV",
                "breadcrumb": "5 つの慣らしミス",
                "h1_for_ld": "アマチュアのモーター慣らしが失敗する理由:5 つのよくある間違い",
            },
        },
    },
    {
        "slug": "tamiya-motor-specs",
        "key": "g3",
        "published": "2026-05-22",
        "updated": "2026-06-12",
        "i18n": {
            "zh": {
                "title": "田宮主流馬達規格與磨合策略對照表 | 紅二/黑金剛/紫頭速查 | MotorLab",
                "description": "田宮 8 款主流 Mini 4WD 馬達(紅二 Hyper Dash、黑金剛 Plasma Dash、紫頭 Rev Tuned、橘頭 Torque Tuned 等)的官方規格與建議磨合策略對照表。銅刷與碳刷馬達的磨合差異,以及田宮競賽合規規則。",
                "keywords": "田宮馬達規格, 四驅車馬達規格, 田宮馬達, 紅二 Hyper Dash, 黑金剛 Plasma Dash, 紫頭 Rev Tuned, 橘頭 Torque Tuned, 灰頭 Atomic Tuned, 綠頭 Power Dash, 白頭 Sprint Dash, 銅刷碳刷差別, 田宮馬達磨合, 田宮競賽規則",
                "breadcrumb": "田宮馬達速查表",
                "h1_for_ld": "田宮主流馬達規格與磨合策略對照表",
            },
            "en": {
                "title": "Which Tamiya Mini 4WD Motor to Use? Speed vs Torque | MotorLab",
                "description": "How to choose a Tamiya Mini 4WD motor: 8 mainstream motors compared by speed vs torque, which to use per course, plus break-in strategy.",
                "keywords": "which Tamiya motor to use, best Tamiya Mini 4WD motor, speed vs torque motor, Tamiya motor for technical course, Hyper Dash 2, Plasma Dash, Power Dash, Sprint Dash, Rev-Tuned, Torque-Tuned, Atomic-Tuned, Light Dash, which is faster sprint dash or power dash, copper vs carbon brush, Tamiya break-in strategy",
                "breadcrumb": "Which Motor to Use",
                "h1_for_ld": "Which Tamiya Mini 4WD Motor to Use? Speed vs Torque & Break-In Strategy",
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
        "published": "2026-05-22",
        "updated": "2026-07-14",
        "i18n": {
            "zh": {
                "title": "洗馬達 vs 磨合馬達:差別在哪?什麼時候做? | MotorLab",
                "description": "四驅車「洗馬達」與「磨馬達(磨合)」是兩個完全不同的程序,卻常被混淆。釐清兩者的時機、做法與目的差異:什麼時候該洗、洗馬達標準流程與上油,以及紅二等馬達的生命週期保養與退役判定,讓你不再洗錯也不磨錯。",
                "keywords": "洗馬達, 洗馬達 vs 磨合, 四驅車洗馬達, 馬達保養週期, 馬達上油, 環保去漬油, WURTH 超潤, 紅二保養, 馬達退役判定",
                "breadcrumb": "洗馬達 vs 磨合馬達",
                "h1_for_ld": "洗馬達 vs 磨合馬達:差別在哪?什麼時候做?",
            },
            "en": {
                "title": "Motor Wash vs Break-in: What's the Difference? | MotorLab",
                "description": "Motor wash vs motor break-in: two different procedures often confused. The timing, method and purpose of each, when to wash, and a Mini 4WD motor care cycle.",
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
        "published": "2026-05-22",
        "updated": "2026-07-14",
        "i18n": {
            "zh": {
                "title": "為什麼磨馬達決定四驅車比賽勝負?競賽水準的磨合差距 | MotorLab",
                "description": "從競賽角度看磨馬達:為什麼業餘馬達磨合方式在比賽中行不通、JCO 等大型賽事的實戰場景、健康指紋與成對配對的競技價值。把四驅車馬達準備從「手感」升級成可量化的「數據」,以及競賽級磨合實際可落地的關鍵思維與做法。",
                "keywords": "四驅車比賽磨馬達, 馬達磨合 比賽, JCO 馬達準備, 馬達成對配對, 馬達健康指紋, MotorLab",
                "breadcrumb": "比賽磨合的重要性",
                "h1_for_ld": "為什麼磨馬達決定四驅車比賽勝負?競賽水準的磨合差距",
            },
            "en": {
                "title": "Why Motor Break-in Decides Mini 4WD Race Outcomes | MotorLab",
                "description": "From a racing angle: why amateur break-in fails at sanctioned Mini 4WD events, and the competitive value of health fingerprints and motor pair matching.",
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
        "published": "2026-05-23",
        "updated": "2026-05-23",
        "i18n": {
            "zh": {
                "title": "四驅車競技進階技巧:常勝玩家不寫在書上的 5 個準備細節 | MotorLab",
                "description": "整理 5 個四驅車競技圈實際在用、卻很少被系統化寫出來的進階準備技巧:馬達編號管理、電池×馬達配對、跑道屬性適配、賽前熱機、電池冷卻輪替。把比賽當系統工程處理的具體做法,幫你穩定每一場賽事的車況與臨場發揮。",
                "keywords": "四驅車進階技巧, 電池馬達配對, 跑道馬達選擇, 賽前熱機, 充電池輪替, MotorLab",
                "breadcrumb": "競技進階技巧",
                "h1_for_ld": "四驅車競技進階技巧:常勝玩家不寫在書上的 5 個準備細節",
            },
            "en": {
                "title": "Advanced Mini 4WD Racing: 5 Prep Details Winners Quietly Do | MotorLab",
                "description": "5 advanced Mini 4WD race-prep details winners rarely write down — beyond the motor: bearings, rollers, braking, weight and pre-race checks that decide podiums.",
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
        "published": "2026-05-23",
        "updated": "2026-05-23",
        "i18n": {
            "zh": {
                "title": "從手感到數據:馬達分析的三支柱方法論 | MotorLab",
                "description": "把馬達調校從「手感」轉成系統工程的三步驟方法論:量測、比較、健康判斷。介紹 MotorLab 整個分析系統背後的概念框架、5 個核心量測指標、3 種比較方式、4 個健康維度與 Health Score 評估邏輯。",
                "keywords": "馬達分析方法論, 馬達量測, 馬達比較, 馬達健康評估, Health Score, MotorLab",
                "breadcrumb": "三支柱方法論",
                "h1_for_ld": "從手感到數據:馬達分析的三支柱方法論",
            },
            "en": {
                "title": "From Feel to Data: A Methodology for Motor Analysis | MotorLab",
                "description": "From feel to data: a three-pillar methodology for Mini 4WD motor analysis — baseline, repeatable testing, and historical comparison to judge condition.",
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
        "published": "2026-05-24",
        "updated": "2026-06-12",
        "i18n": {
            "zh": {
                "title": "四驅車馬達衰退的 8 個徵兆與退役判定門檻 | MotorLab",
                "description": "整理 8 個馬達衰退徵兆(性能、聲音、外觀)與 RPM 下降 4 段門檻(< 5% / 5-10% / 10-20% / > 20%)的退役判定。建立 baseline 後可量化判斷該洗、該退役、還是繼續用,避免本番前發現馬達失效。",
                "keywords": "馬達衰退徵兆, 馬達退役判定, 馬達壽命, RPM 下降 馬達, 馬達異常 診斷, MotorLab",
                "breadcrumb": "馬達衰退與退役",
                "h1_for_ld": "四驅車馬達衰退的 8 個徵兆與退役判定門檻",
            },
            "en": {
                "title": "8 Signs Your Mini 4WD Motor Is Dying: Wash vs Retire | MotorLab",
                "description": "8 signs your Mini 4WD motor is dying, and when to wash vs retire — performance/sound/visual cues plus RPM-drop thresholds to decide before a race.",
                "keywords": "Mini 4WD motor degradation signs, motor retirement, motor lifespan, RPM drop motor, motor failure diagnosis, MotorLab",
                "breadcrumb": "Motor Degradation & Retirement",
                "h1_for_ld": "8 Signs Your Mini 4WD Motor Is Dying — When to Wash vs Retire",
            },
            "ja": {
                "title": "ミニ四駆 モーターが死にかけ?寿命の 8 サインと引退判定 | MotorLab",
                "description": "モーターの寿命・死にかけを見抜く 8 サイン(性能・音・外観)と RPM 低下 4 段階閾値(< 5% / 5-10% / 10-20% / > 20%)による引退判定。ベースライン構築後、洗浄・引退・続行を定量的に判断、本番でモーターが死ぬ前に対処可能。",
                "keywords": "ミニ四駆 モーター 死亡, モーター 死にかけ, モーター 寿命, モーター 衰退 サイン, モーター 引退 判定, RPM 低下 モーター, モーター 異常 診断, MotorLab",
                "breadcrumb": "モーター寿命と引退",
                "h1_for_ld": "ミニ四駆 モーターが死にかけ?寿命の 8 サインと引退判定",
            },
        },
    },
    # ---------- g9:田宮全 15 款馬達規格對照(/benchmarks/ 首篇,D23 分類)----------
    {
        "slug": "tamiya-mini-4wd-motor-specs-list",
        "key": "g9",
        "published": "2026-05-25",
        "updated": "2026-05-25",
        "type": "benchmarks",
        "i18n": {
            "zh": {
                "title": "田宮 Mini 4WD® 全 15 款馬達規格對照表(含 PRO 系列)| MotorLab",
                "description": "田宮(TAMIYA, INC.)Mini 4WD® 全 15 款馬達官方規格對照表 — 標準系列 9 款(單軸)+ PRO 系列 6 款(雙軸)。整理 RPM、扭力(mN·m)、電流(A)、Speed/Torque 等級與官方比賽合規限制。",
                "keywords": "田宮馬達, 田宮 15 款馬達, 田宮馬達規格, Mini 4WD PRO 馬達, 雙軸馬達, 單軸馬達, 田宮馬達對照表, Hyper-Dash PRO, Mach-Dash PRO, Plasma-Dash, Ultra-Dash, Power-Dash, Sprint-Dash, 田宮比賽合規, 紅二, 黑金剛",
                "breadcrumb": "全 15 款馬達規格",
                "h1_for_ld": "田宮 Mini 4WD® 全 15 款馬達規格對照表(含 PRO 系列)",
            },
            "en": {
                "title": "Tamiya Mini 4WD Motor Chart: All 15 Motors (RPM, Torque) | MotorLab",
                "description": "Complete Tamiya Mini 4WD motor chart — all 15 motors (9 standard + 6 PRO) with RPM, torque, current and race-legality. Compare and find the fastest.",
                "keywords": "Tamiya Mini 4WD motor chart, Tamiya motor specs table, Tamiya motor specifications, list of Tamiya motors, Tamiya 15 motors, Mini 4WD PRO motors, double-shaft motor, single-shaft motor, Hyper-Dash PRO, Mach-Dash PRO, Plasma-Dash, Ultra-Dash, Power-Dash, Sprint-Dash, fastest Tamiya motor, Tamiya race compliance",
                "breadcrumb": "Full Lineup (15 Motors)",
                "h1_for_ld": "Tamiya Mini 4WD Motor Chart — All 15 Motors",
            },
            "ja": {
                "title": "タミヤ Mini 4WD® 全 15 種モーター規格対照表(PRO シリーズ含む)| MotorLab",
                "description": "タミヤ(TAMIYA, INC.)Mini 4WD® 全 15 種モーターの公式スペック対照表 — 標準シリーズ 9 種(片軸)と Mini 4WD PRO シリーズ 6 種(両軸)。RPM、トルク(mN·m)、電流(A)、Speed/Torque 評価と公式競技ルールを網羅。",
                "keywords": "タミヤ モーター, タミヤ 15 種 モーター, ミニ四駆 PRO モーター, 両軸モーター, 片軸モーター, タミヤ モーター 規格, ハイパーダッシュ PRO, マッハダッシュ PRO, プラズマダッシュ, ウルトラダッシュ, パワーダッシュ, スプリントダッシュ, タミヤ 公式競技ルール, ミニ四駆 モーター 対照表",
                "breadcrumb": "全 15 種モーター規格",
                "h1_for_ld": "タミヤ Mini 4WD® 全 15 種モーター規格対照表(PRO シリーズ含む)",
            },
        },
    },
    # ---------- g10:軌道分析與馬達選型(methodology hub)----------
    {
        "slug": "track-analysis-motor-selection",
        "key": "g10",
        "published": "2026-06-04",
        "updated": "2026-07-14",
        "type": "guides",
        "i18n": {
            "zh": {
                "title": "四驅車軌道分析與馬達選型:高速軌/技術軌/立體軌 | MotorLab",
                "description": "用可量化的「軌道區段比例法」分析任何一條 Mini 4WD® 賽道:拆成直線、彎道、特殊三種區段判斷高速軌/技術軌/立體軌,對應馬達、齒比與輪徑。附 2025 田宮 Japan Cup 官方賽道實例分析。",
                "keywords": "四驅車軌道分析, 馬達選型, 高速軌, 技術軌, 立體軌, 軌道類型, 齒比選擇, 田宮賽道, Japan Cup 2025, Mini 4WD 賽道攻略, 馬達轉速扭力, 賽道區段比例",
                "breadcrumb": "軌道分析與馬達選型",
                "h1_for_ld": "四驅車軌道分析與馬達選型:用區段比例判斷高速軌/技術軌/立體軌",
            },
            "en": {
                "title": "Mini 4WD Track Analysis & Motor Selection by Section Ratio | MotorLab",
                "description": "A section-ratio method to classify any Mini 4WD track as high-speed, technical or 3D, then match motor, gear ratio and wheel. With a Japan Cup example.",
                "keywords": "Mini 4WD track analysis, motor selection, high-speed course, technical course, 3D course, gear ratio selection, Tamiya circuit, Japan Cup 2025, Mini 4WD course strategy, motor RPM torque, track section ratio",
                "breadcrumb": "Track Analysis & Motor Selection",
                "h1_for_ld": "Mini 4WD Track Analysis & Motor Selection by Section Ratio",
            },
            "ja": {
                "title": "Mini 4WD コース分析とモーター選び:高速/テクニカル/立体 | MotorLab",
                "description": "定量化できる「コース区間比率法」であらゆる Mini 4WD® コースを分析:ストレート・カーブ・特殊区間に分解して高速コース/テクニカルコース/立体コースを判定し、モーター・ギア比・タイヤ径を対応づけ。2025 タミヤ ジャパンカップ公式コースの実例分析付き。",
                "keywords": "ミニ四駆 コース分析, モーター 選び方, 高速コース, テクニカルコース, 立体コース, ギア比 選び方, タミヤ コース, ジャパンカップ 2025, ミニ四駆 コース攻略, モーター 回転数 トルク, コース 区間比率",
                "breadcrumb": "コース分析とモーター選び",
                "h1_for_ld": "Mini 4WD コース分析とモーター選び:区間比率で高速/テクニカル/立体を判定",
            },
        },
    },
    # ---------- g11:飛車風險判定模型(methodology hub)----------
    {
        "slug": "crash-risk-trigger-model",
        "key": "g11",
        "published": "2026-06-04",
        "updated": "2026-06-04",
        "type": "guides",
        "i18n": {
            "zh": {
                "title": "四驅車為什麼會飛車?Speed/Geometry/Stability 三觸發模型 | MotorLab",
                "description": "四驅車比賽飛車(出軌)不是運氣,而是速度、賽道幾何、車體穩定性三種觸發疊加超過臨界的結果。本文提供 Speed/Geometry/Stability 三觸發判定模型、現場風險計數法、常見必飛組合與對應改裝對策。",
                "keywords": "四驅車飛車, Mini 4WD 改裝, 賽道分析, 四驅車設定, 飛車原因, 田宮日本杯, 煞車調整, 重心調整, 齒比設定, 賽道判讀, 出軌, 觸發模型",
                "breadcrumb": "飛車風險判定模型",
                "h1_for_ld": "四驅車為什麼會飛車?Speed / Geometry / Stability 三觸發判定模型",
            },
            "en": {
                "title": "Why Mini 4WD Cars Crash: The 3-Trigger Risk Model | MotorLab",
                "description": "Mini 4WD crashes aren't random: they happen when Speed, Geometry and Stability triggers stack past a threshold. A trigger model with on-site risk counting.",
                "keywords": "Mini 4WD setup, Mini 4WD crash, course out, track analysis, Tamiya Mini 4WD, braking setup, gear ratio, center of gravity, stability tuning, racing setup strategy, cornering speed control, trigger model",
                "breadcrumb": "Crash Risk Trigger Model",
                "h1_for_ld": "Why Mini 4WD Cars Crash: The Speed / Geometry / Stability Trigger Model",
            },
            "ja": {
                "title": "ミニ四駆がコースアウトする原因?3-Trigger 判定モデル | MotorLab",
                "description": "ミニ四駆のコースアウトは偶然ではなく、スピード・コース形状・車体安定性の 3 要因が重なり臨界を超えた結果。本記事は Speed/Geometry/Stability の 3-Trigger 判定モデル、レース現場でのリスク計数法、よくあるコースアウトパターンと対応セッティングを解説します。",
                "keywords": "ミニ四駆 コースアウト 原因, セッティング, ジャパンカップ, ブレーキ調整, 重心, ギア比, 安定性, コーナー対策, 速度制御, トリガーモデル, ミニ四駆 改造",
                "breadcrumb": "コースアウト判定モデル",
                "h1_for_ld": "ミニ四駆がコースアウトする原因?Speed / Geometry / Stability 3-Trigger モデル",
            },
        },
    },
    # ---------- g12:先選別後磨合 —— 用電流讀出馬達體質(methodology hub)----------
    {
        "slug": "motor-selection-before-break-in",
        "key": "g12",
        "published": "2026-07-02",
        "updated": "2026-07-02",
        "type": "guides",
        "i18n": {
            "zh": {
                "title": "先選別,後磨合:用電流讀出馬達體質 | MotorLab",
                "description": "同一批、同型號的馬達,體質天生不同。磨合只能改善電刷與整流子的接觸面,鐵芯、磁路、動平衡的先天差異磨不掉。本文教你先量測、後磨合:用無載電流當損耗轉矩指標,先挑出體質好的個體,再把時間與碳刷壽命投資在值得的馬達上。",
                "keywords": "馬達選別, 選馬達, 磨馬達, 馬達磨合, 損耗轉矩, 無載電流, 馬達體質, 馬達挑選, Kt 轉矩常數, Km 馬達常數, Ke, MotorLab",
                "breadcrumb": "馬達選別",
                "h1_for_ld": "先選別,後磨合:用電流讀出馬達體質",
            },
            "en": {
                "title": "Select Motors Before Break-in: Grade by Current | MotorLab",
                "description": "Same batch, unequal motors. Measure before break-in: no-load current is a loss-torque index — grade motors first, invest break-in only in the good ones.",
                "keywords": "motor selection, motor grading, Mini 4WD motor, no-load current, loss torque, torque constant Kt, motor constant Km, Ke, measure before break-in, MotorLab",
                "breadcrumb": "Select Before Break-in",
                "h1_for_ld": "Select Motors Before Break-in: Read a Motor's Constitution by Current",
            },
            "ja": {
                "title": "選別してから慣らす:電流でモーターの素性を読む | MotorLab",
                "description": "同じロット・同じ型番でもモーターの素性は違う。慣らしで直るのはブラシと整流子の接触面だけで、鉄芯・磁路・バランスの先天差は消えない。先に測って後で慣らす:無負荷電流を損失トルク指標に素性の良い個体を選び、時間とブラシ寿命を価値ある個体に投資する方法。",
                "keywords": "モーター選別, モーター 選び方, モーター慣らし, 損失トルク, 無負荷電流, 素性, トルク定数 Kt, モーター定数 Km, Ke, MotorLab",
                "breadcrumb": "モーター選別",
                "h1_for_ld": "選別してから慣らす:電流でモーターの素性を読む",
            },
        },
    },
    # ---------- g13:磨馬達要磨多久 —— R 磨合曲線實測(methodology hub)----------
    {
        "slug": "motor-break-in-resistance-curve",
        "key": "g13",
        "published": "2026-07-07",
        "updated": "2026-07-07",
        "type": "guides",
        "i18n": {
            "zh": {
                "title": "磨馬達要磨多久?連續量測 560 次的磨合曲線 | MotorLab",
                "description": "磨馬達到底要磨多久?我們對同一顆 Mach-Dash PRO 連續量測 560 次,把內部電阻畫成一條磨合曲線:前 80 次爬升是接觸面成形、中段平穩是磨合完成、後段離散上升是衰退。看曲線何時轉平,就知道該不該繼續磨。",
                "keywords": "磨馬達, 磨馬達要磨多久, 馬達磨合, 磨合完成, 磨合曲線, 馬達壽命, 碳刷 接觸電阻, Mach-Dash PRO, 迷你四驅車 馬達實測, MotorLab",
                "breadcrumb": "磨合曲線實測",
                "h1_for_ld": "磨馬達到底要磨多久?一顆馬達連續量測 560 次給你答案",
            },
            "en": {
                "title": "How Long to Break In a Motor? 560 Runs, One Curve | MotorLab",
                "description": "How long to break in a motor? We ran one Mach-Dash PRO 560 times, plotting resistance: early rise, plateau, then rising scatter — read where it flattens.",
                "keywords": "motor break-in duration, how long to break in a motor, Mini 4WD motor break-in, break-in curve, motor life, brush contact resistance, Mach-Dash PRO, motor endurance test, MotorLab",
                "breadcrumb": "Break-in R Curve",
                "h1_for_ld": "How Long to Break In a Motor? 560 Runs on One Mach-Dash PRO, One Resistance Curve",
            },
            "ja": {
                "title": "モーター慣らしはどれくらい?連続 560 回計測の慣らし曲線 | MotorLab",
                "description": "モーター慣らしはどれくらい必要?同じ Mach-Dash PRO を連続 560 回計測し内部抵抗を 1 本の曲線に。最初の約 80 回の上昇は接触面形成、中盤の平坦は慣らし完了、後半のばらつき増大は劣化。曲線が平らになった点が慣らしをやめる目安。",
                "keywords": "モーター慣らし 時間, モーター慣らし どれくらい, ミニ四駆 モーター慣らし, 慣らし曲線, モーター 寿命, ブラシ 接触抵抗, マッハダッシュ PRO, モーター 耐久テスト, MotorLab",
                "breadcrumb": "慣らし曲線実測",
                "h1_for_ld": "モーター慣らしはどれくらい必要?同じモーターを連続 560 回計測した答え",
            },
        },
    },
    # ---------- g14:磨馬達控速 vs 控壓(methodology hub)----------
    {
        "slug": "motor-break-in-speed-vs-voltage",
        "key": "g14",
        "published": "2026-07-14",
        "updated": "2026-07-14",
        "type": "guides",
        "i18n": {
            "zh": {
                "title": "為什麼磨馬達要鎖轉速不鎖電壓?控速 vs 控壓 | MotorLab",
                "description": "幾乎所有人磨馬達都用「定電壓」,轉速只拿來量。但從物理看,決定磨合品質的是接觸面滑動速度(=轉速),不是電壓。本文從物理比較控電壓 vs 控轉速:為什麼定電壓下轉速會漂、跨馬達不一致,而閉環控速能鎖住條件、可重現。",
                "keywords": "磨馬達, 控速 控壓, 定電壓 磨合, 鎖轉速 磨合, 馬達磨合 電壓, 閉環控速, 磨合控制, 迷你四驅車 磨馬達, MotorLab",
                "breadcrumb": "控速 vs 控壓",
                "h1_for_ld": "為什麼磨馬達要鎖轉速,不鎖電壓?",
            },
            "en": {
                "title": "Why Break In a Motor at Fixed Speed, Not Fixed Voltage? | MotorLab",
                "description": "Everyone breaks in at fixed voltage — but break-in quality is set by RPM (the contact sliding speed), not voltage. Fixed-voltage vs fixed-speed, explained.",
                "keywords": "motor break-in control, fixed voltage vs fixed speed, closed-loop break-in, Mini 4WD motor break-in, break-in RPM, constant voltage break-in, brush seating, MotorLab",
                "breadcrumb": "Speed vs Voltage",
                "h1_for_ld": "Why Break In a Motor at Fixed Speed, Not Fixed Voltage",
            },
            "ja": {
                "title": "なぜモーター慣らしは電圧より回転数を固定すべき? | MotorLab",
                "description": "ほぼ全員が「定電圧」でモーター慣らしをし、回転数は測るだけ。だが物理的に慣らしの品質を決めるのは接触面の摺動速度(=回転数)で、電圧ではない。定電圧 vs 定回転数を物理から比較:なぜ定電圧では回転数がずれ再現できないのか。",
                "keywords": "モーター慣らし 制御, 定電圧 定回転数, 閉ループ 慣らし, ミニ四駆 モーター慣らし, 慣らし 回転数, 定電圧 慣らし, MotorLab",
                "breadcrumb": "定電圧 vs 定回転数",
                "h1_for_ld": "なぜモーター慣らしは電圧ではなく回転数を固定するのか?",
            },
        },
    },
]

# UI 字串(教學頁面通用元件:nav / 麵包屑 / 分頁)
#   bc_section:依文章 type 的麵包屑中段標籤,對應 HANDOFF D23 五個分類資料夾
UI_STRINGS = {
    "zh": {
        "back_home": "← 回首頁",
        "bc_home": "首頁",
        "bc_guides": "教學",  # 舊鍵保留(向後相容,新文章用 bc_section)
        "prev": "← 上一篇",
        "next": "下一篇 →",
        "home_label": "回教學首頁",
        "read_more": "閱讀完整文章 →",
        "byline": "編輯者:MotorLab Team",
        "date_pub": "發表",
        "date_upd": "更新",
        "hub_count": "{n} 篇文章 →",
        "bc_section": {
            "guides": "教學",
            "benchmarks": "效能對比",
            "system": "系統",
            "docs": "文件",
            "knowledge_base": "知識庫",
            "methodology": "方法論",
        },
    },
    "en": {
        "back_home": "← Back to home",
        "bc_home": "Home",
        "bc_guides": "Guides",
        "prev": "← Previous",
        "next": "Next →",
        "home_label": "Back to guides",
        "read_more": "Read full article →",
        "byline": "Edited by MotorLab Team",
        "date_pub": "Published",
        "date_upd": "Updated",
        "hub_count": "{n} articles →",
        "bc_section": {
            "guides": "Guides",
            "benchmarks": "Benchmarks",
            "system": "System",
            "docs": "Docs",
            "knowledge_base": "Knowledge Base",
            "methodology": "Methodology",
        },
    },
    "ja": {
        "back_home": "← ホームへ戻る",
        "bc_home": "ホーム",
        "bc_guides": "ガイド",
        "prev": "← 前の記事",
        "next": "次の記事 →",
        "home_label": "ガイド一覧へ",
        "read_more": "全文を読む →",
        "byline": "編集者:MotorLab Team",
        "date_pub": "公開",
        "date_upd": "更新",
        "hub_count": "{n} 件の記事 →",
        "bc_section": {
            "guides": "ガイド",
            "benchmarks": "ベンチマーク",
            "system": "システム",
            "docs": "ドキュメント",
            "knowledge_base": "ナレッジベース",
            "methodology": "方法論",
        },
    },
}

# slug 與 g{n} 的快速反查
SLUG_BY_GKEY = {g["key"]: g["slug"] for g in GUIDES}
# 文章 type 的快速反查(D23 分類,default 為 guides 維持向後相容)
TYPE_BY_GKEY = {g["key"]: g.get("type", "guides") for g in GUIDES}

# ============================================================
# HUBS:首頁知識庫的 3 個入口分類 + 對應的獨立 hub 頁面
#   URL:    /{lang_prefix}/{slug}/index.html
#   include:該 hub 收錄的 article g-key 列表(虛擬 curation,不動原文章 URL)
# 注意:guides / benchmarks hub 的 slug 與 D23 type 同名 — hub 頁正好放在
#       type 資料夾根目錄(/guides/index.html 同時是 hub 與 type 列表)。
#       methodology 是純 curation hub,實體文章仍住原本的 /guides/ 下。
# ============================================================
HUBS = [
    {
        "slug": "guides",
        "include": ["g1", "g2", "g4"],
        "i18n": {
            "zh": {
                "title": "教學 — Mini 4WD® 馬達磨合與調校教學系列 | MotorLab",
                "description": "Mini 4WD® 馬達磨合的系統化教學系列 — 從新馬達為何要磨合的物理原理、4 個關鍵變數、10 階段標準流程、5 個常見錯誤,到「洗馬達 vs 磨合」的觀念釐清。",
                "h1": "教學",
                "lead": "從馬達磨合的科學原理、實作步驟、常見錯誤,到保養觀念。為新手與回鍋玩家準備的系統化教學系列。",
                "keywords": "馬達磨合教學, 馬達磨合教程, 四驅車馬達教學, 馬達磨合 how-to, Mini 4WD 教學",
            },
            "en": {
                "title": "Mini 4WD® Motor Tuning Guides | MotorLab",
                "description": "Systematic Mini 4WD motor break-in guides: the physics, the 10-stage procedure, common mistakes and wash-vs-break-in. For new and returning racers.",
                "h1": "Guides",
                "lead": "How-to articles covering the physics, practical steps, common mistakes, and maintenance concepts behind Mini 4WD motor tuning. For new and returning racers.",
                "keywords": "Mini 4WD motor tuning guides, motor break-in tutorial, how to break in Mini 4WD motors, Tamiya motor guides",
            },
            "ja": {
                "title": "Mini 4WD® モーター調整ガイド集 | MotorLab",
                "description": "Mini 4WD® モーター慣らしの体系的ガイド集 — 新品モーターに慣らしが必要な物理原理、4 つの重要制御変数、10 段階標準フロー、よくある間違い、洗浄 vs 慣らしの概念整理。",
                "h1": "ガイド",
                "lead": "モーター慣らしの科学的原理、実践手順、よくある間違い、メンテナンス概念を網羅。初心者から復帰勢まで向けの体系的ガイド集。",
                "keywords": "ミニ四駆 モーター 慣らし ガイド, モーター 調整 how-to, タミヤ モーター ガイド, ブレークイン 手順",
            },
        },
    },
    {
        "slug": "benchmarks",
        "include": ["g3", "g9"],
        "i18n": {
            "zh": {
                "title": "效能對比 — 田宮 Mini 4WD® 馬達規格速查 | MotorLab",
                "description": "田宮 Mini 4WD® 馬達官方規格速查與磨合策略對照 — 涵蓋 8 款主流入門/進階馬達,以及全 15 款 PRO + 標準系列完整對照(RPM、扭力、電流、比賽合規)。",
                "h1": "效能對比",
                "lead": "Mini 4WD 各款馬達的官方規格速查與性能對照,協助你依車架類型與賽道特性挑選最佳搭配。",
                "keywords": "田宮馬達規格對照, Mini 4WD 馬達速查, Tamiya motor specs, Mini 4WD PRO 馬達, 紅二, 黑金剛, Hyper Dash, Plasma Dash",
            },
            "en": {
                "title": "Tamiya Mini 4WD® Motor Specs & Benchmarks | MotorLab",
                "description": "Quick-reference specs and benchmarks for Tamiya Mini 4WD motors: 8 mainstream models plus the full 15-motor PRO + standard lineup with RPM, torque and current.",
                "h1": "Benchmarks",
                "lead": "Official specs and benchmarks for Mini 4WD motors. Pick the right motor for your chassis and course profile.",
                "keywords": "Tamiya Mini 4WD motor specs, Mini 4WD PRO motors, motor benchmarks, Hyper-Dash PRO, Plasma-Dash, Sprint-Dash, Tamiya motor comparison",
            },
            "ja": {
                "title": "タミヤ Mini 4WD® モーター規格対照 | MotorLab",
                "description": "タミヤ Mini 4WD® モーターの公式スペック速査と慣らし戦略対照表 — 主要 8 種モーター + 全 15 種 PRO・標準シリーズの RPM、トルク、電流、公式競技ルールを網羅。",
                "h1": "ベンチマーク",
                "lead": "タミヤ Mini 4WD モーターの公式仕様とベンチマーク対照。シャーシタイプとコース特性に応じたモーター選びに。",
                "keywords": "タミヤ ミニ四駆 モーター 規格, Mini 4WD PRO モーター, モーター ベンチマーク, ハイパーダッシュ PRO, プラズマダッシュ, スプリントダッシュ",
            },
        },
    },
    {
        "slug": "methodology",
        "include": ["g5", "g6", "g7", "g8", "g10", "g11", "g12", "g13", "g14"],
        "i18n": {
            "zh": {
                "title": "方法論 — Mini 4WD® 馬達分析與比賽策略 | MotorLab",
                "description": "從感覺到數據的進階方法論 — 為什麼磨合決定比賽勝負、5 個進階準備技巧、馬達分析三支柱、衰退徵兆與退役判定。職業車手的系統化思維。",
                "h1": "方法論",
                "lead": "進階分析方法與比賽策略系列 — 把馬達調校從「感覺」推進到「數據」,從個別技巧推進到系統化方法論。",
                "keywords": "馬達分析方法論, 馬達調校方法論, Mini 4WD 比賽策略, 馬達健康指紋, RPM 分析, 進階馬達準備",
            },
            "en": {
                "title": "Mini 4WD® Motor Analysis Methodology | MotorLab",
                "description": "Advanced Mini 4WD analysis methodology and race strategy: prep techniques, a three-pillar framework, degradation signs and crash prevention.",
                "h1": "Methodology",
                "lead": "Advanced analysis methodology and competitive strategy — moving motor tuning from feel-based to data-driven, from individual tips to systematic frameworks.",
                "keywords": "Mini 4WD motor analysis methodology, motor tuning methodology, racing strategy, motor health fingerprint, RPM analysis",
            },
            "ja": {
                "title": "Mini 4WD® モーター分析方法論 | MotorLab",
                "description": "感覚からデータへ — 上級者向け方法論:なぜ慣らしがレース結果を決めるか、勝者がやる 5 つの準備技、3 支柱分析フレームワーク、衰退診断。",
                "h1": "方法論",
                "lead": "上級分析方法論と競技戦略 — モーター調整を「感覚」から「データ」へ、個別テクニックから体系的フレームワークへ。",
                "keywords": "ミニ四駆 モーター 分析 方法論, モーター 調整 方法論, レース 戦略, モーター 健康指紋, RPM 分析",
            },
        },
    },
]

# guide key → hub slug 反查(讓首頁卡片轉換知道每張卡屬於哪個 hub)
HUB_BY_GKEY = {g_key: h["slug"] for h in HUBS for g_key in h["include"]}


# ============================================================
# SYSTEM:商品外觀/系統介紹頁(/system/<slug>/,D23 system 分類)
#   build_system_page() 產生圖文展示頁,內容皆在此 config(不在母版),
#   CSS 用母版 <style> 的 .sys-* 類別,沿用 .guide-page 的 nav/breadcrumb/footer。
#   images 為三語共用;features / gallery / dim_rows 為各語言 list。
#   dot:特色卡標題前的小圓點(對應實機可見元件顏色)— "" 表無圓點。
# ============================================================
SYSTEM = {
    "slug": "product-design",
    "type": "system",
    "images": {
        "hero": "/images/og/MotorLab_V1-1.png",
        "gallery": [
            "/images/og/MotorLab_V1-2.png",
            "/images/og/MotorLab_V1-5.png",
            "/images/og/MotorLab_V1-3.png",
            "/images/og/MotorLab_V1-4.png",
            "/images/og/MotorLab_V1-6.png",
        ],
        "dimensions": "/images/og/MotorLab_dimensions.png",
    },
    "i18n": {
        "zh": {
            "title": "馬達磨合機外觀設計:Mini 4WD® 精密測試機 | MotorLab",
            "description": "MotorLab 馬達磨合機的外觀設計介紹 — 低調黑一體機身、對稱雙側護柱、嵌入式字標、前置馬達夾持模組與側向主動散熱。160 × 81 × 90 mm 桌面尺寸,延續實機 Web UI 的工程儀器設計語言。",
            "keywords": "MotorLab 外觀, 馬達磨合機 外觀, 馬達磨合機 設計, 桌上馬達測試機, Mini 4WD 馬達磨合機",
            "breadcrumb": "商品外觀",
            "h1_for_ld": "MotorLab 馬達磨合機外觀設計",
            "eyebrow": "Product Design · 商品外觀",
            "hero_title": "為每一顆<br><span class='sys-accent'>Mini 4WD<span class='sys-reg'>®</span> 馬達</span><br>而生的精密測試機",
            "hero_p": "低調黑機身、對稱護柱、嵌入式字標 —— MotorLab 的外觀延續 Web UI 的工程儀器語言,把「桌上實驗室」的精密感做進每一道折線。",
            "chips": ["尺寸 <b>160 × 81 × 90 mm</b>", "機身 <b>低調黑</b>"],
            "dl_eyebrow": "Design Language · 設計語言",
            "dl_h2": "不是電器,是一台桌上實驗儀器",
            "dl_p": "機身採用低反光的低調黑塊體。形體上以對稱、厚實的雙側護柱包覆核心模組,既是搬運時的提把,也是運轉時的結構保護;所有外露元件(夾具、感測座、散熱口、狀態燈)都被收進俐落的折線之中,沒有多餘裝飾,只留下工程感。",
            "feat_eyebrow": "Exterior Highlights · 外觀特色",
            "feat_h2": "每一個細節都有功能",
            "feat_lead": "外觀上看得到的每一處設計,都對應一個實際用途 —— 從夾持、散熱到狀態提示。",
            "features": [
                {"dot": "", "t": "低調黑機身", "d": "厚實塊體搭配導角折線,低反光表面減少桌面雜光干擾;正面嵌入式「MotorLab」字標,品牌識別一體成形。"},
                {"dot": "", "t": "對稱雙側護柱", "d": "兩側立柱兼具提把與防護機能,搬運時好握、運轉時保護核心模組,也讓整體視覺維持力學上的對稱平衡。"},
                {"dot": "sys-dot-red", "t": "前置馬達夾持模組", "d": "正面陽極夾具搭配感測座,馬達一放即定位,是整台機器的視覺焦點,也是量測精度的起點。"},
                {"dot": "sys-dot-cyan", "t": "側向主動散熱", "d": "側面內嵌散熱風扇與導風開口,長時間磨合也能維持穩定工作溫度,風道收在機身輪廓之內不破壞造型。"},
                {"dot": "sys-dot-blue", "t": "自訂多彩指示燈", "d": "一眼辨識電源與運轉狀態;極簡的單點光源,呼應儀器級的克制美學。"},
                {"dot": "", "t": "精巧桌面尺寸", "d": "160 × 81 × 90 mm 的緊湊體積,單手可移動,輕鬆融入任何工作桌或維修檯,不佔空間。"},
            ],
            "gal_eyebrow": "Gallery · 多角度檢視",
            "gal_h2": "360° 看清每一面",
            "gallery_caps": [
                {"b": "正視", "tag": "FRONT", "d": "對稱護柱包覆中央夾持模組,字標與狀態燈一字排開。"},
                {"b": "裝載", "tag": "MOUNTED", "d": "馬達置入夾具、鎖上感測座的實際使用狀態。"},
                {"b": "散熱面", "tag": "SIDE", "d": "側向散熱風扇與沉孔鎖點,工程結構一覽無遺。"},
                {"b": "俯視", "tag": "TOP", "d": "感測座與夾持軸線由上而下對齊,佈局工整。"},
                {"b": "透視圖", "tag": "X-RAY", "d": "半透視視角下的內部佈局。"},
            ],
            "dim_eyebrow": "Dimensions · 尺寸與結構",
            "dim_h2": "三視圖與尺寸",
            "dim_lead": "完整三視圖 + 立體圖,所有尺寸以毫米(mm)標示。",
            "dim_rows": [
                {"k": "長度 Length", "v": "160", "u": "mm"},
                {"k": "寬度 Width", "v": "81", "u": "mm"},
                {"k": "高度 Height", "v": "90", "u": "mm"},
                {"k": "機身配色 Finish", "v": "低調黑", "u": ""},
            ],
        },
        "en": {
            "title": "Mini 4WD Motor Break-in Machine: Hardware Design | MotorLab",
            "description": "The exterior design of the MotorLab Mini 4WD® break-in machine: a low-key matte-black unibody with front clamp module and active cooling, 160x81x90 mm.",
            "keywords": "MotorLab product design, motor break-in machine design, Mini 4WD motor tester, desktop motor test rig, matte black enclosure",
            "breadcrumb": "Product Design",
            "h1_for_ld": "MotorLab Motor Break-in Machine — Exterior Design",
            "eyebrow": "Product Design",
            "hero_title": "A precision rig built<br>for every <span class='sys-accent'>Mini 4WD<span class='sys-reg'>®</span> motor</span>",
            "hero_p": "Low-key matte black body, symmetric guard pillars, an embedded wordmark — MotorLab's exterior carries the engineering-instrument language of its Web UI, folding desktop-lab precision into every chamfered edge.",
            "chips": ["Size <b>160 × 81 × 90 mm</b>", "Finish <b>Matte black</b>"],
            "dl_eyebrow": "Design Language",
            "dl_h2": "Not an appliance — a desktop lab instrument",
            "dl_p": "The body is a low-reflection matte-black block. Symmetric, substantial guard pillars wrap the core module — a carry handle when moving it, structural protection while running. Every exposed element (clamp, sensor seat, cooling vent, status light) is tucked into clean folds: no decoration, only engineering.",
            "feat_eyebrow": "Exterior Highlights",
            "feat_h2": "Every detail has a function",
            "feat_lead": "Every visible design choice on the exterior maps to a real purpose — from clamping and cooling to status indication.",
            "features": [
                {"dot": "", "t": "Matte black unibody", "d": "A solid block with chamfered folds; the low-reflection surface cuts desktop glare, and the front-embedded “MotorLab” wordmark makes branding part of the form."},
                {"dot": "", "t": "Symmetric guard pillars", "d": "The two pillars double as a carry handle and protection — easy to grip when moving, shielding the core module while running, and keeping the whole form mechanically balanced."},
                {"dot": "sys-dot-red", "t": "Front motor-clamp module", "d": "An anodized clamp plus sensor seat on the front: drop a motor in and it locates instantly — the visual focal point, and the starting point of measurement accuracy."},
                {"dot": "sys-dot-cyan", "t": "Side active cooling", "d": "A built-in fan and air channel on the side hold a stable working temperature through long break-in runs, with the airflow path tucked inside the silhouette."},
                {"dot": "sys-dot-blue", "t": "Custom multi-color indicator", "d": "Read power and run state at a glance; a minimal single point of light, echoing the instrument-grade restraint."},
                {"dot": "", "t": "Compact desktop size", "d": "At 160 × 81 × 90 mm it moves with one hand and slips onto any workbench or repair desk without taking over the space."},
            ],
            "gal_eyebrow": "Gallery",
            "gal_h2": "See every face, 360°",
            "gallery_caps": [
                {"b": "Front", "tag": "FRONT", "d": "Symmetric pillars wrap the central clamp module; wordmark and status light line up across the face."},
                {"b": "Mounted", "tag": "MOUNTED", "d": "A motor seated in the clamp with the sensor seat locked down — the actual in-use state."},
                {"b": "Cooling side", "tag": "SIDE", "d": "Side cooling fan and counterbored mounting points — the engineering structure laid bare."},
                {"b": "Top", "tag": "TOP", "d": "Sensor seat and clamp axis align top-to-bottom; a tidy layout."},
                {"b": "See-through", "tag": "X-RAY", "d": "The internal layout under a semi-transparent view."},
            ],
            "dim_eyebrow": "Dimensions",
            "dim_h2": "Three views & dimensions",
            "dim_lead": "Full three-view drawing plus an isometric view, all dimensions in millimetres (mm).",
            "dim_rows": [
                {"k": "Length", "v": "160", "u": "mm"},
                {"k": "Width", "v": "81", "u": "mm"},
                {"k": "Height", "v": "90", "u": "mm"},
                {"k": "Finish", "v": "Matte black", "u": ""},
            ],
        },
        "ja": {
            "title": "モーター慣らし機の外観デザイン:Mini 4WD® 精密テスト機 | MotorLab",
            "description": "MotorLab モーター慣らし機の外観デザイン紹介 — 低反射のマットブラック一体ボディ、左右対称のガードピラー、埋め込みワードマーク、前面クランプ、側面アクティブ冷却。160 × 81 × 90 mm のデスクトップサイズ、実機 Web UI と同じ工学計器のデザイン言語。",
            "keywords": "MotorLab 外観, モーター慣らし機 デザイン, ミニ四駆 モーター テスト機, デスクトップ モーター測定機",
            "breadcrumb": "外観デザイン",
            "h1_for_ld": "MotorLab モーター慣らし機の外観デザイン",
            "eyebrow": "Product Design",
            "hero_title": "すべての<br><span class='sys-accent'>Mini 4WD<span class='sys-reg'>®</span> モーター</span>のために<br>生まれた精密テスト機",
            "hero_p": "低反射のマットブラックボディ、左右対称のガードピラー、埋め込みワードマーク —— MotorLab の外観は Web UI の工学計器の言語を受け継ぎ、「卓上ラボ」の精密さを一つひとつの折り線に込めています。",
            "chips": ["サイズ <b>160 × 81 × 90 mm</b>", "仕上げ <b>マットブラック</b>"],
            "dl_eyebrow": "Design Language",
            "dl_h2": "家電ではなく、卓上の計測器",
            "dl_p": "ボディは低反射のマットブラックの塊。左右対称で厚みのあるガードピラーがコアモジュールを包み、運搬時は取っ手に、稼働時は構造保護になります。露出する要素(クランプ、センサー座、冷却口、ステータスランプ)はすべて端正な折り線の中に収められ、装飾を排して工学的な質感だけを残しました。",
            "feat_eyebrow": "Exterior Highlights",
            "feat_h2": "すべてのディテールに機能がある",
            "feat_lead": "外観で見えるすべてのデザインが、実際の用途に対応しています —— クランプ、冷却からステータス表示まで。",
            "features": [
                {"dot": "", "t": "マットブラック一体ボディ", "d": "面取りされた折り線を備えた厚みのある塊。低反射の表面が卓上の雑光を抑え、前面に埋め込まれた「MotorLab」ワードマークがブランドを造形と一体化させます。"},
                {"dot": "", "t": "左右対称のガードピラー", "d": "2 本のピラーは取っ手と保護を兼ね、運搬時は握りやすく、稼働時はコアモジュールを守り、全体を力学的にバランスさせます。"},
                {"dot": "sys-dot-red", "t": "前面モータークランプ", "d": "前面のアノダイズドクランプとセンサー座。モーターを置くだけで即座に位置決めされ、視覚的な焦点であり、測定精度の起点でもあります。"},
                {"dot": "sys-dot-cyan", "t": "側面アクティブ冷却", "d": "側面に内蔵された冷却ファンと導風口が、長時間の慣らしでも安定した動作温度を保ちます。風路はシルエットの内側に収められています。"},
                {"dot": "sys-dot-blue", "t": "カスタム多色インジケーター", "d": "電源と稼働状態を一目で識別。ミニマルな単一光源が、計器グレードの抑制を表現します。"},
                {"dot": "", "t": "コンパクトな卓上サイズ", "d": "160 × 81 × 90 mm のコンパクトな体積で片手で移動でき、どんな作業机や整備台にも収まります。"},
            ],
            "gal_eyebrow": "Gallery",
            "gal_h2": "360°、すべての面を見る",
            "gallery_caps": [
                {"b": "正面", "tag": "FRONT", "d": "対称のピラーが中央のクランプモジュールを包み、ワードマークとステータスランプが一列に並びます。"},
                {"b": "装着", "tag": "MOUNTED", "d": "クランプにモーターを置き、センサー座を固定した実使用状態。"},
                {"b": "冷却面", "tag": "SIDE", "d": "側面の冷却ファンとざぐり穴の固定点 — 工学構造が一目で分かります。"},
                {"b": "上面", "tag": "TOP", "d": "センサー座とクランプ軸が上下で揃った、整然としたレイアウト。"},
                {"b": "透視", "tag": "X-RAY", "d": "半透視で見た内部レイアウト。"},
            ],
            "dim_eyebrow": "Dimensions",
            "dim_h2": "三面図と寸法",
            "dim_lead": "完全な三面図と立体図、寸法はすべてミリメートル(mm)表記。",
            "dim_rows": [
                {"k": "長さ Length", "v": "160", "u": "mm"},
                {"k": "幅 Width", "v": "81", "u": "mm"},
                {"k": "高さ Height", "v": "90", "u": "mm"},
                {"k": "仕上げ Finish", "v": "マットブラック", "u": ""},
            ],
        },
    },
}


# /lab/ 馬達型號篩選下拉清單(對齊磨合機韌體預設型號;"Other" 收尾)
# 三語共用(型號為英文專名,不在地化)。新增韌體型號時同步更新此處。
LAB_MOTOR_MODELS = [
    "Torque-Tuned 2 PRO", "Light-Dash PRO", "Atomic-Tuned 2 PRO", "Hyper-Dash PRO",
    "Rev-Tuned 2 PRO", "Mach-Dash PRO",
    "Torque-Tuned 2", "Light-Dash", "Sprint-Dash", "Atomic-Tuned 2", "Hyper-Dash 3",
    "Ultra-Dash", "Rev-Tuned 2", "Power-Dash", "Plasma-Dash", "Other",
]

# ============================================================
# LAB:全球磨合資料上傳/下載平台(/lab/,互動式 app 頁)
#   build_lab_page() 產生靜態殼 + 內嵌 app JS;後端是 Google Apps Script
#   (見 docs repo 的 LAB_UPLOAD_PLAN.md / gas/Code.gs)。
#   內容皆在此 config(不在母版),CSS 用母版 <style> 的 .lab-* 類別,
#   沿用 .guide-page 的 guide-nav / breadcrumb / footer(含 D10 商標聲明)。
#   "api_url":部署 GAS Web App 後把 /exec URL 填進來,再跑 build.py。
#   守 D6(不洩漏硬體型號)、D10(Mini 4WD®)、D13(不強調地域)。
# ============================================================
LAB = {
    "api_url": "https://script.google.com/macros/s/AKfycbwhKscBnh5EdzIjQP90wwWbm-AqWyeWm9pTE071mHpxHLOCEyoCOMudW89p3WTax-qi/exec",
    "i18n": {
        "zh": {
            "title": "全球馬達磨合資料庫:上傳/下載紀錄 | MotorLab",
            "description": "上傳你的 Mini 4WD® 馬達磨合機實測紀錄或下載全球玩家分享、經簽章驗證的磨合資料。下載原檔可直接匯入馬達磨合機重現。",
            "keywords": "馬達磨合資料, 馬達磨合紀錄分享, Mini 4WD 磨合數據, 馬達磨合設定下載, 磨合配方分享",
            "breadcrumb": "資料庫",
            "h1_for_ld": "全球馬達磨合資料庫",
            "eyebrow": "Data Lab · 全球馬達磨合資料庫",
            "hero_title": "上傳・下載<br><span class='lab-accent'>全球 Mini 4WD<span class='lab-reg'>®</span> 馬達磨合資料</span>",
            "hero_p": "把馬達磨合機產出的磨合配方紀錄分享給全世界或下載別人的配方,下載原檔可直接匯入你的馬達磨合機重現。",
            "up_eyebrow": "App · 上傳・下載",
            "up_h2": "分享與套用磨合配方",
            "app_cta": "請由 MotorLab Web UI 內進行上傳分享與下載套用。本頁僅供瀏覽全球玩家公開分享的磨合配方。",
            "tos": "公開分享的紀錄中,署名/國家欄位在你的馬達磨合機系統設定中設置,系統預設為匿名。如需移除已上傳的紀錄,請來信 motorlab.tw@gmail.com。",
            "ls_eyebrow": "Browse · 瀏覽",
            "ls_h2": "全球玩家的磨合紀錄",
            "ls_note": "馬達磨合資料庫中所有的配方檔由全球 MotorLab 使用者提供,使用者自行評估下載使用。",
            "f_motor": "馬達型號篩選",
            "f_country": "國家篩選",
            "f_comp_all": "全部",
            "f_comp_yes": "僅完整磨合",
            "f_comp_no": "僅中斷紀錄",
            "f_sort": "排序",
            "f_show": "顯示",
            "c_rpm": "最高轉速 R.P.M",
            "c_rpm_avg": "平均轉速 R.P.M",
            "c_current": "穩定電流 mA",
            "f_refresh": "重新整理",
            "ls_loading": "載入中…",
            "js": {
                "no_api": "資料服務尚未設定(管理員請填入 GAS 網址)。",
                "uploading": "上傳並驗證中…",
                "up_ok": "上傳成功,已收錄!",
                "up_dup": "這筆紀錄已經在資料庫裡了。",
                "up_err": "上傳失敗",
                "err_network": "網路錯誤,請稍後再試。",
                "empty": "目前沒有符合條件的紀錄。",
                "loading": "載入中…",
                "preparing": "準備下載原檔…",
                "c_motor": "馬達型號",
                "c_owner": "分享者",
                "c_country": "國家",
                "c_rpm": "最高轉速 R.P.M",
                "c_rpm_avg": "平均轉速 R.P.M",
                "c_current": "穩定電流 mA",
                "c_date": "磨合日期",
                "anon": "匿名",
                "incomplete": "中斷",
                "download": "下載原檔",
                "count": "共 {shown} / {total} 筆",
                "prev": "上一頁",
                "next": "下一頁"
            }
        },
        "en": {
            "title": "Global Motor Break-in Data Library | MotorLab",
            "description": "Upload your Mini 4WD® motor break-in records or download signature-verified data shared by racers worldwide — re-import the original file into your machine.",
            "keywords": "motor break-in data, Mini 4WD break-in records, motor tuning data sharing, break-in profile download, Mini 4WD telemetry",
            "breadcrumb": "Data Library",
            "h1_for_ld": "Global Motor Break-in Data Library",
            "eyebrow": "Data Lab",
            "hero_title": "Upload &amp; download<br><span class='lab-accent'>Mini 4WD<span class='lab-reg'>®</span> break-in data, worldwide</span>",
            "hero_p": "Share the break-in profiles your motor break-in machine produces with the world, or download someone else's profile — the original file re-imports straight into your machine.",
            "up_eyebrow": "App · Upload &amp; Download",
            "up_h2": "Share &amp; apply break-in profiles",
            "app_cta": "Upload, share, download and apply profiles from within the MotorLab Web UI. This page is for browsing the break-in profiles players share worldwide.",
            "tos": "For publicly shared records, the name/country fields are set in your motor break-in machine's system settings and default to anonymous. To remove an uploaded record, email motorlab.tw@gmail.com.",
            "ls_eyebrow": "Browse",
            "ls_h2": "Break-in records from racers worldwide",
            "ls_note": "All profiles in this library are submitted by MotorLab users worldwide. Download and use them at your own discretion.",
            "f_motor": "Filter by motor",
            "f_country": "Filter by country",
            "f_comp_all": "All",
            "f_comp_yes": "Completed only",
            "f_comp_no": "Interrupted only",
            "f_sort": "Sort",
            "f_show": "Show",
            "c_rpm": "Max R.P.M",
            "c_rpm_avg": "Avg R.P.M",
            "c_current": "Stable mA",
            "f_refresh": "Refresh",
            "ls_loading": "Loading…",
            "js": {
                "no_api": "Data service not configured yet (admin: set the GAS URL).",
                "uploading": "Uploading and verifying…",
                "up_ok": "Uploaded and added!",
                "up_dup": "This record is already in the library.",
                "up_err": "Upload failed",
                "err_network": "Network error, please try again.",
                "empty": "No records match your filters.",
                "loading": "Loading…",
                "preparing": "Preparing the original file…",
                "c_motor": "Motor",
                "c_owner": "Shared by",
                "c_country": "Country",
                "c_rpm": "Max R.P.M",
                "c_rpm_avg": "Avg R.P.M",
                "c_current": "Stable mA",
                "c_date": "Break-in date",
                "anon": "Anonymous",
                "incomplete": "Interrupted",
                "download": "Download",
                "count": "{shown} / {total} records",
                "prev": "Prev",
                "next": "Next"
            }
        },
        "ja": {
            "title": "グローバル モーター慣らしデータ庫 | MotorLab",
            "description": "Mini 4WD® モーター慣らし機の実測記録をアップロード、または世界中のレーサーが共有した署名検証済みデータをダウンロード。元ファイルをマシンに再インポートできます。",
            "keywords": "モーター慣らし データ, ミニ四駆 慣らし 記録 共有, モーター 調整 データ, 慣らし 設定 ダウンロード, ミニ四駆 テレメトリ",
            "breadcrumb": "データ庫",
            "h1_for_ld": "グローバル モーター慣らしデータ庫",
            "eyebrow": "Data Lab · データ庫",
            "hero_title": "アップロード・ダウンロード<br><span class='lab-accent'>世界の Mini 4WD<span class='lab-reg'>®</span> 慣らしデータ</span>",
            "hero_p": "モーター慣らし機が生成した慣らしレシピ記録を世界に共有、あるいは誰かのレシピをダウンロード —— 元ファイルはそのままモーター慣らし機に再インポートできます。",
            "up_eyebrow": "App · アップロード・ダウンロード",
            "up_h2": "慣らしレシピの共有と適用",
            "app_cta": "アップロード・共有・ダウンロード・適用は MotorLab Web UI 内で行ってください。本ページは世界中のプレイヤーが公開した慣らしレシピの閲覧専用です。",
            "tos": "公開共有される記録の名前/国の欄はモーター慣らし機のシステム設定で設定され、初期値は匿名です。記録の削除は motorlab.tw@gmail.com までご連絡ください。",
            "ls_eyebrow": "Browse · 一覧",
            "ls_h2": "世界のレーサーの慣らし記録",
            "ls_note": "このデータ庫のすべてのレシピは世界中の MotorLab ユーザーから提供されています。ダウンロード・利用は各自の判断でお願いします。",
            "f_motor": "モーターで絞り込み",
            "f_country": "国で絞り込み",
            "f_comp_all": "すべて",
            "f_comp_yes": "完走のみ",
            "f_comp_no": "中断のみ",
            "f_sort": "並べ替え",
            "f_show": "表示",
            "c_rpm": "最高回転数 R.P.M",
            "c_rpm_avg": "平均回転数 R.P.M",
            "c_current": "安定電流 mA",
            "f_refresh": "更新",
            "ls_loading": "読み込み中…",
            "js": {
                "no_api": "データサービス未設定(管理者:GAS URL を設定してください)。",
                "uploading": "アップロードして検証中…",
                "up_ok": "アップロード完了、収録しました!",
                "up_dup": "この記録はすでにデータ庫にあります。",
                "up_err": "アップロード失敗",
                "err_network": "ネットワークエラー、後でお試しください。",
                "empty": "条件に合う記録がありません。",
                "loading": "読み込み中…",
                "preparing": "元ファイルを準備中…",
                "c_motor": "モーター",
                "c_owner": "共有者",
                "c_country": "国",
                "c_rpm": "最高回転数 R.P.M",
                "c_rpm_avg": "平均回転数 R.P.M",
                "c_current": "安定電流 mA",
                "c_date": "慣らし日",
                "anon": "匿名",
                "incomplete": "中断",
                "download": "ダウンロード",
                "count": "{shown} / {total} 件",
                "prev": "前へ",
                "next": "次へ"
            }
        }
    }
}


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

    # --- 7c. 內部跨頁連結(nav 的 data-syslink)改寫成對應語言的 URL ---
    # 母版寫 zh 絕對路徑;en/ja 首頁要連到 /en/.. 、/ja/.. 的同頁
    sys_prefix = "" if lang == "zh" else f"/{lang}"
    sys_href = f"{sys_prefix}/{SYSTEM.get('type', 'system')}/{SYSTEM['slug']}/"
    for a in soup.select("a[data-syslink]"):
        a["href"] = sys_href
        del a["data-syslink"]

    # --- 7d. 內部跨頁連結(nav 的 data-lablink)改寫成對應語言的 URL ---
    # /lab/ 全球磨合資料平台(LAB_UPLOAD_PLAN);頂層 /lab/,各語言加前綴
    lab_prefix = "" if lang == "zh" else f"/{lang}"
    lab_href = f"{lab_prefix}/lab/"
    for a in soup.select("a[data-lablink]"):
        a["href"] = lab_href
        del a["data-lablink"]

    # --- 7e. 內部跨頁連結(nav 的 data-manuallink)改寫成對應語言的 URL ---
    # /docs/user-manual/ 使用者手冊(D23 docs 分類);各語言加前綴
    manual_href = f"{lab_prefix}/docs/{MANUAL['slug']}/"
    for a in soup.select("a[data-manuallink]"):
        a["href"] = manual_href
        del a["data-manuallink"]

    # --- 7f. 內部跨頁連結(footer 的 data-verifylink)改寫成對應語言的 /verify/ ---
    verify_href = f"{lab_prefix}/verify/"
    for a in soup.select("a[data-verifylink]"):
        a["href"] = verify_href
        del a["data-verifylink"]

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
# 首頁 #guides 區段 → 3 個大 hub 入口卡片(A 案,D27)
# 不在首頁列文章 cards;使用者點 hub 卡進入對應的 hub 頁(/guides/, /benchmarks/, /methodology/)
# ============================================================
def _transform_guides_to_cards(soup, lang):
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    ui = UI_STRINGS[lang]

    # 找 guides-grid(原本含 9 個 article),整塊換成 hub-cards 容器
    grid = soup.find("div", class_="guides-grid")
    if grid is None:
        return
    parent = grid.parent
    grid_index = list(parent.contents).index(grid)
    grid.extract()  # 砍掉原本 9 個 article guide-article(連同容器)

    hub_cards = soup.new_tag("div", attrs={"class": "hub-cards"})
    for h in HUBS:
        hub_slug = h["slug"]
        if lang not in h["i18n"]:
            continue
        h_i18n = h["i18n"][lang]
        card = soup.new_tag("a", attrs={
            "class": "hub-card",
            "href": f"{lang_prefix}/{hub_slug}/",
        })
        # tag(slug 大寫,brand-neutral,跨語言通用)
        tag = soup.new_tag("span", attrs={"class": "hub-card-tag"})
        tag.string = hub_slug.upper()
        card.append(tag)
        # 標題(用 bc_section label,例如「教學」)
        title = soup.new_tag("h3", attrs={"class": "hub-card-title"})
        title.string = ui["bc_section"].get(hub_slug, h_i18n["h1"])
        card.append(title)
        # 描述(用 hub.i18n.lead)
        desc = soup.new_tag("p", attrs={"class": "hub-card-desc"})
        desc_frag = BeautifulSoup(h_i18n["lead"], "html.parser")
        for child in list(desc_frag.children):
            desc.append(child)
        card.append(desc)
        # 文章數(例如「3 篇文章 →」)
        meta = soup.new_tag("div", attrs={"class": "hub-card-meta"})
        n = len(h["include"])
        meta.string = ui["hub_count"].format(n=n)
        card.append(meta)
        hub_cards.append(card)

    parent.insert(grid_index, hub_cards)


# ============================================================
def _fix_footer_verify(footer_el, lang):
    """獨立頁沿用母版 footer(原樣搬入,不經 build_lang)。這裡把 footer 內
    的 data-verifylink 連結改寫成對應語言的 /verify/,並清掉屬性,避免屬性外洩
    與 en/ja 頁連到中文 /verify/。footer 其餘文字沿用母版既有行為(不動)。"""
    if footer_el is None:
        return
    prefix = "" if lang == "zh" else f"/{lang}"
    for a in footer_el.select("a[data-verifylink]"):
        a["href"] = f"{prefix}/verify/"
        del a["data-verifylink"]


# 獨立教學分頁產生器:/guides/<slug>/index.html
# 完全沿用首頁的 <head> + <style>(視覺一致),body 換成 guide layout
# ============================================================
def build_guide_page(slug, lang, src_html, i18n, guide_cfg):
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    g_i18n = guide_cfg["i18n"][lang]
    ui = UI_STRINGS[lang]
    article_type = guide_cfg.get("type", "guides")
    section_label = ui["bc_section"].get(article_type, ui["bc_guides"])
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    page_url = f"{SITE}{lang_prefix}/{article_type}/{slug}/"
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

    # 3b. 獨立頁面把文章標題從 <h3> 升級成 <h1>(SEO:每頁應有單一 H1)
    # 母版維持 <h3> 因為它在首頁 card grid 是次級標題;build_guide_page 在
    # 抽出來變成獨立頁時必須是 <h1>(Bing/Google 都把缺 H1 列為警告)
    title_h3 = target_article.find("h3")
    if title_h3 is not None:
        title_h3.name = "h1"

    # 3b-2. 章節小標 <h4> → <h2>(SEO:獨立頁標題層級應為 h1→h2,不可從 h1 直接跳到 h4)
    #       母版文章內 <h4> 沿用首頁 card 視覺;抽成獨立頁後,各章節即 H1 之下的主段落 → 應為 H2。
    #       文章內 h4 皆為同級章節(無巢狀,見 HANDOFF 結構),故一律升 h2。
    #       CSS .guide-article h2 已對齊原 h4 樣式(index.src.html),視覺零變動。
    for sec_h4 in target_article.find_all("h4"):
        sec_h4.name = "h2"

    # 3c. 在 H1 後插入作者署名(MotorLab Team,三語對應 byline 文字)
    #     僅獨立頁顯示,首頁 card 不顯示(card 結構只保留 tag/h3/lead)
    if title_h3 is not None:
        byline = soup.new_tag("p", attrs={"class": "guide-byline"})
        byline.string = ui["byline"]
        title_h3.insert_after(byline)
        # 發表 / 最後更新 日期(更新僅在有異動使用者可見內容時顯示,≠ 發表日才呈現)
        pub = guide_cfg.get("published")
        upd = guide_cfg.get("updated")
        if pub:
            date_p = soup.new_tag("p", attrs={"class": "guide-dates"})
            date_txt = f'{ui["date_pub"]} {pub}'
            if upd and upd != pub:
                date_txt += f'　·　{ui["date_upd"]} {upd}'
            date_p.string = date_txt
            byline.insert_after(date_p)

    # 4. 保留 footer
    footer_el = soup.find("footer")
    footer_extracted = footer_el.extract() if footer_el else None
    _fix_footer_verify(footer_extracted, lang)

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

    # 7. hreflang 三向互指 + x-default(三語版 URL 用文章 type)
    head = soup.head
    for hl_lang, hl_cfg in LANGS.items():
        hl_attr = hl_cfg["html_lang"]
        hl_prefix = "" if hl_lang == "zh" else f"/{hl_lang}"
        hl_url = f"{SITE}{hl_prefix}/{article_type}/{slug}/"
        link = soup.new_tag("link", attrs={"rel": "alternate", "hreflang": hl_attr, "href": hl_url})
        head.append(link)
    # x-default 指 zh
    link = soup.new_tag("link", attrs={
        "rel": "alternate", "hreflang": "x-default",
        "href": f"{SITE}/{article_type}/{slug}/",
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
        "datePublished": guide_cfg.get("published"),
        "dateModified": guide_cfg.get("updated") or guide_cfg.get("published"),
        "author": {"@type": "Organization", "name": "MotorLab Team", "url": SITE + "/"},
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
            {"@type": "ListItem", "position": 2, "name": section_label, "item": f"{home_url}#guides"},
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
        f'<a href="{home_url}#guides">{section_label}</a><span class="sep">/</span>'
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
        g_type = g.get("type", "guides")
        return (
            f'<div class="{css_class}">'
            f'<a href="{lang_prefix}/{g_type}/{g["slug"]}/">'
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
# Hub 頁面產生器:/{lang_prefix}/{hub_slug}/index.html
#   列出該 hub include 的所有 article 卡片(連結到文章實體 URL)
#   完全沿用 .guide-page CSS,layout 與 guide-page 一致
# ============================================================
def _card_for_guide_on_hub(soup, src_html, i18n, guide_cfg, lang):
    """產生 hub 頁面上某篇 guide 的 card(同 _transform_guides_to_cards 的單張)"""
    cfg = LANGS[lang]
    lang_dict = i18n.get(lang, {})
    zh_dict = i18n["zh"]
    g_key = guide_cfg["key"]
    g_i18n = guide_cfg["i18n"].get(lang, guide_cfg["i18n"]["zh"])
    article_type = guide_cfg.get("type", "guides")
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    href = f"{lang_prefix}/{article_type}/{guide_cfg['slug']}/"

    # 從來源裡找該 guide 的 article block,抽出 tag/h3/lead 三段
    fresh = BeautifulSoup(src_html, "lxml")
    for el in fresh.select("[data-i18n]"):
        key = el.get("data-i18n")
        if not key.startswith(g_key + "."):
            continue
        text = lang_dict.get(key) or zh_dict.get(key)
        if text is not None:
            frag = BeautifulSoup(text, "html.parser")
            el.clear()
            for child in list(frag.children):
                el.append(child)

    target = None
    for art in fresh.select("article.guide-article"):
        t = art.select_one(".guide-tag")
        if t and t.get("data-i18n", "").startswith(g_key + "."):
            target = art
            break
    if target is None:
        return None

    # 新組裝 card(tag + h3 + lead + read-more link)— 都用 soup 的 builder
    new_card = soup.new_tag("article", attrs={"class": "guide-article"})
    for sel in (".guide-tag", "h3", ".guide-lead"):
        node = target.select_one(sel)
        if node is not None:
            new_card.append(BeautifulSoup(str(node), "html.parser"))
    link = soup.new_tag("a", attrs={"class": "guide-card-link", "href": href})
    link.string = UI_STRINGS[lang]["read_more"]
    new_card.append(link)
    return new_card


def build_hub_page(hub_cfg, lang, src_html, i18n):
    """產生 hub 索引頁(/{lang_prefix}/{hub_slug}/index.html)"""
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    ui = UI_STRINGS[lang]
    slug = hub_cfg["slug"]
    h_i18n = hub_cfg["i18n"][lang]
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    page_url = f"{SITE}{lang_prefix}/{slug}/"
    home_url = f"{SITE}{lang_prefix}/"
    section_label = ui["bc_section"].get(slug, slug)
    kb_label = ui["bc_section"]["knowledge_base"]

    # 1. <html lang>
    soup.html["lang"] = cfg["html_lang"]

    # 2. 砍現有 JSON-LD 與 hreflang
    for s in soup.find_all("script", {"type": "application/ld+json"}):
        s.decompose()
    for tag in soup.find_all("link", {"rel": "alternate"}):
        tag.decompose()

    # 3. 留 footer,清掉 body 其他
    footer_el = soup.find("footer")
    footer_extracted = footer_el.extract() if footer_el else None
    _fix_footer_verify(footer_extracted, lang)

    # 4. <title> / meta / canonical
    if soup.title:
        soup.title.string = h_i18n["title"]

    def set_meta(attr, attr_val, content):
        tag = soup.find("meta", {attr: attr_val})
        if tag:
            tag["content"] = content

    set_meta("name", "description", h_i18n["description"])
    # zh/ja 頁附加 en keywords(品牌通用)
    kw = h_i18n["keywords"]
    if lang != "en" and "en" in hub_cfg["i18n"]:
        kw = kw + ", " + hub_cfg["i18n"]["en"]["keywords"]
    set_meta("name", "keywords", kw)
    set_meta("http-equiv", "Content-Language", cfg["html_lang"])
    set_meta("property", "og:type", "website")
    set_meta("property", "og:url", page_url)
    set_meta("property", "og:title", h_i18n["title"])
    set_meta("property", "og:description", h_i18n["description"])
    set_meta("property", "og:locale", cfg["og_locale"])
    set_meta("name", "twitter:title", h_i18n["title"])
    set_meta("name", "twitter:description", h_i18n["description"])

    canon = soup.find("link", {"rel": "canonical"})
    if canon:
        canon["href"] = page_url

    # 5. hreflang 三向 + x-default
    head = soup.head
    for hl_lang, hl_cfg in LANGS.items():
        hl_prefix = "" if hl_lang == "zh" else f"/{hl_lang}"
        hl_url = f"{SITE}{hl_prefix}/{slug}/"
        head.append(soup.new_tag("link", attrs={
            "rel": "alternate", "hreflang": hl_cfg["html_lang"], "href": hl_url
        }))
    head.append(soup.new_tag("link", attrs={
        "rel": "alternate", "hreflang": "x-default", "href": f"{SITE}/{slug}/"
    }))

    # 6. JSON-LD: CollectionPage + BreadcrumbList + ItemList
    items_for_ld = []
    for g_key in hub_cfg["include"]:
        g_cfg = next((g for g in GUIDES if g["key"] == g_key), None)
        if g_cfg is None:
            continue
        g_lang = g_cfg["i18n"].get(lang, g_cfg["i18n"]["zh"])
        g_type = g_cfg.get("type", "guides")
        g_url = f"{SITE}{lang_prefix}/{g_type}/{g_cfg['slug']}/"
        items_for_ld.append({
            "@type": "ListItem",
            "position": len(items_for_ld) + 1,
            "url": g_url,
            "name": g_lang.get("h1_for_ld", g_lang["title"]),
        })

    collection_ld = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": h_i18n["title"],
        "description": h_i18n["description"],
        "inLanguage": cfg["html_lang"],
        "url": page_url,
        "isPartOf": {"@type": "WebSite", "name": "MotorLab.tw", "url": SITE + "/"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(items_for_ld),
            "itemListElement": items_for_ld,
        },
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui["bc_home"], "item": home_url},
            {"@type": "ListItem", "position": 2, "name": kb_label, "item": f"{home_url}#guides"},
            {"@type": "ListItem", "position": 3, "name": section_label, "item": page_url},
        ],
    }
    for data in (collection_ld, breadcrumb_ld):
        s = soup.new_tag("script", attrs={"type": "application/ld+json"})
        s.string = json.dumps(data, ensure_ascii=False, indent=2)
        head.append(s)

    # 7. <body>:nav + breadcrumb + h1 + lead + cards grid + footer
    soup.body.clear()
    soup.body["class"] = "guide-page"

    nav_html = (
        f'<nav class="guide-nav"><div class="container">'
        f'<a class="brand" href="{home_url}"><span>MotorLab<span class="tag">.tw</span></span></a>'
        f'<a class="back-link" href="{home_url}">{ui["back_home"]}</a>'
        f'</div></nav>'
    )
    soup.body.append(BeautifulSoup(nav_html, "html.parser"))

    main_el = soup.new_tag("main")
    container = soup.new_tag("div", attrs={"class": "container"})

    bc_html = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb">'
        f'<a href="{home_url}">{ui["bc_home"]}</a><span class="sep">/</span>'
        f'<a href="{home_url}#guides">{kb_label}</a><span class="sep">/</span>'
        f'<span class="current">{section_label}</span>'
        f'</nav>'
    )
    container.append(BeautifulSoup(bc_html, "html.parser"))

    # Hub header(h1 + lead)
    header = soup.new_tag("div", attrs={"class": "hub-header"})
    h1 = soup.new_tag("h1")
    h1.string = h_i18n["h1"]
    header.append(h1)
    lead = soup.new_tag("p", attrs={"class": "hub-lead"})
    lead_frag = BeautifulSoup(h_i18n["lead"], "html.parser")
    for child in list(lead_frag.children):
        lead.append(child)
    header.append(lead)
    container.append(header)

    # 卡片網格
    grid = soup.new_tag("div", attrs={"class": "guides-grid"})
    for g_key in hub_cfg["include"]:
        g_cfg = next((g for g in GUIDES if g["key"] == g_key), None)
        if g_cfg is None:
            continue
        card = _card_for_guide_on_hub(soup, src_html, i18n, g_cfg, lang)
        if card is not None:
            grid.append(card)
    container.append(grid)

    main_el.append(container)
    soup.body.append(main_el)

    if footer_extracted is not None:
        soup.body.append(footer_extracted)

    return str(soup)


# ============================================================
# 商品外觀頁產生器:/{lang_prefix}/system/<slug>/index.html
#   圖文展示頁(hero + 設計語言 + 特色 + gallery + 尺寸),內容全部來自 SYSTEM config。
#   沿用母版 <head>/<style> 與 .guide-page 的 guide-nav / breadcrumb / footer。
# ============================================================
def build_system_page(sys_cfg, lang, src_html, i18n):
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    ui = UI_STRINGS[lang]
    slug = sys_cfg["slug"]
    page_type = sys_cfg.get("type", "system")
    s = sys_cfg["i18n"][lang]
    imgs = sys_cfg["images"]
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    page_url = f"{SITE}{lang_prefix}/{page_type}/{slug}/"
    home_url = f"{SITE}{lang_prefix}/"

    # 1. <html lang>
    soup.html["lang"] = cfg["html_lang"]

    # 2. 砍現有 JSON-LD 與 hreflang(加本頁專用的)
    for sc in soup.find_all("script", {"type": "application/ld+json"}):
        sc.decompose()
    for tag in soup.find_all("link", {"rel": "alternate"}):
        tag.decompose()

    # 3. 留 footer(含 D10 商標聲明),清掉 body 其他
    footer_el = soup.find("footer")
    footer_extracted = footer_el.extract() if footer_el else None
    _fix_footer_verify(footer_extracted, lang)

    # 4. <title> / meta / canonical
    if soup.title:
        soup.title.string = s["title"]

    def set_meta(attr, attr_val, content):
        tag = soup.find("meta", {attr: attr_val})
        if tag:
            tag["content"] = content

    set_meta("name", "description", s["description"])
    kw = s["keywords"]
    if lang != "en" and "en" in sys_cfg["i18n"]:
        kw = kw + ", " + sys_cfg["i18n"]["en"]["keywords"]
    set_meta("name", "keywords", kw)
    set_meta("http-equiv", "Content-Language", cfg["html_lang"])
    set_meta("property", "og:type", "website")
    set_meta("property", "og:url", page_url)
    set_meta("property", "og:title", s["title"])
    set_meta("property", "og:description", s["description"])
    set_meta("property", "og:locale", cfg["og_locale"])
    set_meta("name", "twitter:title", s["title"])
    set_meta("name", "twitter:description", s["description"])

    canon = soup.find("link", {"rel": "canonical"})
    if canon:
        canon["href"] = page_url

    # 5. hreflang 三向 + x-default
    head = soup.head
    for hl_lang, hl_cfg in LANGS.items():
        hl_prefix = "" if hl_lang == "zh" else f"/{hl_lang}"
        hl_url = f"{SITE}{hl_prefix}/{page_type}/{slug}/"
        head.append(soup.new_tag("link", attrs={
            "rel": "alternate", "hreflang": hl_cfg["html_lang"], "href": hl_url
        }))
    head.append(soup.new_tag("link", attrs={
        "rel": "alternate", "hreflang": "x-default", "href": f"{SITE}/{page_type}/{slug}/"
    }))

    # 6. JSON-LD: WebPage(primaryImageOfPage)+ BreadcrumbList
    webpage_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": s["h1_for_ld"],
        "description": s["description"],
        "inLanguage": cfg["html_lang"],
        "url": page_url,
        "isPartOf": {"@type": "WebSite", "name": "MotorLab.tw", "url": SITE + "/"},
        "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + imgs["hero"]},
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui["bc_home"], "item": home_url},
            {"@type": "ListItem", "position": 2, "name": s["breadcrumb"], "item": page_url},
        ],
    }
    for data in (webpage_ld, breadcrumb_ld):
        sc = soup.new_tag("script", attrs={"type": "application/ld+json"})
        sc.string = json.dumps(data, ensure_ascii=False, indent=2)
        head.append(sc)

    # 7. <body>:nav + hero + 設計語言 + 特色 + gallery + 尺寸 + footer
    soup.body.clear()
    soup.body["class"] = "guide-page"

    nav_html = (
        f'<nav class="guide-nav"><div class="container">'
        f'<a class="brand" href="{home_url}"><span>MotorLab<span class="tag">.tw</span></span></a>'
        f'<a class="back-link" href="{home_url}">{ui["back_home"]}</a>'
        f'</div></nav>'
    )
    soup.body.append(BeautifulSoup(nav_html, "html.parser"))

    main_el = soup.new_tag("main")

    # 7a. Hero(breadcrumb + h1 + p + chips + 立體圖)
    bc_html = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb">'
        f'<a href="{home_url}">{ui["bc_home"]}</a><span class="sep">/</span>'
        f'<span class="current">{s["breadcrumb"]}</span>'
        f'</nav>'
    )
    chips_html = "".join(f'<span class="sys-chip">{c}</span>' for c in s["chips"])
    hero_html = (
        f'<section class="sys-hero"><div class="container">{bc_html}'
        f'<div class="sys-hero-grid"><div>'
        f'<div class="sys-eyebrow">{s["eyebrow"]}</div>'
        f'<h1 class="sys-hero-title">{s["hero_title"]}</h1>'
        f'<p class="sys-hero-p">{s["hero_p"]}</p>'
        f'<div class="sys-chips">'
        f'<span class="sys-chip m1">M1</span><span class="sys-chip pro">PRO</span>{chips_html}'
        f'</div></div>'
        f'<div class="sys-panel"><img src="{imgs["hero"]}" alt="{s["h1_for_ld"]}"></div>'
        f'</div></div></section>'
    )
    main_el.append(BeautifulSoup(hero_html, "html.parser"))

    # 7b. 設計語言
    dl_html = (
        f'<section class="sys-section"><div class="container">'
        f'<div class="sys-eyebrow">{s["dl_eyebrow"]}</div>'
        f'<h2 class="sys-h2">{s["dl_h2"]}</h2>'
        f'<p class="sys-lead">{s["dl_p"]}</p>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(dl_html, "html.parser"))

    # 7c. 外觀特色
    fcards = ""
    for i, f in enumerate(s["features"], 1):
        dot = f'<span class="sys-dot {f["dot"]}"></span>' if f["dot"] else ""
        fcards += (
            f'<div class="sys-fcard"><div class="sys-num">{i:02d}</div>'
            f'<h3>{dot}{f["t"]}</h3><p>{f["d"]}</p></div>'
        )
    feat_html = (
        f'<section class="sys-section sys-band"><div class="container">'
        f'<div class="sys-eyebrow">{s["feat_eyebrow"]}</div>'
        f'<h2 class="sys-h2">{s["feat_h2"]}</h2>'
        f'<p class="sys-lead">{s["feat_lead"]}</p>'
        f'<div class="sys-feature-grid">{fcards}</div>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(feat_html, "html.parser"))

    # 7d. 多角度 gallery
    gitems = ""
    for img, cap in zip(imgs["gallery"], s["gallery_caps"]):
        gitems += (
            f'<div class="sys-gitem"><div class="sys-panel"><img src="{img}" alt="{cap["b"]}"></div>'
            f'<div class="sys-cap"><b>{cap["b"]} <span>{cap["tag"]}</span></b>{cap["d"]}</div></div>'
        )
    gal_html = (
        f'<section class="sys-section"><div class="container">'
        f'<div class="sys-eyebrow">{s["gal_eyebrow"]}</div>'
        f'<h2 class="sys-h2">{s["gal_h2"]}</h2>'
        f'<div class="sys-gallery-grid">{gitems}</div>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(gal_html, "html.parser"))

    # 7e. 尺寸與結構
    drows = ""
    for r in s["dim_rows"]:
        unit = f' <small>{r["u"]}</small>' if r["u"] else ""
        drows += (
            f'<div class="sys-dim-row"><span class="k">{r["k"]}</span>'
            f'<span class="v">{r["v"]}{unit}</span></div>'
        )
    dim_html = (
        f'<section class="sys-section sys-band"><div class="container">'
        f'<div class="sys-eyebrow">{s["dim_eyebrow"]}</div>'
        f'<h2 class="sys-h2">{s["dim_h2"]}</h2>'
        f'<p class="sys-lead">{s["dim_lead"]}</p>'
        f'<div class="sys-dim-wrap">'
        f'<div class="sys-panel"><img src="{imgs["dimensions"]}" alt="{s["dim_h2"]}"></div>'
        f'<div class="sys-dim-specs">{drows}</div>'
        f'</div></div></section>'
    )
    main_el.append(BeautifulSoup(dim_html, "html.parser"))

    soup.body.append(main_el)
    if footer_extracted is not None:
        soup.body.append(footer_extracted)

    return str(soup)


# ============================================================
# /lab/ 全球磨合資料平台:內嵌 app JS(__佔位__ 由 build_lab_page 取代)
#   後端 API 是 Google Apps Script(見 docs repo gas/Code.gs)。
#   上傳走 base64 + text/plain(規避 GAS CORS preflight);下載 passthrough。
# ============================================================
LAB_APP_JS = r"""
(function () {
  var API = "__API_URL__";
  var T = __I18N_JSON__;
  function $(id) { return document.getElementById(id); }
  function hasApi() { return API && API.indexOf("PUT_") !== 0; }
  function apiq(qs) { return API + (API.indexOf("?") < 0 ? "?" : "&") + qs; }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function fmtNum(n) {
    if (n === "" || n == null || isNaN(n)) return "—";
    return Number(n).toLocaleString();
  }
  // 可排序欄位 → 取值函式(數值欄轉 Number,日期欄按字串)
  var SORT_GETTERS = {
    rpm_max_overall: function (it) { return Number(it.rpm_max_overall) || 0; },
    rpm_avg_overall: function (it) { return Number(it.rpm_avg_overall) || 0; },
    stable_current_overall: function (it) { return Number(it.stable_current_overall) || 0; }
  };
  var sortKey = "";   // 目前排序欄位(空 = 不排序,維持後端「新到舊」),由下拉選單驅動
  var sortDir = -1;   // 1 升冪 / -1 降冪
  var page = 1;       // 目前頁碼(1-based)
  var lastFiltered = [];  // 最近一次篩選+排序後的完整結果(供翻頁用)

  function render(items) {
    var box = $("lab-results");
    if (!box) return;
    if (!items || !items.length) { box.innerHTML = '<p class="lab-muted">' + esc(T.empty) + "</p>"; return; }
    var h = '<table class="lab-table"><thead><tr>' +
      "<th>" + esc(T.c_motor) + "</th><th>" + esc(T.c_owner) + "</th><th>" + esc(T.c_country) +
      "</th><th>" + esc(T.c_rpm) + "</th><th>" + esc(T.c_rpm_avg) + "</th><th>" + esc(T.c_current) +
      "</th><th>" + esc(T.c_date) + "</th></tr></thead><tbody>";
    items.forEach(function (it) {
      var owner = (it.owner_name && it.owner_name !== "--") ? it.owner_name : T.anon;
      var country = (it.owner_country && it.owner_country !== "--") ? it.owner_country : "—";
      var date = String(it.timestamp_start || "").replace("T", " ").slice(0, 16);
      var comp = (it.completed === true || it.completed === "true");
      var badge = comp ? "" : ' <span class="lab-tag-warn">' + esc(T.incomplete) + "</span>";
      h += "<tr><td><b>" + esc(it.motor_model || "—") + "</b>" + badge +
        '<div class="lab-sub">' + esc(it.user_label || "") + "</div></td>" +
        "<td>" + esc(owner) + "</td><td>" + esc(country) + "</td>" +
        '<td class="lab-mono">' + fmtNum(it.rpm_max_overall) + "</td>" +
        '<td class="lab-mono">' + fmtNum(it.rpm_avg_overall) + "</td>" +
        '<td class="lab-mono">' + fmtNum(it.stable_current_overall) + "</td>" +
        '<td class="lab-mono">' + esc(date) + "</td></tr>";
    });
    box.innerHTML = h + "</tbody></table>";
  }

  var ALL = [];  // 後端抓回的全量紀錄(快取),篩選/排序/分頁在前端即時做(方案 B)

  function applyFilter() {
    page = 1;  // 任何篩選/排序/筆數變更都回到第 1 頁
    var m = (($("lab-f-motor") || {}).value || "").trim().toLowerCase();
    var c = (($("lab-f-country") || {}).value || "").trim().toLowerCase();
    var cp = ($("lab-f-completed") || {}).value || "";
    // 排序下拉:值格式 "key|dir"(dir = 1 升 / -1 降);空 = 不排序
    var sv = ($("lab-f-sort") || {}).value || "";
    if (sv) { var parts = sv.split("|"); sortKey = parts[0]; sortDir = (parts[1] === "1") ? 1 : -1; }
    else { sortKey = ""; }
    var out = ALL.filter(function (it) {
      if (m && String(it.motor_model || "").toLowerCase() !== m) return false;  // 下拉:精確相等
      if (c && String(it.owner_country || "").toLowerCase().indexOf(c) < 0) return false;  // 國家:子字串
      if (cp) {
        var done = (it.completed === true || it.completed === "true");
        if (cp === "true" && !done) return false;
        if (cp === "false" && done) return false;
      }
      return true;
    });
    // 排序(若有選欄位);否則維持後端回傳順序(新到舊)
    if (sortKey && SORT_GETTERS[sortKey]) {
      var get = SORT_GETTERS[sortKey];
      out.sort(function (a, b) { return (get(a) - get(b)) * sortDir; });
    }
    lastFiltered = out;
    renderPage();
  }

  // 依目前 page + 顯示筆數切頁渲染 + 更新計數 + 翻頁列
  function renderPage() {
    var out = lastFiltered;
    var total = out.length;
    var size = parseInt(($("lab-f-pagesize") || {}).value, 10) || 10;
    var pages = Math.max(1, Math.ceil(total / size));
    if (page > pages) page = pages;
    if (page < 1) page = 1;
    var start = (page - 1) * size;
    var shown = out.slice(start, start + size);
    render(shown);
    var cnt = $("lab-count");
    if (cnt) {
      // 顯示「目前頁區間 / 總數」,例:11–20 / 50
      var from = total ? start + 1 : 0;
      var to = start + shown.length;
      cnt.textContent = T.count.replace("{shown}", from + "–" + to).replace("{total}", total);
    }
    renderPager(pages);
  }

  function renderPager(pages) {
    var el = $("lab-pager");
    if (!el) return;
    if (pages <= 1) { el.innerHTML = ""; return; }
    el.innerHTML =
      '<button type="button" class="lab-btn lab-btn-sm" id="lab-prev"' + (page <= 1 ? " disabled" : "") + ">‹ " + esc(T.prev) + "</button>" +
      '<span class="lab-page-ind">' + page + " / " + pages + "</span>" +
      '<button type="button" class="lab-btn lab-btn-sm" id="lab-next"' + (page >= pages ? " disabled" : "") + ">" + esc(T.next) + " ›</button>";
    var pv = $("lab-prev"), nx = $("lab-next");
    if (pv) pv.addEventListener("click", function () { if (page > 1) { page--; renderPage(); scrollTop(); } });
    if (nx) nx.addEventListener("click", function () { page++; renderPage(); scrollTop(); });
  }

  function scrollTop() {
    var b = $("lab-results");
    if (b && b.scrollIntoView) b.scrollIntoView({ block: "start" });
  }

  function loadList() {
    var box = $("lab-results");
    if (!box) return;
    if (!hasApi()) { box.innerHTML = '<p class="lab-muted">' + esc(T.no_api) + "</p>"; return; }
    box.innerHTML = '<p class="lab-muted">' + esc(T.loading) + "</p>";
    fetch(apiq("action=list&limit=200")).then(function (r) { return r.json(); }).then(function (d) {
      if (d.ok) { ALL = d.items || []; applyFilter(); }
      else box.innerHTML = '<p class="lab-muted">' + esc(d.err || T.err_network) + "</p>";
    }).catch(function () { box.innerHTML = '<p class="lab-muted">' + esc(T.err_network) + "</p>"; });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var rf = $("lab-refresh");
    if (rf) rf.addEventListener("click", loadList);
    // 即時篩選/排序/分頁:從快取運算,不再每次打 GAS(瀏覽專用,上傳/下載在 APP 內)
    var fm = $("lab-f-motor"), fc = $("lab-f-country"), fcp = $("lab-f-completed"),
        fps = $("lab-f-pagesize"), fsort = $("lab-f-sort");
    if (fm) fm.addEventListener("change", applyFilter);   // 下拉用 change
    if (fc) fc.addEventListener("input", applyFilter);    // 文字框用 input
    if (fcp) fcp.addEventListener("change", applyFilter);
    if (fps) fps.addEventListener("change", applyFilter); // 顯示筆數
    if (fsort) fsort.addEventListener("change", applyFilter); // 排序下拉
    loadList();
  });
})();
"""


def build_lab_page(lab_cfg, lang, src_html, i18n):
    """產生 /lab/ 全球磨合資料平台頁(互動式 app,沿用 .guide-page 殼)。"""
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    ui = UI_STRINGS[lang]
    s = lab_cfg["i18n"][lang]
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    page_url = f"{SITE}{lang_prefix}/lab/"
    home_url = f"{SITE}{lang_prefix}/"

    # 1. <html lang>
    soup.html["lang"] = cfg["html_lang"]

    # 2. 砍現有 JSON-LD 與 hreflang
    for sc in soup.find_all("script", {"type": "application/ld+json"}):
        sc.decompose()
    for tag in soup.find_all("link", {"rel": "alternate"}):
        tag.decompose()

    # 3. 留 footer(含 D10 商標聲明)
    footer_el = soup.find("footer")
    footer_extracted = footer_el.extract() if footer_el else None
    _fix_footer_verify(footer_extracted, lang)

    # 4. <title> / meta / canonical
    if soup.title:
        soup.title.string = s["title"]

    def set_meta(attr, attr_val, content):
        tag = soup.find("meta", {attr: attr_val})
        if tag:
            tag["content"] = content

    set_meta("name", "description", s["description"])
    kw = s["keywords"]
    if lang != "en" and "en" in lab_cfg["i18n"]:
        kw = kw + ", " + lab_cfg["i18n"]["en"]["keywords"]
    set_meta("name", "keywords", kw)
    set_meta("http-equiv", "Content-Language", cfg["html_lang"])
    set_meta("property", "og:type", "website")
    set_meta("property", "og:url", page_url)
    set_meta("property", "og:title", s["title"])
    set_meta("property", "og:description", s["description"])
    set_meta("property", "og:locale", cfg["og_locale"])
    set_meta("name", "twitter:title", s["title"])
    set_meta("name", "twitter:description", s["description"])

    canon = soup.find("link", {"rel": "canonical"})
    if canon:
        canon["href"] = page_url

    # 5. hreflang 三向 + x-default
    head = soup.head
    for hl_lang, hl_cfg in LANGS.items():
        hl_prefix = "" if hl_lang == "zh" else f"/{hl_lang}"
        head.append(soup.new_tag("link", attrs={
            "rel": "alternate", "hreflang": hl_cfg["html_lang"], "href": f"{SITE}{hl_prefix}/lab/"
        }))
    head.append(soup.new_tag("link", attrs={
        "rel": "alternate", "hreflang": "x-default", "href": f"{SITE}/lab/"
    }))

    # 6. JSON-LD: WebApplication + BreadcrumbList
    webapp_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": s["h1_for_ld"],
        "description": s["description"],
        "inLanguage": cfg["html_lang"],
        "url": page_url,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Web",
        "isPartOf": {"@type": "WebSite", "name": "MotorLab.tw", "url": SITE + "/"},
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui["bc_home"], "item": home_url},
            {"@type": "ListItem", "position": 2, "name": s["breadcrumb"], "item": page_url},
        ],
    }
    for data in (webapp_ld, breadcrumb_ld):
        sc = soup.new_tag("script", attrs={"type": "application/ld+json"})
        sc.string = json.dumps(data, ensure_ascii=False, indent=2)
        head.append(sc)

    # 7. <body>:guide-nav + app 主體 + footer
    soup.body.clear()
    soup.body["class"] = "guide-page"

    nav_html = (
        f'<nav class="guide-nav"><div class="container">'
        f'<a class="brand" href="{home_url}"><span>MotorLab<span class="tag">.tw</span></span></a>'
        f'<a class="back-link" href="{home_url}">{ui["back_home"]}</a>'
        f'</div></nav>'
    )
    soup.body.append(BeautifulSoup(nav_html, "html.parser"))

    main_el = soup.new_tag("main")

    # 7a. Hero
    bc_html = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb">'
        f'<a href="{home_url}">{ui["bc_home"]}</a><span class="sep">/</span>'
        f'<span class="current">{s["breadcrumb"]}</span></nav>'
    )
    hero_html = (
        f'<section class="lab-hero"><div class="container">{bc_html}'
        f'<div class="lab-eyebrow">{s["eyebrow"]}</div>'
        f'<h1 class="lab-hero-title">{s["hero_title"]}</h1>'
        f'<p class="lab-hero-p">{s["hero_p"]}</p>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(hero_html, "html.parser"))

    # 7b. APP 導引區(上傳/下載皆於 MotorLab APP 內進行,網頁僅瀏覽)
    up_html = (
        f'<section class="lab-section"><div class="container">'
        f'<div class="lab-eyebrow">{s["up_eyebrow"]}</div>'
        f'<h2 class="lab-h2">{s["up_h2"]}</h2>'
        f'<div class="lab-appnote">'
        f'<p class="lab-appnote-main">{s["app_cta"]}</p>'
        f'<p class="lab-tos">{s["tos"]}</p>'
        f'</div>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(up_html, "html.parser"))

    # 7c. 篩選 + 列表
    list_html = (
        f'<section class="lab-section lab-band"><div class="container">'
        f'<div class="lab-eyebrow">{s["ls_eyebrow"]}</div>'
        f'<h2 class="lab-h2">{s["ls_h2"]}</h2>'
        f'<p class="lab-lead">{s["ls_note"]}</p>'
        f'<div class="lab-filters">'
        f'<select id="lab-f-motor" class="lab-input">'
        f'<option value="">{s["f_motor"]}</option>'
        + "".join(f'<option value="{m}">{m}</option>' for m in LAB_MOTOR_MODELS) +
        f'</select>'
        f'<input type="text" id="lab-f-country" class="lab-input" placeholder="{s["f_country"]}">'
        f'<select id="lab-f-completed" class="lab-input">'
        f'<option value="">{s["f_comp_all"]}</option>'
        f'<option value="true">{s["f_comp_yes"]}</option>'
        f'<option value="false">{s["f_comp_no"]}</option>'
        f'</select>'
        f'<select id="lab-f-sort" class="lab-input" aria-label="{s["f_sort"]}">'
        f'<option value="">{s["f_sort"]}</option>'
        f'<option value="rpm_max_overall|-1">{s["c_rpm"]} ▼</option>'
        f'<option value="rpm_max_overall|1">{s["c_rpm"]} ▲</option>'
        f'<option value="rpm_avg_overall|-1">{s["c_rpm_avg"]} ▼</option>'
        f'<option value="rpm_avg_overall|1">{s["c_rpm_avg"]} ▲</option>'
        f'<option value="stable_current_overall|-1">{s["c_current"]} ▼</option>'
        f'<option value="stable_current_overall|1">{s["c_current"]} ▲</option>'
        f'</select>'
        f'<select id="lab-f-pagesize" class="lab-input" aria-label="{s["f_show"]}">'
        f'<option value="10">{s["f_show"]} 10</option>'
        f'<option value="50">{s["f_show"]} 50</option>'
        f'<option value="100">{s["f_show"]} 100</option>'
        f'</select>'
        f'<button type="button" class="lab-btn" id="lab-refresh">{s["f_refresh"]}</button>'
        f'<div class="lab-count" id="lab-count"></div>'
        f'</div>'
        f'<div class="lab-results" id="lab-results"><p class="lab-muted">{s["ls_loading"]}</p></div>'
        f'<div class="lab-pager" id="lab-pager"></div>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(list_html, "html.parser"))

    soup.body.append(main_el)
    if footer_extracted is not None:
        soup.body.append(footer_extracted)

    # 8. 內嵌 app script(注入 API URL 與該語言的 JS 字串)
    app_js = LAB_APP_JS.replace("__API_URL__", lab_cfg["api_url"])
    app_js = app_js.replace("__I18N_JSON__", json.dumps(s["js"], ensure_ascii=False))
    script_tag = soup.new_tag("script")
    script_tag.string = app_js
    soup.body.append(script_tag)

    return str(soup)


# ============================================================
# VERIFY:正版查驗頁(/verify/)
#   使用者在機器「系統設定 → 正版查驗」看到設備 ID(12 hex),來此輸入查驗。
#   靜態站無後端 → 用 JSONP 打 GAS verify_public,回兩態 {ok:true/false}(防探測)。
#   來源交接:firmware docs/website_verify_page_spec.md。目前用「方案 A」現成 URL,
#   之後改「方案 B」獨立唯讀 GAS 只需換 VERIFY["api_url"] 一行。
# ============================================================
VERIFY = {
    # 方案 B(spec §5):獨立唯讀 GAS(gas/verify_public_standalone.gs),內建 JSONP,
    # 只讀白名單、不曝光更新/白名單那支。已實測 JSONP 正常(2026-07-10)。
    "api_url": "https://script.google.com/macros/s/AKfycbyyxHYnwbg3r3KINjsTjllB1CCoKF6cc_F7uX34QVdfbB1Vw9JXtHD-bckOfjv7QspbSg/exec",
    "i18n": {
        "zh": {
            "title": "正版查驗 | MotorLab",
            "description": "輸入 MotorLab 馬達磨合機上的設備 ID,即時查驗是否為正版註冊機。",
            "keywords": "MotorLab 正版查驗, 設備 ID 查驗, 正版認證, 馬達磨合機正版",
            "breadcrumb": "正版查驗",
            "h1_for_ld": "MotorLab 正版查驗",
            "eyebrow": "Verify · 正版查驗",
            "hero_title": "正版查驗",
            "hero_p": "輸入機器「系統設定 → 正版查驗」顯示的設備 ID,即時查驗是否為正版註冊機。",
            "form_label": "設備 ID",
            "input_ph": "輸入設備 ID(12 碼)",
            "btn": "查驗",
            "note": "請確認你正在<b>官方網站</b>(https://motorlab-tw.github.io/)進行查驗。設備 ID 可在機器「系統設定 → 正版查驗」中查看。查驗結果僅代表該設備 ID 是否在正版名單,不涉及個人資料。",
            "js": {
                "checking": "查驗中…",
                "timeout": "✗ 連線逾時,請稍後再試",
                "netfail": "✗ 連線失敗,請稍後再試",
                "badfmt": "⚠ 設備 ID 需為 12 位十六進位(0-9, A-F)",
                "genuine": "✅ <b>正版認證</b>",
                "notfound": "❌ <b>查無此機</b>　此設備 ID 未在正版名單,請聯繫原購買通路。",
                "busy": "⏳ 查驗繁忙,請稍後再試"
            }
        },
        "en": {
            "title": "Genuine Product Verification | MotorLab",
            "description": "Enter the Device ID from your MotorLab motor break-in machine to instantly verify it is a genuine, registered unit.",
            "keywords": "MotorLab genuine verification, device ID check, product authenticity, genuine motor break-in machine",
            "breadcrumb": "Verify",
            "h1_for_ld": "MotorLab Genuine Product Verification",
            "eyebrow": "Verify",
            "hero_title": "Genuine Product Verification",
            "hero_p": "Enter the Device ID shown in your machine's System Settings → Genuine Verification to instantly check whether it is a genuine, registered unit.",
            "form_label": "Device ID",
            "input_ph": "Enter Device ID (12 chars)",
            "btn": "Verify",
            "note": "Please confirm you are on the <b>official website</b> (https://motorlab-tw.github.io/). Find your Device ID in the machine's System Settings → Genuine Verification. The result only indicates whether the Device ID is on the genuine list; no personal data is involved.",
            "js": {
                "checking": "Verifying…",
                "timeout": "✗ Connection timed out, please try again later",
                "netfail": "✗ Connection failed, please try again later",
                "badfmt": "⚠ Device ID must be 12 hex characters (0-9, A-F)",
                "genuine": "✅ <b>Genuine product verified</b>",
                "notfound": "❌ <b>Not found.</b>　This Device ID is not on the genuine list; please contact your place of purchase.",
                "busy": "⏳ Busy, please try again later"
            }
        },
        "ja": {
            "title": "正規品認証 | MotorLab",
            "description": "MotorLab モーター慣らし機の「デバイス ID」を入力し、正規登録機かどうかをその場で確認できます。",
            "keywords": "MotorLab 正規品認証, デバイス ID 確認, 正規品チェック, モーター慣らし機 正規品",
            "breadcrumb": "正規品認証",
            "h1_for_ld": "MotorLab 正規品認証",
            "eyebrow": "Verify · 正規品認証",
            "hero_title": "正規品認証",
            "hero_p": "機器の「システム設定 → 正規品認証」に表示されるデバイス ID を入力すると、正規登録機かどうかをその場で確認できます。",
            "form_label": "デバイス ID",
            "input_ph": "デバイス ID を入力(12 桁)",
            "btn": "確認",
            "note": "<b>公式サイト</b>(https://motorlab-tw.github.io/)で確認していることをご確認ください。デバイス ID は機器の「システム設定 → 正規品認証」で確認できます。結果はデバイス ID が正規リストにあるかどうかのみを示し、個人情報は関与しません。",
            "js": {
                "checking": "確認中…",
                "timeout": "✗ 接続タイムアウト、後でもう一度お試しください",
                "netfail": "✗ 接続に失敗しました、後でもう一度お試しください",
                "badfmt": "⚠ デバイス ID は 12 桁の十六進数(0-9, A-F)です",
                "genuine": "✅ <b>正規品として認証されました</b>",
                "notfound": "❌ <b>見つかりません。</b>　このデバイス ID は正規リストにありません。ご購入元にお問い合わせください。",
                "busy": "⏳ 混雑しています、後でもう一度お試しください"
            }
        }
    }
}

# /verify/ JSONP 查驗邏輯(__API_URL__ / __I18N_JSON__ 由 build_verify_page 取代)
VERIFY_APP_JS = r"""
(function(){
  var VERIFY_URL = "__API_URL__";
  var I18N = __I18N_JSON__;
  var input = document.getElementById('vf-id');
  var btn = document.getElementById('vf-btn');
  var out = document.getElementById('vf-result');
  function normMac(s){ return (s||'').toUpperCase().replace(/[^0-9A-F]/g,''); }
  function setResult(html, cls){ out.className = 'vf-result vf-show' + (cls ? (' ' + cls) : ''); out.innerHTML = html; }
  function verify(){
    var mac = normMac(input.value);
    if(!/^[0-9A-F]{12}$/.test(mac)){ setResult(I18N.badfmt, 'warn'); return; }
    setResult(I18N.checking, 'muted');
    btn.disabled = true;
    var cb = 'v_' + Date.now();
    var s = document.createElement('script');
    var timer = setTimeout(function(){ cleanup(); setResult(I18N.timeout, 'bad'); }, 12000);
    function cleanup(){ clearTimeout(timer); try{ delete window[cb]; }catch(e){ window[cb] = undefined; } if(s.parentNode) s.parentNode.removeChild(s); btn.disabled = false; }
    window[cb] = function(res){ cleanup(); render(res); };
    s.onerror = function(){ cleanup(); setResult(I18N.netfail, 'bad'); };
    s.src = VERIFY_URL + '?action=verify_public&mac=' + encodeURIComponent(mac) + '&callback=' + cb + '&t=' + Date.now();
    document.body.appendChild(s);
  }
  function render(res){
    if(res && res.reason === 'rate_limited'){ setResult(I18N.busy, 'warn'); return; }
    if(res && res.ok === true) setResult(I18N.genuine, 'ok');
    else setResult(I18N.notfound, 'bad');
  }
  if(btn) btn.addEventListener('click', verify);
  if(input){
    input.addEventListener('keydown', function(e){ if(e.key === 'Enter'){ e.preventDefault(); verify(); } });
    input.addEventListener('input', function(){ var p = input.selectionStart; input.value = normMac(input.value); try{ input.setSelectionRange(p, p); }catch(e){} });
  }
})();
"""

# 查驗頁專屬 CSS(注入 head;版面沿用 .lab-* 系統,只補表單與結果狀態)
VERIFY_CSS = """
.vf-box{max-width:520px;margin:0 auto;text-align:center}
.vf-label{display:block;font-size:13px;color:var(--text-muted);margin-bottom:8px;letter-spacing:.04em;text-transform:uppercase}
.vf-row{display:flex;gap:10px;flex-wrap:wrap;justify-content:center}
.vf-row .lab-input{flex:1;min-width:200px;font-family:monospace;font-size:18px;letter-spacing:.12em;text-align:center;text-transform:uppercase}
.vf-row .lab-btn{white-space:nowrap}
.vf-result{margin-top:22px;min-height:1.6em;font-size:17px;line-height:1.6;opacity:0;transition:opacity .18s}
.vf-result.vf-show{opacity:1}
.vf-result.ok{color:#34d399}
.vf-result.bad{color:var(--text-secondary)}
.vf-result.warn{color:#fbbf24}
.vf-result.muted{color:var(--text-muted)}
.vf-note{max-width:560px;margin:28px auto 0;font-size:13px;line-height:1.8;color:var(--text-muted)}
"""


def build_verify_page(verify_cfg, lang, src_html, i18n):
    """產生 /verify/ 正版查驗頁(靜態殼 + JSONP 查驗,沿用 .guide-page / .lab-* 殼)。"""
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    ui = UI_STRINGS[lang]
    s = verify_cfg["i18n"][lang]
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    page_url = f"{SITE}{lang_prefix}/verify/"
    home_url = f"{SITE}{lang_prefix}/"

    soup.html["lang"] = cfg["html_lang"]

    for sc in soup.find_all("script", {"type": "application/ld+json"}):
        sc.decompose()
    for tag in soup.find_all("link", {"rel": "alternate"}):
        tag.decompose()

    footer_el = soup.find("footer")
    footer_extracted = footer_el.extract() if footer_el else None
    _fix_footer_verify(footer_extracted, lang)

    if soup.title:
        soup.title.string = s["title"]

    def set_meta(attr, attr_val, content):
        tag = soup.find("meta", {attr: attr_val})
        if tag:
            tag["content"] = content

    set_meta("name", "description", s["description"])
    kw = s["keywords"]
    if lang != "en" and "en" in verify_cfg["i18n"]:
        kw = kw + ", " + verify_cfg["i18n"]["en"]["keywords"]
    set_meta("name", "keywords", kw)
    set_meta("http-equiv", "Content-Language", cfg["html_lang"])
    set_meta("property", "og:type", "website")
    set_meta("property", "og:url", page_url)
    set_meta("property", "og:title", s["title"])
    set_meta("property", "og:description", s["description"])
    set_meta("property", "og:locale", cfg["og_locale"])
    set_meta("name", "twitter:title", s["title"])
    set_meta("name", "twitter:description", s["description"])

    canon = soup.find("link", {"rel": "canonical"})
    if canon:
        canon["href"] = page_url

    head = soup.head
    for hl_lang, hl_cfg in LANGS.items():
        hl_prefix = "" if hl_lang == "zh" else f"/{hl_lang}"
        head.append(soup.new_tag("link", attrs={
            "rel": "alternate", "hreflang": hl_cfg["html_lang"], "href": f"{SITE}{hl_prefix}/verify/"
        }))
    head.append(soup.new_tag("link", attrs={
        "rel": "alternate", "hreflang": "x-default", "href": f"{SITE}/verify/"
    }))

    # 查驗頁專屬 CSS
    style_tag = soup.new_tag("style")
    style_tag.string = VERIFY_CSS
    head.append(style_tag)

    webapp_ld = {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": s["h1_for_ld"],
        "description": s["description"],
        "inLanguage": cfg["html_lang"],
        "url": page_url,
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Web",
        "isPartOf": {"@type": "WebSite", "name": "MotorLab.tw", "url": SITE + "/"},
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui["bc_home"], "item": home_url},
            {"@type": "ListItem", "position": 2, "name": s["breadcrumb"], "item": page_url},
        ],
    }
    for data in (webapp_ld, breadcrumb_ld):
        sc = soup.new_tag("script", attrs={"type": "application/ld+json"})
        sc.string = json.dumps(data, ensure_ascii=False, indent=2)
        head.append(sc)

    soup.body.clear()
    soup.body["class"] = "guide-page"

    nav_html = (
        f'<nav class="guide-nav"><div class="container">'
        f'<a class="brand" href="{home_url}"><span>MotorLab<span class="tag">.tw</span></span></a>'
        f'<a class="back-link" href="{home_url}">{ui["back_home"]}</a>'
        f'</div></nav>'
    )
    soup.body.append(BeautifulSoup(nav_html, "html.parser"))

    main_el = soup.new_tag("main")

    bc_html = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb">'
        f'<a href="{home_url}">{ui["bc_home"]}</a><span class="sep">/</span>'
        f'<span class="current">{s["breadcrumb"]}</span></nav>'
    )
    hero_html = (
        f'<section class="lab-hero"><div class="container">{bc_html}'
        f'<div class="lab-eyebrow">{s["eyebrow"]}</div>'
        f'<h1 class="lab-hero-title">{s["hero_title"]}</h1>'
        f'<p class="lab-hero-p">{s["hero_p"]}</p>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(hero_html, "html.parser"))

    form_html = (
        f'<section class="lab-section"><div class="container">'
        f'<div class="vf-box">'
        f'<label class="vf-label" for="vf-id">{s["form_label"]}</label>'
        f'<div class="vf-row">'
        f'<input type="text" id="vf-id" class="lab-input" maxlength="12" '
        f'autocapitalize="characters" autocomplete="off" spellcheck="false" '
        f'inputmode="latin" placeholder="{s["input_ph"]}">'
        f'<button type="button" class="lab-btn" id="vf-btn">{s["btn"]}</button>'
        f'</div>'
        f'<div class="vf-result" id="vf-result" aria-live="polite"></div>'
        f'<p class="vf-note">{s["note"]}</p>'
        f'</div>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(form_html, "html.parser"))

    soup.body.append(main_el)
    if footer_extracted is not None:
        soup.body.append(footer_extracted)

    app_js = VERIFY_APP_JS.replace("__API_URL__", verify_cfg["api_url"])
    app_js = app_js.replace("__I18N_JSON__", json.dumps(s["js"], ensure_ascii=False))
    script_tag = soup.new_tag("script")
    script_tag.string = app_js
    soup.body.append(script_tag)

    return str(soup)


# ============================================================
# MANUAL:使用者手冊(/docs/user-manual/,D23 docs 分類首篇)
#   內容來自韌體 repo USER_MANUAL.md,守 D6(無硬體型號)。
#   每語言 = meta(title/desc/...) + sections[{id,t,html}]。
#   build_manual_page() 產生「左側目錄 + 右側章節」的長文件頁,沿用 .guide-page 殼。
# ============================================================
MANUAL = {
    "slug": "user-manual",
    "type": "docs",
    "fw": "v3.2.29",
    "i18n": {
        "zh": {
            "title": "MotorLab 使用者手冊:馬達磨合機操作說明 | MotorLab",
            "description": "MotorLab Mini 4WD® 馬達磨合機完整使用手冊 — 連線、馬達特性量測、馬達磨合、馬達測試、歷史紀錄、全球磨合資料庫、AI 健康管理、軸承/電刷測試、系統設定、安全保護、工廠重設與常見問題。對應韌體 v3.2.29。",
            "keywords": "MotorLab 使用手冊, 馬達磨合機操作, 馬達磨合機說明書, MotorLab 教學, 馬達磨合機設定",
            "breadcrumb": "使用者手冊",
            "eyebrow": "Docs · 使用者手冊",
            "h1": "MotorLab 使用者手冊",
            "lead": "Mini 4WD® 馬達磨合機完整操作說明。對應韌體 v3.2.29。功能隨版本更新,新版可能多出未列選項。",
            "toc_label": "目錄",
            "fw_note": "本手冊適用 MotorLab v3.2.29 韌體。",
        },
        "en": {
            "title": "MotorLab User Manual: Motor Break-in Machine Guide | MotorLab",
            "description": "Complete user manual for the MotorLab Mini 4WD® motor break-in machine — connection, motor characterization, break-in, testing, history records, global database, AI health management, bearing/brush tests, system settings, safety, factory reset and FAQ. For firmware v3.2.29.",
            "keywords": "MotorLab user manual, motor break-in machine guide, MotorLab instructions, motor tester manual, Mini 4WD break-in machine",
            "breadcrumb": "User Manual",
            "eyebrow": "Docs · User Manual",
            "h1": "MotorLab User Manual",
            "lead": "Complete operating guide for the Mini 4WD® motor break-in machine. For firmware v3.2.29. Features evolve with each release; newer firmware may add options not listed here.",
            "toc_label": "Contents",
            "fw_note": "This manual applies to MotorLab firmware v3.2.29.",
        },
        "ja": {
            "title": "MotorLab ユーザーマニュアル:モーター慣らし機操作ガイド | MotorLab",
            "description": "MotorLab Mini 4WD® モーター慣らし機の完全ユーザーマニュアル — 接続、モーター特性測定、慣らし、テスト、履歴記録、グローバルデータ庫、AI 健康管理、ベアリング/ブラシ測定、システム設定、安全保護、工場出荷リセット、FAQ。ファームウェア v3.2.29 対応。",
            "keywords": "MotorLab マニュアル, モーター慣らし機 操作, MotorLab 使い方, モーターテスター 説明書, ミニ四駆 慣らし機",
            "breadcrumb": "ユーザーマニュアル",
            "eyebrow": "Docs · ユーザーマニュアル",
            "h1": "MotorLab ユーザーマニュアル",
            "lead": "Mini 4WD® モーター慣らし機の完全操作ガイド。ファームウェア v3.2.29 対応。機能はバージョンごとに更新され、新版では未記載の項目が増える場合があります。",
            "toc_label": "目次",
            "fw_note": "本マニュアルは MotorLab ファームウェア v3.2.29 に対応します。",
        },
    },
    "sections": {
        "zh": [
            {"id": "start", "t": "一、快速開始", "html": (
                "<ol>"
                "<li>接通電源 → 板載指示燈亮、聽到開機嗶聲。</li>"
                "<li>手機 / 平板 / 電腦的 WiFi 連「<b>MotorTester</b>」(預設密碼 <code>12345678</code>)。</li>"
                "<li>瀏覽器開 <code>http://10.10.10.1/</code>。</li>"
                "<li><b>第一件事</b>:系統設定 → WiFi 設定,把密碼改強密碼(否則任何人都能操作機器)。</li>"
                "</ol>"
            )},
            {"id": "connect", "t": "二、連線", "html": (
                "<table class='manual-table'><tbody>"
                "<tr><th>網址</th><td><code>http://10.10.10.1/</code>(<b>不是</b> https)</td></tr>"
                "<tr><th>熱點</th><td><code>MotorTester</code> / <code>12345678</code>(可改名)</td></tr>"
                "<tr><th>裝置</th><td>手機 / 平板 / 筆電皆可,建議大螢幕</td></tr>"
                "<tr><th>連線數</th><td><b>同時只有一台可操作</b>(單一連線,見下)</td></tr>"
                "<tr><th>注意</th><td>機器熱點<b>無對外網路</b>;iPhone 跳「無網際網路」選「保持」即可</td></tr>"
                "</tbody></table>"
                "<p><b>單一連線(多台切換)</b>:操作介面同時只允許一台裝置控制,避免兩台同時下命令衝突。</p>"
                "<ul>"
                "<li><b>後連的裝置自動接管</b>:用新裝置開啟介面後,它即成為控制端。</li>"
                "<li><b>舊裝置自動停用</b>:先前那台會顯示「已被其他裝置接管」並停止更新(數值與圖表凍結),不會再送出命令。</li>"
                "<li><b>要換回舊裝置</b>:在該裝置上<b>重新整理頁面</b>即可重新接管(換成另一台被停用)。</li>"
                "<li>中途換裝置不影響進行中的磨合 / 測試——程序在機器端持續執行,新裝置連上後會直接顯示目前進度。</li>"
                "</ul>"
            )},
            {"id": "home", "t": "三、首頁", "html": (
                "<p>九個功能按鈕:</p>"
                "<p class='manual-pills'>馬達特性量測 · 馬達磨合 · 馬達測試 · 歷史紀錄 · AI 智慧馬達健康管理(Pro)· 軸承阻力測試 · 電刷接觸穩定測試 · 全球磨合資料庫 · 系統設定</p>"
                "<p>標題顯示 <code>MotorLab M1</code> 或 <code>MotorLab PRO</code>。</p>"
            )},
            {"id": "charexp", "t": "四、馬達特性量測", "html": (
                "<p class='manual-intro'>全自動量出馬達的特性參數與損耗,<b>給參考數據、不評分不排名</b> —— 同型號馬達互相比較、自己判斷。約 1~2 分鐘,過程溫和,適合全新未磨合馬達。</p>"
                "<p><b>操作</b>:首頁 →「馬達特性量測」→ 選方向(預設正轉)→「開始量測」→ 全程自動,過程中請勿觸碰馬達 → 完成顯示數據表。</p>"
                "<p><b>怎麼看數據(表內每項都標了方向)</b>:</p>"
                "<ul>"
                "<li><b>★ Km(品質因數)</b>:<b>越高越好</b> —— 選別馬達的首要指標。</li>"
                "<li><b>★ T_loss(損耗轉矩)/ I0</b>:同轉速下<b>越低越好</b>。</li>"
                "<li><b>Ke(磁路強度)</b>:無絕對好壞 —— 數值相近的馬達互相比較才準確(偏高=偏扭力、偏低=偏轉速)。</li>"
                "<li><b>R(內部電阻)</b>:越低越好。</li>"
                "<li><b>損耗擬合 R² / Ke 漂移</b>:資料品質指標(R² 越接近 1、漂移越低,這筆數據越可信)。</li>"
                "</ul>"
                "<p><b>建議用法</b>:同批新馬達逐顆量測 → 依 ★Km 與 ★T_loss 挑出體質好的再投入磨合(省磨合工時);磨合後<b>再測同一顆</b>對照 —— 損耗類應下降(磨合有效)、Ke / R 應幾乎不變。</p>"
                "<div class='manual-note'><b>注意</b>:量測失敗(馬達未起轉 / 鎖定逾時 / 過流)會顯示原因,重試即可;建議測 2 次看重複性。</div>"
            )},
            {"id": "breakin", "t": "五、馬達磨合", "html": (
                "<p class='manual-intro'>低速長時間運轉,讓電刷與整流子貼合到最佳接觸。分 <b>10 階段(a~j)</b>,預設約 5 小時。</p>"
                "<p><b>操作</b>:首頁 →「馬達磨合程式」→ 選<b>馬達型號</b>(16 款下拉)+ 填<b>備註</b>(選填,≤40 字)→ 確認 10 階段參數(直接點數字欄修改,改完自動套用)→「啟動」。</p>"
                "<p>每階段流程:緩啟動 → 運轉中 → 緩停止 → 冷卻中 → 下一階段。全部完成 → 嗶 3 聲 → 自動存入歷史紀錄。</p>"
                "<p><b>運轉中可按</b>:</p>"
                "<table class='manual-table'><thead><tr><th>按鈕</th><th>行為</th></tr></thead><tbody>"
                "<tr><td>停止</td><td>緩停後結束,紀錄標「使用者中止」</td></tr>"
                "<tr><td>歸零</td><td>清最大轉速 / 穩定電流峰值,不中斷</td></tr>"
                "<tr><td>回首頁</td><td>切回首頁,磨合<b>背景繼續跑</b></td></tr>"
                "</tbody></table>"
                "<div class='manual-note'><b>注意</b>:運轉中所有設定鎖定;勿中途斷電(資料遺失);高溫會自動停止並存檔;想快速驗機就把每階段時間改短。每階段可設電壓 / 方向 / 運轉時間 / 冷卻時間 / 穩定電流容差。</div>"
            )},
            {"id": "test", "t": "六、馬達測試", "html": (
                "<p class='manual-intro'>單階段即時觀察,<b>不寫入紀錄</b>。</p>"
                "<p>首頁 →「馬達測試程式」→ 設 <b>電壓(0.6~4.0V,預設 1V)/ 運轉時間 / 方向 / 穩定電流容差</b> →「啟動」→ 看即時數據與圖表,到時自動停。智慧模式下電流提前穩定會以「stable」結束。</p>"
                "<div class='manual-note'><b>注意</b>:電壓上限 4.0V 保護馬達,勿繞過;反轉接正轉前先按一次「停止」。</div>"
            )},
            {"id": "records", "t": "七、歷史紀錄", "html": (
                "<p class='manual-intro'>自動儲存每次磨合完整資料,最多 <b>50 筆</b>。</p>"
                "<p>每筆顯示名稱 / 開始時間 / 時長 / 模式 / 結束原因 / 最大轉速 / 平均轉速 / 穩定電流。</p>"
                "<table class='manual-table'><thead><tr><th>按鈕</th><th>用途</th></tr></thead><tbody>"
                "<tr><td>檢視</td><td>看每一階段數據</td></tr>"
                "<tr><td>套用</td><td>把 10 階段參數一鍵套回磨合頁</td></tr>"
                "<tr><td>匯出</td><td>下載 JSON(可再匯入)或 CSV(Excel 開)</td></tr>"
                "<tr><td>刪除</td><td>移除(不可復原)</td></tr>"
                "</tbody></table>"
                "<ul>"
                "<li><b>容量滿(50 筆)</b>:管理中可選「自動覆寫」(啟動時刪最舊)或「不覆寫」(預設,啟動被擋需手動清)。</li>"
                "<li><b>匯入</b>:選之前匯出的 JSON(id 重複會覆蓋)。只收 JSON。每個匯出檔帶<b>簽章驗證</b>:同台 / 同批機器可互通,竄改過或非本批機器的檔會被拒絕;改檔名不影響(驗的是內容)。</li>"
                "<li><b>檔名</b>:<code>motorlab_&lt;日期&gt;_&lt;時間&gt;_&lt;型號&gt;[_&lt;備註&gt;]</code>,採磨合開始時間 → 同筆重複匯出檔名一致。</li>"
                "<li>韌體更新 / 工廠重設<b>都不會清紀錄</b>。</li>"
                "</ul>"
            )},
            {"id": "database", "t": "八、全球磨合資料庫", "html": (
                "<p class='manual-intro'>與全球玩家分享磨合紀錄,機器<b>直接連網</b>完成,不必匯出再上網站。需連<b>有外網的 WiFi</b>(M1 / Pro 都能用)。</p>"
                "<p><b>瀏覽 / 下載</b>:首頁 →「全球磨合資料庫」→ 連網後列出最新 100 筆 → 用 <b>馬達型號 / 國家 / 完成狀態</b> 即時篩選 → 每筆可「下載」(存進本機)或「下載並套用」(存入並把配方套到磨合頁)。</p>"
                "<p><b>分享自己的</b>:歷史紀錄 → 點開某筆 → 詳情頁底部「分享到全球資料庫」→ 確認框<b>明列將公開的欄位</b>(型號 / 備註 / 分享者 / 國家 / 完整數據;填了名字會提醒顯示真名)→ 確認上傳。已上傳過會提示「這筆已在資料庫」(非錯誤)。</p>"
                "<div class='manual-note'><b>注意</b>:下載的紀錄會經簽章驗證;上傳即同意公開,需移除請來信 <b>motorlab.tw@gmail.com</b>;連到無外網的 WiFi 會提示「無法連到伺服器」。</div>"
            )},
            {"id": "ai", "t": "九、AI 智慧馬達健康管理(Pro)", "html": (
                "<p class='manual-intro'>為每顆馬達建立健康指紋,定期重測比對,給 0~100 分與建議。<b>跟自己比,不跟別顆比</b>。</p>"
                "<ol>"
                "<li>首頁 →「AI 智慧馬達健康管理」→「+ 新增馬達」。</li>"
                "<li>填 <b>馬達型號</b>(下拉)+ <b>備註</b>(選填)+ <b>起始電壓</b> + <b>電壓間距</b>(自動取 5 點)。</li>"
                "<li>確認 → 自動跑約 <b>2.5 分鐘</b> 建立基準。</li>"
                "</ol>"
                "<p>之後每張卡片可做 <b>完整檢測</b>(約 2.5 分,最準)或 <b>快速檢測</b>(約 1.5 分,±5%)。結果頁顯示分數、等級(Optimal / Acceptable / Warning / Critical)、趨勢圖、五項指標、文字建議。</p>"
                "<div class='manual-note'><b>注意</b>:每顆最多 50 次歷史,整機最多 20 顆;檢測中勿斷電 / 勿按其他鈕;高溫會自動中止;M1 版按鈕灰色(點下提示升級)。</div>"
            )},
            {"id": "bearing", "t": "十、軸承阻力測試", "html": (
                "<p class='manual-intro'>量軸承順暢度,任何版本可用。<b>完全靜止時間越久 → 軸承越順</b>。</p>"
                "<p>首頁 →「軸承阻力測試」→ 選測試電壓(<b>2.4V 或 3V</b>)→「開始測試」→ 機器加速到該電壓 → 穩定轉速 5 秒 → <b>直接斷電(不剎車)</b> → 計時到完全靜止 → 顯示 <b>完全靜止時間</b>。</p>"
                "<div class='manual-note'><b>注意</b>:馬達空載慣性小,本測試<b>只顯示時間、不做好壞評定</b>,請拿同一顆馬達不同時期、或不同馬達的時間互相比較;需轉速感應器正常;建議測 2~3 次看重複性。</div>"
            )},
            {"id": "brush", "t": "十一、電刷接觸穩定測試", "html": (
                "<p class='manual-intro'>量電刷接觸是否均勻,約 35 秒,任何版本可用。<b>接觸不均 → 電流抖動 → CV 上升</b>。</p>"
                "<p>首頁 →「電刷接觸穩定測試」→「開始測試」即可(<b>不需手轉軸心</b>)。流程固定在 <b>1V</b>:電壓 10 秒內由 0 緩升到 1V → 1V 保持 5 秒 → 1V 採樣電流 20 秒 → 顯示 <b>電流變異係數 CV%</b>。</p>"
                "<p><b>怎麼看 CV%</b>:CV 是固定電壓下電流的抖動程度,<b>是相對比較工具、沒有絕對好壞線</b>(不同型號馬達天生不同)。建議這樣用:</p>"
                "<ul>"
                "<li>同一顆馬達 <b>磨合前 vs 磨合後</b>:CV 下降 = 電刷磨開、接觸變好。</li>"
                "<li>同一顆馬達 <b>長期追蹤</b>:CV 逐漸上升 = 電刷磨損 / 整流子變髒。</li>"
                "<li><b>馬達 A vs B</b> 相對比較。</li>"
                "</ul>"
                "<div class='manual-note'><b>注意</b>:固定 1V、固定流程,才能跨次 / 跨馬達公平比較;建議測 2~3 次看重複性。</div>"
            )},
            {"id": "settings", "t": "十二、系統設定", "html": (
                "<p class='manual-intro'>系統運轉中此頁只留「回首頁」可按,其餘鎖定。</p>"
                "<table class='manual-table'><tbody>"
                "<tr><th>使用者設定</th><td>名稱 / 國家(≤32 字,預設 <code>--</code>),寫入每筆紀錄當出處。已產生的紀錄不回填。</td></tr>"
                "<tr><th>WiFi 設定</th><td>改熱點名稱 / 密碼(8~63 字)→ 儲存後機器重啟,須重新連新熱點。忘密碼見第十四節。</td></tr>"
                "<tr><th>語言</th><td>中文 / English / 日本語 切換(預設中文)。按「確定」後<b>系統重新啟動</b>乾淨載入(約 10 秒,頁面自動重新載入);運轉中切換則只重載頁面、不中斷程序。</td></tr>"
                "<tr><th>磨合模式</th><td>純運轉時間 / 智慧穩定電流判定(達時間<b>或</b>電流提前穩定即進下一階段)。</td></tr>"
                "<tr><th>溫度校正</th><td>顯示與實際有偏差時加補償(±20°C)。</td></tr>"
                "<tr><th>高溫鎖定</th><td>設定高溫鎖定溫度(預設 50°C,範圍 25~60°C)。當前溫度高於設定值 5°C 以上持續 10 秒即進入高溫鎖定(停機,須按歸零解除)。區塊內同時顯示當前溫度。</td></tr>"
                "<tr><th>平均轉速設定</th><td>容差(相鄰兩秒轉速差)下拉選單 120~600 RPM,<b>預設 240</b>。容差越大越容易判定穩定但反應較遲鈍;馬達較不穩可調高。</td></tr>"
                "<tr><th>緩啟動</th><td>採線性升壓(電壓由 0 在 5 秒內平順線性升到目標電壓,與緩停止同風格),<b>無可調參數</b>。電壓輸出已校準,不需設定啟動扭矩。</td></tr>"
                "<tr><th>取得授權</th><td>M1 升 Pro,見下。</td></tr>"
                "<tr><th>軟體更新</th><td>透過家裡 WiFi 自動取得最新韌體,見下。</td></tr>"
                "<tr><th>RGB 狀態燈</th><td>雙燈(內建 / 面板)輸出位置 + 亮度(0~100%)+ 5 組狀態樣式,見下。</td></tr>"
                "<tr><th>工程模式</th><td>密碼保護的進階校正與離線更新(一般使用者用不到)。</td></tr>"
                "<tr><th>WiFi 列表</th><td>最多記憶 8 組外部 WiFi;「清空列表」用於轉手設備(不影響 Pro 授權)。</td></tr>"
                "</tbody></table>"
                "<p><b>取得授權(M1 → Pro)</b>:系統設定 →「取得授權」→ 選家裡 WiFi 連線 → 機器自動驗證購買 → 未購買則顯示 QR Code → <b>用另一台有外網的裝置掃碼結帳</b> → 機器每 10 秒自動查詢,付款成功即解鎖。全程約 1~3 分鐘、<b>不必手動輸入金鑰</b>、最久 10 分鐘逾時可重試。退費過會顯示「重新取得授權」。</p>"
                "<p><b>軟體更新</b>:系統設定 →「檢查更新」→ 選 WiFi → 有新版自動下載寫入(進度到 100%)→ 自動重啟、頁面自動重載。<b>過程勿關電源 / 瀏覽器</b>(中途斷電有保護自動回舊版);下載約 1.6MB,家用 WiFi 約 5~10 秒。</p>"
                "<p><b>RGB 狀態燈</b>:</p>"
                "<ul>"
                "<li><b>輸出位置</b>:面板 / 面板+內建(預設)/ 內建,點按即時切換。</li>"
                "<li><b>亮度</b>:拖滑桿 → 按「預覽」(試 5 秒不儲存,可多試)→ 滿意按「套用」儲存。(分兩步是避免連續寫入造成連線卡頓。)</li>"
                "<li><b>狀態樣式(5 組)</b>:由上而下掃描,狀態符合即顯示對應 狀態(無 / 高溫 / 冷卻 / 待機 / 運轉)× 色相 × 模式(常亮 / 閃爍 / 呼吸)× 間隔 / 週期;同樣「預覽 / 套用」兩步。</li>"
                "</ul>"
                "<p><b>工程模式</b>:需密碼(密碼錯 3 次鎖 60 秒,10 分鐘無操作自動登出)。</p>"
            )},
            {"id": "safety", "t": "十三、安全與保護", "html": (
                "<table class='manual-table'><thead><tr><th>機制</th><th>觸發 / 行為</th></tr></thead><tbody>"
                "<tr><td>高溫保護</td><td>兩種觸發:① 溫度感測器警報;② 當前溫度高於「高溫鎖定溫度」設定值 5°C 以上持續 10 秒(見系統設定)。任一觸發 → 立即停馬達 + 嗶 5 聲 + 鎖定。鎖定期間狀態列 / 旗標 / 狀態燈持續顯示高溫,首頁只剩「馬達磨合 / 馬達測試」可進、操作頁只剩「歸零 / 回首頁」可按。<b>即使溫度已降回也須按「歸零」才解除</b>(仍高溫時按歸零會再次鎖定,須先降溫)。</td></tr>"
                "<tr><td>緩啟動 / 緩停止</td><td>啟動為 5 秒線性升壓(0V→目標電壓),停止為 3 秒線性下降,避免電流爆衝與機械衝擊。</td></tr>"
                "<tr><td>電流上限</td><td>固定 4A 量測上限,超過讀值封頂(不停機,但長時間高電流可能觸發高溫)。</td></tr>"
                "<tr><td>開機鎖定</td><td>開機 30 秒內連續 3 次崩潰 → 自動切回上一版韌體。</td></tr>"
                "</tbody></table>"
            )},
            {"id": "reset", "t": "十四、工廠重設(救援)", "html": (
                "<p><b>用途</b>:忘記 WiFi 名稱 / 密碼時,把熱點重設回 <code>MotorTester</code> / <code>12345678</code>。</p>"
                "<p><b>做法</b>:把機器上的「工廠重設」接點短接 3.3V(或按對應按鈕)<b>持續 5 秒</b> → 嗶 10 聲 → 自動重啟。</p>"
                "<div class='manual-note'><b>只重設 WiFi 熱點名稱與密碼</b>,以下全部保留:磨合參數 / 各項校正與設定 / Pro 授權 / 歷史紀錄 / 馬達指紋 / RGB 設定 / 已記憶外部 WiFi。</div>"
            )},
            {"id": "faq", "t": "十五、常見問題", "html": (
                "<table class='manual-table'><thead><tr><th>問題</th><th>處理</th></tr></thead><tbody>"
                "<tr><td>開機沒嗶聲</td><td>確認電源 5V、蜂鳴器接線</td></tr>"
                "<tr><td>Web UI 使用中無反應</td><td>檢查是否仍連接著機器 WiFi(MotorTester);裝置可能自動切回有網路的 WiFi → 重新連回機器熱點並重整網頁</td></tr>"
                "<tr><td>連得上但網頁打不開</td><td>確認是 <code>http://</code>(非 https)、關行動數據、強制重整(Ctrl+Shift+R)</td></tr>"
                "<tr><td>一直顯示「套用中…」</td><td>通常 WiFi 不穩,重整網頁即可(內建 8 秒監視會轉紅字提示)</td></tr>"
                "<tr><td>磨合中途換馬達</td><td>按「停止」→ 換馬達 → 重新「啟動」(新一次是全新紀錄)</td></tr>"
                "<tr><td>取得授權卡在連線</td><td>家裡 WiFi 密碼錯 / 無外網 / 訊號弱 → 重輸入或換 WiFi</td></tr>"
                "<tr><td>Pro 退費後</td><td>機器連網重驗時<b>自動退回 M1</b>;想再買按「重新取得授權」</td></tr>"
                "<tr><td>紅色「AP 密碼仍為預設」橫幅</td><td>至 WiFi 設定改密碼</td></tr>"
                "<tr><td>轉手給別人</td><td>工程模式重置校正 → 清空 WiFi 列表 →(選)清紀錄 / 刪馬達 → 工廠重設。Pro 授權綁機器無法轉移</td></tr>"
                "<tr><td>更新失敗會變磚嗎</td><td>不會,有雙韌體區自動回退 + 簽章驗證 + USB 救援</td></tr>"
                "<tr><td>待機可拔電源嗎</td><td>可,建議馬達完全停止、無「套用中」、無更新進行中</td></tr>"
                "</tbody></table>"
            )},
            {"id": "led", "t": "十六、狀態燈號", "html": (
                "<p>預設配置(可在「RGB 狀態燈」修改):</p>"
                "<table class='manual-table'><thead><tr><th>系統狀態</th><th>預設</th><th>含義</th></tr></thead><tbody>"
                "<tr><td>高溫鎖定</td><td>紅閃</td><td>觸發高溫保護,須降溫並按「歸零」</td></tr>"
                "<tr><td>冷卻中</td><td>黃常亮</td><td>階段間冷卻,馬達靜止</td></tr>"
                "<tr><td>待機</td><td>藍呼吸</td><td>等待指令</td></tr>"
                "<tr><td>運轉中</td><td>綠呼吸</td><td>磨合 / 測試 / 檢測中</td></tr>"
                "<tr><td>燈滅</td><td>—</td><td>無匹配或全關</td></tr>"
                "</tbody></table>"
                "<p class='manual-contact'><b>回報問題</b>請一併提供:韌體版本(系統設定 → 軟體更新)、版本變體(首頁 M1 / PRO)、問題畫面截圖、是否在運轉中、重現步驟。客服:<b>motorlab.tw@gmail.com</b></p>"
            )},
        ],
        "en": [
            {"id": "start", "t": "1. Quick Start", "html": (
                "<ol>"
                "<li>Power on → onboard indicator lights up, you hear a boot beep.</li>"
                "<li>On your phone / tablet / PC, join the WiFi network “<b>MotorTester</b>” (default password <code>12345678</code>).</li>"
                "<li>Open <code>http://10.10.10.1/</code> in a browser.</li>"
                "<li><b>First thing to do</b>: System Settings → WiFi Settings, change the password to a strong one (otherwise anyone can operate the machine).</li>"
                "</ol>"
            )},
            {"id": "connect", "t": "2. Connection", "html": (
                "<table class='manual-table'><tbody>"
                "<tr><th>Address</th><td><code>http://10.10.10.1/</code> (<b>not</b> https)</td></tr>"
                "<tr><th>Hotspot</th><td><code>MotorTester</code> / <code>12345678</code> (renamable)</td></tr>"
                "<tr><th>Device</th><td>Phone / tablet / laptop all work; a larger screen is recommended</td></tr>"
                "<tr><th>Connections</th><td><b>Only one device can operate at a time</b> (single-connection, see below)</td></tr>"
                "<tr><th>Note</th><td>The hotspot has <b>no internet</b>; on iPhone, tap “Keep” when it warns “No Internet Connection”</td></tr>"
                "</tbody></table>"
                "<p><b>Single-connection (switching devices)</b>: only one device may control the interface at a time, preventing two devices from issuing conflicting commands.</p>"
                "<ul>"
                "<li><b>The newest device takes over</b>: open the interface on a new device and it becomes the controller.</li>"
                "<li><b>The old device is disabled</b>: it shows “Taken over by another device” and stops updating (values and charts freeze); it no longer sends commands.</li>"
                "<li><b>To switch back</b>: simply <b>refresh the page</b> on that device to take control again (the other one is then disabled).</li>"
                "<li>Switching devices does not affect a running break-in / test — the procedure keeps running on the machine, and a newly connected device shows the current progress right away.</li>"
                "</ul>"
            )},
            {"id": "home", "t": "3. Home Screen", "html": (
                "<p>Nine function buttons:</p>"
                "<p class='manual-pills'>Motor Characterization · Motor Break-in · Motor Test · History Records · AI Motor Health (Pro) · Bearing Resistance Test · Brush Contact Stability Test · Global Database · System Settings</p>"
                "<p>The title shows <code>MotorLab M1</code> or <code>MotorLab PRO</code>.</p>"
            )},
            {"id": "charexp", "t": "4. Motor Characterization", "html": (
                "<p class='manual-intro'>Fully automatic measurement of a motor's characteristic parameters and losses — <b>reference data, no scoring or ranking</b>. Compare motors of the same model and judge for yourself. About 1–2 minutes, gentle enough for brand-new, un-broken-in motors.</p>"
                "<p><b>Steps</b>: Home →「Motor Characterization」→ pick a direction (forward by default) →「Start」→ fully automatic; do not touch the motor during the run → a data table is shown when done.</p>"
                "<p><b>Reading the data (each item is labelled with its direction)</b>:</p>"
                "<ul>"
                "<li><b>★ Km (quality factor)</b>: <b>higher is better</b> — the primary metric for grading motors.</li>"
                "<li><b>★ T_loss (loss torque) / I0</b>: at the same RPM, <b>lower is better</b>.</li>"
                "<li><b>Ke (magnetic strength)</b>: no absolute good/bad — only meaningful when comparing motors with similar values (higher = torque-leaning, lower = speed-leaning).</li>"
                "<li><b>R (internal resistance)</b>: lower is better.</li>"
                "<li><b>Loss-fit R² / Ke drift</b>: data-quality indicators (R² closer to 1 and lower drift means a more trustworthy reading).</li>"
                "</ul>"
                "<p><b>Suggested use</b>: measure each motor in a new batch → pick the strong ones by ★Km and ★T_loss before investing break-in time; after break-in, <b>re-measure the same motor</b> — the loss figures should drop (break-in worked) while Ke / R stay almost unchanged.</p>"
                "<div class='manual-note'><b>Note</b>: a failed measurement (motor didn't spin up / lock-in timeout / over-current) shows the reason — just retry; measure twice to check repeatability.</div>"
            )},
            {"id": "breakin", "t": "5. Motor Break-in", "html": (
                "<p class='manual-intro'>Long, low-speed running that beds the brushes against the commutator for optimal contact. Split into <b>10 stages (a–j)</b>, about 5 hours by default.</p>"
                "<p><b>Steps</b>: Home →「Motor Break-in」→ pick the <b>motor model</b> (16-model dropdown) + enter a <b>note</b> (optional, ≤40 chars) → confirm the 10-stage parameters (tap a number field to edit; changes apply automatically) →「Start」.</p>"
                "<p>Each stage: soft-start → running → soft-stop → cooling → next stage. When all finish → 3 beeps → automatically saved to History Records.</p>"
                "<p><b>While running you can press</b>:</p>"
                "<table class='manual-table'><thead><tr><th>Button</th><th>Behaviour</th></tr></thead><tbody>"
                "<tr><td>Stop</td><td>Soft-stops then ends; record marked “user-stopped”</td></tr>"
                "<tr><td>Reset</td><td>Clears max-RPM / stable-current peaks without interrupting</td></tr>"
                "<tr><td>Home</td><td>Returns to home; break-in <b>keeps running in the background</b></td></tr>"
                "</tbody></table>"
                "<div class='manual-note'><b>Note</b>: all settings lock while running; don’t cut power mid-run (data loss); overheating auto-stops and saves; to bench-test quickly, shorten each stage’s time. Each stage sets voltage / direction / run time / cool time / stable-current tolerance.</div>"
            )},
            {"id": "test", "t": "6. Motor Test", "html": (
                "<p class='manual-intro'>Single-stage live observation, <b>not written to records</b>.</p>"
                "<p>Home →「Motor Test」→ set <b>voltage (0.6–4.0V, default 1V) / run time / direction / stable-current tolerance</b> →「Start」→ watch live data and charts; stops automatically at time. In smart mode, if the current settles early it ends as “stable”.</p>"
                "<div class='manual-note'><b>Note</b>: the 4.0V cap protects the motor — don’t bypass it; press “Stop” once before switching from reverse to forward.</div>"
            )},
            {"id": "records", "t": "7. History Records", "html": (
                "<p class='manual-intro'>Every break-in is saved in full automatically, up to <b>50 records</b>.</p>"
                "<p>Each shows name / start time / duration / mode / end reason / max RPM / avg RPM / stable current.</p>"
                "<table class='manual-table'><thead><tr><th>Button</th><th>Use</th></tr></thead><tbody>"
                "<tr><td>View</td><td>See per-stage data</td></tr>"
                "<tr><td>Apply</td><td>One-tap the 10-stage parameters back to the break-in page</td></tr>"
                "<tr><td>Export</td><td>Download JSON (re-importable) or CSV (opens in Excel)</td></tr>"
                "<tr><td>Delete</td><td>Remove (irreversible)</td></tr>"
                "</tbody></table>"
                "<ul>"
                "<li><b>When full (50)</b>: in Manage choose “auto-overwrite” (deletes oldest on start) or “no overwrite” (default; start is blocked, clear manually).</li>"
                "<li><b>Import</b>: pick a previously exported JSON (duplicate id overwrites). JSON only. Each export carries a <b>signature</b>: same / same-batch machines interchange, but tampered or other-batch files are rejected; renaming doesn’t matter (the content is verified).</li>"
                "<li><b>Filename</b>: <code>motorlab_&lt;date&gt;_&lt;time&gt;_&lt;model&gt;[_&lt;note&gt;]</code>, using the break-in start time → repeated exports of the same record share the filename.</li>"
                "<li>Firmware updates / factory reset <b>never clear records</b>.</li>"
                "</ul>"
            )},
            {"id": "database", "t": "8. Global Break-in Database", "html": (
                "<p class='manual-intro'>Share break-in records with players worldwide — done <b>directly over the network from the machine</b>, no export-then-upload needed. Requires WiFi <b>with internet</b> (M1 / Pro both work).</p>"
                "<p><b>Browse / download</b>: Home →「Global Database」→ after connecting, the latest 100 records are listed → filter live by <b>motor model / country / completion</b> → each can be “Download” (saves locally) or “Download &amp; Apply” (saves and applies the profile to the break-in page).</p>"
                "<p><b>Share yours</b>: History Records → open a record → at the bottom of the detail page “Share to Global Database” → the confirm box <b>lists exactly what becomes public</b> (model / note / sharer / country / full data; if you entered a name it warns it shows your real name) → confirm upload. If already uploaded it notes “this record is already in the database” (not an error).</p>"
                "<div class='manual-note'><b>Note</b>: downloaded records are signature-verified; uploading means agreeing to make it public — to remove, email <b>motorlab.tw@gmail.com</b>; connecting to WiFi without internet shows “cannot reach the server”.</div>"
            )},
            {"id": "ai", "t": "9. AI Motor Health Management (Pro)", "html": (
                "<p class='manual-intro'>Builds a health fingerprint per motor, re-measures periodically and compares, giving a 0–100 score with advice. <b>Compared against itself, not against other motors</b>.</p>"
                "<ol>"
                "<li>Home →「AI Motor Health」→「+ Add Motor」.</li>"
                "<li>Enter <b>motor model</b> (dropdown) + <b>note</b> (optional) + <b>start voltage</b> + <b>voltage step</b> (5 points auto-selected).</li>"
                "<li>Confirm → runs about <b>2.5 minutes</b> to build the baseline.</li>"
                "</ol>"
                "<p>Afterwards each card can run a <b>Full check</b> (~2.5 min, most accurate) or <b>Quick check</b> (~1.5 min, ±5%). The result page shows the score, grade (Optimal / Acceptable / Warning / Critical), trend chart, five metrics and written advice.</p>"
                "<div class='manual-note'><b>Note</b>: up to 50 history entries per motor, 20 motors per machine; don’t cut power or press other buttons during a check; overheating auto-aborts; on M1 the button is greyed (tapping prompts an upgrade).</div>"
            )},
            {"id": "bearing", "t": "10. Bearing Resistance Test", "html": (
                "<p class='manual-intro'>Measures bearing smoothness, available on any edition. <b>Longer time to a complete stop → smoother bearing</b>.</p>"
                "<p>Home →「Bearing Resistance Test」→ pick a test voltage (<b>2.4V or 3V</b>) →「Start」→ the machine accelerates to that voltage → holds steady RPM for 5 s → <b>cuts power directly (no braking)</b> → times until a complete stop → shows the <b>time-to-complete-stop</b>.</p>"
                "<div class='manual-note'><b>Note</b>: an unloaded motor has little inertia, so this test <b>only shows the time and gives no good/bad rating</b> — compare the same motor at different times, or different motors, against each other; needs a working RPM sensor; measure 2–3 times to check repeatability.</div>"
            )},
            {"id": "brush", "t": "11. Brush Contact Stability Test", "html": (
                "<p class='manual-intro'>Measures whether brush contact is even, about 35 seconds, any edition. <b>Uneven contact → current jitter → higher CV</b>.</p>"
                "<p>Home →「Brush Contact Stability Test」→ just press「Start」(<b>no manual shaft turning</b>). The routine is fixed at <b>1V</b>: voltage ramps from 0 to 1V within 10 s → holds 1V for 5 s → samples current at 1V for 20 s → shows the <b>current coefficient of variation, CV%</b>.</p>"
                "<p><b>Reading CV%</b>: CV is how much the current jitters at a fixed voltage — <b>a relative comparison tool with no absolute good/bad line</b> (different motor models differ by nature). Use it like this:</p>"
                "<ul>"
                "<li>Same motor <b>before vs after break-in</b>: CV drops = brushes bedded in, contact improved.</li>"
                "<li>Same motor <b>tracked over time</b>: CV creeping up = brush wear / dirty commutator.</li>"
                "<li><b>Motor A vs B</b> relative comparison.</li>"
                "</ul>"
                "<div class='manual-note'><b>Note</b>: the fixed 1V and fixed routine are what make runs / motors fairly comparable; measure 2–3 times to check repeatability.</div>"
            )},
            {"id": "settings", "t": "12. System Settings", "html": (
                "<p class='manual-intro'>While the system is running, only “Home” is available here; everything else is locked.</p>"
                "<table class='manual-table'><tbody>"
                "<tr><th>User Settings</th><td>Name / country (≤32 chars, default <code>--</code>), written into each record as its origin. Existing records are not back-filled.</td></tr>"
                "<tr><th>WiFi Settings</th><td>Change hotspot name / password (8–63 chars) → the machine restarts after saving; reconnect to the new hotspot. Forgot the password? See section 14.</td></tr>"
                "<tr><th>Language</th><td>Switch 中文 / English / 日本語 (default Chinese). After pressing OK the <b>system restarts</b> for a clean load (~10 s, the page reloads automatically); switching mid-run only reloads the page without interrupting the procedure.</td></tr>"
                "<tr><th>Break-in Mode</th><td>Pure run-time / smart stable-current (advances on time <b>or</b> when current settles early).</td></tr>"
                "<tr><th>Temp Calibration</th><td>Add compensation when the display deviates from reality (±20°C).</td></tr>"
                "<tr><th>Overheat Lock</th><td>Set the overheat-lock temperature (default 50°C, range 25–60°C). When the current temperature stays 5°C above the set value for 10 seconds, it enters overheat lock (stops, must press Reset to clear). The block also shows the current temperature.</td></tr>"
                "<tr><th>Avg-RPM Setting</th><td>Tolerance (RPM difference between consecutive seconds), dropdown 120–600 RPM, <b>default 240</b>. A larger tolerance settles more easily but reacts slower; raise it for a less steady motor.</td></tr>"
                "<tr><th>Soft-start</th><td>Linear voltage ramp (voltage rises smoothly from 0 to the target over 5 s, matching soft-stop), <b>no adjustable parameters</b>. Output voltage is calibrated, so no start-torque setting is needed.</td></tr>"
                "<tr><th>Get License</th><td>Upgrade M1 to Pro, see below.</td></tr>"
                "<tr><th>Software Update</th><td>Auto-fetch the latest firmware over home WiFi, see below.</td></tr>"
                "<tr><th>RGB Status Light</th><td>Dual lights (built-in / panel) output location + brightness (0–100%) + 5 status styles, see below.</td></tr>"
                "<tr><th>Engineering Mode</th><td>Password-protected advanced calibration and offline update (not needed by normal users).</td></tr>"
                "<tr><th>WiFi List</th><td>Remembers up to 8 external WiFi networks; “Clear list” for handing the device on (does not affect Pro license).</td></tr>"
                "</tbody></table>"
                "<p><b>Get License (M1 → Pro)</b>: System Settings →「Get License」→ pick your home WiFi → the machine verifies the purchase automatically → if not purchased it shows a QR code → <b>scan and pay on another internet-connected device</b> → the machine polls every 10 s and unlocks on payment. About 1–3 minutes total, <b>no manual key entry</b>, retry if it times out after 10 minutes. After a refund it shows “Re-acquire license”.</p>"
                "<p><b>Software Update</b>: System Settings →「Check for Updates」→ pick WiFi → if there’s a new version it downloads and writes automatically (progress to 100%) → auto-restarts and reloads the page. <b>Don’t cut power / close the browser</b> during this (power loss mid-update auto-reverts to the old version); ~1.6MB download, about 5–10 s on home WiFi.</p>"
                "<p><b>RGB Status Light</b>:</p>"
                "<ul>"
                "<li><b>Output location</b>: panel / panel+built-in (default) / built-in, switches instantly on tap.</li>"
                "<li><b>Brightness</b>: drag the slider →「Preview」(tries it for 5 s without saving, repeatable) → when happy press「Apply」to save. (Two steps avoid connection stutter from continuous writes.)</li>"
                "<li><b>Status styles (5)</b>: scanned top-down; the first matching status shows its status (none / overheat / cooling / standby / running) × hue × mode (solid / blink / breathe) × interval / period; same Preview / Apply two-step.</li>"
                "</ul>"
                "<p><b>Engineering Mode</b>: requires a password (3 wrong attempts lock for 60 s; auto-logout after 10 minutes idle).</p>"
            )},
            {"id": "safety", "t": "13. Safety & Protection", "html": (
                "<table class='manual-table'><thead><tr><th>Mechanism</th><th>Trigger / behaviour</th></tr></thead><tbody>"
                "<tr><td>Overheat protection</td><td>Two triggers: (1) temperature-sensor alarm; (2) current temperature 5°C above the “overheat-lock temperature” for 10 seconds (see System Settings). Either one → motor stops immediately + 5 beeps + lock. While locked, the status bar / flag / status light keep showing overheat; home leaves only “Break-in / Test” enterable and the operation page only “Reset / Home”. <b>Even after the temperature drops you must press “Reset” to clear</b> (pressing Reset while still hot re-locks; cool down first).</td></tr>"
                "<tr><td>Soft-start / soft-stop</td><td>Start is a 5-second linear voltage ramp (0V→target), stop is a 3-second linear ramp down, avoiding current surges and mechanical shock.</td></tr>"
                "<tr><td>Current cap</td><td>Fixed 4A measurement ceiling; readings clamp above it (no shutdown, but sustained high current may trigger overheat).</td></tr>"
                "<tr><td>Boot lock</td><td>3 crashes within 30 s of boot → automatically reverts to the previous firmware.</td></tr>"
                "</tbody></table>"
            )},
            {"id": "reset", "t": "14. Factory Reset (Rescue)", "html": (
                "<p><b>Purpose</b>: when you’ve forgotten the WiFi name / password, reset the hotspot back to <code>MotorTester</code> / <code>12345678</code>.</p>"
                "<p><b>How</b>: short the machine’s “factory reset” contact to 3.3V (or press the corresponding button) <b>for 5 seconds</b> → 10 beeps → auto-restart.</p>"
                "<div class='manual-note'><b>Only the WiFi hotspot name and password are reset</b>; all of the following are kept: break-in parameters / all calibrations and settings / Pro license / history records / motor fingerprints / RGB settings / remembered external WiFi.</div>"
            )},
            {"id": "faq", "t": "15. FAQ", "html": (
                "<table class='manual-table'><thead><tr><th>Problem</th><th>Fix</th></tr></thead><tbody>"
                "<tr><td>No beep on power-on</td><td>Check 5V power and buzzer wiring</td></tr>"
                "<tr><td>Web UI unresponsive during use</td><td>Check you’re still connected to the machine’s WiFi (MotorTester); your device may have auto-switched to an internet WiFi → reconnect to the machine hotspot and refresh the page</td></tr>"
                "<tr><td>Connects but page won’t open</td><td>Make sure it’s <code>http://</code> (not https), turn off mobile data, force-refresh (Ctrl+Shift+R)</td></tr>"
                "<tr><td>Stuck on “Applying…”</td><td>Usually unstable WiFi; just refresh the page (a built-in 8-second watchdog turns the text red)</td></tr>"
                "<tr><td>Swap motor mid-break-in</td><td>Press “Stop” → swap → “Start” again (a new run is a brand-new record)</td></tr>"
                "<tr><td>License stuck on connecting</td><td>Wrong home WiFi password / no internet / weak signal → re-enter or change WiFi</td></tr>"
                "<tr><td>After a Pro refund</td><td>On the next online re-check the machine <b>auto-reverts to M1</b>; to buy again press “Re-acquire license”</td></tr>"
                "<tr><td>Red “AP password still default” banner</td><td>Change the password in WiFi Settings</td></tr>"
                "<tr><td>Handing it to someone else</td><td>Reset calibration in engineering mode → clear WiFi list → (optional) clear records / delete motors → factory reset. The Pro license is bound to the machine and cannot be transferred</td></tr>"
                "<tr><td>Can a failed update brick it?</td><td>No — dual firmware partitions with auto-rollback + signature verification + USB rescue</td></tr>"
                "<tr><td>Can I unplug while idle?</td><td>Yes; best when the motor is fully stopped, no “Applying…”, no update in progress</td></tr>"
                "</tbody></table>"
            )},
            {"id": "led", "t": "16. Status Lights", "html": (
                "<p>Default configuration (editable in “RGB Status Light”):</p>"
                "<table class='manual-table'><thead><tr><th>System state</th><th>Default</th><th>Meaning</th></tr></thead><tbody>"
                "<tr><td>Overheat lock</td><td>Red blink</td><td>Overheat protection triggered; cool down and press “Reset”</td></tr>"
                "<tr><td>Cooling</td><td>Yellow solid</td><td>Inter-stage cooling, motor still</td></tr>"
                "<tr><td>Standby</td><td>Blue breathe</td><td>Awaiting commands</td></tr>"
                "<tr><td>Running</td><td>Green breathe</td><td>Break-in / test / check in progress</td></tr>"
                "<tr><td>Off</td><td>—</td><td>No match or all off</td></tr>"
                "</tbody></table>"
                "<p class='manual-contact'>When <b>reporting a problem</b>, please include: firmware version (System Settings → Software Update), edition (M1 / PRO on home), a screenshot, whether it was running, and steps to reproduce. Support: <b>motorlab.tw@gmail.com</b></p>"
            )},
        ],
        "ja": [
            {"id": "start", "t": "1. クイックスタート", "html": (
                "<ol>"
                "<li>電源を接続 → 基板のインジケーターが点灯し、起動音が鳴ります。</li>"
                "<li>スマホ / タブレット / PC の WiFi で「<b>MotorTester</b>」に接続(初期パスワード <code>12345678</code>)。</li>"
                "<li>ブラウザで <code>http://10.10.10.1/</code> を開きます。</li>"
                "<li><b>最初にやること</b>:システム設定 → WiFi 設定で、パスワードを強固なものに変更(そうしないと誰でも機器を操作できます)。</li>"
                "</ol>"
            )},
            {"id": "connect", "t": "2. 接続", "html": (
                "<table class='manual-table'><tbody>"
                "<tr><th>アドレス</th><td><code>http://10.10.10.1/</code>(<b>https ではありません</b>)</td></tr>"
                "<tr><th>ホットスポット</th><td><code>MotorTester</code> / <code>12345678</code>(名称変更可)</td></tr>"
                "<tr><th>デバイス</th><td>スマホ / タブレット / ノート PC いずれも可。大きな画面推奨</td></tr>"
                "<tr><th>接続数</th><td><b>同時に操作できるのは 1 台のみ</b>(単一接続、下記参照)</td></tr>"
                "<tr><th>注意</th><td>機器のホットスポットは<b>インターネットなし</b>。iPhone で「インターネット未接続」が出たら「保持」を選択</td></tr>"
                "</tbody></table>"
                "<p><b>単一接続(複数台の切替)</b>:操作画面を制御できるのは同時に 1 台のみ。2 台が同時にコマンドを送る競合を防ぎます。</p>"
                "<ul>"
                "<li><b>後から接続した端末が引き継ぐ</b>:新しい端末で画面を開くと、その端末が制御側になります。</li>"
                "<li><b>前の端末は自動で無効化</b>:「他の端末に引き継がれました」と表示され更新を停止(数値とグラフが凍結)、コマンドも送らなくなります。</li>"
                "<li><b>元の端末に戻すには</b>:その端末で<b>ページを再読込</b>すれば再び制御を引き継げます(もう一方が無効化)。</li>"
                "<li>途中で端末を切り替えても進行中の慣らし / テストには影響しません——処理は機器側で継続し、新しく接続した端末には現在の進捗がそのまま表示されます。</li>"
                "</ul>"
            )},
            {"id": "home", "t": "3. ホーム画面", "html": (
                "<p>9 つの機能ボタン:</p>"
                "<p class='manual-pills'>モーター特性測定 · モーター慣らし · モーターテスト · 履歴記録 · AI モーター健康管理(Pro)· ベアリング抵抗測定 · ブラシ接触安定測定 · グローバルデータ庫 · システム設定</p>"
                "<p>タイトルに <code>MotorLab M1</code> または <code>MotorLab PRO</code> を表示。</p>"
            )},
            {"id": "charexp", "t": "4. モーター特性測定", "html": (
                "<p class='manual-intro'>モーターの特性パラメータと損失を全自動で測定 —— <b>参考データのみ、採点・ランキングなし</b>。同型モーターを比較して自分で判断します。約 1〜2 分、動作は穏やかで、新品の未慣らしモーターにも安心。</p>"
                "<p><b>操作</b>:ホーム →「モーター特性測定」→ 方向を選択(初期は正転)→「測定開始」→ 全自動、測定中はモーターに触れない → 完了するとデータ表を表示。</p>"
                "<p><b>データの見方(表内の各項目に方向を明記)</b>:</p>"
                "<ul>"
                "<li><b>★ Km(品質係数)</b>:<b>高いほど良い</b> —— モーター選別の最重要指標。</li>"
                "<li><b>★ T_loss(損失トルク)/ I0</b>:同回転数で<b>低いほど良い</b>。</li>"
                "<li><b>Ke(磁気強度)</b>:絶対的な良し悪しはなし —— 数値が近いモーター同士の比較で意味を持つ(高め=トルク寄り、低め=回転寄り)。</li>"
                "<li><b>R(内部抵抗)</b>:低いほど良い。</li>"
                "<li><b>損失フィット R² / Ke ドリフト</b>:データ品質の指標(R² が 1 に近く、ドリフトが小さいほど信頼できる)。</li>"
                "</ul>"
                "<p><b>推奨の使い方</b>:新品ロットを 1 個ずつ測定 → ★Km と ★T_loss で体質の良い個体を選んでから慣らしに投入(慣らし工数を節約);慣らし後に<b>同じ個体を再測定</b>して対照 —— 損失系は低下(慣らし効果)、Ke / R はほぼ不変のはず。</p>"
                "<div class='manual-note'><b>注意</b>:測定失敗(モーター未起動 / ロックインのタイムアウト / 過電流)は理由を表示、再試行すれば OK;再現性確認のため 2 回測定を推奨。</div>"
            )},
            {"id": "breakin", "t": "5. モーター慣らし", "html": (
                "<p class='manual-intro'>低速で長時間運転し、ブラシと整流子を最適な接触に馴染ませます。<b>10 段階(a〜j)</b>、初期設定で約 5 時間。</p>"
                "<p><b>操作</b>:ホーム →「モーター慣らし」→ <b>モーター型番</b>(16 種プルダウン)を選択 + <b>備考</b>(任意、40 字以内)を入力 → 10 段階のパラメータを確認(数値欄をタップして編集、変更は自動適用)→「開始」。</p>"
                "<p>各段階の流れ:ソフトスタート → 運転中 → ソフトストップ → 冷却中 → 次の段階。すべて完了 → ビープ 3 回 → 履歴記録に自動保存。</p>"
                "<p><b>運転中に押せるボタン</b>:</p>"
                "<table class='manual-table'><thead><tr><th>ボタン</th><th>動作</th></tr></thead><tbody>"
                "<tr><td>停止</td><td>ソフトストップ後に終了。記録は「ユーザー中止」</td></tr>"
                "<tr><td>リセット</td><td>最高回転数 / 安定電流のピークをクリア(中断しない)</td></tr>"
                "<tr><td>ホーム</td><td>ホームに戻る。慣らしは<b>バックグラウンドで継続</b></td></tr>"
                "</tbody></table>"
                "<div class='manual-note'><b>注意</b>:運転中は全設定がロック。途中で電源を切らない(データ消失);高温時は自動停止して保存;素早く検証したい場合は各段階の時間を短く。各段階で 電圧 / 方向 / 運転時間 / 冷却時間 / 安定電流許容差 を設定可。</div>"
            )},
            {"id": "test", "t": "6. モーターテスト", "html": (
                "<p class='manual-intro'>単段階のリアルタイム観察。<b>記録には保存されません</b>。</p>"
                "<p>ホーム →「モーターテスト」→ <b>電圧(0.6〜4.0V、初期 1V)/ 運転時間 / 方向 / 安定電流許容差</b> を設定 →「開始」→ リアルタイムデータとグラフを確認、時間で自動停止。スマートモードでは電流が早く安定すると「stable」で終了。</p>"
                "<div class='manual-note'><b>注意</b>:4.0V の上限はモーター保護のため、回避しない;逆転から正転に切り替える前に一度「停止」を押す。</div>"
            )},
            {"id": "records", "t": "7. 履歴記録", "html": (
                "<p class='manual-intro'>慣らしごとの全データを自動保存、最大 <b>50 件</b>。</p>"
                "<p>各件に 名称 / 開始時刻 / 所要時間 / モード / 終了理由 / 最高回転数 / 平均回転数 / 安定電流 を表示。</p>"
                "<table class='manual-table'><thead><tr><th>ボタン</th><th>用途</th></tr></thead><tbody>"
                "<tr><td>表示</td><td>各段階のデータを見る</td></tr>"
                "<tr><td>適用</td><td>10 段階パラメータをワンタップで慣らしページへ</td></tr>"
                "<tr><td>エクスポート</td><td>JSON(再インポート可)または CSV(Excel で開く)をダウンロード</td></tr>"
                "<tr><td>削除</td><td>削除(復元不可)</td></tr>"
                "</tbody></table>"
                "<ul>"
                "<li><b>満杯時(50 件)</b>:管理で「自動上書き」(開始時に最古を削除)または「上書きしない」(初期値。開始がブロックされ手動削除が必要)を選択。</li>"
                "<li><b>インポート</b>:以前エクスポートした JSON を選択(id 重複は上書き)。JSON のみ。各エクスポートには<b>署名検証</b>付き:同一 / 同一ロットの機器は互換、改ざん済みや別ロットのファイルは拒否;ファイル名変更は無関係(内容を検証)。</li>"
                "<li><b>ファイル名</b>:<code>motorlab_&lt;日付&gt;_&lt;時刻&gt;_&lt;型番&gt;[_&lt;備考&gt;]</code>、慣らし開始時刻を使用 → 同一件の再エクスポートはファイル名が一致。</li>"
                "<li>ファームウェア更新 / 工場出荷リセットでも<b>記録は消えません</b>。</li>"
                "</ul>"
            )},
            {"id": "database", "t": "8. グローバル慣らしデータ庫", "html": (
                "<p class='manual-intro'>世界中のプレイヤーと慣らし記録を共有。機器が<b>直接ネット接続</b>して完了し、エクスポートしてサイトへ上げる必要はありません。<b>インターネットのある WiFi</b> が必要(M1 / Pro 両対応)。</p>"
                "<p><b>閲覧 / ダウンロード</b>:ホーム →「グローバルデータ庫」→ 接続後、最新 100 件を表示 → <b>モーター型番 / 国 / 完走状態</b> でリアルタイム絞り込み → 各件を「ダウンロード」(本体に保存)または「ダウンロードして適用」(保存しレシピを慣らしページに適用)。</p>"
                "<p><b>自分の記録を共有</b>:履歴記録 → 1 件を開く → 詳細ページ下部「グローバルデータ庫に共有」→ 確認ダイアログが<b>公開される項目を明示</b>(型番 / 備考 / 共有者 / 国 / 全データ;名前を入力していれば実名表示の警告)→ アップロード確定。アップロード済みなら「この記録は既にデータ庫にあります」と表示(エラーではありません)。</p>"
                "<div class='manual-note'><b>注意</b>:ダウンロードした記録は署名検証されます;アップロードは公開への同意を意味します。削除は <b>motorlab.tw@gmail.com</b> へ;インターネットのない WiFi に接続すると「サーバーに接続できません」と表示。</div>"
            )},
            {"id": "ai", "t": "9. AI モーター健康管理(Pro)", "html": (
                "<p class='manual-intro'>モーターごとに健康指紋を作成し、定期的に再測定・比較して 0〜100 点とアドバイスを提示。<b>他のモーターとではなく、自分自身と比較</b>します。</p>"
                "<ol>"
                "<li>ホーム →「AI モーター健康管理」→「+ モーター追加」。</li>"
                "<li><b>モーター型番</b>(プルダウン)+ <b>備考</b>(任意)+ <b>開始電圧</b> + <b>電圧間隔</b>(5 点自動選択)を入力。</li>"
                "<li>確認 → 約 <b>2.5 分</b> でベースラインを自動構築。</li>"
                "</ol>"
                "<p>以降、各カードで <b>フル検査</b>(約 2.5 分、最も正確)または <b>クイック検査</b>(約 1.5 分、±5%)を実行可。結果ページにスコア、等級(Optimal / Acceptable / Warning / Critical)、トレンドグラフ、5 項目の指標、テキストアドバイスを表示。</p>"
                "<div class='manual-note'><b>注意</b>:1 モーターにつき履歴最大 50 回、1 台につき 20 モーターまで;検査中は電源を切らず他のボタンも押さない;高温時は自動中止;M1 ではボタンがグレー(タップでアップグレード案内)。</div>"
            )},
            {"id": "bearing", "t": "10. ベアリング抵抗測定", "html": (
                "<p class='manual-intro'>ベアリングの滑らかさを測定、全エディションで利用可。<b>完全停止までの時間が長いほどベアリングは滑らか</b>。</p>"
                "<p>ホーム →「ベアリング抵抗測定」→ テスト電圧(<b>2.4V または 3V</b>)を選択 →「測定開始」→ 機器がその電圧まで加速 → 安定回転数を 5 秒保持 → <b>そのまま電源を切断(ブレーキなし)</b> → 完全停止まで計測 → <b>完全停止時間</b> を表示。</p>"
                "<div class='manual-note'><b>注意</b>:無負荷のモーターは慣性が小さいため、本測定は<b>時間のみ表示し良否評価は行いません</b>。同じモーターの異なる時期、または異なるモーターの時間を相互比較してください;回転センサーが正常である必要;再現性確認のため 2〜3 回測定を推奨。</div>"
            )},
            {"id": "brush", "t": "11. ブラシ接触安定測定", "html": (
                "<p class='manual-intro'>ブラシ接触が均一かを約 35 秒で測定、全エディション対応。<b>接触不均一 → 電流のばらつき → CV 上昇</b>。</p>"
                "<p>ホーム →「ブラシ接触安定測定」→「測定開始」を押すだけ(<b>軸の手動回転は不要</b>)。手順は <b>1V</b> 固定:電圧を 10 秒以内で 0 から 1V まで緩やかに昇圧 → 1V を 5 秒保持 → 1V で電流を 20 秒サンプリング → <b>電流変異係数 CV%</b> を表示。</p>"
                "<p><b>CV% の見方</b>:CV は固定電圧下での電流のばらつき度で、<b>相対比較のツールであり絶対的な良否ラインはありません</b>(モーター型番ごとに元々異なる)。次のように使います:</p>"
                "<ul>"
                "<li>同じモーターの <b>慣らし前 vs 慣らし後</b>:CV 低下 = ブラシが馴染み接触改善。</li>"
                "<li>同じモーターの <b>長期追跡</b>:CV が徐々に上昇 = ブラシ摩耗 / 整流子の汚れ。</li>"
                "<li><b>モーター A vs B</b> の相対比較。</li>"
                "</ul>"
                "<div class='manual-note'><b>注意</b>:1V 固定・手順固定だからこそ、回・モーターをまたいで公平に比較できます;再現性確認のため 2〜3 回測定を推奨。</div>"
            )},
            {"id": "settings", "t": "12. システム設定", "html": (
                "<p class='manual-intro'>システム運転中、このページは「ホーム」のみ操作可、他はロックされます。</p>"
                "<table class='manual-table'><tbody>"
                "<tr><th>ユーザー設定</th><td>名前 / 国(32 字以内、初期値 <code>--</code>)。各記録に出処として書き込まれます。既存の記録には反映されません。</td></tr>"
                "<tr><th>WiFi 設定</th><td>ホットスポット名 / パスワード(8〜63 字)を変更 → 保存後に機器が再起動、新しいホットスポットへ再接続。パスワードを忘れた場合は第 14 節参照。</td></tr>"
                "<tr><th>言語</th><td>中文 / English / 日本語 を切替(初期値は中国語)。「確定」を押すと<b>システムが再起動</b>してクリーンに読み込み(約 10 秒、ページは自動再読込);運転中の切替はページ再読込のみで処理は中断しません。</td></tr>"
                "<tr><th>慣らしモード</th><td>運転時間のみ / スマート安定電流判定(時間到達<b>または</b>電流が早く安定したら次段階へ)。</td></tr>"
                "<tr><th>温度校正</th><td>表示と実際にずれがある場合に補正を追加(±20°C)。</td></tr>"
                "<tr><th>高温ロック</th><td>高温ロック温度を設定(初期 50°C、範囲 25〜60°C)。現在温度が設定値より 5°C 以上高い状態が 10 秒続くと高温ロックに入る(停止、リセットで解除)。ブロック内に現在温度も表示。</td></tr>"
                "<tr><th>平均回転数設定</th><td>許容差(隣接 2 秒の回転数差)、プルダウン 120〜600 RPM、<b>初期 240</b>。許容差が大きいほど安定と判定しやすいが反応は鈍め;モーターが不安定なら大きめに。</td></tr>"
                "<tr><th>ソフトスタート</th><td>直線的な昇圧(電圧を 0 から 5 秒で目標電圧まで滑らかに、ソフトストップと同じ挙動)、<b>調整パラメータなし</b>。出力電圧は校正済みで、始動トルクの設定は不要。</td></tr>"
                "<tr><th>ライセンス取得</th><td>M1 を Pro に。下記参照。</td></tr>"
                "<tr><th>ソフトウェア更新</th><td>自宅 WiFi 経由で最新ファームを自動取得。下記参照。</td></tr>"
                "<tr><th>RGB ステータスライト</th><td>デュアルライト(内蔵 / パネル)の出力位置 + 明るさ(0〜100%)+ 5 つの状態スタイル。下記参照。</td></tr>"
                "<tr><th>エンジニアリングモード</th><td>パスワード保護の高度な校正とオフライン更新(一般ユーザーには不要)。</td></tr>"
                "<tr><th>WiFi リスト</th><td>外部 WiFi を最大 8 組記憶;「リストを消去」は機器の譲渡用(Pro ライセンスには影響しません)。</td></tr>"
                "</tbody></table>"
                "<p><b>ライセンス取得(M1 → Pro)</b>:システム設定 →「ライセンス取得」→ 自宅 WiFi を選んで接続 → 機器が購入を自動検証 → 未購入なら QR コードを表示 → <b>別のインターネット接続デバイスでスキャンして決済</b> → 機器が 10 秒ごとに自動照会、決済成功で解除。全体で約 1〜3 分、<b>キーの手動入力は不要</b>、10 分でタイムアウトしたら再試行可。返金後は「ライセンス再取得」と表示。</p>"
                "<p><b>ソフトウェア更新</b>:システム設定 →「更新を確認」→ WiFi を選択 → 新版があれば自動ダウンロード・書き込み(進捗 100% まで)→ 自動再起動・ページ自動再読込。<b>途中で電源 / ブラウザを閉じない</b>(更新中の電源断は保護で旧版へ自動復帰);ダウンロード約 1.6MB、自宅 WiFi で約 5〜10 秒。</p>"
                "<p><b>RGB ステータスライト</b>:</p>"
                "<ul>"
                "<li><b>出力位置</b>:パネル / パネル+内蔵(初期)/ 内蔵、タップで即時切替。</li>"
                "<li><b>明るさ</b>:スライダーを動かす →「プレビュー」(保存せず 5 秒お試し、繰り返し可)→ 良ければ「適用」で保存。(2 段階なのは連続書き込みによる接続のもたつき防止のため。)</li>"
                "<li><b>状態スタイル(5 組)</b>:上から下へ走査し、最初に一致した状態を表示。状態(なし / 高温 / 冷却 / 待機 / 運転)× 色相 × モード(常時点灯 / 点滅 / 呼吸)× 間隔 / 周期;同じく「プレビュー / 適用」の 2 段階。</li>"
                "</ul>"
                "<p><b>エンジニアリングモード</b>:パスワードが必要(3 回間違えると 60 秒ロック、10 分無操作で自動ログアウト)。</p>"
            )},
            {"id": "safety", "t": "13. 安全と保護", "html": (
                "<table class='manual-table'><thead><tr><th>機構</th><th>トリガー / 動作</th></tr></thead><tbody>"
                "<tr><td>高温保護</td><td>2 つのトリガー:① 温度センサー警報;② 現在温度が「高温ロック温度」設定値より 5°C 以上高い状態が 10 秒継続(システム設定参照)。いずれかで → 直ちにモーター停止 + ビープ 5 回 + ロック。ロック中はステータスバー / フラグ / ステータスライトが高温を表示し続け、ホームは「慣らし / テスト」のみ、操作画面は「リセット / ホーム」のみ操作可。<b>温度が下がってもリセットを押すまで解除されません</b>(高温のままリセットすると再ロック、先に冷却を)。</td></tr>"
                "<tr><td>ソフトスタート / ソフトストップ</td><td>始動は 5 秒の直線的な昇圧(0V→目標電圧)、停止は 3 秒の直線的な立下げ。電流の急増と機械的衝撃を防止。</td></tr>"
                "<tr><td>電流上限</td><td>測定上限は固定 4A。超過分は読値が頭打ち(停止はしないが、長時間の高電流は高温を誘発する場合あり)。</td></tr>"
                "<tr><td>起動ロック</td><td>起動後 30 秒以内に 3 回連続クラッシュ → 自動的に前バージョンのファームへ復帰。</td></tr>"
                "</tbody></table>"
            )},
            {"id": "reset", "t": "14. 工場出荷リセット(レスキュー)", "html": (
                "<p><b>用途</b>:WiFi 名 / パスワードを忘れたとき、ホットスポットを <code>MotorTester</code> / <code>12345678</code> に戻します。</p>"
                "<p><b>方法</b>:機器の「工場出荷リセット」接点を 3.3V に短絡(または対応ボタンを押す)<b>5 秒間保持</b> → ビープ 10 回 → 自動再起動。</p>"
                "<div class='manual-note'><b>WiFi ホットスポット名とパスワードのみリセット</b>。以下はすべて保持:慣らしパラメータ / 各種校正と設定 / Pro ライセンス / 履歴記録 / モーター指紋 / RGB 設定 / 記憶済み外部 WiFi。</div>"
            )},
            {"id": "faq", "t": "15. よくある質問", "html": (
                "<table class='manual-table'><thead><tr><th>問題</th><th>対処</th></tr></thead><tbody>"
                "<tr><td>起動音が鳴らない</td><td>電源 5V とブザー配線を確認</td></tr>"
                "<tr><td>Web UI が操作中に無反応</td><td>機器の WiFi(MotorTester)に接続されているか確認;端末がインターネット WiFi に自動切替している場合あり → 機器のホットスポットに再接続してページを再読込</td></tr>"
                "<tr><td>接続できるがページが開かない</td><td><code>http://</code>(https ではない)を確認、モバイルデータをオフ、強制再読込(Ctrl+Shift+R)</td></tr>"
                "<tr><td>「適用中…」のまま</td><td>多くは WiFi 不安定。ページを再読込すれば OK(内蔵 8 秒監視が赤字で通知)</td></tr>"
                "<tr><td>慣らし途中でモーター交換</td><td>「停止」→ 交換 → 再度「開始」(新たな実行は新規記録)</td></tr>"
                "<tr><td>ライセンス取得が接続で止まる</td><td>自宅 WiFi パスワード誤り / 外部ネットなし / 電波弱 → 再入力または WiFi 変更</td></tr>"
                "<tr><td>Pro 返金後</td><td>次回オンライン再検証時に<b>自動的に M1 へ戻る</b>;再購入は「ライセンス再取得」</td></tr>"
                "<tr><td>赤い「AP パスワードが初期値のまま」バナー</td><td>WiFi 設定でパスワードを変更</td></tr>"
                "<tr><td>他人に譲る</td><td>エンジニアリングモードで校正リセット → WiFi リスト消去 →(任意)記録消去 / モーター削除 → 工場出荷リセット。Pro ライセンスは機器に紐づき譲渡不可</td></tr>"
                "<tr><td>更新失敗で文鎮化する?</td><td>しません。デュアルファーム領域の自動復帰 + 署名検証 + USB レスキュー</td></tr>"
                "<tr><td>待機中に電源を抜いてよい?</td><td>可。モーター完全停止、「適用中」なし、更新中でない状態が望ましい</td></tr>"
                "</tbody></table>"
            )},
            {"id": "led", "t": "16. ステータスランプ", "html": (
                "<p>初期設定(「RGB ステータスライト」で変更可):</p>"
                "<table class='manual-table'><thead><tr><th>システム状態</th><th>初期</th><th>意味</th></tr></thead><tbody>"
                "<tr><td>高温ロック</td><td>赤点滅</td><td>高温保護が作動。冷却して「リセット」を押す</td></tr>"
                "<tr><td>冷却中</td><td>黄点灯</td><td>段階間の冷却、モーター静止</td></tr>"
                "<tr><td>待機</td><td>青呼吸</td><td>コマンド待ち</td></tr>"
                "<tr><td>運転中</td><td>緑呼吸</td><td>慣らし / テスト / 検査中</td></tr>"
                "<tr><td>消灯</td><td>—</td><td>一致なしまたは全消灯</td></tr>"
                "</tbody></table>"
                "<p class='manual-contact'><b>問題報告</b>の際は次を併せてご提供ください:ファームウェアバージョン(システム設定 → ソフトウェア更新)、エディション(ホームの M1 / PRO)、画面のスクリーンショット、運転中かどうか、再現手順。サポート:<b>motorlab.tw@gmail.com</b></p>"
            )},
        ],
    },
}


def build_manual_page(man_cfg, lang, src_html, i18n):
    """產生 /docs/user-manual/ 使用者手冊頁(左目錄 + 右章節,沿用 .guide-page 殼)。"""
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    ui = UI_STRINGS[lang]
    s = man_cfg["i18n"][lang]
    secs = man_cfg["sections"][lang]
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    page_url = f"{SITE}{lang_prefix}/docs/{man_cfg['slug']}/"
    home_url = f"{SITE}{lang_prefix}/"

    soup.html["lang"] = cfg["html_lang"]

    for sc in soup.find_all("script", {"type": "application/ld+json"}):
        sc.decompose()
    for tag in soup.find_all("link", {"rel": "alternate"}):
        tag.decompose()

    footer_el = soup.find("footer")
    footer_extracted = footer_el.extract() if footer_el else None
    _fix_footer_verify(footer_extracted, lang)

    if soup.title:
        soup.title.string = s["title"]

    def set_meta(attr, attr_val, content):
        tag = soup.find("meta", {attr: attr_val})
        if tag:
            tag["content"] = content

    set_meta("name", "description", s["description"])
    kw = s["keywords"]
    if lang != "en" and "en" in man_cfg["i18n"]:
        kw = kw + ", " + man_cfg["i18n"]["en"]["keywords"]
    set_meta("name", "keywords", kw)
    set_meta("http-equiv", "Content-Language", cfg["html_lang"])
    set_meta("property", "og:type", "article")
    set_meta("property", "og:url", page_url)
    set_meta("property", "og:title", s["title"])
    set_meta("property", "og:description", s["description"])
    set_meta("property", "og:locale", cfg["og_locale"])
    set_meta("name", "twitter:title", s["title"])
    set_meta("name", "twitter:description", s["description"])

    canon = soup.find("link", {"rel": "canonical"})
    if canon:
        canon["href"] = page_url

    head = soup.head
    for hl_lang, hl_cfg in LANGS.items():
        hl_prefix = "" if hl_lang == "zh" else f"/{hl_lang}"
        head.append(soup.new_tag("link", attrs={
            "rel": "alternate", "hreflang": hl_cfg["html_lang"],
            "href": f"{SITE}{hl_prefix}/docs/{man_cfg['slug']}/"
        }))
    head.append(soup.new_tag("link", attrs={
        "rel": "alternate", "hreflang": "x-default", "href": f"{SITE}/docs/{man_cfg['slug']}/"
    }))

    # JSON-LD: TechArticle + BreadcrumbList
    article_ld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": s["h1"],
        "description": s["description"],
        "inLanguage": cfg["html_lang"],
        "url": page_url,
        "author": {"@type": "Organization", "name": "MotorLab Team"},
        "publisher": {"@type": "Organization", "name": "MotorLab.tw", "url": SITE + "/"},
        "isPartOf": {"@type": "WebSite", "name": "MotorLab.tw", "url": SITE + "/"},
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": ui["bc_home"], "item": home_url},
            {"@type": "ListItem", "position": 2, "name": s["breadcrumb"], "item": page_url},
        ],
    }
    for data in (article_ld, breadcrumb_ld):
        sc = soup.new_tag("script", attrs={"type": "application/ld+json"})
        sc.string = json.dumps(data, ensure_ascii=False, indent=2)
        head.append(sc)

    soup.body.clear()
    soup.body["class"] = "guide-page"

    nav_html = (
        f'<nav class="guide-nav"><div class="container">'
        f'<a class="brand" href="{home_url}"><span>MotorLab<span class="tag">.tw</span></span></a>'
        f'<a class="back-link" href="{home_url}">{ui["back_home"]}</a>'
        f'</div></nav>'
    )
    soup.body.append(BeautifulSoup(nav_html, "html.parser"))

    main_el = soup.new_tag("main")

    bc_html = (
        f'<nav class="breadcrumb" aria-label="Breadcrumb">'
        f'<a href="{home_url}">{ui["bc_home"]}</a><span class="sep">/</span>'
        f'<span class="current">{s["breadcrumb"]}</span></nav>'
    )
    hero_html = (
        f'<section class="lab-hero"><div class="container">{bc_html}'
        f'<div class="lab-eyebrow">{s["eyebrow"]}</div>'
        f'<h1 class="lab-hero-title">{s["h1"]}</h1>'
        f'<p class="lab-hero-p">{s["lead"]}</p>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(hero_html, "html.parser"))

    # 目錄 + 章節:兩欄(.manual-layout)
    toc_items = "".join(f'<li><a href="#{x["id"]}">{x["t"]}</a></li>' for x in secs)
    sections_html = "".join(
        f'<section class="manual-section" id="{x["id"]}">'
        f'<h2>{x["t"]}</h2>{x["html"]}</section>'
        for x in secs
    )
    body_html = (
        f'<section class="lab-section"><div class="container">'
        f'<div class="manual-layout">'
        f'<aside class="manual-toc"><div class="manual-toc-label">{s["toc_label"]}</div>'
        f'<ul>{toc_items}</ul></aside>'
        f'<div class="manual-body">{sections_html}'
        f'<p class="manual-fwnote">{s["fw_note"]}</p>'
        f'</div></div></div></section>'
    )
    main_el.append(BeautifulSoup(body_html, "html.parser"))

    soup.body.append(main_el)
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
    print("=== 文章分頁(/{type}/<slug>/,D23 分類)===")
    for guide in GUIDES:
        article_type = guide.get("type", "guides")
        for lang in ("zh", "en", "ja"):
            if lang not in guide["i18n"]:
                continue  # 該語言尚未撰寫該篇 → 跳過
            slug = guide["slug"]
            lang_prefix = "" if lang == "zh" else f"{lang}/"
            out_dir = f"{lang_prefix}{article_type}/{slug}"
            out_path = f"{out_dir}/index.html"
            os.makedirs(out_dir, exist_ok=True)
            html_out = build_guide_page(slug, lang, src_html, i18n, guide)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html_out)
            size = len(html_out.encode("utf-8"))
            print(f"  ✅ {out_path:<55} {size:>9,} bytes  ({lang})")

    print()
    print("=== Hub 索引頁(/{hub_slug}/,D27 curation)===")
    for hub in HUBS:
        for lang in ("zh", "en", "ja"):
            if lang not in hub["i18n"]:
                continue
            lang_prefix = "" if lang == "zh" else f"{lang}/"
            out_dir = f"{lang_prefix}{hub['slug']}"
            out_path = f"{out_dir}/index.html"
            os.makedirs(out_dir, exist_ok=True)
            html_out = build_hub_page(hub, lang, src_html, i18n)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html_out)
            size = len(html_out.encode("utf-8"))
            print(f"  ✅ {out_path:<45} {size:>9,} bytes  ({lang})")

    print()
    print("=== 商品外觀頁(/system/<slug>/,D23 system 分類)===")
    sys_type = SYSTEM.get("type", "system")
    for lang in ("zh", "en", "ja"):
        if lang not in SYSTEM["i18n"]:
            continue
        lang_prefix = "" if lang == "zh" else f"{lang}/"
        out_dir = f"{lang_prefix}{sys_type}/{SYSTEM['slug']}"
        out_path = f"{out_dir}/index.html"
        os.makedirs(out_dir, exist_ok=True)
        html_out = build_system_page(SYSTEM, lang, src_html, i18n)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_out)
        size = len(html_out.encode("utf-8"))
        print(f"  ✅ {out_path:<45} {size:>9,} bytes  ({lang})")

    print()
    print("=== 全球磨合資料平台(/lab/,GAS 後端)===")
    for lang in ("zh", "en", "ja"):
        if lang not in LAB["i18n"]:
            continue
        lang_prefix = "" if lang == "zh" else f"{lang}/"
        out_dir = f"{lang_prefix}lab"
        out_path = f"{out_dir}/index.html"
        os.makedirs(out_dir, exist_ok=True)
        html_out = build_lab_page(LAB, lang, src_html, i18n)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_out)
        size = len(html_out.encode("utf-8"))
        print(f"  ✅ {out_path:<45} {size:>9,} bytes  ({lang})")
    if LAB["api_url"].startswith("PUT_"):
        print("  ⚠ LAB['api_url'] 尚未設定 — /lab/ 上線前要填入 GAS Web App URL")

    print()
    print("=== 正版查驗(/verify/,GAS verify_public / JSONP)===")
    for lang in ("zh", "en", "ja"):
        if lang not in VERIFY["i18n"]:
            continue
        lang_prefix = "" if lang == "zh" else f"{lang}/"
        out_dir = f"{lang_prefix}verify"
        out_path = f"{out_dir}/index.html"
        os.makedirs(out_dir, exist_ok=True)
        html_out = build_verify_page(VERIFY, lang, src_html, i18n)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_out)
        size = len(html_out.encode("utf-8"))
        print(f"  ✅ {out_path:<45} {size:>9,} bytes  ({lang})")

    print()
    print("=== 使用者手冊(/docs/user-manual/,D23 docs 分類)===")
    man_type = MANUAL.get("type", "docs")
    for lang in ("zh", "en", "ja"):
        if lang not in MANUAL["i18n"]:
            continue
        lang_prefix = "" if lang == "zh" else f"{lang}/"
        out_dir = f"{lang_prefix}{man_type}/{MANUAL['slug']}"
        out_path = f"{out_dir}/index.html"
        os.makedirs(out_dir, exist_ok=True)
        html_out = build_manual_page(MANUAL, lang, src_html, i18n)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_out)
        size = len(html_out.encode("utf-8"))
        print(f"  ✅ {out_path:<45} {size:>9,} bytes  ({lang})")

    print()
    print("完成!3 個語言版本 + 教學分頁 + 3 個 hub 索引頁 + 商品外觀頁 + /lab/ + /verify/ + 使用者手冊已產生。")
    print("=" * 55)


if __name__ == "__main__":
    main()

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
import html

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
        "description": "MotorLab — 專為 Mini 4WD® 玩家打造的精密馬達磨合測試系統。十五大專業功能:磨合三模式、馬達特性量測、AI 健康管理、AI 扭力預測、軸承阻力、CV 電刷穩定診斷、三層安全保護、高溫鎖定、線上更新、田宮馬達規格速查。讓馬達調校可量化。",
        "og_title": "MotorLab — Mini 4WD® 馬達磨合測試系統",
        "og_desc": "為每一顆 Mini 4WD® 馬達建立可量化的健康指紋。十五大專業功能:磨合三模式、馬達特性量測、AI 健康管理、AI 扭力預測、軸承阻力分析、電刷穩定診斷、三層安全保護、高溫鎖定、田宮馬達規格速查。",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "為每一顆 Mini 4WD® 馬達建立可量化的健康指紋",
        "ld_org_desc": "為 Mini 4WD® 玩家打造的精密馬達磨合與測試系統研發工作室",
        "ld_site_desc": "MotorLab — Mini 4WD® 馬達磨合與精密測試系統官方網站",
        "ld_app_desc": "Mini 4WD® 馬達磨合與精密測試系統。內建十階段可程式化磨合、AI 智慧馬達健康管理、AI 智慧扭力預測、軸承阻力測試、電刷接觸穩定診斷。",
    },
    "en": {
        "title": "MotorLab — Mini 4WD® Motor Break-in & Diagnostics System",
        "description": "MotorLab — precision Mini 4WD® motor break-in & diagnostics. Motor characterization, three-mode break-in, AI health management, bearing resistance.",
        "og_title": "MotorLab — Mini 4WD® Motor Break-in & Test System",
        "og_desc": "Build a measurable health fingerprint for every Mini 4WD® motor. Fifteen professional tools: motor characterization, three-mode break-in, AI health management, AI torque prediction, bearing resistance analysis, brush stability diagnostics, triple-layer safety protection, overheat lock and a global break-in data library.",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "Build a measurable health fingerprint for every Mini 4WD® motor",
        "ld_org_desc": "An R&D studio building precision motor break-in and testing systems for Mini 4WD® racers.",
        "ld_site_desc": "Official site of the MotorLab Mini 4WD® motor break-in and precision testing system.",
        "ld_app_desc": "Mini 4WD® motor break-in and precision testing system. Includes 10-stage programmable break-in, AI motor health management, AI torque prediction, bearing resistance analysis and brush contact stability diagnostics.",
    },
    "ja": {
        "title": "MotorLab — Mini 4WD® モーター慣らし・テストシステム | 精密モーター診断スタジオ",
        "description": "MotorLab — Mini 4WD® プレイヤー向けの精密モーター慣らし・診断システム。モーター特性測定、慣らし 3 モード、AI 健康管理、ベアリング抵抗、CV ブラシ安定診断、高温保護を搭載。",
        "og_title": "MotorLab — Mini 4WD® モーター慣らし・テストシステム",
        "og_desc": "すべての Mini 4WD® モーターに定量化できる健康指紋を。15 のプロ機能:モーター特性測定、10 段階慣らし、AI 健康管理、AI トルク予測、ベアリング抵抗解析、ブラシ安定診断、三層安全保護、高温ロック、グローバル慣らしデータ庫。",
        "tw_title": "MotorLab — Mini 4WD® Motor Lab",
        "tw_desc": "すべての Mini 4WD® モーターに定量化できる健康指紋を",
        "ld_org_desc": "Mini 4WD® プレイヤーのための精密モーター慣らし・測定システムを開発するスタジオ。",
        "ld_site_desc": "MotorLab — Mini 4WD® モーター慣らし・精密測定システムの公式サイト。",
        "ld_app_desc": "Mini 4WD® モーター慣らし・精密測定システム。慣らし 3 モード、AI モーター健康管理、AI トルク予測、ベアリング抵抗解析、ブラシ接触安定診断を内蔵。",
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
        "updated": "2026-07-23",
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
        "updated": "2026-07-22",
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
        "updated": "2026-07-17",
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
    # ---------- g15:導電油磨馬達(methodology hub)----------
    {
        "slug": "conductive-oil-motor-break-in",
        "key": "g15",
        "published": "2026-07-17",
        "updated": "2026-07-17",
        "type": "guides",
        "i18n": {
            "zh": {
                "title": "導電油磨馬達真的有效嗎?轉速升高的真相 | MotorLab",
                "description": "導電油(導電性磨合油)磨馬達,加了轉速立刻上升、聲音變順,真的把馬達磨好了嗎?本文從物理拆解:轉速升高有一部分是碳粉暫時導電的假象,不等於接觸面磨好。持平分析導電油的優缺點、短期與長期差異,以及怎麼判斷馬達真實的磨合狀態。",
                "keywords": "導電油, 導電油 磨馬達, 導電性磨合油, 磨馬達 油, 馬達磨合油, 磨馬達, 馬達磨合, 迷你四驅車 馬達, 導電油 有效嗎, MotorLab",
                "breadcrumb": "導電油磨馬達",
                "h1_for_ld": "導電油磨馬達真的有效嗎?轉速升高背後的物理真相",
            },
            "en": {
                "title": "Does Conductive Oil Really Help Motor Break-In? | MotorLab",
                "description": "Conductive oil spikes RPM instantly \u2014 but part of that jump is carbon bridging contacts, not a better contact face. What's real and what's illusion, fairly.",
                "keywords": "conductive oil, conductive break-in oil, motor break-in oil, Mini 4WD motor oil, does conductive oil work, motor break-in, brush commutator, MotorLab",
                "breadcrumb": "Conductive Oil",
                "h1_for_ld": "Does Conductive Oil Really Break In a Motor? The Physics Behind the RPM Jump",
            },
            "ja": {
                "title": "導電オイルは慣らしに効く?回転数上昇の正体 | MotorLab",
                "description": "導電オイル(導電性慣らしオイル)でモーター慣らしをすると回転数が一気に上がり音も滑らかに。でも本当に慣らせている?物理で分解すると、その回転数上昇の一部はカーボン粉が接点を一時的に導通させる見かけで、接触面が良くなったわけではない。導電オイルの利点と欠点、短期と長期、そして本当の慣らし状態の見方を公平に解説。",
                "keywords": "導電オイル, モーター慣らしオイル, 慣らしオイル, ミニ四駆 モーター慣らし, 導電オイル 効果, モーター オイル, ブラシ コミュテーター, MotorLab",
                "breadcrumb": "導電オイル",
                "h1_for_ld": "導電オイルは本当にモーターを慣らせる?回転数上昇の物理的な正体",
            },
        },
    },
    {
        "slug": "motor-slow-causes-fixes",
        "key": "g16",
        "published": "2026-07-17",
        "updated": "2026-07-17",
        "type": "guides",
        "i18n": {
            "zh": {
            "title": "馬達變慢、沒力了?5 個原因與對策(先別急著換) | MotorLab",
            "description": "馬達突然變慢、沒力,不一定是壽命到了。本文把「馬達變慢」拆成 5 個常見原因 —— 電池、髒污、潤滑、退磁、電刷磨損,分清可逆與不可逆,教你用一套快速流程判斷該清、該養、還是該退役,別急著花錢換新。",
            "keywords": "馬達變慢, 馬達沒力, 馬達 轉速下降, 馬達 變慢 原因, 迷你四驅車 馬達 變慢, 馬達 退磁, 四驅車 馬達, MotorLab",
            "breadcrumb": "馬達變慢原因",
            "h1_for_ld": "馬達變慢、沒力了?5 個原因與對策",
            },
            "en": {
            "title": "Mini 4WD Motor Got Slow? 5 Causes and Fixes | MotorLab",
            "description": "A Mini 4WD motor that suddenly got slow is not always worn out. This breaks slow motor into 5 common causes — battery, dirt, lube, demagnetization, brush wear — reversible vs not, with a quick flow to decide: clean, maintain, or retire.",
            "keywords": "Mini 4WD motor slow, motor lost power, motor RPM drop, why motor got slow, motor demagnetization, Mini 4WD motor, MotorLab",
            "breadcrumb": "Motor Got Slow",
            "h1_for_ld": "Mini 4WD Motor Got Slow? 5 Causes and Fixes",
            },
            "ja": {
            "title": "ミニ四駆モーターが遅くなった?5 つの原因と対処 | MotorLab",
            "description": "モーターが急に遅く・パワーダウンしたのは寿命とは限りません。「遅くなった」を 5 つの原因 —— 電池・汚れ・潤滑・減磁・ブラシ摩耗 —— に分解し、可逆か不可逆かを見分けて、洗う・整備する・引退のどれかを素早く判断する流れを解説。すぐ買い替える前に。",
            "keywords": "ミニ四駆 モーター 遅い, モーター パワーダウン, モーター 回転数 低下, モーター 遅くなった 原因, モーター 減磁, ミニ四駆 モーター, MotorLab",
            "breadcrumb": "モーターが遅い",
            "h1_for_ld": "ミニ四駆モーターが遅くなった?5 つの原因と対処",
            },
        },
    },
    # ---------- g17:智慧磨合宣傳頁(磨合何時該停,12 小時過磨實驗)----------
    #             = 效能對比「15 款馬達同條件實測」系列起始章
    {
        "slug": "when-to-stop-motor-break-in",
        "key": "g17",
        "published": "2026-07-23",
        "updated": "2026-07-23",
        "type": "benchmarks",
        "i18n": {
            "zh": {
                "title": "馬達越磨越快,其實已磨壞?12 小時實測:磨合何時該停 | MotorLab",
                "description": "馬達磨合要磨多久?我們把一顆 Mach-Dash PRO 連續磨 12 小時、超過 550 萬轉:收益一小時就領完,繼續磨轉速反而越磨越快——那是磁力流失的假象,體質不可逆下滑。智慧磨合偵測穩態自動停,替你停在剛剛好。",
                "keywords": "馬達磨合 何時停, 磨合 磨多久, 過度磨合, 馬達 過磨, 智慧磨合, 田宮 15 款馬達 實測, 迷你四驅車 馬達磨合, MotorLab",
                "breadcrumb": "磨合何時該停",
                "h1_for_ld": "轉速越磨越快,其實已磨壞了?12 小時連續磨給你看",
            },
            "en": {
                "title": "Motor Faster the Longer You Run It? When to Stop Break-In: a 12-Hour Test | MotorLab",
                "description": "How long should motor break-in run? We ground one Mach-Dash PRO for 12 straight hours — over 5.5 million revolutions. The gains were banked within an hour; grinding on made RPM climb, an illusion of fading magnets while the motor irreversibly declined. Smart break-in detects steady state and stops at just right.",
                "keywords": "when to stop motor break-in, how long to break in mini 4wd motor, over break-in motor, motor break-in time, smart break-in, tamiya 15 motor test, MotorLab",
                "breadcrumb": "When to Stop Break-In",
                "h1_for_ld": "Faster the Longer You Run It — Or Already Damaged? A 12-Hour Nonstop Break-In",
            },
            "ja": {
                "title": "ミニ四駆 モーター慣らし 失敗の正体:寿命まで 12 時間回した実測 | MotorLab",
                "description": "モーター慣らしの失敗で最も多いのが「回しすぎ」。Mach-Dash PRO 1 個を寿命が尽きるまで連続 12 時間・550 万回転回した実測:利得は最初の 1 時間で出切り、その後は回転数だけが上がる——磁力低下の錯覚で、体質は不可逆に低下。スマート慣らしは定常状態を検出し、ちょうどいいところで自動停止します。",
                "keywords": "ミニ四駆 モーター慣らし 失敗, ミニ四駆 モーター 寿命, ミニ四駆 モーター 死亡, ミニ四駆 慣らし 時間, モーター 回しすぎ, スマート慣らし, タミヤ 15 機種 実測, MotorLab",
                "breadcrumb": "慣らしの止めどき",
                "h1_for_ld": "回すほど速くなるのは慣らし失敗のサイン?寿命まで 12 時間回してみた",
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
        "include": ["g1", "g2", "g4", "g16"],
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
        "include": ["g3", "g9", "g17"],
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
        "include": ["g5", "g6", "g7", "g8", "g10", "g11", "g12", "g13", "g14", "g15"],
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
            "f_mode_all": "全部模式",
            "f_mode_v": "電壓模式",
            "f_mode_s": "轉速模式",
            "f_sort": "排序",
            "f_show": "顯示",
            "c_rpm": "最高轉速 R.P.M",
            "c_rpm_avg": "平均轉速 R.P.M",
            "c_current": "穩定值",
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
                "c_current": "穩定值",
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
            "f_mode_all": "All modes",
            "f_mode_v": "Voltage",
            "f_mode_s": "Speed",
            "f_sort": "Sort",
            "f_show": "Show",
            "c_rpm": "Max R.P.M",
            "c_rpm_avg": "Avg R.P.M",
            "c_current": "Stable value",
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
                "c_current": "Stable value",
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
            "f_mode_all": "全モード",
            "f_mode_v": "電圧",
            "f_mode_s": "回転数",
            "f_sort": "並べ替え",
            "f_show": "表示",
            "c_rpm": "最高回転数 R.P.M",
            "c_rpm_avg": "平均回転数 R.P.M",
            "c_current": "安定値",
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
                "c_current": "安定値",
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
    "馬達健康診斷, 洗馬達, 紅二馬達, 黑金剛, 馬達保護, "
    "過流保護, 電流急停, 安全保護機制, "
    "電磁干擾防護, 馬達燒毀防護, "
    "四驅車 馬達磨合, 田宮 馬達磨合, 四驅車 磨合方法"
)
_KW_EN = (
    "MotorLab, Mini 4WD, Hyper Dash, Plasma Dash, "
    "motor break-in, motor test, Tamiya Mini 4WD, "
    "overcurrent protection, motor safety, "
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

    # --- 7g. 內部跨頁連結(hero 的 data-presalelink)改寫成對應語言的 /presale/ ---
    presale_href = f"{lab_prefix}/presale/"
    for a in soup.select("a[data-presalelink]"):
        a["href"] = presale_href
        del a["data-presalelink"]

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
  // 穩定值:轉速模式(drive_mode=1)的穩定值是 mV → 顯示成 V;電壓模式是 mA。
  function fmtStable(it) {
    var v = it.stable_current_overall;
    if (v === "" || v == null || isNaN(v)) return "—";
    v = Number(v);
    if (String(it.drive_mode) === "1") return (v / 1000).toFixed(2) + " V";  // mV → V
    return fmtNum(v) + " mA";
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
        '<td class="lab-mono">' + fmtStable(it) + "</td>" +
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
    var md = ($("lab-f-mode") || {}).value || "";   // 模式:voltage / speed / 空=全部
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
      if (md) {
        var isSpeed = (String(it.drive_mode) === "1");  // 轉速模式
        if (md === "speed" && !isSpeed) return false;
        if (md === "voltage" && isSpeed) return false;
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
        fmd = $("lab-f-mode"), fps = $("lab-f-pagesize"), fsort = $("lab-f-sort");
    if (fm) fm.addEventListener("change", applyFilter);   // 下拉用 change
    if (fc) fc.addEventListener("input", applyFilter);    // 文字框用 input
    if (fcp) fcp.addEventListener("change", applyFilter);
    if (fmd) fmd.addEventListener("change", applyFilter); // 模式篩選
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
        f'<select id="lab-f-mode" class="lab-input">'
        f'<option value="">{s["f_mode_all"]}</option>'
        f'<option value="voltage">{s["f_mode_v"]}</option>'
        f'<option value="speed">{s["f_mode_s"]}</option>'
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
# PRESALE:搶先登記・意向調查頁(/presale/)
#   即將開賣(限量首批・預計 2026 年底)。首頁 hero 只放吸引連結 → 本頁填意向 →
#   送出後回首頁。靜態站無後端 → JSONP 打 GAS(gas/waitlist_standalone.gs)。
#   欄位:email(必填)+ 購買意願 + 版本 + 期望價格(自由填含幣別)+ 所在國家
#   (時區/語系離線偵測、Intl.DisplayNames 在地化、可改)。
# ============================================================
PRESALE = {
    # 部署 gas/waitlist_standalone.gs 後,把 /exec 網址填到這行:
    "api_url": "https://script.google.com/macros/s/AKfycbxnF-wU3tgnxN4TBrlpgzuuaiL87GuhEwwbiqXtrMjwIhmzoHy9Ddv15_j_vuELck07/exec",
    "i18n": {
        "zh": {
            "title": "意向調查・限量首批 | MotorLab 馬達磨合機",
            "description": "MotorLab 精密馬達磨合/檢測機預計 2026 年底限量首批發售。留下 email 與購買意向,開賣第一時間通知你,也協助我們把首批數量備得剛剛好。",
            "keywords": "MotorLab 預購, 馬達磨合機 預購, 限量首批, 意向調查, mini 四驅車 馬達磨合機",
            "breadcrumb": "意向調查",
            "h1_for_ld": "MotorLab 意向調查・限量首批",
            "eyebrow": "Pre-launch · 意向調查",
            "hero_title": "意向調查・限量首批",
            "badge": "2026 年底限量首批・意向調查",
            "hero_p": "MotorLab 精密馬達磨合/檢測機預計 <b>2026 年底</b>限量首批發售。留個資料、告訴我你的購買意向。",
            "email_label": "Email(必填)",
            "email_ph": "you@example.com",
            "intent_label": "購買意願",
            "intent_opts": ["開賣就想買", "看價格再決定", "先了解、觀望"],
            "edition_label": "想要的版本",
            "edition_opts": ["PRO(完整・含 AI 健康管理)", "M1(入門)", "還沒決定"],
            "qty_label": "購買數量",
            "qty_ph": "例:1 台 / 2–3 台",
            "price_label": "期望價格(選填)",
            "price_ph": "例:NT$3500 / ¥15000 / US$120",
            "country_label": "所在國家/地區",
            "country_ph": "你的國家/地區",
            "select_ph": "請選擇",
            "btn": "送出意向",
            "note": "這些資料僅用於開賣通知與首批數量規劃,不濫發信、不轉給第三方。",
            "done_title": "感謝您的填寫",
            "done_sub": "已收到你的購買意向,正在返回首頁…",
            "js": {
                "lang": "zh",
                "bademail": "⚠ 請輸入正確的 email",
                "sending": "送出中…",
                "ok": "✓ 感謝!已收到你的意向,開賣第一時間通知你。正在返回首頁…",
                "err": "✗ 送出失敗,請稍後再試,或私訊 IG @motorlab.tw。",
                "soon": "登記管道即將開放 —— 先追蹤 IG @motorlab.tw"
            }
        },
        "en": {
            "title": "Interest Survey · Limited First Batch | MotorLab",
            "description": "MotorLab's precision motor break-in / test machine ships in a limited first batch in late 2026. Leave your email and buying intent and we will notify you the moment it launches.",
            "keywords": "MotorLab pre-order, motor break-in machine pre-order, limited first batch, intent survey, mini 4wd motor break-in machine",
            "breadcrumb": "Interest Survey",
            "h1_for_ld": "MotorLab Interest Survey · Limited First Batch",
            "eyebrow": "Pre-launch · Interest survey",
            "hero_title": "Interest Survey · Limited First Batch",
            "badge": "Late 2026 · Limited first batch · Interest survey",
            "hero_p": "MotorLab's precision motor break-in / test machine ships in a limited first batch in <b>late 2026</b>. Leave your details and tell us your buying intent.",
            "email_label": "Email (required)",
            "email_ph": "you@example.com",
            "intent_label": "Buying intent",
            "intent_opts": ["Ready to buy at launch", "Depends on the price", "Just exploring for now"],
            "edition_label": "Which edition",
            "edition_opts": ["PRO (full · with AI health management)", "M1 (entry)", "Not sure yet"],
            "qty_label": "Quantity",
            "qty_ph": "e.g. 1 / 2–3 units",
            "price_label": "Target price (optional)",
            "price_ph": "e.g. US$120 / NT$3500 / ¥15000",
            "country_label": "Country / region",
            "country_ph": "Your country / region",
            "select_ph": "Select…",
            "btn": "Submit intent",
            "note": "Used only to notify you at launch and plan the first batch. No spam, never shared with third parties.",
            "done_title": "Thank you!",
            "done_sub": "Your buying intent is recorded. Returning to home…",
            "js": {
                "lang": "en",
                "bademail": "⚠ Please enter a valid email",
                "sending": "Sending…",
                "ok": "✓ Thank you! Your intent is in — we’ll notify you at launch. Returning to home…",
                "err": "✗ Submission failed, please try again later, or DM IG @motorlab.tw.",
                "soon": "Sign-ups opening soon — follow IG @motorlab.tw"
            }
        },
        "ja": {
            "title": "意向調査・限定初回ロット | MotorLab",
            "description": "MotorLab 精密モーター慣らし/検査機は 2026 年末に限定初回ロットで発売予定。メールと購入意向をご登録いただくと、発売時に一番にお知らせします。",
            "keywords": "MotorLab 予約, モーター慣らし機 予約, 限定初回ロット, 意向調査, ミニ四駆 モーター慣らし機",
            "breadcrumb": "意向調査",
            "h1_for_ld": "MotorLab 意向調査・限定初回ロット",
            "eyebrow": "Pre-launch · 意向調査",
            "hero_title": "意向調査・限定初回ロット",
            "badge": "2026 年末限定初回ロット・意向調査",
            "hero_p": "MotorLab 精密モーター慣らし/検査機は <b>2026 年末</b>に限定初回ロットで発売予定です。ご連絡先と購入意向をお知らせください。",
            "email_label": "メール(必須)",
            "email_ph": "you@example.com",
            "intent_label": "購入意向",
            "intent_opts": ["発売したら買いたい", "価格次第", "まずは検討中"],
            "edition_label": "希望バージョン",
            "edition_opts": ["PRO(フル・AI ヘルス管理付き)", "M1(エントリー)", "まだ未定"],
            "qty_label": "購入台数",
            "qty_ph": "例:1 台 / 2–3 台",
            "price_label": "希望価格(任意)",
            "price_ph": "例:¥15000 / US$120 / NT$3500",
            "country_label": "国 / 地域",
            "country_ph": "あなたの国 / 地域",
            "select_ph": "選択してください",
            "btn": "意向を送信",
            "note": "発売のお知らせと初回ロットの数量計画にのみ使用します。スパムや第三者提供はありません。",
            "done_title": "ご記入ありがとうございます",
            "done_sub": "購入意向を受け付けました。ホームへ戻ります…",
            "js": {
                "lang": "ja",
                "bademail": "⚠ 正しいメールアドレスを入力してください",
                "sending": "送信中…",
                "ok": "✓ ありがとうございます!意向を受け付けました。発売時にお知らせします。ホームへ戻ります…",
                "err": "✗ 送信に失敗しました。後でもう一度、または IG @motorlab.tw へ。",
                "soon": "登録は近日開始 — IG @motorlab.tw をフォロー"
            }
        }
    }
}

# /presale/ JSONP 送出邏輯(__API_URL__ / __HOME_URL__ / __LOCALE__ / __I18N_JSON__ 由 build_presale_page 取代)
PRESALE_APP_JS = r"""
(function () {
  var API = "__API_URL__";
  var HOME = "__HOME_URL__";
  var LOCALE = "__LOCALE__";
  var I18N = __I18N_JSON__;
  function byId(id) { return document.getElementById(id); }
  var form = byId('ps-form'), email = byId('ps-email'), intent = byId('ps-intent'),
      edition = byId('ps-edition'), qty = byId('ps-qty'), price = byId('ps-price'),
      country = byId('ps-country'), btn = byId('ps-btn'), msg = byId('ps-msg');
  // 所在國家:時區→ISO 區碼(退回語系副標籤),用 Intl.DisplayNames 在地化成國名並預填(可改)
  var TZ = { 'Asia/Taipei':'TW','Asia/Tokyo':'JP','Asia/Kuala_Lumpur':'MY','Asia/Kuching':'MY','Asia/Hong_Kong':'HK','Asia/Singapore':'SG','Asia/Shanghai':'CN','Asia/Chongqing':'CN','Asia/Urumqi':'CN','Asia/Macau':'MO','Asia/Seoul':'KR','Asia/Bangkok':'TH','Asia/Jakarta':'ID','Asia/Manila':'PH','Asia/Ho_Chi_Minh':'VN','Asia/Kolkata':'IN','Asia/Dubai':'AE','Australia/Sydney':'AU','Australia/Melbourne':'AU','Australia/Perth':'AU','Pacific/Auckland':'NZ','Europe/London':'GB','Europe/Paris':'FR','Europe/Berlin':'DE','Europe/Madrid':'ES','Europe/Rome':'IT','Europe/Amsterdam':'NL','Europe/Warsaw':'PL','America/New_York':'US','America/Chicago':'US','America/Denver':'US','America/Los_Angeles':'US','America/Toronto':'CA','America/Vancouver':'CA','America/Sao_Paulo':'BR','America/Mexico_City':'MX' };
  var det = { region: '', tz: '', locale: '' };
  try { det.tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
  det.locale = navigator.language || navigator.userLanguage || '';
  det.region = TZ[det.tz] || '';
  if (!det.region) { var m = det.locale.match(/[-_]([A-Za-z]{2})\b/); if (m) det.region = m[1].toUpperCase(); }
  function regionName(cc) { try { if (cc && typeof Intl !== 'undefined' && Intl.DisplayNames) { return (new Intl.DisplayNames([LOCALE], { type: 'region' })).of(cc) || ''; } } catch (e) {} return ''; }
  if (country && !country.value) { country.value = regionName(det.region); }
  function setMsg(t, cls) { msg.textContent = t; msg.className = 'ps-msg ps-show' + (cls ? (' ' + cls) : ''); }
  function submit(e) {
    if (e && e.preventDefault) e.preventDefault();
    var em = (email.value || '').trim();
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(em)) { setMsg(I18N.bademail, 'warn'); if (email.focus) email.focus(); return false; }
    if (API.indexOf('script.google') < 0) { setMsg(I18N.soon, 'muted'); return false; }
    btn.disabled = true; setMsg(I18N.sending, 'muted');
    var cb = 'ps_' + Date.now(); var s = document.createElement('script');
    var timer = setTimeout(function () { cleanup(); btn.disabled = false; setMsg(I18N.err, 'bad'); }, 12000);
    function cleanup() { clearTimeout(timer); try { delete window[cb]; } catch (x) { window[cb] = undefined; } if (s.parentNode) s.parentNode.removeChild(s); }
    window[cb] = function (r) {
      cleanup();
      if (r && r.ok) {
        if (form) form.style.display = 'none';
        var done = byId('ps-done'); if (done) done.style.display = 'block';
        setTimeout(function () { location.href = HOME; }, 2600);
      } else { btn.disabled = false; setMsg(I18N.err, 'bad'); }
    };
    s.onerror = function () { cleanup(); btn.disabled = false; setMsg(I18N.err, 'bad'); };
    var q = '?action=presale&email=' + encodeURIComponent(em)
      + '&intent=' + encodeURIComponent(intent ? intent.value : '')
      + '&edition=' + encodeURIComponent(edition ? edition.value : '')
      + '&qty=' + encodeURIComponent(qty ? qty.value.trim() : '')
      + '&price=' + encodeURIComponent(price ? price.value.trim() : '')
      + '&country=' + encodeURIComponent(country ? country.value.trim() : '')
      + '&region=' + encodeURIComponent(det.region)
      + '&tz=' + encodeURIComponent(det.tz)
      + '&locale=' + encodeURIComponent(det.locale)
      + '&lang=' + encodeURIComponent(I18N.lang || '')
      + '&callback=' + cb + '&t=' + Date.now();
    s.src = API + q; document.body.appendChild(s); return false;
  }
  if (form) form.addEventListener('submit', submit);
})();
"""

# 搶先登記頁專屬 CSS(注入 head;沿用 .guide-page / .lab-* 殼,補表單樣式)
PRESALE_CSS = """
.ps-box{max-width:560px;margin:0 auto}
.ps-form{display:flex;flex-direction:column;gap:16px}
.ps-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.ps-field{display:flex;flex-direction:column;gap:6px;text-align:left}
.ps-lab{font-size:13px;color:var(--text-muted);letter-spacing:.03em}
.ps-input{width:100%;box-sizing:border-box;padding:12px 14px;background:var(--bg-primary,#0f1216);border:1px solid var(--border,#2b313c);border-radius:10px;color:var(--text-primary,#e8ebf0);font-size:15px;font-family:inherit}
.ps-input:focus{outline:none;border-color:#35d0df}
.ps-btn{width:100%;margin-top:2px}
.ps-msg{min-height:1.4em;font-size:15px;line-height:1.6;opacity:0;transition:opacity .18s;text-align:center}
.ps-msg.ps-show{opacity:1}
.ps-msg.ok{color:#34d399}
.ps-msg.bad{color:#f87171}
.ps-msg.warn{color:#fbbf24}
.ps-msg.muted{color:var(--text-muted)}
.ps-note{font-size:12.5px;line-height:1.7;color:var(--text-muted);text-align:center;margin:0}
.ps-badge{display:inline-block;margin:4px 0 2px;padding:7px 14px;border-radius:999px;background:rgba(53,208,223,.10);border:1px solid rgba(53,208,223,.35);color:#8fe3ee;font-size:13.5px;font-weight:600;letter-spacing:.02em}
.ps-done{text-align:center;padding:48px 12px}
.ps-done-t{font-size:clamp(26px,5vw,40px);font-weight:700;color:var(--text-primary,#e8ebf0);line-height:1.35;margin-bottom:14px}
.ps-done-s{font-size:16px;line-height:1.7;color:var(--text-muted)}
@media(max-width:520px){.ps-grid{grid-template-columns:1fr}}
"""


def build_presale_page(presale_cfg, lang, src_html, i18n):
    """產生 /presale/ 搶先登記・意向調查頁(靜態殼 + JSONP 送出 → 成功後回首頁)。"""
    soup = BeautifulSoup(src_html, "lxml")
    cfg = LANGS[lang]
    ui = UI_STRINGS[lang]
    s = presale_cfg["i18n"][lang]
    lang_prefix = "" if lang == "zh" else f"/{lang}"
    page_url = f"{SITE}{lang_prefix}/presale/"
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
    if lang != "en" and "en" in presale_cfg["i18n"]:
        kw = kw + ", " + presale_cfg["i18n"]["en"]["keywords"]
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
            "rel": "alternate", "hreflang": hl_cfg["html_lang"], "href": f"{SITE}{hl_prefix}/presale/"
        }))
    head.append(soup.new_tag("link", attrs={
        "rel": "alternate", "hreflang": "x-default", "href": f"{SITE}/presale/"
    }))

    style_tag = soup.new_tag("style")
    style_tag.string = PRESALE_CSS
    head.append(style_tag)

    webpage_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": s["h1_for_ld"],
        "description": s["description"],
        "inLanguage": cfg["html_lang"],
        "url": page_url,
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
    for data in (webpage_ld, breadcrumb_ld):
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
        f'<div class="ps-badge">{s["badge"]}</div>'
        f'<p class="lab-hero-p">{s["hero_p"]}</p>'
        f'</div></section>'
    )
    main_el.append(BeautifulSoup(hero_html, "html.parser"))

    def opts(items):
        o = f'<option value="" selected>{html.escape(s["select_ph"])}</option>'
        for it in items:
            o += f'<option value="{html.escape(it)}">{html.escape(it)}</option>'
        return o

    form_html = (
        f'<section class="lab-section"><div class="container"><div class="ps-box">'
        f'<form id="ps-form" class="ps-form">'
        f'<label class="ps-field"><span class="ps-lab">{s["email_label"]}</span>'
        f'<input type="email" id="ps-email" class="ps-input" required autocomplete="email" '
        f'placeholder="{s["email_ph"]}"></label>'
        f'<div class="ps-grid">'
        f'<label class="ps-field"><span class="ps-lab">{s["intent_label"]}</span>'
        f'<select id="ps-intent" class="ps-input">{opts(s["intent_opts"])}</select></label>'
        f'<label class="ps-field"><span class="ps-lab">{s["edition_label"]}</span>'
        f'<select id="ps-edition" class="ps-input">{opts(s["edition_opts"])}</select></label>'
        f'<label class="ps-field"><span class="ps-lab">{s["qty_label"]}</span>'
        f'<input type="text" id="ps-qty" class="ps-input" maxlength="20" '
        f'inputmode="numeric" placeholder="{s["qty_ph"]}"></label>'
        f'<label class="ps-field"><span class="ps-lab">{s["price_label"]}</span>'
        f'<input type="text" id="ps-price" class="ps-input" maxlength="40" '
        f'placeholder="{s["price_ph"]}"></label>'
        f'<label class="ps-field"><span class="ps-lab">{s["country_label"]}</span>'
        f'<input type="text" id="ps-country" class="ps-input" maxlength="60" '
        f'autocomplete="country-name" placeholder="{s["country_ph"]}"></label>'
        f'</div>'
        f'<button type="submit" class="lab-btn ps-btn" id="ps-btn">{s["btn"]}</button>'
        f'<div class="ps-msg" id="ps-msg" aria-live="polite"></div>'
        f'<p class="ps-note">{s["note"]}</p>'
        f'</form>'
        f'<div id="ps-done" class="ps-done" style="display:none" aria-live="polite">'
        f'<div class="ps-done-t">{s["done_title"]}</div>'
        f'<div class="ps-done-s">{s["done_sub"]}</div>'
        f'</div>'
        f'</div></div></section>'
    )
    main_el.append(BeautifulSoup(form_html, "html.parser"))

    soup.body.append(main_el)
    if footer_extracted is not None:
        soup.body.append(footer_extracted)

    app_js = PRESALE_APP_JS.replace("__API_URL__", presale_cfg["api_url"])
    app_js = app_js.replace("__HOME_URL__", home_url)
    app_js = app_js.replace("__LOCALE__", cfg["html_lang"])
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
    "fw": "v3.5.0",
    "i18n": {
        "zh": {
            "title": "MotorLab 使用者手冊:馬達磨合機操作說明 | MotorLab",
            "description": "MotorLab Mini 4WD® 馬達磨合機完整使用手冊 — 連線、馬達特性量測、磨合三模式、馬達測試、歷史紀錄、全球磨合資料庫、AI 健康管理、軸承/電刷測試、田宮馬達規格、系統設定、安全保護、WiFi 重設與常見問題。對應韌體 v3.5.0。",
            "keywords": "MotorLab 使用手冊, 馬達磨合機操作, 馬達磨合機說明書, MotorLab 教學, 馬達磨合機設定",
            "breadcrumb": "使用者手冊",
            "eyebrow": "Docs · 使用者手冊",
            "h1": "MotorLab 使用者手冊",
            "lead": "Mini 4WD® 馬達磨合機完整操作說明。對應韌體 v3.5.0。功能隨版本更新,新版可能多出未列選項。",
            "toc_label": "目錄",
            "fw_note": "本手冊適用 MotorLab v3.5.0 韌體(2026-07-15)。",
        },
        "en": {
            "title": "MotorLab User Manual: Motor Break-in Machine Guide | MotorLab",
            "description": "Complete user manual for the MotorLab Mini 4WD® motor break-in machine — connection, motor characterization, three-mode break-in, testing, history records, global database, AI health management, bearing/brush tests, Tamiya motor specs, system settings, safety, WiFi reset and FAQ. For firmware v3.5.0.",
            "keywords": "MotorLab user manual, motor break-in machine guide, MotorLab instructions, motor tester manual, Mini 4WD break-in machine",
            "breadcrumb": "User Manual",
            "eyebrow": "Docs · User Manual",
            "h1": "MotorLab User Manual",
            "lead": "Complete operating guide for the Mini 4WD® motor break-in machine. For firmware v3.5.0. Features evolve with each release; newer firmware may add options not listed here.",
            "toc_label": "Contents",
            "fw_note": "This manual applies to MotorLab firmware v3.5.0 (2026-07-15).",
        },
        "ja": {
            "title": "MotorLab ユーザーマニュアル:モーター慣らし機操作ガイド | MotorLab",
            "description": "MotorLab Mini 4WD® モーター慣らし機の完全ユーザーマニュアル — 接続、モーター特性測定、慣らし 3 モード、テスト、履歴記録、グローバルデータ庫、AI 健康管理、ベアリング/ブラシ測定、タミヤモーター規格、システム設定、安全保護、WiFi リセット、FAQ。ファームウェア v3.5.0 対応。",
            "keywords": "MotorLab マニュアル, モーター慣らし機 操作, MotorLab 使い方, モーターテスター 説明書, ミニ四駆 慣らし機",
            "breadcrumb": "ユーザーマニュアル",
            "eyebrow": "Docs · ユーザーマニュアル",
            "h1": "MotorLab ユーザーマニュアル",
            "lead": "Mini 4WD® モーター慣らし機の完全操作ガイド。ファームウェア v3.5.0 対応。機能はバージョンごとに更新され、新版では未記載の項目が増える場合があります。",
            "toc_label": "目次",
            "fw_note": "本マニュアルは MotorLab ファームウェア v3.5.0（2026-07-15）に対応します。",
        },
    },
    "sections": {
        "zh": [
            {"id": "precautions", "t": "〇、使用前必讀・安全須知", "html": (
                "<div class='manual-note'><b>首次使用前請詳閱本章。未依安全須知使用所造成之人身傷害、財物損失或機器損害,使用者須自負責任,亦不予保固。</b></div>"
                "<h3>🔴 電源安全</h3><ul><li>本機須用 <b>DC 5V／6A 以上</b>、<b>具安規認證</b>的電源供應器。</li><li><b>使用規格不符的電源(電壓過高、劣質、無安規、來路不明或改裝)將導致機器損壞,並有引發火災的危險;因此造成的故障或損害不予保固。</b></li><li>勿在電源線材或接頭破損、發燙、有異味時繼續使用。</li></ul>"
                "<h3>🔴 運轉安全(馬達高速旋轉)</h3><ul><li><b>馬達運轉中,嚴禁用手、工具或任何物體觸碰轉軸、齒輪或反射盤</b>——高速旋轉會造成割傷、捲入、飛甩傷害。</li><li>運轉前確認馬達<b>牢固裝在治具上</b>,未固定的馬達高速旋轉可能飛脫。</li><li><b>臉部、頭髮、鬆散衣物、飾品</b>勿靠近運轉中的馬達。</li><li>馬達與周邊零件運轉後會<b>發熱燙手</b>,停機後勿立即徒手觸摸。</li><li>運轉中若有異音、異味、冒煙、火花,<b>立即切斷電源</b>並檢查。</li></ul>"
                "<h3>🔴 環境安全</h3><ul><li><b>本機不防水</b>:使用與存放<b>遠離水源、潮濕、雨淋</b>;勿讓液體(水、油、飲料)潑濺到機身或電路。</li><li>放置於<b>平穩、堅固、耐熱、不可燃</b>的桌面;勿在鋪毯、紙張、易燃物上運作。</li><li>保持四周<b>通風散熱</b>,勿覆蓋機身散熱孔;勿在密閉高溫環境長時間運作。</li><li>遠離火源、熱源、陽光直曬。</li></ul>"
                "<h3>🔴 操作安全</h3><ul><li><b>兒童請在成人監護下使用</b>;零件與馬達含小物與尖銳邊緣,勿讓幼童單獨接觸。</li><li>勿自行拆解、改裝機器或電路;勿以本機驅動非指定的馬達或負載。</li><li><b>端子僅供連接馬達</b>,勿接電池、電源或其他負載,以免短路損壞。</li><li>長時間不使用時<b>拔除電源</b>。</li></ul>"
                "<h3>⚠ 量測數據注意</h3><ul><li>本機數據<b>僅供同一台機器上的前後對照與相對比較</b>;不同設備／儀器數據有系統性差異,<b>勿與他人或市售數據直接比較</b>。</li><li>量測時請勿使用<b>導電型磨合油</b>(會使讀數失真,詳見「五、馬達磨合」)。</li></ul>"
                "<p class='manual-intro'>本機內建高溫保護、過流／短路／卡轉／離治具偵測、緩啟動緩停止等多重自動防護(詳見「十四、安全與保護」),但這些是輔助,<b>不能取代使用者的安全操作與看管</b>。</p>"
            )},
            {"id": "start", "t": "一、快速開始", "html": (
                "<div class='manual-note'>🔴 <b>接電源前務必確認</b>:本機須用 <b>DC 5V／6A 以上</b>、具安規認證的電源供應器。<b>使用規格不符的電源會導致機器損壞、甚至引發火災,且不予保固</b>(詳見「〇、使用前必讀」與「十四、安全與保護」)。</div>"
                "<ol><li>接通電源 → 板載指示燈亮、聽到開機嗶聲。</li><li>手機 / 平板 / 電腦的 WiFi 連「<b>MotorTester</b>」(預設密碼 <code>12345678</code>)。</li><li>瀏覽器開 <code>http://10.10.10.1/</code>。</li><li><b>第一件事</b>:系統設定 → WiFi 設定,把密碼改強密碼(否則任何人都能操作機器)。</li></ol>"
            )},
            {"id": "connect", "t": "二、連線", "html": (
                "<table class='manual-table'><tbody><tr><th>網址</th><td><code>http://10.10.10.1/</code>(<b>不是</b> https)</td></tr><tr><th>熱點</th><td><code>MotorTester</code> / <code>12345678</code>(可改名)</td></tr><tr><th>裝置</th><td>手機 / 平板 / 筆電皆可,建議大螢幕</td></tr><tr><th>連線數</th><td><b>同時只有一台可操作</b>(單一連線,見下)</td></tr><tr><th>注意</th><td>機器熱點<b>無對外網路</b>;iPhone 跳「無網際網路」選「保持」即可</td></tr></tbody></table><p><b>單一連線(多台切換)</b>:操作介面同時只允許一台裝置控制,避免兩台同時下命令衝突。</p><ul><li><b>後連的裝置自動接管</b>:用新裝置開啟介面後,它即成為控制端。</li><li><b>舊裝置自動停用</b>:先前那台會顯示「已被其他裝置接管」並停止更新(數值與圖表凍結),不會再送出命令。</li><li><b>要換回舊裝置</b>:在該裝置上<b>重新整理頁面</b>即可重新接管。</li><li>中途換裝置不影響進行中的磨合 / 測試——程序在機器端持續執行,新裝置連上後直接顯示目前進度。</li></ul>"
            )},
            {"id": "home", "t": "三、首頁", "html": (
                "<p>十個功能按鈕:</p><p class='manual-pills'>馬達特性量測 · 馬達磨合 · 馬達測試 · 歷史紀錄 · AI 智慧馬達健康管理(Pro)· 軸承阻力測試 · 電刷接觸穩定測試 · 全球磨合資料庫 · 田宮馬達規格 · 系統設定</p><p>標題顯示 <code>MotorLab M1</code> 或 <code>MotorLab PRO</code>。</p>"
            )},
            {"id": "charexp", "t": "四、馬達特性量測", "html": (
                "<p class='manual-intro'>全自動量出馬達的特性參數與損耗,<b>給參考數據、不評分不排名</b>——同型號馬達互相比較、自己判斷。系統自動<b>連續量測 3 趟取平均</b>,約 5 分鐘,過程溫和,適合全新未磨合馬達。</p><p><b>操作</b>:首頁 →「馬達特性量測」→ 選方向(預設正轉)+ 選<b>馬達型號</b>(16 款下拉)+ 填<b>備註</b>(選填,40 字以內)→「開始量測」→ 全程自動(顯示第幾趟與進度),過程中請勿觸碰馬達 → 完成顯示數據表並<b>自動存入量測紀錄</b>。</p><p><b>怎麼看數據(表內每項都標了方向)</b>:</p><ul><li><b>★ I0(無載電流)</b>:同轉速下<b>越低越好</b>——重複性最佳,選別馬達的首要指標。</li><li><b>★ Km(品質因數)/ ★ T_loss(損耗轉矩)</b>:輔助指標(Km 越高越好、T_loss 越低越好)。</li><li><b>Ke(磁路強度)</b>:無絕對好壞——數值相近的馬達互相比較才準確(偏高=偏扭力、偏低=偏轉速)。</li><li><b>KV(轉速常數,rpm/V)</b>:由 Ke 換算——KV × 電壓 ≈ 空載轉速(例 KV 14000 × 3V ≈ 42000 RPM),方便與市面標示對照。</li><li><b>R(內部電阻)</b>:越低越好。</li><li><b>起轉電壓</b>:僅參考——單次隨機性大,適合當同一顆馬達的長期健康對照(日後明顯升高=軸承 / 電刷劣化警訊)。</li><li><b>損耗擬合 R² / Ke 漂移</b>:資料品質指標(越接近 1、漂移越低越可信)。</li><li><b>3 趟一致性</b>:各趟 I0 的最大差異;顯示 ⚠ 代表馬達不穩或架設鬆動,該筆數據僅供參考,建議檢查後重測。</li></ul><p><b>量測紀錄</b>:量測頁 →「量測紀錄」。每次成功量測自動儲存(含全部指標與各轉速點資料),最多 <b>50 筆</b>,滿了自動刪最舊;可檢視詳情、可刪除。</p><p><b>建議用法</b>:</p><ul><li>同批新馬達逐顆量測 → 依 ★I0 挑體質好的再投入磨合(省磨合工時)。</li><li>磨合後<b>再測同一顆</b>對照:損耗類應下降(磨合有效);Ke / R 應幾乎不變。</li><li>比較不同馬達盡量在<b>相近溫度</b>下測;馬達剛裝上或冷機重啟後第一次數據可能偏高,以第二次起為準。</li></ul><div class='manual-note'><b>注意</b>:量測失敗(馬達未起轉 / 鎖定逾時 / 過流)會顯示原因,重試即可。若反覆失敗或待機時轉速不為 0,請檢查轉速感測器與反射盤的對位。</div>"
            )},
            {"id": "breakin", "t": "五、馬達磨合(三種模式)", "html": (
                "<p class='manual-intro'>低速長時間運轉,讓電刷與整流子貼合到最佳接觸。磨合頁最上方有<b>三個模式按鈕</b>(運轉中不可切換)。</p><table class='manual-table'><thead><tr><th>模式</th><th>適合</th><th>一句話</th></tr></thead><tbody><tr><td><b>電壓模式</b></td><td>有自己配方的玩家</td><td>各階段固定電壓運轉(傳統方式)</td></tr><tr><td><b>轉速模式 (Beta)</b></td><td>想以轉速為基準的玩家</td><td>各階段自動控速在設定轉速,電壓穩定即自動換階</td></tr><tr><td><b>智慧模式 (Beta)</b></td><td>想無腦磨合的玩家</td><td>一鍵自動磨合:系統自己磨、自己量、磨好自動停</td></tr></tbody></table><h3>電壓模式</h3><p>首頁 →「馬達磨合程式」→ 選<b>馬達型號</b>(16 款)+ 填<b>備註</b>(40 字以內)→ 選<b>判停標準</b>(純時間限制=各階段跑滿設定時間;智慧穩定電流=電流提前穩定就換階,時間為上限)→ 選<b>磨合趟數</b>(1~6,預設 1)→ 逐趟確認 10 階段參數(多趟用分頁籤切換趟;直接點數字欄修改)→「啟動」。</p><ul><li>每階段可設:電壓(0.6~4.0V,<b>0=跳過</b>)/ 方向 / 磨合秒(10~600,預設 60)/ 冷卻秒(10~600,預設 60)/ 穩定電流容差(2~50mA)。</li><li>多趟可按「<b>本趟複製到之後所有趟</b>」快速填表;趟數旁即時顯示<b>預估總時長</b>。</li><li>輸入超出範圍會自動改為上下限並閃光提示。</li></ul><div class='manual-note'><b>重點</b>:使用新馬達磨合時,碳刷及整流子尚未完成整形,可依趟數將容差值的設定逐漸由大縮小。</div><h3>轉速模式 (Beta)</h3><p>與電壓模式相同的階段表,但第一欄改為<b>目標轉速</b>(6000~30000,每 1000 一階,<b>0=跳過</b>)——機器自動調整電壓把馬達鎖定在該轉速。</p><ul><li><b>判停標準</b>(嚴格 / 標準 / 寬鬆):馬達在該轉速下驅動電壓穩定即視為磨順、提前換階;磨合秒為上限。嚴格=要更穩才過關(磨得較透);寬鬆=較快換階(全新馬達一直換不了階可改寬鬆)。</li><li>階段結果欄顯示<b>穩定電壓</b>;推不到目標轉速會以安全上限電壓跑滿時間並標「<b>未達標</b>」(通常代表目標轉速訂太高,或馬達 / 治具異常)。</li><li>方向、時間、趟數、複製等操作皆與電壓模式相同。</li></ul><h3>智慧模式 (Beta)</h3><p><b>碳刷 Dash 系型號專用</b>的一鍵自動磨合:選<b>馬達型號</b> + 填<b>備註</b> + 選<b>時間上限</b>(磨到完成為止 / 2h / 3h / 4h)→「啟動」,其餘全自動——系統以漸進轉速磨合並持續量測,<b>偵測到穩態(馬達不再進步)時自動停止</b>並嗶聲提示。</p><ul><li>畫面即時顯示:目前輪次 / 目前動作 / 已進行時間 / 收斂進度,以及<b>磨合指標曲線圖</b>(每輪落點 + 移動平均,曲線走平=接近完成)。</li><li>過程中馬達<b>正反轉交替</b>磨合(電刷兩面對稱貼合)並週期性自動量測,聲音與轉速有規律變化屬正常。</li><li>可隨時按「停止」優雅收尾(量完當輪才停)。其他型號請用電壓 / 轉速模式。</li></ul><div class='manual-note'><b>重要:量測 / 磨合請勿使用「導電潤滑油」。</b>市面標榜「導電」的磨合油(含導電碳粉)加入後轉速瞬升、電壓瞬降,那<b>不是真的磨好,而是碳粉暫時導電的假象</b>。本機所有判定(穩定電流 / 轉速 / 內阻)量測的是電刷與整流子的<b>真實接觸狀態</b>,導電油會使讀數失真偏樂觀,油一洗掉就打回原形(這類油品說明書自己也註明「洗淨後才穩定、才會更好轉」)。正確做法:全程不用這類油;若已使用,請徹底洗淨後再上機量測。一般軸承微量潤滑不受影響,此警告僅針對「導電型磨合油」。</div><h3>共同行為</h3><p>每階段流程:緩啟動 → 運轉中 → 緩停止 → 冷卻中 → 下一階段;跑完一趟自動接下一趟(顯示「第 x/y 趟 · 階段 c」)。全部完成 → 嗶 3 聲 → 自動存入歷史紀錄(電壓 / 轉速模式,含每趟每階段結果)。</p><p><b>運轉中可按</b>:</p><table class='manual-table'><thead><tr><th>按鈕</th><th>行為</th></tr></thead><tbody><tr><td>停止</td><td>緩停後結束,紀錄標「使用者中止」</td></tr><tr><td>歸零</td><td>清最大轉速 / 穩定電流峰值,不中斷</td></tr><tr><td>回首頁</td><td>切回首頁,磨合<b>背景繼續跑</b></td></tr></tbody></table><div class='manual-note'><b>注意</b>:運轉中所有設定鎖定;勿中途斷電(資料遺失);高溫會自動停止並存檔;想快速驗機就把每階段時間改短。即時數據多一格 <b>KV(rpm/V)</b>＝目前轉速除以馬達電壓,供快速對比馬達狀態。</div>"
            )},
            {"id": "test", "t": "六、馬達測試", "html": (
                "<p class='manual-intro'>單階段即時觀察,<b>不寫入紀錄</b>。</p><p>首頁 →「馬達測試程式」→ 設 <b>電壓(0.6~4.0V,預設 1V)/ 運轉時間(10~600 秒,預設 60)/ 方向 / 穩定電流容差(2~50mA)/ 判停標準</b>(純時間限制 或 智慧穩定電流＝電流提前穩定即提早結束,預設後者;此設定與磨合頁<b>各自獨立</b>)→「啟動」→ 看即時數據與圖表(含 <b>KV</b> 即時值),到時或穩定即自動停。</p><div class='manual-note'><b>注意</b>:電壓上限 4.0V 保護馬達,勿繞過;反轉接正轉前先按一次「停止」。</div>"
            )},
            {"id": "records", "t": "七、歷史紀錄", "html": (
                "<p class='manual-intro'>自動儲存每次磨合完整資料,最多 <b>50 筆</b>。</p><p>每筆顯示名稱 / 開始時間 / 時長 / 模式 / 結束原因 / 最大轉速 / 平均轉速 / 穩定電流。</p><table class='manual-table'><thead><tr><th>按鈕</th><th>用途</th></tr></thead><tbody><tr><td>檢視</td><td>看每一階段數據(多趟紀錄含各趟各階段)</td></tr><tr><td>套用</td><td>把配方(趟數 + 各趟 10 階段參數)一鍵套回磨合頁;舊單趟紀錄套用後趟數=1</td></tr><tr><td>匯出</td><td>下載 JSON(可再匯入)或 CSV(Excel 開)</td></tr><tr><td>刪除</td><td>移除(不可復原)</td></tr></tbody></table><ul><li><b>容量滿(50 筆)</b>:管理中可選「自動覆寫」(啟動時刪最舊)或「不覆寫」(預設,啟動被擋需手動清)。</li><li><b>匯入</b>:選之前匯出的 JSON(id 重複會覆蓋)。只收 JSON。每個匯出檔帶<b>簽章驗證</b>:同台 / 同批機器可互通,竄改或非本批機器的檔會被拒絕;改檔名不影響(驗的是內容)。</li><li><b>檔名</b>:<code>motorlab_&lt;日期&gt;_&lt;時間&gt;_&lt;型號&gt;[_&lt;備註&gt;]</code>,採磨合開始時間 → 同筆重複匯出檔名一致。</li><li>韌體更新 / WiFi 重設<b>都不會清紀錄</b>。</li></ul>"
            )},
            {"id": "database", "t": "八、全球磨合資料庫", "html": (
                "<p class='manual-intro'>與全球玩家分享磨合紀錄,機器<b>直接連網</b>完成,不必匯出再上網站。需連<b>有外網的 WiFi</b>(M1 / Pro 都能用)。</p><p><b>瀏覽 / 下載</b>:首頁 →「全球磨合資料庫」→ 連網後列出最新 100 筆 → 用 <b>馬達型號 / 國家 / 完成狀態</b> 即時篩選 → 每筆可「下載」(存進本機)或「下載並套用」(存入並把配方套到磨合頁)。</p><p><b>分享自己的</b>:歷史紀錄 → 點開某筆 → 詳情頁底部「分享到全球資料庫」→ 確認框<b>明列將公開的欄位</b>(型號 / 備註 / 分享者 / 國家 / 完整數據;填了名字會提醒顯示真名)→ 確認上傳。已上傳過會提示「這筆已在資料庫」(非錯誤)。</p><div class='manual-note'><b>注意</b>:下載的紀錄會經簽章驗證;上傳即同意公開,需移除請來信 <b>motorlab.tw@gmail.com</b>;連到無外網的 WiFi 會提示「無法連到伺服器」。</div>"
            )},
            {"id": "health", "t": "九、AI 智慧馬達健康管理(Pro)", "html": (
                "<p class='manual-intro'>為每顆馬達建立健康指紋,定期重測比對,給 0~100 分與建議。<b>跟自己比,不跟別顆比</b>。</p><ol><li>首頁 →「AI 智慧馬達健康管理」→「+ 新增馬達」。</li><li>填 <b>馬達型號</b>(下拉)+ <b>備註</b>(選填)+ <b>起始電壓</b> + <b>電壓間距</b>(自動取 5 點)。</li><li>確認 → 自動跑約 <b>2.5 分鐘</b> 建立基準。</li></ol><p>之後每張卡片可做 <b>完整檢測</b>(約 2.5 分,最準)或 <b>快速檢測</b>(約 1.5 分,±5%)。結果頁顯示分數、等級(Optimal / Acceptable / Warning / Critical)、趨勢圖、五項指標、文字建議。</p><div class='manual-note'><b>注意</b>:每顆最多 50 次歷史,整機最多 20 顆;檢測中勿斷電 / 勿按其他鈕;高溫會自動中止;M1 版按鈕灰色(點下提示升級)。</div>"
            )},
            {"id": "bearing", "t": "十、軸承阻力測試", "html": (
                "<p class='manual-intro'>量軸承順暢度,任何版本可用。<b>完全靜止時間越久 → 軸承越順</b>。</p><p>首頁 →「軸承阻力測試」→ 選測試電壓(<b>2.4V 或 3V</b>)→「開始測試」→ 機器加速到該電壓 → 穩定轉速 5 秒 → <b>直接斷電(不剎車)</b> → 計時到完全靜止 → 顯示 <b>完全靜止時間</b>。</p><div class='manual-note'><b>注意</b>:馬達空載慣性小,本測試<b>只顯示時間、不做好壞評定</b>,請拿同一顆馬達不同時期、或不同馬達的時間互比;需轉速感應器正常;建議測 2~3 次看重複性。</div>"
            )},
            {"id": "brush", "t": "十一、電刷接觸穩定測試", "html": (
                "<p class='manual-intro'>量電刷接觸是否均勻,約 35 秒,任何版本可用。<b>接觸不均 → 電流抖動 → CV 上升</b>。</p><p>首頁 →「電刷接觸穩定測試」→「開始測試」即可(<b>不需手轉軸心</b>)。流程固定在 <b>1V</b>:電壓 10 秒內由 0 緩升到 1V → 1V 保持 5 秒 → 1V 採樣電流 20 秒 → 顯示 <b>電流變異係數 CV%</b>。</p><p><b>怎麼看 CV%</b>:CV 是固定電壓下電流的抖動程度,<b>是相對比較工具、沒有絕對好壞線</b>(不同型號天生不同)。建議:</p><ul><li>同一顆馬達 <b>磨合前 vs 磨合後</b>:CV 下降 = 電刷磨開、接觸變好。</li><li>同一顆馬達 <b>長期追蹤</b>:CV 逐漸上升 = 電刷磨損 / 整流子變髒。</li><li><b>馬達 A vs B</b> 相對比較。</li></ul><div class='manual-note'><b>注意</b>:固定 1V、固定流程,才能跨次 / 跨馬達公平比較;建議測 2~3 次看重複性。</div>"
            )},
            {"id": "tamiya", "t": "十二、田宮馬達規格", "html": (
                "<p class='manual-intro'>內建 15 款田宮 Mini 4WD 馬達的官方規格速查表(PRO 雙軸 6 款 + 標準單軸 9 款):型號 / 負載轉速 / 電流 / 電壓 / 扭力。</p><ul><li>表列數值為<b>田宮官方公布之推薦負載下數據</b>(適正電壓 2.4~3.0V);如有型號新增或規格變動,以田宮發表之最新規格為準。</li><li>Ultra-Dash 與 Plasma-Dash 超出官方賽事規則上限,於官方賽事禁用。</li><li>本產品與株式會社田宮(TAMIYA)無任何關聯,亦未受其授權、贊助或背書。</li></ul>"
            )},
            {"id": "settings", "t": "十三、系統設定", "html": (
                "<p class='manual-intro'>系統運轉中此頁只留「回首頁」可按,其餘鎖定。</p><table class='manual-table'><tbody><tr><th>使用者設定</th><td>名稱 / 國家(32 字以內,預設 <code>--</code>),寫入每筆紀錄當出處。已產生的紀錄不回填。</td></tr><tr><th>WiFi 設定</th><td>改熱點名稱 / 密碼(8~63 字)→ 儲存後機器重啟,須重新連新熱點。忘密碼見第十五章。</td></tr><tr><th>語言</th><td>中文 / English / 日本語 切換(預設中文)。按「確定」後<b>系統重新啟動</b>乾淨載入(約 10 秒,頁面自動重新載入);運轉中切換則只重載頁面、不中斷程序。</td></tr><tr><th>正版查驗</th><td>顯示本機 ID,可至官網查驗頁自行確認機器為正版(v3.4.1 起)。</td></tr><tr><th>溫度校正</th><td>顯示與實際有偏差時加補償(±20°C)。</td></tr><tr><th>高溫鎖定</th><td>設定高溫鎖定溫度(預設 50°C,範圍 25~60°C)。當前溫度高於設定值 5°C 以上持續 10 秒即進入高溫鎖定(停機,須按歸零解除)。區塊內同時顯示當前溫度。</td></tr><tr><th>平均轉速設定</th><td>容差(相鄰兩秒轉速差)下拉 120~600 RPM,<b>預設 240</b>。容差越大越容易判定穩定但反應較遲鈍;馬達較不穩可調高。</td></tr><tr><th>緩啟動</th><td>電壓由 0 在 5 秒內平順線性升到目標電壓(與緩停止同風格),<b>無可調參數</b>。電壓輸出已校準,不需設定啟動扭矩。</td></tr><tr><th>取得授權</th><td>M1 升 Pro,見下。</td></tr><tr><th>軟體更新</th><td>透過家裡 WiFi 自動取得最新韌體,見下。</td></tr><tr><th>RGB 狀態燈</th><td>雙燈(內建 / 面板)輸出位置 + 亮度(0~100%)+ 5 組狀態樣式,見下。</td></tr><tr><th>工程模式</th><td>密碼保護的進階校正與離線更新(一般使用者用不到)。</td></tr><tr><th>WiFi 列表</th><td>最多記憶 8 組外部 WiFi;「清空列表」用於轉手設備(不影響 Pro 授權)。</td></tr></tbody></table><p><b>取得授權(M1 → Pro)</b>:系統設定 →「取得授權」→ 選家裡 WiFi 連線 → 機器自動驗證購買 → 未購買則顯示 QR Code → 用另一台有外網的裝置掃碼結帳 → 機器每 10 秒自動查詢,付款成功即解鎖。全程約 1~3 分鐘、<b>不必手動輸入金鑰</b>、最久 10 分鐘逾時可重試。退費過會顯示「重新取得授權」。</p><p><b>軟體更新</b>:系統設定 →「檢查更新」→ 選 WiFi → 有新版自動下載寫入(進度到 100%)→ 自動重啟、頁面自動重載。<b>過程勿關電源 / 瀏覽器</b>(中途斷電有保護自動回舊版);下載約 1.6MB,家用 WiFi 約 5~10 秒。</p><p><b>RGB 狀態燈</b>:輸出位置(面板 / 面板+內建(預設)/ 內建,即時切換)、亮度(拖滑桿 →「預覽」試 5 秒 → 滿意「套用」儲存;分兩步是避免連續寫入造成連線卡頓)、狀態樣式 5 組(狀態=無 / 高溫 / 冷卻 / 待機 / 運轉 × 色相 × 模式 × 週期,同樣預覽 / 套用兩步)。</p><p><b>工程模式</b>:需密碼(密碼錯 3 次鎖 60 秒,10 分鐘無操作自動登出)。</p>"
            )},
            {"id": "safety", "t": "十四、安全與保護", "html": (
                "<p class='manual-intro'>機器在任何驅動馬達的程序(磨合 / 測試 / 特性量測 / 軸承 / 電刷 / 健康檢測)中全程自動監測,異常時<b>立即停止並跳出說明框</b>:</p><table class='manual-table'><thead><tr><th>保護</th><th>觸發時機</th><th>反應</th></tr></thead><tbody><tr><td>未偵測到馬達</td><td>通電但無馬達電流(未裝或接線鬆脫)</td><td>&lt; 3 秒內停</td></tr><tr><td>馬達卡住</td><td>高電流但不轉(卡死)</td><td>&lt; 5 秒內停</td></tr><tr><td>讀不到轉速訊號</td><td>有吃電流但轉速持續為 0(<b>馬達未上治具</b>或感測異常)</td><td>&lt; 4 秒內停</td></tr><tr><td>輸出短路</td><td>輸出端子近乎短路</td><td>緊急停止(&lt; 0.15 秒)</td></tr><tr><td>高溫</td><td>超過設定溫度</td><td>立即停 + 鎖定</td></tr></tbody></table><p>觸發時<b>蜂鳴器響 4 長聲</b>,畫面彈出「運轉已停止」+ 原因,排除後可重新啟動。<b>供電規格 DC 5V / 6A(不可低於)</b>;供電不足時頂部會出現琥珀色警示「可能無法達到設定電壓」,供電夠力才能輸出準確電壓。</p><table class='manual-table'><thead><tr><th>機制</th><th>觸發 / 行為</th></tr></thead><tbody><tr><td>高溫保護</td><td>兩種觸發:① 溫度感測器警報;② 當前溫度高於「高溫鎖定溫度」設定值 5°C 以上持續 10 秒。任一觸發 → 立即停 + 嗶 5 聲 + 鎖定。<b>即使溫度已降回也須按「歸零」才解除</b>(仍高溫時按歸零會再次鎖定,須先降溫)。鎖定期間狀態列 / 旗標 / 狀態燈持續顯示高溫,首頁只剩「馬達磨合 / 馬達測試」可進、操作頁只剩「歸零 / 回首頁」可按。</td></tr><tr><td>緩啟動 / 緩停止</td><td>啟動為 5 秒線性升壓(0V→目標電壓),停止為 3 秒線性下降,避免電流爆衝與機械衝擊。</td></tr><tr><td>電流上限</td><td>固定 4A 量測上限,超過讀值封頂(不停機,但長時間高電流可能觸發高溫)。</td></tr><tr><td>開機鎖定</td><td>開機 30 秒內連續 3 次崩潰 → 自動切回上一版韌體。</td></tr></tbody></table>"
            )},
            {"id": "wifireset", "t": "十五、WiFi 重設(救援)", "html": (
                "<p class='manual-intro'><b>用途</b>:忘記 WiFi 名稱 / 密碼時,把熱點重設回 <code>MotorTester</code> / <code>12345678</code>。</p><p><b>做法</b>:把機器上的「WiFi 重設」接點短接(或按對應按鈕)<b>持續 5 秒</b> → 嗶 10 聲 → 自動重啟。</p><p><b>只重設 WiFi 熱點名稱與密碼</b>,以下全部保留:磨合參數 / 各項校正與設定 / <b>Pro 授權</b> / 歷史紀錄 / 馬達指紋 / RGB 設定 / 已記憶外部 WiFi。</p>"
            )},
            {"id": "faq", "t": "十六、常見問題", "html": (
                "<table class='manual-table'><thead><tr><th>問題</th><th>處理</th></tr></thead><tbody><tr><td>開機沒嗶聲</td><td>確認電源 5V</td></tr><tr><td>連得上但網頁打不開</td><td>確認是 <code>http://</code>(非 https)、關行動數據、強制重整(Ctrl+Shift+R)</td></tr><tr><td>一直顯示「套用中…」</td><td>通常 WiFi 不穩,重整網頁即可(內建 8 秒監視會轉紅字提示)</td></tr><tr><td>長時間磨合中手機 / 平板斷線</td><td>裝置閒置會自動斷開熱點,屬正常現象 —— 重新連上機器 WiFi 並重整頁面即可;磨合在機器端持續進行,不受斷線影響</td></tr><tr><td>忘記 WiFi 密碼連不上</td><td>用機上 WiFi 重設接點長按 5 秒(見「十五、WiFi 重設」),只重設熱點名稱與密碼,其他設定與紀錄全保留</td></tr><tr><td>響了 4 長聲自動停機,怎麼恢復</td><td>依畫面顯示的原因排除(馬達未夾緊 / 端子接觸不良 / 輸出短路 / 感測器沒對準)→ 不用重開機,直接重新「啟動」即可,故障狀態會自動清除</td></tr><tr><td>一啟動幾秒就自動停</td><td>通常是保護動作,看畫面原因:電流過低=馬達沒接好;電流過高=卡轉或短路;另檢查是否有供電不足紅色警示</td></tr><tr><td>馬達在轉但轉速顯示 0</td><td>檢查反射標記是否面向感測器、治具是否對準;避免強光直射感測區。持續讀不到會觸發保護自動停機(約 4 秒)</td></tr><tr><td>高溫鎖定解不開</td><td>等溫度降到門檻以下再按「歸零」;若環境溫度偏高,可到系統設定調高門檻(上限 60°C)或檢查溫度校正補償</td></tr><tr><td>轉速模式階段標「未達標」</td><td>目標轉速超過該馬達能力(以安全上限電壓跑滿時間收尾)→ 調低目標轉速;若馬達明明有力,檢查治具架設與感測器</td></tr><tr><td>智慧模式適用哪些馬達</td><td>碳刷系列;其他型號請用電壓或轉速模式</td></tr><tr><td>智慧模式為什麼有時跑很久</td><td>它磨到「偵測到穩態」才停,每顆馬達狀況差異大;可用時間上限(2h / 3h / 4h)兜底</td></tr><tr><td>磨合要磨幾趟才夠</td><td>沒有標準答案,看「穩定」指標是否收斂;不想自己判斷就用智慧模式,磨到穩態自動停</td></tr><tr><td>加了「導電磨合油」數值特別漂亮</td><td>那是碳粉暫時導電的<b>假象</b>,非真實磨合。請洗淨油品後再量測;本機判定基於馬達真實電氣狀態,導電油會使讀數失真偏樂觀(詳見「五、馬達磨合」警告)</td></tr><tr><td>同一顆馬達每次量的數值有點不同</td><td>正常。電刷接觸與溫度會造成小幅自然漂移;判讀看<b>趨勢與多次平均</b>,不要比單點</td></tr><tr><td>我的數據跟別人 / 網路上的比不起來</td><td>電壓基準、供電、治具、量測方式不同都會造成系統性差異;<b>同一台機器上的前後比較</b>最可靠</td></tr><tr><td>KV 值是什麼</td><td>目前轉速 ÷ 馬達實得電壓(rpm/V),快速比對馬達狀態的指標 —— 同電壓下數字越高轉得越快</td></tr><tr><td>支援哪些馬達</td><td>田宮 Mini 4WD 130 型馬達(單軸 / 雙軸皆可上治具)</td></tr><tr><td>供電器有什麼要求</td><td>DC 5V / 6A 以上、具安規認證;供電不足時介面會出現警示,常見於線材過細或小瓦數供電器。⚠ <b>規格不符的電源會損壞機器並有火災風險,且不予保固</b>(見「十四、安全與保護」)</td></tr><tr><td>取得授權卡在連線</td><td>家裡 WiFi 密碼錯 / 無外網 / 訊號弱 → 重輸入或換 WiFi</td></tr><tr><td>Pro 退費後</td><td>機器連網重驗時<b>自動退回 M1</b>;想再買按「重新取得授權」</td></tr><tr><td>紅色「AP 密碼仍為預設」橫幅</td><td>至 WiFi 設定改密碼</td></tr><tr><td>量測資料會上傳雲端嗎</td><td>不會,100% 存在機器本機;只有你主動按「上傳」的配方會進全球資料庫</td></tr><tr><td>歷史紀錄滿 50 筆會怎樣</td><td>預設自動覆蓋最舊一筆(可關閉);重要紀錄建議先匯出 JSON/CSV</td></tr><tr><td>軟體更新會清掉我的紀錄嗎</td><td>不會,更新保留所有設定、校正與歷史紀錄</td></tr><tr><td>更新失敗會變磚嗎</td><td>不會,有自動回退到前一版本</td></tr><tr><td>待機可拔電源嗎</td><td>可,建議馬達完全停止、無「套用中」、無更新進行中</td></tr></tbody></table>"
            )},
            {"id": "leds", "t": "十七、狀態燈號與聲響提示", "html": (
                "<p><b>狀態燈</b>(預設配置,可在「RGB 狀態燈」修改):</p><table class='manual-table'><thead><tr><th>系統狀態</th><th>預設</th><th>含義</th></tr></thead><tbody><tr><td>高溫鎖定</td><td>紅閃</td><td>觸發高溫保護,須降溫並按「歸零」</td></tr><tr><td>冷卻中</td><td>黃常亮</td><td>階段間冷卻,馬達靜止</td></tr><tr><td>待機</td><td>藍呼吸</td><td>等待指令</td></tr><tr><td>運轉中</td><td>綠呼吸</td><td>磨合 / 測試 / 檢測中</td></tr><tr><td>燈滅</td><td>—</td><td>無匹配或全關</td></tr></tbody></table><p><b>聲響提示</b>(蜂鳴器,不可自訂;所有聲響於事件發生後約 1 秒響起——待馬達降速,聲聲清晰):</p><table class='manual-table'><thead><tr><th>聲響</th><th>情境</th></tr></thead><tbody><tr><td>賽車倒數 4 響(3 短 + 1 長高音)</td><td>開機完成</td></tr><tr><td>2 聲</td><td>馬達測試完成</td></tr><tr><td>3 聲</td><td>磨合完成(電壓 / 轉速模式全部趟跑完;智慧模式磨合完成自動停止)</td></tr><tr><td>5 短聲</td><td>高溫鎖定(須降溫後按「歸零」解除)</td></tr><tr><td><b>4 長聲</b></td><td><b>馬達故障停機</b>(未偵測到馬達 / 卡住 / 讀不到轉速 / 輸出短路,畫面同步顯示原因)</td></tr><tr><td>10 聲</td><td>WiFi 重設觸發(隨後自動重啟)</td></tr></tbody></table><p class='manual-contact'><b>回報問題</b>請一併提供:韌體版本(系統設定 → 軟體更新)、版本變體(首頁 M1 / PRO)、問題畫面截圖、是否在運轉中、重現步驟。客服:<b>motorlab.tw@gmail.com</b></p>"
            )},
        ],
        "en": [
            {"id": "precautions", "t": "0. Read First — Safety", "html": (
                "<div class='manual-note'><b>Read this chapter before first use. The user bears sole responsibility for any injury, property loss or machine damage caused by use that ignores these safety notes, which is also not covered by warranty.</b></div>"
                "<h3>🔴 Power safety</h3><ul><li>Use a <b>DC 5V / 6A or higher</b>, <b>safety-certified</b> power adapter.</li><li><b>Using an out-of-spec adapter (over-voltage, poor quality, uncertified, unknown origin or modified) will damage the machine and risks fire; resulting faults or damage are not covered by warranty.</b></li><li>Stop using if the power cable or connector is damaged, hot or smells odd.</li></ul>"
                "<h3>🔴 Operation safety (high-speed rotation)</h3><ul><li><b>While the motor is running, never touch the shaft, gears or reflector with hands, tools or any object</b> — high-speed rotation can cut, entangle or fling parts.</li><li>Confirm the motor is <b>firmly mounted on the jig</b> before running; an unsecured motor may fly off.</li><li>Keep <b>face, hair, loose clothing and jewellery</b> away from a running motor.</li><li>The motor and nearby parts get <b>hot</b> after running — do not touch bare-handed right after stopping.</li><li>If you notice abnormal noise, smell, smoke or sparks, <b>cut the power immediately</b> and inspect.</li></ul>"
                "<h3>🔴 Environment safety</h3><ul><li><b>Not waterproof</b>: keep away from water, damp and rain; do not let liquids (water, oil, drinks) splash onto the body or circuitry.</li><li>Place on a <b>flat, solid, heat-resistant, non-flammable</b> surface; never run it on carpet, paper or flammable materials.</li><li>Keep the surroundings <b>ventilated</b>; do not cover the vents; do not run for long in a sealed, hot space.</li><li>Keep away from fire, heat sources and direct sunlight.</li></ul>"
                "<h3>🔴 Handling safety</h3><ul><li><b>Children must be supervised by an adult</b>; parts and motors contain small items and sharp edges.</li><li>Do not disassemble or modify the machine or circuit; do not drive non-specified motors or loads.</li><li><b>The terminals are only for connecting a motor</b> — do not connect batteries, power or other loads, to avoid short-circuit damage.</li><li>Unplug the power when not in use for a long time.</li></ul>"
                "<h3>⚠ Measurement data note</h3><ul><li>Data is <b>only for before/after and relative comparison on the same machine</b>; readings differ systematically across devices/instruments — <b>do not compare directly with others or market figures</b>.</li><li>Do not use <b>conductive break-in oil</b> during measurement (it distorts readings; see &quot;5. Break-in&quot;).</li></ul>"
                "<p class='manual-intro'>The machine has multiple automatic safeguards — overheat protection, over-current / short-circuit / stall / off-jig detection, soft start/stop (see &quot;14. Safety &amp; Protection&quot;) — but these are aids and <b>cannot replace safe operation and supervision</b>.</p>"
            )},
            {"id": "start", "t": "1. Quick Start", "html": (
                "<div class='manual-note'>🔴 <b>Before connecting power</b>: use a <b>DC 5V / 6A or higher</b>, safety-certified adapter. <b>An out-of-spec adapter can damage the machine or even cause fire, and voids the warranty</b> (see &quot;0. Read First&quot; and &quot;14. Safety &amp; Protection&quot;).</div>"
                "<ol><li>Connect power → the onboard indicator lights up and you hear the startup beep.</li><li>On your phone / tablet / PC, join the WiFi network <b>MotorTester</b> (default password <code>12345678</code>).</li><li>Open <code>http://10.10.10.1/</code> in a browser.</li><li><b>Do this first</b>: System Settings → WiFi Settings, change the password to a strong one (otherwise anyone can operate the machine).</li></ol>"
            )},
            {"id": "connect", "t": "2. Connection", "html": (
                "<table class='manual-table'><tbody><tr><th>URL</th><td><code>http://10.10.10.1/</code> (<b>not</b> https)</td></tr><tr><th>Hotspot</th><td><code>MotorTester</code> / <code>12345678</code> (renameable)</td></tr><tr><th>Device</th><td>Phone / tablet / laptop all work; a larger screen is recommended</td></tr><tr><th>Connections</th><td><b>Only one device can control at a time</b> (single session, see below)</td></tr><tr><th>Note</th><td>The machine hotspot has <b>no internet access</b>; if iPhone shows “No Internet,” choose “Keep”</td></tr></tbody></table><p><b>Single session (switching between devices)</b>: only one device may control the interface at a time, to avoid two devices issuing conflicting commands.</p><ul><li><b>The newest device takes over</b>: opening the interface on a new device makes it the controller.</li><li><b>The old device is disabled</b>: it shows “taken over by another device” and stops updating (values and charts freeze).</li><li><b>To switch back</b>: simply <b>refresh the page</b> on that device to reclaim control.</li><li>Switching devices does not affect a break-in / test in progress — the program keeps running on the machine, and the new device shows the current progress on connect.</li></ul>"
            )},
            {"id": "home", "t": "3. Home Screen", "html": (
                "<p>Ten function buttons:</p><p class='manual-pills'>Motor Characterization · Break-in · Motor Test · History · AI Motor Health (Pro) · Bearing Resistance · Brush Stability · Global Break-in Database · Tamiya Motor Specs · System Settings</p><p>The title shows <code>MotorLab M1</code> or <code>MotorLab PRO</code>.</p>"
            )},
            {"id": "charexp", "t": "4. Motor Characterization", "html": (
                "<p class='manual-intro'>Automatically measures a motor’s characteristic parameters and losses, giving <b>reference data — no scoring, no ranking</b>. Compare same-model motors and judge for yourself. The system <b>runs 3 consecutive passes and averages them</b>, about 5 minutes, gentle enough for brand-new un-run motors.</p><p><b>How to run</b>: Home → “Motor Characterization” → pick direction (default forward) + pick <b>motor model</b> (16-model dropdown) + add a <b>note</b> (optional, up to 40 chars) → “Start” → fully automatic (shows pass number and progress); do not touch the motor → on completion it shows the data table and <b>auto-saves to the measurement log</b>.</p><p><b>Reading the data (each row is labeled with its direction)</b>:</p><ul><li><b>★ I0 (no-load current)</b>: at the same speed, <b>lower is better</b> — the most repeatable metric and the primary one for grading motors.</li><li><b>★ Km (quality factor) / ★ T_loss (loss torque)</b>: supporting metrics (higher Km is better, lower T_loss is better).</li><li><b>Ke (magnetic strength)</b>: no absolute good/bad — only meaningful when comparing motors with similar values (higher = torque-leaning, lower = speed-leaning).</li><li><b>KV (speed constant, rpm/V)</b>: converted from Ke — KV × voltage ≈ no-load speed (e.g. KV 14000 × 3V ≈ 42000 RPM), handy for comparing with published ratings.</li><li><b>R (internal resistance)</b>: lower is better.</li><li><b>Startup voltage</b>: reference only — highly random in a single run; best used to track one motor over time (a clear rise later = bearing / brush wear warning).</li><li><b>Loss-fit R² / Ke drift</b>: data-quality indicators (closer to 1 and lower drift = more trustworthy).</li><li><b>3-pass consistency</b>: the max spread of I0 across passes; a warning flag means the motor is unstable or the mounting is loose, so treat that reading as reference only — check and re-measure.</li></ul><p><b>Measurement log</b>: Measurement page → “Log.” Every successful run is saved automatically (all metrics and per-speed-point data), up to <b>50 entries</b>; the oldest is deleted when full. You can view details or delete.</p><p><b>Suggested use</b>:</p><ul><li>Measure a batch of new motors one by one → pick the good ones by ★I0 before investing break-in time.</li><li>After break-in, <b>re-measure the same motor</b>: loss metrics should drop (break-in worked); Ke / R should barely change.</li><li>Compare motors at <b>similar temperatures</b>; the first reading after mounting or a cold restart may run high — rely on the second onward.</li></ul><div class='manual-note'><b>Note</b>: a failed run (motor didn’t start / lock timeout / overcurrent) shows the reason — just retry. If it keeps failing, or speed reads non-zero while idle, check the alignment of the speed sensor and reflector.</div>"
            )},
            {"id": "breakin", "t": "5. Break-in (Three Modes)", "html": (
                "<p class='manual-intro'>Long, low-speed running that beds the brushes to the commutator. The top of the break-in page has <b>three mode buttons</b> (cannot switch while running).</p><table class='manual-table'><thead><tr><th>Mode</th><th>Best for</th><th>In one line</th></tr></thead><tbody><tr><td><b>Voltage mode</b></td><td>Players with their own recipe</td><td>Fixed voltage per stage (the classic way)</td></tr><tr><td><b>Speed mode (Beta)</b></td><td>Players who prefer an RPM target</td><td>Auto speed-control to your target; advances when voltage stabilizes</td></tr><tr><td><b>Smart mode (Beta)</b></td><td>Players who want it hands-off</td><td>One-tap auto break-in: the machine runs, measures and stops itself</td></tr></tbody></table><h3>Voltage mode</h3><p>Home → “Break-in Program” → pick <b>motor model</b> (16) + <b>note</b> (up to 40 chars) → pick <b>stop criterion</b> (Time-only = each stage runs its full time; Smart stable-current = advance early once current settles, time is the cap) → pick <b>passes</b> (1–6, default 1) → confirm the 10-stage parameters for each pass (use the tabs to switch passes; click a number cell to edit) → “Start.”</p><ul><li>Each stage: voltage (0.6–4.0V, <b>0 = skip</b>) / direction / run seconds (10–600, default 60) / cooling seconds (10–600, default 60) / stable-current tolerance (2–50mA).</li><li>With multiple passes, “<b>copy this pass to all following</b>” fills the table fast; the <b>estimated total time</b> shows next to the pass count.</li><li>Out-of-range input is auto-clamped to the limit with a single flash.</li></ul><div class='manual-note'><b>Tip</b>: for a brand-new motor the brushes and commutator are not yet shaped — you can tighten the tolerance gradually from loose to tight across passes.</div><h3>Speed mode (Beta)</h3><p>Same 10-stage table as voltage mode, but the first column becomes <b>target RPM</b> (6000–30000, steps of 1000, <b>0 = skip</b>) — the machine adjusts voltage to lock the motor at that speed.</p><ul><li><b>Stop criterion</b> (Strict / Standard / Loose): once the drive voltage at that speed is stable, the stage is considered broken-in and advances early; the run seconds act as an upper bound. Strict = needs to be steadier (deeper, longer); Loose = advances faster (switch to it if a brand-new motor never advances).</li><li>The stage result column shows the <b>stable voltage</b>; if the motor can’t reach the target RPM it runs the full time at the safe voltage cap and is flagged <b>“not reached”</b> (usually the target is set too high, or the motor / jig is faulty).</li><li>Direction, time, passes and copy all work the same as voltage mode.</li></ul><h3>Smart mode (Beta)</h3><p>One-tap auto break-in <b>for brushed Dash-series models</b>: pick <b>model</b> + <b>note</b> + <b>time cap</b> (until done / 2h / 3h / 4h) → “Start,” the rest is automatic — the system runs at progressive speeds while measuring, and <b>stops automatically once it detects steady state (the motor no longer improves)</b> with a beep.</p><ul><li>Live display: current round / current action / elapsed time / convergence progress, plus a <b>break-in metric curve</b> (per-round points + moving average; a flattening curve = near done).</li><li>The motor <b>alternates forward/reverse</b> (bedding both brush faces symmetrically) and measures periodically; rhythmic changes in sound and speed are normal.</li><li>You can press “Stop” anytime for a graceful finish (it stops after finishing the current round). Use voltage / speed mode for other models.</li></ul><div class='manual-note'><b>Important: do not use “conductive break-in oil” when measuring / breaking in.</b> Some break-in oils marketed as “conductive” (they contain conductive carbon powder) make RPM jump and voltage drop the instant you add them — that’s <b>not real break-in, just an illusion from the carbon temporarily conducting</b>. Every judgment here (stable current / RPM / internal resistance) measures the <b>true brush-commutator contact</b>; conductive oil skews readings optimistically and reverts once washed off. Correct approach: don’t use such oils at all; if you already did, wash it off thoroughly before measuring. Normal light bearing lubrication is unaffected — this warning is only about “conductive break-in oil.”</div><h3>Common behavior</h3><p>Each stage: soft-start → running → soft-stop → cooling → next stage; after a pass it auto-continues to the next (shows “pass x/y · stage c”). All done → 3 beeps → auto-saved to History (voltage / speed mode, with every pass and stage result).</p><p><b>While running you can press</b>:</p><table class='manual-table'><thead><tr><th>Button</th><th>Action</th></tr></thead><tbody><tr><td>Stop</td><td>Soft-stops and ends; record marked “user aborted”</td></tr><tr><td>Reset</td><td>Clears max-RPM / stable-current peaks without interrupting</td></tr><tr><td>Home</td><td>Returns home; break-in <b>keeps running in the background</b></td></tr></tbody></table><div class='manual-note'><b>Note</b>: all settings lock while running; don’t cut power mid-run (data loss); overheating auto-stops and saves; to bench-check quickly, shorten each stage’s time. One extra live field, <b>KV (rpm/V)</b> = current speed ÷ motor voltage, for a quick read on motor state.</div>"
            )},
            {"id": "test", "t": "6. Motor Test", "html": (
                "<p class='manual-intro'>Single-stage live observation, <b>not written to records</b>.</p><p>Home → “Motor Test” → set <b>voltage (0.6–4.0V, default 1V) / run time (10–600 s, default 60) / direction / stable-current tolerance (2–50mA) / stop criterion</b> (Time-only or Smart stable-current = end early once current settles, default the latter; this setting is <b>independent</b> from the break-in page) → “Start” → watch live data and charts (incl. live <b>KV</b>); it stops automatically at time or on stabilization.</p><div class='manual-note'><b>Note</b>: the 4.0V ceiling protects the motor — don’t bypass it; press “Stop” once before switching from reverse to forward.</div>"
            )},
            {"id": "records", "t": "7. History", "html": (
                "<p class='manual-intro'>Automatically saves the full data of every break-in, up to <b>50 entries</b>.</p><p>Each entry shows name / start time / duration / mode / end reason / max RPM / average RPM / stable current.</p><table class='manual-table'><thead><tr><th>Button</th><th>Use</th></tr></thead><tbody><tr><td>View</td><td>See per-stage data (multi-pass records include every pass and stage)</td></tr><tr><td>Apply</td><td>One-tap load the recipe (passes + each pass’s 10 stages) back to the break-in page; old single-pass records apply as pass count = 1</td></tr><tr><td>Export</td><td>Download JSON (re-importable) or CSV (opens in Excel)</td></tr><tr><td>Delete</td><td>Remove (irreversible)</td></tr></tbody></table><ul><li><b>When full (50)</b>: in management you can choose “auto-overwrite” (delete oldest on start) or “no overwrite” (default; start is blocked, clear manually).</li><li><b>Import</b>: pick a previously exported JSON (matching id overwrites). JSON only. Each export carries a <b>signature check</b>: files interoperate across the same / same-batch machine; tampered or foreign-batch files are rejected; renaming doesn’t matter (the content is verified).</li><li><b>Filename</b>: <code>motorlab_&lt;date&gt;_&lt;time&gt;_&lt;model&gt;[_&lt;note&gt;]</code>, using the break-in start time → re-exports of the same entry share a filename.</li><li>Firmware update / WiFi reset <b>never clear records</b>.</li></ul>"
            )},
            {"id": "database", "t": "8. Global Break-in Database", "html": (
                "<p class='manual-intro'>Share break-in records with players worldwide, done <b>directly from the machine online</b> — no export-then-upload. Requires a <b>WiFi with internet</b> (M1 / Pro both work).</p><p><b>Browse / download</b>: Home → “Global Break-in Database” → once online it lists the latest 100 → filter live by <b>motor model / country / completion status</b> → each entry offers “Download” (save locally) or “Download &amp; Apply” (save and load the recipe to the break-in page).</p><p><b>Share your own</b>: History → open an entry → “Share to Global Database” at the bottom → the confirm box <b>lists exactly what will be public</b> (model / note / sharer / country / full data; if you filled in a name it warns your real name shows) → confirm upload. If already uploaded, it says “already in the database” (not an error).</p><div class='manual-note'><b>Note</b>: downloaded records pass a signature check; uploading means agreeing to make it public — to remove, email <b>motorlab.tw@gmail.com</b>; connecting to WiFi without internet shows “cannot reach server.”</div>"
            )},
            {"id": "health", "t": "9. AI Motor Health (Pro)", "html": (
                "<p class='manual-intro'>Builds a health fingerprint for each motor, re-tests periodically and gives a 0–100 score with advice. <b>Compares a motor to itself, not to others</b>.</p><ol><li>Home → “AI Motor Health” → “+ Add Motor.”</li><li>Fill in <b>model</b> (dropdown) + <b>note</b> (optional) + <b>start voltage</b> + <b>voltage step</b> (5 points auto-picked).</li><li>Confirm → runs about <b>2.5 minutes</b> to build the baseline.</li></ol><p>Afterwards each card offers a <b>Full check</b> (~2.5 min, most accurate) or <b>Quick check</b> (~1.5 min, ±5%). The result page shows the score, grade (Optimal / Acceptable / Warning / Critical), trend chart, five metrics and written advice.</p><div class='manual-note'><b>Note</b>: up to 50 records per motor, 20 motors per machine; don’t cut power or press other buttons mid-check; overheating auto-aborts; M1 buttons are grayed out (tapping prompts an upgrade).</div>"
            )},
            {"id": "bearing", "t": "10. Bearing Resistance Test", "html": (
                "<p class='manual-intro'>Measures bearing smoothness, works on any edition. <b>Longer time-to-full-stop → smoother bearing</b>.</p><p>Home → “Bearing Resistance Test” → pick test voltage (<b>2.4V or 3V</b>) → “Start” → the machine spins up to that voltage → holds steady 5 s → <b>cuts power directly (no braking)</b> → times until fully stopped → shows <b>time to full stop</b>.</p><div class='manual-note'><b>Note</b>: an unloaded motor has little inertia, so this test <b>only shows time and makes no good/bad judgment</b> — compare the same motor at different times, or different motors; the speed sensor must work; run 2–3 times for repeatability.</div>"
            )},
            {"id": "brush", "t": "11. Brush Contact Stability Test", "html": (
                "<p class='manual-intro'>Measures whether brush contact is even, about 35 s, any edition. <b>Uneven contact → jittery current → higher CV</b>.</p><p>Home → “Brush Contact Stability Test” → “Start” (<b>no need to turn the shaft by hand</b>). The flow is fixed at <b>1V</b>: voltage ramps 0→1V over 10 s → holds 1V for 5 s → samples current at 1V for 20 s → shows the <b>current coefficient of variation CV%</b>.</p><p><b>Reading CV%</b>: CV is how much current jitters at a fixed voltage — <b>a relative comparison tool with no absolute good/bad line</b> (models differ by nature). Suggested use:</p><ul><li>Same motor, <b>before vs after break-in</b>: falling CV = brushes bedded, better contact.</li><li>Same motor, <b>long-term tracking</b>: rising CV = brush wear / dirty commutator.</li><li><b>Motor A vs B</b> relative comparison.</li></ul><div class='manual-note'><b>Note</b>: the fixed 1V and fixed flow are what make cross-run / cross-motor comparison fair; run 2–3 times for repeatability.</div>"
            )},
            {"id": "tamiya", "t": "12. Tamiya Motor Specs", "html": (
                "<p class='manual-intro'>A built-in quick-reference of 15 Tamiya Mini 4WD motors’ official specs (PRO dual-shaft 6 + standard single-shaft 9): model / load RPM / current / voltage / torque.</p><ul><li>Listed values are <b>Tamiya’s officially published recommended-load figures</b> (proper voltage 2.4–3.0V); if models are added or specs change, Tamiya’s latest published spec prevails.</li><li>Ultra-Dash and Plasma-Dash exceed official race-rule limits and are banned in official races.</li><li>This product has no affiliation with TAMIYA, INC. and is not authorized, sponsored or endorsed by it.</li></ul>"
            )},
            {"id": "settings", "t": "13. System Settings", "html": (
                "<p class='manual-intro'>While the system is running, only “Home” is active on this page; the rest is locked.</p><table class='manual-table'><tbody><tr><th>User settings</th><td>Name / country (up to 32 chars, default <code>--</code>), written into each record as its source. Existing records are not back-filled.</td></tr><tr><th>WiFi settings</th><td>Change hotspot name / password (8–63 chars) → the machine restarts after saving; reconnect to the new hotspot. Forgot the password? See Chapter 15.</td></tr><tr><th>Language</th><td>Chinese / English / Japanese (default Chinese). Pressing OK <b>restarts the system</b> for a clean load (~10 s); switching while running only reloads the page without interrupting the program.</td></tr><tr><th>Authenticity check</th><td>Shows the unit ID; verify your machine is genuine on the official site’s check page (since v3.4.1).</td></tr><tr><th>Temperature calibration</th><td>Add compensation when the reading differs from actual (±20°C).</td></tr><tr><th>Overheat lock</th><td>Set the overheat-lock temperature (default 50°C, range 25–60°C). If the current temperature stays 5°C above the setting for 10 s, it enters overheat lock (stops; press Reset to clear). The block also shows current temperature.</td></tr><tr><th>Average-speed setting</th><td>Tolerance (RPM diff between adjacent seconds) dropdown 120–600 RPM, <b>default 240</b>. A larger tolerance judges “stable” more easily but reacts slower; raise it for less-stable motors.</td></tr><tr><th>Soft-start</th><td>Voltage ramps linearly from 0 to target over 5 s (same style as soft-stop), <b>no adjustable parameters</b>. Voltage output is calibrated; no start-torque setting needed.</td></tr><tr><th>Get license</th><td>Upgrade M1 to Pro, see below.</td></tr><tr><th>Software update</th><td>Fetch the latest firmware automatically over home WiFi, see below.</td></tr><tr><th>RGB status light</th><td>Dual lights (built-in / panel) output location + brightness (0–100%) + 5 status styles, see below.</td></tr><tr><th>Engineering mode</th><td>Password-protected advanced calibration and offline update (not needed by regular users).</td></tr><tr><th>WiFi list</th><td>Remembers up to 8 external WiFi networks; “clear list” is for handing the device on (does not affect Pro licensing).</td></tr></tbody></table><p><b>Get license (M1 → Pro)</b>: System Settings → “Get License” → pick your home WiFi → the machine verifies your purchase automatically → if not purchased it shows a QR code → scan and check out on another internet device → the machine polls every 10 s and unlocks on payment. About 1–3 minutes, <b>no manual key entry</b>, retry if it times out (max 10 min).</p><p><b>Software update</b>: System Settings → “Check for updates” → pick WiFi → a new version downloads and writes automatically (progress to 100%) → auto-restart, page auto-reloads. <b>Don’t cut power / close the browser</b> during it (a power cut mid-way is protected and rolls back); ~1.6MB download, ~5–10 s on home WiFi.</p><p><b>RGB status light</b>: output location (panel / panel+built-in / built-in, switches live), brightness (drag slider → “Preview” for 5 s → “Apply” to save), and 5 status styles (status = none / overheat / cooling / idle / running × hue × mode × period, same Preview / Apply two-step).</p><p><b>Engineering mode</b>: requires a password (3 wrong tries locks it for 60 s; auto-logout after 10 min idle).</p>"
            )},
            {"id": "safety", "t": "14. Safety &amp; Protection", "html": (
                "<p class='manual-intro'>During any motor-driving program (break-in / test / characterization / bearing / brush / health check) the machine monitors continuously and, on any anomaly, <b>stops immediately and pops up an explanation</b>:</p><table class='manual-table'><thead><tr><th>Protection</th><th>Trigger</th><th>Response</th></tr></thead><tbody><tr><td>No motor detected</td><td>Powered but no motor current (not fitted or loose wiring)</td><td>Stops in &lt; 3 s</td></tr><tr><td>Motor stalled</td><td>High current but not turning (jammed)</td><td>Stops in &lt; 5 s</td></tr><tr><td>No speed signal</td><td>Drawing current but speed stays 0 (<b>motor not on the jig</b> or sensor fault)</td><td>Stops in &lt; 4 s</td></tr><tr><td>Output short</td><td>Output terminals near a short</td><td>Emergency stop (&lt; 0.15 s)</td></tr><tr><td>Overheat</td><td>Above the set temperature</td><td>Stops immediately + locks</td></tr></tbody></table><p>On trigger the <b>buzzer sounds 4 long beeps</b>, and the screen pops “Operation stopped” + reason; restart after resolving. <b>Power spec DC 5V / 6A (do not go below)</b>; when supply is insufficient an amber warning appears at the top — accurate output needs adequate supply.</p><table class='manual-table'><thead><tr><th>Mechanism</th><th>Trigger / behavior</th></tr></thead><tbody><tr><td>Overheat protection</td><td>Two triggers: (1) temperature-sensor alarm; (2) current temp 5°C above the “overheat-lock” setting for 10 s. Either → immediate stop + 5 beeps + lock. <b>Even after it cools you must press “Reset” to clear</b> (pressing Reset while still hot re-locks).</td></tr><tr><td>Soft-start / soft-stop</td><td>Start is a 5 s linear ramp (0V→target), stop is a 3 s linear ramp down, avoiding current surges and mechanical shock.</td></tr><tr><td>Current ceiling</td><td>Fixed 4A measurement ceiling; readings cap above it (no stop, but sustained high current may trigger overheat).</td></tr><tr><td>Boot lock</td><td>3 consecutive crashes within 30 s of boot → auto-rollback to the previous firmware.</td></tr></tbody></table>"
            )},
            {"id": "wifireset", "t": "15. WiFi Reset (Rescue)", "html": (
                "<p class='manual-intro'><b>Purpose</b>: when you forget the WiFi name / password, reset the hotspot back to <code>MotorTester</code> / <code>12345678</code>.</p><p><b>How</b>: short the “WiFi Reset” contact on the machine (or press the matching button) and <b>hold for 5 seconds</b> → 10 beeps → auto-restart.</p><p><b>Only the WiFi hotspot name and password are reset</b>; all of the following are kept: break-in parameters / all calibration and settings / <b>Pro license</b> / history / motor fingerprints / RGB settings / remembered external WiFi.</p>"
            )},
            {"id": "faq", "t": "16. FAQ", "html": (
                "<table class='manual-table'><thead><tr><th>Problem</th><th>Fix</th></tr></thead><tbody><tr><td>No beep on power-up</td><td>Check the 5V supply</td></tr><tr><td>Connects but page won’t open</td><td>Confirm <code>http://</code> (not https), turn off mobile data, hard-refresh (Ctrl+Shift+R)</td></tr><tr><td>Stuck on “Applying…”</td><td>Usually unstable WiFi — just refresh the page (a built-in 8-second monitor turns the text red)</td></tr><tr><td>Phone / tablet disconnects during a long break-in</td><td>Idle devices auto-drop the hotspot — this is normal; reconnect to the machine’s WiFi and refresh the page. The break-in keeps running on the machine, unaffected by the disconnect</td></tr><tr><td>Forgot the WiFi password, can’t connect</td><td>Hold the on-board WiFi-reset contact for 5 s (see “15. WiFi Reset”); it only resets the hotspot name and password — all other settings and records are kept</td></tr><tr><td>It stopped with 4 long beeps — how do I recover?</td><td>Clear the cause shown on screen (motor not clamped / poor terminal contact / output short / sensor misaligned) → no reboot needed, just press “Start” again; the fault state clears automatically</td></tr><tr><td>It auto-stops a few seconds after starting</td><td>Usually a protection action — check the on-screen reason: current too low = motor not connected; current too high = stalled or shorted; also check for a red under-supply warning</td></tr><tr><td>Motor spins but speed reads 0</td><td>Check that the reflective mark faces the sensor and the jig is aligned; avoid strong light on the sensor area. Persistent no-reading triggers a protective auto-stop (~4 s)</td></tr><tr><td>Overheat lock won’t clear</td><td>Wait for the temperature to drop below the threshold, then press “Reset”; if ambient is high, raise the threshold in System Settings (max 60°C) or check the temperature-calibration offset</td></tr><tr><td>Speed-mode stage flagged “not reached”</td><td>Target RPM exceeds the motor’s ability (it finishes the stage at the safe voltage ceiling) → lower it; if the motor is clearly strong, check the jig mounting and sensor</td></tr><tr><td>Which motors suit Smart mode</td><td>Brushed series; use voltage or speed mode for others</td></tr><tr><td>Why does Smart mode sometimes run so long?</td><td>It stops only when it “detects a steady state,” and motors vary a lot; the time cap (2h / 3h / 4h) is the backstop</td></tr><tr><td>How many passes is enough?</td><td>There’s no fixed answer — watch whether the “stable” metric converges; if you’d rather not judge, use Smart mode and it auto-stops at steady state</td></tr><tr><td>Numbers look great after “conductive break-in oil”</td><td>That’s an <b>illusion</b> from carbon powder temporarily conducting, not real break-in. Clean off the oil before measuring; the machine judges the motor’s true electrical state, and conductive oil skews readings optimistically (see the “5. Break-in” warning)</td></tr><tr><td>Same motor reads slightly different each time</td><td>Normal. Brush contact and temperature cause small natural drift; read the <b>trend and multi-run average</b>, don’t compare single points</td></tr><tr><td>My numbers don’t match other people’s / the internet</td><td>Different voltage baselines, supply, jigs and methods all cause systematic differences; <b>before-vs-after on the same machine</b> is the most reliable</td></tr><tr><td>What is KV?</td><td>Current RPM ÷ the motor’s actual voltage (rpm/V), a quick indicator of motor state — at the same voltage, higher means faster</td></tr><tr><td>Which motors are supported?</td><td>Tamiya Mini 4WD 130-type motors (single- or double-shaft, both fit the jig)</td></tr><tr><td>Power-supply requirements?</td><td>DC 5V / 6A or more, safety-certified; when supply is insufficient the UI shows a warning, common with thin cables or low-wattage adapters. ⚠ <b>An out-of-spec adapter can damage the machine and risks fire, and is not covered by warranty</b> (see &quot;14. Safety &amp; Protection&quot;)</td></tr><tr><td>Get License stuck connecting</td><td>Wrong home-WiFi password / no internet / weak signal → re-enter or switch WiFi</td></tr><tr><td>After a Pro refund</td><td>The machine <b>auto-reverts to M1</b> on the next online re-check; press “Get License” to buy again</td></tr><tr><td>Red “AP password still default” banner</td><td>Change the password in WiFi settings</td></tr><tr><td>Is my measurement data uploaded to the cloud?</td><td>No — it’s 100% stored on the machine; only recipes you actively “upload” go to the global database</td></tr><tr><td>What happens when history hits 50 records?</td><td>By default it auto-overwrites the oldest (can be turned off); export important records as JSON/CSV first</td></tr><tr><td>Will a software update wipe my records?</td><td>No — updates keep all settings, calibration and history</td></tr><tr><td>Can a failed update brick it?</td><td>No — there’s automatic rollback to the previous version</td></tr><tr><td>Can I unplug at idle?</td><td>Yes; best when the motor is fully stopped, no “Applying…,” no update in progress</td></tr></tbody></table>"
            )},
            {"id": "leds", "t": "17. Status Lights &amp; Sounds", "html": (
                "<p><b>Status lights</b> (default config, editable under “RGB status light”):</p><table class='manual-table'><thead><tr><th>System state</th><th>Default</th><th>Meaning</th></tr></thead><tbody><tr><td>Overheat lock</td><td>Red flashing</td><td>Overheat protection triggered; cool down and press “Reset”</td></tr><tr><td>Cooling</td><td>Yellow solid</td><td>Inter-stage cooling, motor idle</td></tr><tr><td>Idle</td><td>Blue breathing</td><td>Waiting for a command</td></tr><tr><td>Running</td><td>Green breathing</td><td>Break-in / test / check in progress</td></tr><tr><td>Off</td><td>—</td><td>No match or all off</td></tr></tbody></table><p><b>Sound cues</b> (buzzer, not customizable):</p><table class='manual-table'><thead><tr><th>Sound</th><th>Situation</th></tr></thead><tbody><tr><td>Race countdown, 4 beeps (3 short + 1 long high)</td><td>Boot complete</td></tr><tr><td>2 beeps</td><td>Motor test complete</td></tr><tr><td>3 beeps</td><td>Break-in complete (voltage / speed mode all passes done; Smart mode auto-stopped when done)</td></tr><tr><td>5 short beeps</td><td>Overheat lock (cool down, then press “Reset” to clear)</td></tr><tr><td><b>4 long beeps</b></td><td><b>Motor fault stop</b> (no motor / stalled / no speed signal / output short; the screen shows the reason)</td></tr><tr><td>10 beeps</td><td>WiFi reset triggered (auto-restart follows)</td></tr></tbody></table><p class='manual-contact'><b>Reporting an issue?</b> Please include: firmware version (System Settings → Software update), edition (M1 / PRO on home), a screenshot, whether it was running, and repro steps. Support: <b>motorlab.tw@gmail.com</b></p>"
            )},
        ],
        "ja": [
            {"id": "precautions", "t": "〇、使用前に必ずお読みください・安全上の注意", "html": (
                "<div class='manual-note'><b>初回使用前に本章を必ずお読みください。安全上の注意に従わない使用による人身傷害・財物損失・機器損傷については、使用者が自己責任を負うものとし、保証の対象外です。</b></div>"
                "<h3>🔴 電源の安全</h3><ul><li>本機には <b>DC 5V／6A 以上</b>、<b>安全規格認証済み</b>の電源アダプターを使用してください。</li><li><b>規格外の電源(過電圧・粗悪品・無認証・出所不明・改造品)は機器を損傷させ、火災の危険があります。これによる故障・損害は保証対象外です。</b></li><li>電源ケーブルやコネクタが破損・発熱・異臭がある場合は使用を中止してください。</li></ul>"
                "<h3>🔴 運転の安全(モーター高速回転)</h3><ul><li><b>モーター運転中は、手・工具・その他の物で回転軸・ギア・反射板に絶対に触れないでください</b>——高速回転により切創・巻き込み・飛散の危険があります。</li><li>運転前にモーターが<b>治具にしっかり固定</b>されているか確認してください。未固定のモーターは飛び出す恐れがあります。</li><li><b>顔・髪・ゆるい衣服・装飾品</b>を運転中のモーターに近づけないでください。</li><li>モーターと周辺部品は運転後<b>高温になります</b>。停止直後に素手で触れないでください。</li><li>運転中に異音・異臭・発煙・火花があれば、<b>直ちに電源を切り</b>点検してください。</li></ul>"
                "<h3>🔴 環境の安全</h3><ul><li><b>本機は防水ではありません</b>:水・湿気・雨から遠ざけて使用・保管し、液体(水・油・飲料)を本体や回路にかけないでください。</li><li><b>平らで頑丈・耐熱・不燃</b>の台に置いてください。カーペット・紙・可燃物の上で動作させないでください。</li><li>周囲の<b>通風・放熱</b>を保ち、放熱孔を塞がないでください。密閉した高温環境での長時間運転は避けてください。</li><li>火源・熱源・直射日光から遠ざけてください。</li></ul>"
                "<h3>🔴 操作の安全</h3><ul><li><b>お子様は大人の監督のもとで使用</b>してください。部品とモーターには小物や鋭利な縁が含まれます。</li><li>機器や回路を分解・改造しないでください。指定外のモーターや負荷を駆動しないでください。</li><li><b>端子はモーター接続専用</b>です。電池・電源・その他の負荷を接続しないでください(短絡損傷防止)。</li><li>長期間使用しない場合は<b>電源を抜いて</b>ください。</li></ul>"
                "<h3>⚠ 測定データの注意</h3><ul><li>本機のデータは<b>同一機器での前後比較・相対比較のみ</b>に使用してください。機器／計器が異なるとデータに系統差があるため、<b>他人や市販データと直接比較しないでください</b>。</li><li>測定時は<b>導電性慣らしオイル</b>を使用しないでください(読み値が歪みます。「五、モーター慣らし」参照)。</li></ul>"
                "<p class='manual-intro'>本機は高温保護、過電流／短絡／ロック／治具外れ検出、ソフトスタート・ソフトストップなど複数の自動保護を内蔵しています(「十四、安全と保護」参照)が、これらは補助であり、<b>安全な操作と監視の代わりにはなりません</b>。</p>"
            )},
            {"id": "start", "t": "一、クイックスタート", "html": (
                "<div class='manual-note'>🔴 <b>電源接続前に必ず確認</b>:本機には <b>DC 5V／6A 以上</b>・安全規格認証済みの電源を使用。<b>規格外の電源は機器を損傷させ、火災の恐れもあり、保証対象外です</b>(「〇、使用前に必ずお読みください」「十四、安全と保護」参照)。</div>"
                "<ol><li>電源を接続 → 基板の表示ランプが点灯し、起動音が鳴ります。</li><li>スマホ / タブレット / PC の WiFi で「<b>MotorTester</b>」に接続(初期パスワード <code>12345678</code>)。</li><li>ブラウザで <code>http://10.10.10.1/</code> を開く。</li><li><b>最初にやること</b>:システム設定 → WiFi 設定でパスワードを強固なものに変更(そうしないと誰でも機器を操作できます)。</li></ol>"
            )},
            {"id": "connect", "t": "二、接続", "html": (
                "<table class='manual-table'><tbody><tr><th>URL</th><td><code>http://10.10.10.1/</code>(https では<b>ありません</b>)</td></tr><tr><th>ホットスポット</th><td><code>MotorTester</code> / <code>12345678</code>(名称変更可)</td></tr><tr><th>端末</th><td>スマホ / タブレット / ノート PC いずれも可、大画面推奨</td></tr><tr><th>接続数</th><td><b>同時に操作できるのは 1 台のみ</b>(シングルセッション、下記)</td></tr><tr><th>注意</th><td>機器のホットスポットは<b>インターネット非対応</b>。iPhone で「インターネット未接続」が出たら「維持」を選択</td></tr></tbody></table><p><b>シングルセッション(複数端末の切替)</b>:2 台が同時にコマンドを出す衝突を避けるため、操作画面を制御できるのは 1 台だけです。</p><ul><li><b>後から接続した端末が自動的に制御を引き継ぎ</b>:新しい端末で画面を開くと、それが制御端末になります。</li><li><b>前の端末は自動的に無効化</b>:「他の端末に引き継がれました」と表示し更新を停止(数値とグラフが固定)。</li><li><b>元の端末に戻すには</b>:その端末で<b>ページを再読み込み</b>すれば制御を取り戻せます。</li><li>途中で端末を替えても進行中の慣らし / テストには影響しません——プログラムは機器側で継続し、新端末は接続後に現在の進捗を表示します。</li></ul>"
            )},
            {"id": "home", "t": "三、ホーム画面", "html": (
                "<p>10 個の機能ボタン:</p><p class='manual-pills'>モーター特性測定 · 慣らし · モーターテスト · 履歴 · AI モーター健康管理(Pro)· ベアリング抵抗 · ブラシ安定 · グローバル慣らしデータ庫 · タミヤモーター規格 · システム設定</p><p>タイトルに <code>MotorLab M1</code> または <code>MotorLab PRO</code> と表示されます。</p>"
            )},
            {"id": "charexp", "t": "四、モーター特性測定", "html": (
                "<p class='manual-intro'>モーターの特性パラメータと損失を全自動で測定し、<b>参考データを提供(採点・ランキングなし)</b>——同型モーター同士を比較し自分で判断します。システムが<b>3 パス連続測定して平均</b>、約 5 分、穏やかな工程で新品の未慣らしモーターにも適します。</p><p><b>操作</b>:ホーム →「モーター特性測定」→ 方向を選択(初期は正転)+ <b>モーター機種</b>を選択(16 機種)+ <b>備考</b>を入力(任意、40 字以内)→「測定開始」→ 全自動(何パス目かと進捗を表示)、測定中はモーターに触れない → 完了でデータ表を表示し<b>測定履歴に自動保存</b>。</p><p><b>データの見方(各項目に方向を明記)</b>:</p><ul><li><b>★ I0(無負荷電流)</b>:同回転数で<b>低いほど良い</b>——再現性が最も高く、選別の第一指標。</li><li><b>★ Km(品質係数)/ ★ T_loss(損失トルク)</b>:補助指標(Km は高いほど、T_loss は低いほど良い)。</li><li><b>Ke(磁気強度)</b>:絶対的な良し悪しなし——数値が近いモーター同士の比較でのみ有効(高め=トルク寄り、低め=回転寄り)。</li><li><b>KV(回転定数、rpm/V)</b>:Ke から換算——KV × 電圧 ≈ 無負荷回転数(例 KV 14000 × 3V ≈ 42000 RPM)、市販表記との照合に便利。</li><li><b>R(内部抵抗)</b>:低いほど良い。</li><li><b>起動電圧</b>:参考のみ——単発ではばらつき大。同一モーターの長期健康比較に向く(後日明らかに上昇=ベアリング / ブラシ劣化の兆候)。</li><li><b>損失フィット R² / Ke ドリフト</b>:データ品質指標(1 に近く、ドリフトが小さいほど信頼できる)。</li><li><b>3 パス一致性</b>:各パスの I0 の最大差。⚠ 表示はモーター不安定または取付緩みを示し、そのデータは参考程度とし、点検して再測定を推奨。</li></ul><p><b>測定履歴</b>:測定ページ →「測定履歴」。成功した測定は自動保存(全指標と各回転点データを含む)、最大 <b>50 件</b>、満杯で最古を自動削除。詳細表示・削除が可能。</p><p><b>おすすめの使い方</b>:</p><ul><li>同ロットの新品を 1 個ずつ測定 → ★I0 で素性の良い個体を選んでから慣らしへ(工数の節約)。</li><li>慣らし後に<b>同じ個体を再測定</b>:損失系は下がるはず(慣らし効果)、Ke / R はほぼ不変。</li><li>異なるモーターの比較は<b>近い温度</b>で。取付直後や冷間再起動後の初回は高めに出ることがあり、2 回目以降を基準に。</li></ul><div class='manual-note'><b>注意</b>:測定失敗(未起動 / ロックタイムアウト / 過電流)は理由を表示、再試行でOK。繰り返し失敗する、または待機中に回転数が 0 でない場合は、回転センサーと反射板の位置合わせを確認してください。</div>"
            )},
            {"id": "breakin", "t": "五、モーター慣らし(3 モード)", "html": (
                "<p class='manual-intro'>低速で長時間運転し、ブラシと整流子を最適な接触に馴染ませます。慣らしページ上部に<b>3 つのモードボタン</b>(運転中は切替不可)。</p><table class='manual-table'><thead><tr><th>モード</th><th>向く人</th><th>一言</th></tr></thead><tbody><tr><td><b>電圧モード</b></td><td>自分のレシピがある人</td><td>各段階を固定電圧で運転(従来方式)</td></tr><tr><td><b>回転数モード (Beta)</b></td><td>回転数を基準にしたい人</td><td>各段階で設定回転数に自動制御、電圧が安定すると自動で次段階へ</td></tr><tr><td><b>スマートモード (Beta)</b></td><td>おまかせで慣らしたい人</td><td>ワンタップ自動慣らし:システムが自分で慣らし・測定・完了で自動停止</td></tr></tbody></table><h3>電圧モード</h3><p>ホーム →「慣らしプログラム」→ <b>機種</b>(16)+ <b>備考</b>(40 字以内)→ <b>判停基準</b>(時間のみ=各段階を設定時間いっぱい運転;スマート安定電流=電流が早く安定したら次段階へ、時間は上限)→ <b>パス数</b>(1~6、初期 1)→ 各パスの 10 段階パラメータを確認(複数パスはタブで切替、数値欄を直接タップして編集)→「開始」。</p><ul><li>各段階の設定:電圧(0.6~4.0V、<b>0=スキップ</b>)/ 方向 / 慣らし秒(10~600、初期 60)/ 冷却秒(10~600、初期 60)/ 安定電流許容差(2~50mA)。</li><li>複数パスでは「<b>このパスを以降すべてにコピー</b>」で素早く入力、パス数の隣に<b>推定総時間</b>を即時表示。</li><li>範囲外の入力は自動的に上下限へ補正し一度点滅して知らせます。</li></ul><div class='manual-note'><b>ポイント</b>:新品モーターの慣らしではブラシと整流子がまだ整形されていないため、公差の設定を回数ごとに大から小へ徐々に絞ることができます。</div><h3>回転数モード (Beta)</h3><p>電圧モードと同じ段階表ですが、最初の列が<b>目標回転数</b>(6000~30000、1000 刻み、<b>0=スキップ</b>)に変わります——機器が電圧を自動調整してモーターをその回転数にロックします。</p><ul><li><b>判停基準</b>(厳格 / 標準 / 緩め):その回転数での駆動電圧が安定すれば慣れたとみなし早めに次段階へ、慣らし秒は上限。厳格=より安定が必要(深く長く)、緩め=早めに次へ(新品が段階を進めない場合は緩めに)。</li><li>段階結果欄に<b>安定電圧</b>を表示。目標回転数に届かない場合は安全上限電圧で時間いっぱい運転し「<b>未達</b>」と表示(通常は目標が高すぎる、またはモーター / 治具の異常)。</li><li>方向・時間・パス数・コピーの操作は電圧モードと同じです。</li></ul><h3>スマートモード (Beta)</h3><p><b>カーボンブラシ Dash 系機種専用</b>のワンタップ自動慣らし:<b>機種</b> + <b>備考</b> + <b>時間上限</b>(完了まで / 2h / 3h / 4h)を選び「開始」、あとは全自動——システムが漸進的な回転数で慣らしながら測定を続け、<b>定常状態(モーターが改善しなくなった)を検出すると自動停止</b>して音で知らせます。</p><ul><li>リアルタイム表示:現在のラウンド / 現在の動作 / 経過時間 / 収束進捗、および<b>慣らし指標カーブ</b>(各ラウンドの点 + 移動平均、平坦化=完了間近)。</li><li>途中でモーターは<b>正転・逆転を交互</b>に慣らし(ブラシ両面を対称に馴染ませ)、周期的に自動測定します。音と回転の規則的な変化は正常です。</li><li>いつでも「停止」で丁寧に終了(そのラウンドの測定後に停止)。他機種は電圧 / 回転数モードを使用してください。</li></ul><div class='manual-note'><b>重要:測定 / 慣らしの際は「導電潤滑オイル」を使用しないでください。</b>「導電」を謳う慣らしオイル(導電カーボン粉入り)を入れると回転数が急上昇・電圧が急低下しますが、それは<b>本当に慣らせたのではなく、カーボンが一時的に導通する錯覚</b>です。本機の全判定(安定電流 / 回転数 / 内部抵抗)はブラシと整流子の<b>真の接触状態</b>を測るため、導電オイルは読値を楽観側に歪め、洗い流すと元に戻ります。正しい方法:この種のオイルは一切使わない;既に使った場合は徹底的に洗浄してから測定を。通常のベアリングへの微量潤滑は影響を受けません —— この警告は「導電型慣らしオイル」のみが対象です。</div><h3>共通の挙動</h3><p>各段階:ソフトスタート → 運転中 → ソフトストップ → 冷却 → 次段階;1 パス終了で自動的に次パスへ(「x/y パス · 段階 c」を表示)。全完了 → ビープ 3 回 → 履歴に自動保存(電圧 / 回転数モード、各パス各段階の結果を含む)。</p><p><b>運転中に押せるボタン</b>:</p><table class='manual-table'><thead><tr><th>ボタン</th><th>動作</th></tr></thead><tbody><tr><td>停止</td><td>ソフトストップ後に終了、記録に「ユーザー中止」</td></tr><tr><td>ゼロリセット</td><td>最大回転 / 安定電流のピークをクリア(中断しない)</td></tr><tr><td>ホーム</td><td>ホームへ戻る、慣らしは<b>バックグラウンドで継続</b></td></tr></tbody></table><div class='manual-note'><b>注意</b>:運転中は全設定がロック;途中で電源を切らない(データ消失);高温時は自動停止して保存;素早く動作確認したい場合は各段階の時間を短く。リアルタイムデータに <b>KV(rpm/V)</b>＝現在回転数 ÷ モーター電圧 の欄が加わり、状態の素早い比較に使えます。</div>"
            )},
            {"id": "test", "t": "六、モーターテスト", "html": (
                "<p class='manual-intro'>単一段階のリアルタイム観察、<b>記録には書き込みません</b>。</p><p>ホーム →「モーターテスト」→ <b>電圧(0.6~4.0V、初期 1V)/ 運転時間(10~600 秒、初期 60)/ 方向 / 安定電流許容差(2~50mA)/ 判停基準</b>(時間のみ、またはスマート安定電流=電流が早く安定したら早期終了、初期は後者;この設定は慣らしページと<b>独立</b>)を設定 →「開始」→ リアルタイムデータとグラフ(<b>KV</b> のリアルタイム値を含む)を確認、時間到達または安定で自動停止。</p><div class='manual-note'><b>注意</b>:4.0V の上限はモーター保護のため回避しない;逆転から正転に切り替える前に一度「停止」を押す。</div>"
            )},
            {"id": "records", "t": "七、履歴", "html": (
                "<p class='manual-intro'>各慣らしの完全データを自動保存、最大 <b>50 件</b>。</p><p>各件に名称 / 開始時刻 / 時間 / モード / 終了理由 / 最大回転 / 平均回転 / 安定電流を表示。</p><table class='manual-table'><thead><tr><th>ボタン</th><th>用途</th></tr></thead><tbody><tr><td>表示</td><td>各段階のデータを確認(複数パス記録は各パス各段階を含む)</td></tr><tr><td>適用</td><td>レシピ(パス数 + 各パス 10 段階)をワンタップで慣らしページに戻す。旧単一パス記録は適用後パス数=1</td></tr><tr><td>エクスポート</td><td>JSON(再インポート可)または CSV(Excel で開ける)をダウンロード</td></tr><tr><td>削除</td><td>削除(復元不可)</td></tr></tbody></table><ul><li><b>満杯(50 件)</b>:管理で「自動上書き」(開始時に最古を削除)か「上書きしない」(初期。開始がブロックされ手動で整理)を選択。</li><li><b>インポート</b>:以前エクスポートした JSON を選択(id 重複は上書き)。JSON のみ。各エクスポートには<b>署名検証</b>が付き、同一 / 同ロットの機器間で相互利用可、改ざんや他ロットのファイルは拒否(ファイル名を変えても内容を検証するので無関係)。</li><li><b>ファイル名</b>:<code>motorlab_&lt;日付&gt;_&lt;時刻&gt;_&lt;機種&gt;[_&lt;備考&gt;]</code>、慣らし開始時刻を採用 → 同一件の再エクスポートは同名。</li><li>ファームウェア更新 / WiFi リセットで<b>記録は消えません</b>。</li></ul>"
            )},
            {"id": "database", "t": "八、グローバル慣らしデータ庫", "html": (
                "<p class='manual-intro'>世界のプレイヤーと慣らし記録を共有。機器が<b>直接オンライン</b>で完了し、エクスポートしてサイトへ上げる手間は不要。<b>インターネット接続のある WiFi</b> が必要(M1 / Pro 両対応)。</p><p><b>閲覧 / ダウンロード</b>:ホーム →「グローバル慣らしデータ庫」→ 接続後に最新 100 件を表示 → <b>機種 / 国 / 完了状態</b>でリアルタイム絞り込み → 各件で「ダウンロード」(本機に保存)または「ダウンロードして適用」(保存してレシピを慣らしページへ)。</p><p><b>自分の記録を共有</b>:履歴 → 該当件を開く → 詳細下部「グローバルデータ庫へ共有」→ 確認ダイアログが<b>公開される項目を明示</b>(機種 / 備考 / 共有者 / 国 / 全データ;名前を入れると実名表示の注意)→ 確認してアップロード。既出の場合は「この記録は既にデータ庫にあります」(エラーではない)。</p><div class='manual-note'><b>注意</b>:ダウンロードした記録は署名検証を通ります;アップロード=公開に同意、削除希望は <b>motorlab.tw@gmail.com</b> へ;外部ネットのない WiFi では「サーバーに接続できません」と表示。</div>"
            )},
            {"id": "health", "t": "九、AI モーター健康管理(Pro)", "html": (
                "<p class='manual-intro'>各モーターに健康指紋を作成し、定期的に再測定して比較、0~100 点と助言を提示。<b>自分自身と比べ、他個体とは比べません</b>。</p><ol><li>ホーム →「AI モーター健康管理」→「+ モーター追加」。</li><li><b>機種</b>(ドロップダウン)+ <b>備考</b>(任意)+ <b>開始電圧</b> + <b>電圧間隔</b>(5 点自動取得)を入力。</li><li>確認 → 約 <b>2.5 分</b>で基準を自動作成。</li></ol><p>以降、各カードで <b>フル検査</b>(約 2.5 分、最も正確)または <b>クイック検査</b>(約 1.5 分、±5%)が可能。結果ページにスコア、等級(Optimal / Acceptable / Warning / Critical)、トレンド図、5 指標、テキスト助言を表示。</p><div class='manual-note'><b>注意</b>:1 個あたり最大 50 回の履歴、1 台あたり最大 20 個;検査中は電源を切らない / 他ボタンを押さない;高温時は自動中止;M1 版はボタンがグレー(タップで升級案内)。</div>"
            )},
            {"id": "bearing", "t": "十、ベアリング抵抗テスト", "html": (
                "<p class='manual-intro'>ベアリングの滑らかさを測定、全エディション対応。<b>完全停止までの時間が長い → ベアリングが滑らか</b>。</p><p>ホーム →「ベアリング抵抗テスト」→ テスト電圧を選択(<b>2.4V または 3V</b>)→「テスト開始」→ その電圧まで加速 → 5 秒安定 → <b>そのまま電源遮断(ブレーキなし)</b> → 完全停止まで計測 → <b>完全停止時間</b>を表示。</p><div class='manual-note'><b>注意</b>:無負荷モーターは慣性が小さいため、本テストは<b>時間のみ表示し良否判定はしません</b>。同一個体の異なる時期、または異なる個体の時間を比較してください;回転センサーが正常であること;再現性のため 2~3 回測定を推奨。</div>"
            )},
            {"id": "brush", "t": "十一、ブラシ接触安定テスト", "html": (
                "<p class='manual-intro'>ブラシ接触の均一性を測定、約 35 秒、全エディション対応。<b>接触ムラ → 電流のばらつき → CV 上昇</b>。</p><p>ホーム →「ブラシ接触安定テスト」→「テスト開始」(<b>軸を手で回す必要なし</b>)。流れは <b>1V</b> 固定:10 秒で 0→1V に緩やかに昇圧 → 1V で 5 秒保持 → 1V で電流を 20 秒サンプリング → <b>電流変動係数 CV%</b> を表示。</p><p><b>CV% の見方</b>:CV は固定電圧下での電流のばらつき度合いで、<b>相対比較のツール、絶対的な良否ラインはありません</b>(機種ごとに元々異なる)。おすすめ:</p><ul><li>同一モーターの <b>慣らし前 vs 後</b>:CV 低下 = ブラシが馴染み接触改善。</li><li>同一モーターの <b>長期追跡</b>:CV 上昇 = ブラシ摩耗 / 整流子の汚れ。</li><li><b>モーター A vs B</b> の相対比較。</li></ul><div class='manual-note'><b>注意</b>:1V 固定・手順固定だからこそ、回数間 / 個体間で公平に比較できます;再現性のため 2~3 回測定を推奨。</div>"
            )},
            {"id": "tamiya", "t": "十二、タミヤモーター規格", "html": (
                "<p class='manual-intro'>タミヤ Mini 4WD モーター 15 機種の公式規格早見表を内蔵(PRO 両軸 6 + 標準片軸 9):機種 / 負荷回転 / 電流 / 電圧 / トルク。</p><ul><li>表の数値は<b>タミヤ公式公表の推奨負荷時データ</b>(適正電圧 2.4~3.0V);機種追加や規格変更があればタミヤ発表の最新規格が優先。</li><li>Ultra-Dash と Plasma-Dash は公式レギュレーション上限を超え、公式大会では使用禁止。</li><li>本製品は株式会社タミヤ(TAMIYA)と一切関係がなく、その承認・後援・推奨も受けていません。</li></ul>"
            )},
            {"id": "settings", "t": "十三、システム設定", "html": (
                "<p class='manual-intro'>システム運転中、このページは「ホーム」のみ操作可、他はロック。</p><table class='manual-table'><tbody><tr><th>ユーザー設定</th><td>名前 / 国(32 字以内、初期 <code>--</code>)、各記録に出所として書き込み。既存記録には反映されません。</td></tr><tr><th>WiFi 設定</th><td>ホットスポット名 / パスワード(8~63 字)を変更 → 保存後に再起動、新ホットスポットへ再接続。パスワードを忘れたら第十五章。</td></tr><tr><th>言語</th><td>中文 / English / 日本語(初期 中文)。「確定」で<b>システムを再起動</b>してクリーンに読み込み(約 10 秒);運転中の切替はページ再読み込みのみで工程は中断しません。</td></tr><tr><th>正規品認証</th><td>本機 ID を表示、公式サイトの認証ページで正規品か自己確認可(v3.4.1 以降)。</td></tr><tr><th>温度校正</th><td>表示と実際にずれがある場合に補償を追加(±20°C)。</td></tr><tr><th>高温ロック</th><td>高温ロック温度を設定(初期 50°C、範囲 25~60°C)。現在温度が設定値より 5°C 以上高い状態が 10 秒続くと高温ロック(停止、ゼロリセットで解除)。ブロック内に現在温度も表示。</td></tr><tr><th>平均回転設定</th><td>許容差(隣接 2 秒の回転差)を 120~600 RPM で選択、<b>初期 240</b>。許容差が大きいほど安定と判定しやすいが反応は鈍い;不安定なモーターは上げる。</td></tr><tr><th>ソフトスタート</th><td>電圧を 0 から 5 秒で目標へ滑らかに線形昇圧(ソフトストップと同様)、<b>調整パラメータなし</b>。電圧出力は校正済みで起動トルク設定は不要。</td></tr><tr><th>ライセンス取得</th><td>M1 を Pro へ、下記参照。</td></tr><tr><th>ソフトウェア更新</th><td>家庭の WiFi 経由で最新ファームを自動取得、下記参照。</td></tr><tr><th>RGB ステータスライト</th><td>デュアル(内蔵 / パネル)出力位置 + 明るさ(0~100%)+ 5 組の状態スタイル、下記参照。</td></tr><tr><th>エンジニアリングモード</th><td>パスワード保護の高度な校正とオフライン更新(一般ユーザーには不要)。</td></tr><tr><th>WiFi リスト</th><td>外部 WiFi を最大 8 組記憶;「リストを消去」は機器の譲渡用(Pro ライセンスには影響なし)。</td></tr></tbody></table><p><b>ライセンス取得(M1 → Pro)</b>:システム設定 →「ライセンス取得」→ 家庭の WiFi を選択 → 機器が購入を自動検証 → 未購入なら QR コード表示 → 別のネット端末でスキャンして決済 → 機器が 10 秒ごとに自動照会、決済成功で解除。全体で約 1~3 分、<b>キーの手入力不要</b>、タイムアウト(最長 10 分)時は再試行可。</p><p><b>ソフトウェア更新</b>:システム設定 →「更新を確認」→ WiFi を選択 → 新版があれば自動ダウンロード・書込(進捗 100% まで)→ 自動再起動、ページ自動再読み込み。<b>途中で電源 / ブラウザを閉じない</b>(途中の電源断は保護され旧版へ復帰);ダウンロード約 1.6MB、家庭 WiFi で約 5~10 秒。</p><p><b>RGB ステータスライト</b>:出力位置(パネル / パネル+内蔵 / 内蔵、即時切替)、明るさ(スライダー →「プレビュー」5 秒 →「適用」で保存)、5 組の状態スタイル(状態=なし / 高温 / 冷却 / 待機 / 運転 × 色相 × モード × 周期、同じくプレビュー / 適用の 2 ステップ)。</p><p><b>エンジニアリングモード</b>:パスワードが必要(3 回誤りで 60 秒ロック、10 分無操作で自動ログアウト)。</p>"
            )},
            {"id": "safety", "t": "十四、安全と保護", "html": (
                "<p class='manual-intro'>モーターを駆動するあらゆる工程(慣らし / テスト / 特性測定 / ベアリング / ブラシ / 健康検査)で機器は全自動で監視し、異常時は<b>直ちに停止して説明を表示</b>します:</p><table class='manual-table'><thead><tr><th>保護</th><th>トリガー</th><th>反応</th></tr></thead><tbody><tr><td>モーター未検出</td><td>通電しているがモーター電流なし(未装着 / 配線緩み)</td><td>&lt; 3 秒以内に停止</td></tr><tr><td>モーター拘束</td><td>高電流だが回らない(固着)</td><td>&lt; 5 秒以内に停止</td></tr><tr><td>回転信号なし</td><td>電流は流れるが回転が 0 のまま(<b>治具未装着</b>やセンサー異常)</td><td>&lt; 4 秒以内に停止</td></tr><tr><td>出力短絡</td><td>出力端子がほぼ短絡</td><td>緊急停止(&lt; 0.15 秒)</td></tr><tr><td>高温</td><td>設定温度を超過</td><td>直ちに停止 + ロック</td></tr></tbody></table><p>トリガー時は<b>ブザーが長音 4 回</b>、画面に「運転を停止しました」+ 理由を表示、解消後に再起動可。<b>電源仕様 DC 5V / 6A(下回らないこと)</b>;供給不足時は上部に琥珀色の警告が出ます、正確な出力には十分な供給が必要です。</p><table class='manual-table'><thead><tr><th>機構</th><th>トリガー / 挙動</th></tr></thead><tbody><tr><td>高温保護</td><td>2 つのトリガー:① 温度センサー警報;② 現在温度が「高温ロック温度」設定より 5°C 以上高い状態が 10 秒。いずれかで → 直ちに停止 + ビープ 5 回 + ロック。<b>温度が下がっても「ゼロリセット」を押すまで解除されません</b>(高温のまま押すと再ロック)。</td></tr><tr><td>ソフトスタート / ストップ</td><td>起動は 5 秒の線形昇圧(0V→目標)、停止は 3 秒の線形降圧で、電流の急増と機械的衝撃を回避。</td></tr><tr><td>電流上限</td><td>4A 固定の測定上限、超過分は読値を頭打ち(停止しないが、長時間の高電流は高温を誘発しうる)。</td></tr><tr><td>起動ロック</td><td>起動 30 秒以内に 3 回連続クラッシュ → 前バージョンのファームへ自動復帰。</td></tr></tbody></table>"
            )},
            {"id": "wifireset", "t": "十五、WiFi リセット(レスキュー)", "html": (
                "<p class='manual-intro'><b>用途</b>:WiFi 名 / パスワードを忘れたとき、ホットスポットを <code>MotorTester</code> / <code>12345678</code> に戻します。</p><p><b>方法</b>:機器の「WiFi リセット」接点を短絡(または対応ボタンを押下)して<b>5 秒間保持</b> → ビープ 10 回 → 自動再起動。</p><p><b>WiFi ホットスポットの名前とパスワードのみをリセット</b>し、以下はすべて保持:慣らしパラメータ / 各種校正と設定 / <b>Pro ライセンス</b> / 履歴 / モーター指紋 / RGB 設定 / 記憶済み外部 WiFi。</p>"
            )},
            {"id": "faq", "t": "十六、よくある質問", "html": (
                "<table class='manual-table'><thead><tr><th>症状</th><th>対処</th></tr></thead><tbody><tr><td>起動音が鳴らない</td><td>電源 5V を確認</td></tr><tr><td>接続できるがページが開けない</td><td><code>http://</code>(https でない)を確認、モバイルデータをオフ、強制再読み込み(Ctrl+Shift+R)</td></tr><tr><td>「適用中…」のまま</td><td>多くは WiFi 不安定、ページを再読み込み(内蔵の 8 秒監視が赤字で知らせます)</td></tr><tr><td>長い慣らし中にスマホ / タブレットが切断される</td><td>端末はアイドルでホットスポットを自動切断します —— 正常な動作です;機器の WiFi に再接続してページを再読み込み。慣らしは機器側で継続し、切断の影響を受けません</td></tr><tr><td>WiFi パスワードを忘れて接続できない</td><td>機器の WiFi リセット接点を 5 秒長押し(「十五、WiFi リセット」参照)、ホットスポット名とパスワードのみリセットされ、他の設定と記録はすべて保持</td></tr><tr><td>長音 4 回で自動停止、復帰するには</td><td>画面表示の原因を解消(モーター未固定 / 端子接触不良 / 出力短絡 / センサー未整合)→ 再起動不要、そのまま再度「開始」で故障状態は自動クリア</td></tr><tr><td>起動して数秒で自動停止する</td><td>通常は保護動作、画面の原因を確認:電流が低すぎ=モーター未接続;電流が高すぎ=固着または短絡;供給不足の赤い警告がないかも確認</td></tr><tr><td>モーターは回るが回転数が 0 表示</td><td>反射マークがセンサーに向いているか、治具が整合しているか確認;センサー部への強い光を避ける。読めない状態が続くと保護で自動停止(約 4 秒)</td></tr><tr><td>高温ロックが解除できない</td><td>温度が閾値未満に下がってから「ゼロリセット」;室温が高い場合はシステム設定で閾値を上げる(上限 60°C)か温度校正の補償を確認</td></tr><tr><td>回転数モードで段階が「未達」</td><td>目標回転数がモーター能力を超過(安全上限電圧で時間いっぱい運転して終了)→ 目標を下げる;明らかに力があるなら治具の取付とセンサーを確認</td></tr><tr><td>スマートモードの対応機種</td><td>カーボンブラシ系列;他機種は電圧または回転数モード</td></tr><tr><td>スマートモードが時々長く回るのはなぜ</td><td>「定常状態を検出」するまで止まらず、モーター差が大きいため;時間上限(2h / 3h / 4h)が兜底</td></tr><tr><td>慣らしは何パスで十分か</td><td>決まった答えはなく、「安定」指標が収束するかを見る;自分で判断したくなければスマートモードで定常状態まで自動停止</td></tr><tr><td>「導電慣らしオイル」を入れると数値が特に良い</td><td>それは炭粉が一時的に導通する<b>錯覚</b>で、真の慣らしではありません。オイルを洗浄してから測定を;本機はモーターの真の電気状態で判定し、導電オイルは読値を楽観側に歪めます(「五、モーター慣らし」の警告参照)</td></tr><tr><td>同じモーターでも毎回数値が少し違う</td><td>正常です。ブラシ接触と温度で小幅な自然ドリフトが生じます;判読は<b>トレンドと複数回平均</b>で、単発を比べない</td></tr><tr><td>自分のデータが他人 / ネットと合わない</td><td>電圧基準、供給、治具、測定方法の違いが系統的な差を生みます;<b>同一機器での前後比較</b>が最も信頼できます</td></tr><tr><td>KV 値とは</td><td>現在回転数 ÷ モーター実効電圧(rpm/V)、モーター状態を素早く比べる指標 —— 同電圧で数値が高いほど速い</td></tr><tr><td>対応するモーターは</td><td>タミヤ Mini 4WD 130 型モーター(片軸 / 両軸とも治具に装着可)</td></tr><tr><td>電源の要件は</td><td>DC 5V / 6A 以上・安全規格認証済み;供給不足時は UI に警告、細いケーブルや小容量アダプターで起こりがち。⚠ <b>規格外の電源は機器を損傷させ火災の危険があり、保証対象外です</b>(「十四、安全と保護」参照)</td></tr><tr><td>ライセンス取得が接続で止まる</td><td>家庭 WiFi のパスワード誤り / ネットなし / 電波弱 → 再入力または WiFi 変更</td></tr><tr><td>Pro 返金後</td><td>次のオンライン再検証時に<b>自動で M1 へ戻る</b>;再購入は「ライセンス再取得」</td></tr><tr><td>赤い「AP パスワードが初期のまま」バナー</td><td>WiFi 設定でパスワードを変更</td></tr><tr><td>測定データはクラウドにアップロードされる?</td><td>されません。100% 機器内に保存;自分で「アップロード」したレシピのみグローバルデータ庫へ</td></tr><tr><td>履歴が 50 件に達したら</td><td>初期設定では最古を自動上書き(無効化可);重要な記録は先に JSON/CSV でエクスポートを</td></tr><tr><td>ソフトウェア更新で記録は消える?</td><td>消えません。更新は全設定・校正・履歴を保持</td></tr><tr><td>更新失敗で文鎮化する?</td><td>しません。前バージョンへの自動復帰があります</td></tr><tr><td>待機中に電源を抜いてよい?</td><td>可。モーター完全停止・「適用中」なし・更新中でないときが安全</td></tr></tbody></table>"
            )},
            {"id": "leds", "t": "十七、ステータスランプと音の合図", "html": (
                "<p><b>ステータスランプ</b>(初期設定、「RGB ステータスライト」で変更可):</p><table class='manual-table'><thead><tr><th>システム状態</th><th>初期</th><th>意味</th></tr></thead><tbody><tr><td>高温ロック</td><td>赤点滅</td><td>高温保護作動、冷却して「ゼロリセット」</td></tr><tr><td>冷却中</td><td>黄点灯</td><td>段階間の冷却、モーター停止</td></tr><tr><td>待機</td><td>青呼吸</td><td>コマンド待ち</td></tr><tr><td>運転中</td><td>緑呼吸</td><td>慣らし / テスト / 検査中</td></tr><tr><td>消灯</td><td>—</td><td>一致なし、または全消灯</td></tr></tbody></table><p><b>音の合図</b>(ブザー、カスタム不可):</p><table class='manual-table'><thead><tr><th>音</th><th>状況</th></tr></thead><tbody><tr><td>レースカウントダウン 4 回(短 3 + 長高音 1)</td><td>起動完了</td></tr><tr><td>2 回</td><td>モーターテスト完了</td></tr><tr><td>3 回</td><td>慣らし完了(電圧 / 回転数モードは全パス終了;スマートモードは完了で自動停止)</td></tr><tr><td>短 5 回</td><td>高温ロック(冷却後「ゼロリセット」で解除)</td></tr><tr><td><b>長 4 回</b></td><td><b>モーター故障停止</b>(未検出 / 拘束 / 回転信号なし / 出力短絡、画面に理由を表示)</td></tr><tr><td>10 回</td><td>WiFi リセット作動(この後自動再起動)</td></tr></tbody></table><p class='manual-contact'><b>問題報告</b>の際は次を併せてご提供ください:ファームウェアバージョン(システム設定 → ソフトウェア更新)、エディション(ホームの M1 / PRO)、画面のスクリーンショット、運転中かどうか、再現手順。サポート:<b>motorlab.tw@gmail.com</b></p>"
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

    # 防呆:i18n 值內未跳脫的撇號會讓內嵌 <script> 語法錯誤 → 全站卡開機動畫。
    # 每個 i18n 行的未跳脫單引號應為偶數(key+value 成對);奇數 = 有裸撇號。
    _q_bad = []
    for _i, _ln in enumerate(src_html.split("\n"), 1):
        if re.match(r"^\s*'[\w.]+':", _ln) and len(re.findall(r"(?<!\\)'", _ln)) % 2:
            _q_bad.append((_i, _ln.strip()[:110]))
    if _q_bad:
        print("❌ 建置中止:i18n 引號不平衡(未跳脫撇號 → 會卡開機動畫,請改成 \\'):")
        for _i, _l in _q_bad:
            print(f"   L{_i}: {_l}")
        sys.exit(1)

    print("=" * 55)
    print("MotorLab.tw 多語言頁面產生器")
    print("=" * 55)

    i18n = extract_i18n(src_html)
    for lang in ("zh", "en", "ja"):
        print(f"  i18n[{lang}]: {len(i18n.get(lang, {}))} keys")
    print()

    # 防呆:body 的每個 data-i18n key,en/ja i18n 都必須覆蓋,否則該語言頁會 fallback 成中文。
    #   架構:zh 內容寫在 body(data-i18n 預設文字),en/ja 由 const i18n 覆蓋。
    #   這道閘擋住「zh 加了新 key、忘了加 en/ja i18n」的常見錯 → 建置中止,不會出漏翻的頁。
    _body_keys = set(re.findall(r'data-i18n="([a-zA-Z0-9._]+)"', src_html))
    _i18n_gap = []
    for _lang in ("en", "ja"):
        _miss = sorted(_body_keys - set(i18n.get(_lang, {})))
        if _miss:
            _i18n_gap.append((_lang, _miss))
    if _i18n_gap:
        print("❌ 建置中止:i18n 三語未同步(en/ja 缺 body key → 該語言頁會 fallback 成中文):")
        for _lang, _miss in _i18n_gap:
            print(f"   [{_lang}] 缺 {len(_miss)} 個:{', '.join(_miss[:20])}{' …' if len(_miss)>20 else ''}")
        print("   → 請在 index.src.html 的 const i18n 對應語言區塊補上這些 key。")
        sys.exit(1)

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
    print("=== 意向調查(/presale/,GAS presale / JSONP)===")
    for lang in ("zh", "en", "ja"):
        if lang not in PRESALE["i18n"]:
            continue
        lang_prefix = "" if lang == "zh" else f"{lang}/"
        out_dir = f"{lang_prefix}presale"
        out_path = f"{out_dir}/index.html"
        os.makedirs(out_dir, exist_ok=True)
        html_out = build_presale_page(PRESALE, lang, src_html, i18n)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_out)
        size = len(html_out.encode("utf-8"))
        print(f"  ✅ {out_path:<45} {size:>9,} bytes  ({lang})")
    if PRESALE["api_url"].startswith("PUT_"):
        print("  ⚠ PRESALE['api_url'] 尚未設定 — 表單先以「即將開放」訊息優雅降級,上線前填 GAS /exec URL")

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

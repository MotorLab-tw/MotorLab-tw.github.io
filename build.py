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
        "description": "MotorLab — 專為 Mini 4WD® 玩家打造的精密馬達磨合測試系統。十大專業功能:十階段可程式化磨合、AI 健康管理、FFT 頻譜、軸承 τ 衰減、CV 電刷穩定診斷、三層安全保護(抗 EMI、< 100 ms 急停、Watchdog 自動復原)、OTA 線上更新、全球馬達磨合資料庫。讓馬達調校可量化。",
        "og_title": "MotorLab — Mini 4WD® 馬達磨合測試系統",
        "og_desc": "為每一顆 Mini 4WD® 馬達建立可量化的健康指紋。十大專業功能:十階段磨合、AI 健康管理、軸承衰減分析、電刷穩定診斷、三層安全保護、全球馬達磨合資料庫。",
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
        "og_desc": "Build a measurable health fingerprint for every Mini 4WD® motor. Ten professional tools: 10-stage break-in, AI health management, bearing decay analysis, brush stability diagnostics, triple-layer safety protection and a global break-in data library.",
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
        "og_desc": "すべての Mini 4WD® モーターに定量化できる健康指紋を。10 のプロ機能:10 段階慣らし、AI 健康管理、ベアリング減衰解析、ブラシ安定診断、三層安全保護機構、グローバル慣らしデータ庫。",
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
                "description": "迷你四驅車馬達磨合(玩家俗稱「磨馬達」)完整教學 — 田宮馬達磨合的科學原理、電壓/轉速/時間/冷卻 4 個關鍵變數、10 階段標準流程,以及磨合完成的判定標準。解答新馬達到底要不要磨、為什麼業餘「水磨」方法行不通。",
                "keywords": "馬達磨合, 磨馬達, 四驅車馬達磨合, 迷你四驅車馬達磨合, 馬達磨合原理, 馬達磨合 10 階段, 田宮馬達磨合, 馬達磨合教學, 磨馬達教學, 紅二磨合, 黑金剛磨合, 碳刷磨合, motor break-in, MotorLab",
                "breadcrumb": "馬達磨合完全指南",
                "h1_for_ld": "四驅車馬達磨合完全指南:從原理到實作",
            },
            "en": {
                "title": "Mini 4WD Motor Break-in Guide: Principles & Practice | MotorLab",
                "description": "Complete Mini 4WD motor break-in guide: the physics of brush seating, 4 control variables, the 10-stage procedure, and how to tell when break-in is done.",
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
        "i18n": {
            "zh": {
                "title": "田宮主流馬達規格與磨合策略對照表 | 紅二/黑金剛/紫頭速查 | MotorLab",
                "description": "田宮 8 款主流 Mini 4WD 馬達(紅二 Hyper Dash、黑金剛 Plasma Dash、紫頭 Rev Tuned、橘頭 Torque Tuned 等)的官方規格與建議磨合策略對照表。銅刷與碳刷馬達的磨合差異,以及田宮競賽合規規則。",
                "keywords": "田宮馬達規格, 四驅車馬達規格, 田宮馬達, 紅二 Hyper Dash, 黑金剛 Plasma Dash, 紫頭 Rev Tuned, 橘頭 Torque Tuned, 灰頭 Atomic Tuned, 綠頭 Power Dash, 白頭 Sprint Dash, 銅刷碳刷差別, 田宮馬達磨合, 田宮競賽規則",
                "breadcrumb": "田宮馬達速查表",
                "h1_for_ld": "田宮主流馬達規格與磨合策略對照表",
            },
            "en": {
                "title": "Tamiya Mini 4WD Motor Specs Chart & Break-in Guide | MotorLab",
                "description": "Official specs and break-in strategy for 8 mainstream Tamiya Mini 4WD motors (Hyper Dash, Plasma Dash, Rev-Tuned and more), plus copper vs carbon brushes.",
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
        "slug": "tamiya-motor-full-lineup",
        "key": "g9",
        "type": "benchmarks",
        "i18n": {
            "zh": {
                "title": "田宮 Mini 4WD® 全 15 款馬達規格對照表(含 PRO 系列)| MotorLab",
                "description": "田宮(TAMIYA, INC.)Mini 4WD® 全 15 款馬達官方規格對照表 — 標準系列 9 款(單軸)+ PRO 系列 6 款(雙軸)。整理 RPM、扭力(mN·m)、電流(A)、Speed/Torque 等級、官方比賽合規限制與對應 MotorLab 磨合策略。",
                "keywords": "田宮馬達, 田宮 15 款馬達, 田宮馬達規格, Mini 4WD PRO 馬達, 雙軸馬達, 單軸馬達, 田宮馬達對照表, Hyper-Dash PRO, Mach-Dash PRO, Plasma-Dash, Ultra-Dash, Power-Dash, Sprint-Dash, 田宮比賽合規, 紅二, 黑金剛",
                "breadcrumb": "全 15 款馬達規格",
                "h1_for_ld": "田宮 Mini 4WD® 全 15 款馬達規格對照表(含 PRO 系列)",
            },
            "en": {
                "title": "Tamiya Mini 4WD® Motors: Full Specs Chart (15 Models) | MotorLab",
                "description": "Spec comparison for all 15 Tamiya Mini 4WD motors — 9 standard + 6 PRO: RPM, torque, current, Speed/Torque ratings, race compliance and break-in strategy.",
                "keywords": "Tamiya Mini 4WD motors, Tamiya 15 motors, Mini 4WD PRO motors, double-shaft motor, single-shaft motor, Tamiya motor specifications, Hyper-Dash PRO, Mach-Dash PRO, Plasma-Dash, Ultra-Dash, Power-Dash, Sprint-Dash, Tamiya race compliance, Tamiya motor comparison table",
                "breadcrumb": "Full Lineup (15 Motors)",
                "h1_for_ld": "Tamiya Mini 4WD® Motor Full Lineup: All 15 Models Spec Comparison",
            },
            "ja": {
                "title": "タミヤ Mini 4WD® 全 15 種モーター規格対照表(PRO シリーズ含む)| MotorLab",
                "description": "タミヤ(TAMIYA, INC.)Mini 4WD® 全 15 種モーターの公式スペック対照表 — 標準シリーズ 9 種(片軸)と Mini 4WD PRO シリーズ 6 種(両軸)。RPM、トルク(mN·m)、電流(A)、Speed/Torque 評価、公式競技ルール、対応する MotorLab 慣らし戦略を網羅。",
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
        "include": ["g5", "g6", "g7", "g8", "g10", "g11"],
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
            "up_eyebrow": "Upload · 上傳",
            "up_h2": "分享你的磨合紀錄",
            "up_p": "選擇馬達磨合機匯出的 .json 檔。系統會在伺服器端驗證簽章、只有未經竄改的紀錄會被收錄。",
            "up_btn": "選擇檔案上傳",
            "up_hint": "或把 .json 檔拖曳到這裡",
            "tos": "上傳即表示你同意公開分享此紀錄。紀錄中的署名/國家欄位在你的馬達磨合機系統設定中設置,系統預設為匿名。如需移除已上傳的紀錄,請來信 motorlab.tw@gmail.com。",
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
            "up_eyebrow": "Upload",
            "up_h2": "Share your break-in record",
            "up_p": "Pick the .json file your machine exported. Signatures are verified server-side — only untampered records are accepted.",
            "up_btn": "Choose a file to upload",
            "up_hint": "or drag a .json file here",
            "tos": "Uploading means you agree to share this record publicly. The name/country fields are set in your motor break-in machine's system settings and default to anonymous. To remove an uploaded record, email motorlab.tw@gmail.com.",
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
            "up_eyebrow": "Upload · アップロード",
            "up_h2": "あなたの慣らし記録を共有",
            "up_p": "マシンが書き出した .json ファイルを選択。署名はサーバー側で検証され、改ざんのない記録のみ収録されます。",
            "up_btn": "ファイルを選択してアップロード",
            "up_hint": "または .json ファイルをここにドラッグ",
            "tos": "アップロードはこの記録の公開共有に同意したことを意味します。名前/国の欄はモーター慣らし機のシステム設定で設定され、初期値は匿名です。記録の削除は motorlab.tw@gmail.com までご連絡ください。",
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

  function setStatus(msg, kind) {
    var el = $("lab-status");
    if (!el) return;
    el.textContent = msg || "";
    el.className = "lab-status" + (kind ? " " + kind : "");
  }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function fmtNum(n) {
    if (n === "" || n == null || isNaN(n)) return "—";
    return Number(n).toLocaleString();
  }
  function abToB64(buf) {
    var bytes = new Uint8Array(buf), bin = "", chunk = 0x8000;
    for (var i = 0; i < bytes.length; i += chunk) {
      bin += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
    }
    return btoa(bin);
  }
  function b64ToBlob(b64) {
    var bin = atob(b64), len = bin.length, bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
    return new Blob([bytes], { type: "application/json" });
  }

  function upload(file) {
    if (!hasApi()) { setStatus(T.no_api, "err"); return; }
    if (!file) return;
    setStatus(T.uploading, "");
    var fr = new FileReader();
    fr.onload = function () {
      var body = JSON.stringify({ file_b64: abToB64(fr.result), filename: file.name || "", hp: ($("lab-hp") || {}).value || "" });
      fetch(API, { method: "POST", headers: { "Content-Type": "text/plain;charset=utf-8" }, body: body })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d.ok && d.dup) setStatus(T.up_dup, "warn");
          else if (d.ok) { setStatus(T.up_ok, "ok"); loadList(); }
          else setStatus(T.up_err + (d.err ? ": " + d.err : ""), "err");
        })
        .catch(function () { setStatus(T.err_network, "err"); });
    };
    fr.readAsArrayBuffer(file);
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
      "</th><th>" + esc(T.c_date) + "</th><th></th></tr></thead><tbody>";
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
        '<td class="lab-mono">' + esc(date) + "</td>" +
        '<td class="lab-row-actions">' +
        '<button type="button" class="lab-btn lab-btn-sm" data-dl="' + esc(it.content_sha256) + '">' + esc(T.download) + "</button>" +
        "</td></tr>";
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

  function download(sha) {
    if (!hasApi()) { setStatus(T.no_api, "err"); return; }
    setStatus(T.preparing, "");
    fetch(apiq("action=get&sha=" + encodeURIComponent(sha)))
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (!d.ok) { setStatus(d.err || T.err_network, "err"); return; }
        var url = URL.createObjectURL(b64ToBlob(d.file_b64));
        var a = document.createElement("a");
        a.href = url; a.download = d.filename || (sha + ".json");
        document.body.appendChild(a); a.click(); document.body.removeChild(a);
        URL.revokeObjectURL(url); setStatus("", "");
      }).catch(function () { setStatus(T.err_network, "err"); });
  }

  document.addEventListener("DOMContentLoaded", function () {
    var btn = $("lab-upload-btn"), file = $("lab-file"), drop = $("lab-drop");
    if (btn && file) btn.addEventListener("click", function () { file.click(); });
    if (file) file.addEventListener("change", function () {
      if (file.files && file.files[0]) { upload(file.files[0]); file.value = ""; }
    });
    if (drop) {
      ["dragover", "dragenter"].forEach(function (ev) {
        drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.add("lab-drag"); });
      });
      ["dragleave", "drop"].forEach(function (ev) {
        drop.addEventListener(ev, function (e) { e.preventDefault(); drop.classList.remove("lab-drag"); });
      });
      drop.addEventListener("drop", function (e) {
        var f = e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0];
        if (f) upload(f);
      });
    }
    var rf = $("lab-refresh");
    if (rf) rf.addEventListener("click", loadList);
    // 即時篩選:輸入框打字即篩(從快取),不再每次打 GAS
    var fm = $("lab-f-motor"), fc = $("lab-f-country"), fcp = $("lab-f-completed"),
        fps = $("lab-f-pagesize"), fsort = $("lab-f-sort");
    if (fm) fm.addEventListener("change", applyFilter);   // 下拉用 change
    if (fc) fc.addEventListener("input", applyFilter);    // 文字框用 input
    if (fcp) fcp.addEventListener("change", applyFilter);
    if (fps) fps.addEventListener("change", applyFilter); // 顯示筆數
    if (fsort) fsort.addEventListener("change", applyFilter); // 排序下拉
    var res = $("lab-results");
    if (res) res.addEventListener("click", function (e) {
      var dl = e.target.getAttribute("data-dl");
      if (dl) download(dl);
    });
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

    # 7b. 上傳區(含 honeypot 隱藏欄位)
    up_html = (
        f'<section class="lab-section"><div class="container">'
        f'<div class="lab-eyebrow">{s["up_eyebrow"]}</div>'
        f'<h2 class="lab-h2">{s["up_h2"]}</h2>'
        f'<p class="lab-lead">{s["up_p"]}</p>'
        f'<div class="lab-upload" id="lab-drop">'
        f'<input type="file" id="lab-file" accept=".json,application/json" hidden>'
        f'<input type="text" id="lab-hp" class="lab-hp" tabindex="-1" autocomplete="off" aria-hidden="true">'
        f'<button type="button" class="lab-btn lab-btn-primary" id="lab-upload-btn">{s["up_btn"]}</button>'
        f'<p class="lab-drop-hint">{s["up_hint"]}</p>'
        f'</div>'
        f'<div class="lab-status" id="lab-status" role="status" aria-live="polite"></div>'
        f'<p class="lab-tos">{s["tos"]}</p>'
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
    print("完成!3 個語言版本 + 教學分頁 + 3 個 hub 索引頁 + 商品外觀頁 + /lab/ 已產生。")
    print("=" * 55)


if __name__ == "__main__":
    main()

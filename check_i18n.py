# -*- coding: utf-8 -*-
"""i18n 三語一致性檢查器。

用途:每次改完母版 index.src.html 的 i18n(或 build.py 的 MANUAL/SEO 等三語 dict)後,
在 build 前跑 `PYTHONUTF8=1 python check_i18n.py`,自動抓出「某 key 在 zh 有、en/ja 缺」
或反之的落差。有落差 → exit 1(可接進 CI / pre-commit)。

檢查兩處三語結構:
1. index.src.html 的 const i18n(沿用 build.py 的 extract_i18n,不會與真正解析漂移)
2. build.py 的 MANUAL["sections"] 三語 section id 是否一一對應

不檢查「內容是否翻譯」(那要人看),只保證「三語 key/章節結構對齊」——
這正是這陣子反覆出錯的地方(zh 加了 key,en/ja 忘了加)。
"""
import io, sys, re, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = "c:/Projects/studio/MotorLab-tw.github.io/"

# 借用 build.py 的 extract_i18n(避免解析邏輯漂移)
spec = importlib.util.spec_from_file_location("buildmod", ROOT + "build.py")
# build.py 頂層可能有副作用(讀檔),用 exec 只取函式較穩;改為直接複製 regex 解析,
# 但為求「與 build.py 同步」,直接 import 並呼叫其 extract_i18n。
buildmod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(buildmod)
except SystemExit:
    pass

fail = 0

# ---------- 1. body 的 data-i18n key 是否都被 en/ja i18n 覆蓋 ----------
# 架構特性:zh 內容寫在 body(data-i18n 元素的預設文字),en/ja 由 const i18n 覆蓋。
# 所以「權威 key 集合」= body 裡所有 data-i18n;真正的 bug 是 en/ja i18n 沒覆蓋到某個 body key
# (= zh 頁正常、en/ja 頁 fallback 成中文)。這正是這陣子反覆出錯的模式。
src = open(ROOT + "index.src.html", encoding="utf-8").read()
i18n = buildmod.extract_i18n(src)
en, ja = set(i18n["en"]), set(i18n["ja"])

# body 裡所有 data-i18n key(權威基準)
body_keys = set(re.findall(r'data-i18n="([a-zA-Z0-9._]+)"', src))

print("=== [1] body data-i18n key 是否被 en/ja i18n 覆蓋 ===")
print(f"    body data-i18n key 數={len(body_keys)};en i18n={len(en)} ja i18n={len(ja)}")
for name, s in (("en", en), ("ja", ja)):
    missing = sorted(body_keys - s)
    if missing:
        fail = 1
        print(f"    ❌ {name} i18n 未覆蓋 {len(missing)} 個 body key(該語言頁會 fallback 成中文):")
        for k in missing:
            print(f"         - {k}")
    else:
        print(f"    ✅ {name} i18n 完整覆蓋所有 body data-i18n key")
# en 與 ja key 集合是否對稱(一邊有一邊沒有 → 漏翻)
only_en = sorted(en - ja)
only_ja = sorted(ja - en)
if only_en:
    fail = 1
    print(f"    ❌ en 有但 ja 沒有 {len(only_en)} 個 key:")
    for k in only_en: print(f"         - {k}")
if only_ja:
    fail = 1
    print(f"    ❌ ja 有但 en 沒有 {len(only_ja)} 個 key:")
    for k in only_ja: print(f"         - {k}")
if not only_en and not only_ja:
    print("    ✅ en / ja i18n key 集合對稱")

# ---------- 2. MANUAL sections 三語 section id 對齊 ----------
print("=== [2] build.py MANUAL sections 三語章節 id 對齊 ===")
MANUAL = getattr(buildmod, "MANUAL", None)
if MANUAL and "sections" in MANUAL:
    secs = MANUAL["sections"]
    ids = {lang: [s["id"] for s in secs[lang]] for lang in ("zh", "en", "ja")}
    print(f"    章數:zh={len(ids['zh'])} en={len(ids['en'])} ja={len(ids['ja'])}")
    if ids["zh"] == ids["en"] == ids["ja"]:
        print("    ✅ 三語章節 id 順序完全一致")
    else:
        fail = 1
        for name in ("en", "ja"):
            miss = [i for i in ids["zh"] if i not in ids[name]]
            extra = [i for i in ids[name] if i not in ids["zh"]]
            if miss:  print(f"    ❌ {name} 缺章節 id: {miss}")
            if extra: print(f"    ❌ {name} 多章節 id: {extra}")
            if ids["zh"] != ids[name] and not miss and not extra:
                print(f"    ❌ {name} 章節順序與 zh 不同")
else:
    print("    (略過:未找到 MANUAL sections)")

print()
if fail:
    print("❌ 三語一致性檢查未通過 —— 修正後再 build/推。")
    sys.exit(1)
else:
    print("✅ 三語一致性檢查通過。")

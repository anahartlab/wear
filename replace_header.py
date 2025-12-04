#!/usr/bin/env python3
# replace_header.py
import os, re, shutil, datetime

HTML_DIR = "."  # папка с html (текущая)
HEADER_FILE = (
    "header.txt"  # файл с новым header (должен содержать <header>...</header>)
)
BACKUP_SUFFIX = ".bak"  # суффикс бэкапа (будет добавлена метка времени)

GOOGLE_TRANSLATE_SNIPPET = """
<style>
.translate-center-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    margin-top: 10px;
    margin-bottom: 10px;
}
#google_translate_element {
    display: inline-block;
    text-align: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.12);
    margin: 0 auto;
}
@media (max-width: 600px) {
    .translate-center-wrapper {
        margin-top: 8px;
        margin-bottom: 8px;
    }
    #google_translate_element {
        padding: 4px 4vw;
        font-size: 8px;
    }
}
</style>
<div class="translate-center-wrapper">
  <div id="google_translate_element"></div>
</div>
<script type="text/javascript">
function googleTranslateElementInit() {
  new google.translate.TranslateElement({
    pageLanguage: 'ru,en',
    includedLanguages: 'ru,en,fr,de,es,pt,hi,ar',
    layout: google.translate.TranslateElement.InlineLayout.SIMPLE
  }, 'google_translate_element');
}
</script>
<script type="text/javascript" src="//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>
"""


def read_header():
    if not os.path.exists(HEADER_FILE):
        raise SystemExit(f"❌ Не найден {HEADER_FILE}")
    txt = open(HEADER_FILE, "r", encoding="utf-8").read()
    if "<header" not in txt.lower() or "</header>" not in txt.lower():
        raise SystemExit("❌ header.txt должен содержать тег <header>...</header>")
    # Insert Google Translate snippet after the marker <!-- INSERT_TRANSLATE_HERE -->
    marker = "<!-- INSERT_TRANSLATE_HERE -->"
    if marker in txt:
        txt = txt.replace(marker, marker + GOOGLE_TRANSLATE_SNIPPET)
    return txt


def backup_path(path):
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{path}{BACKUP_SUFFIX}.{ts}"


def replace_header_in_file(path, new_header):
    txt = open(path, "r", encoding="utf-8").read()
    pattern = re.compile(r"(?is)(<header\b.*?>).*?(</header>)")
    if not pattern.search(txt):
        return False
    # делаем бэкап
    shutil.copy2(path, backup_path(path))
    new_txt = pattern.sub(new_header, txt, count=1)
    open(path, "w", encoding="utf-8").write(new_txt)
    return True


def main():
    new_header = read_header()
    files = [
        f
        for f in os.listdir(HTML_DIR)
        if f.lower().endswith(".html") and os.path.isfile(os.path.join(HTML_DIR, f))
    ]
    if not files:
        print("⚠️ HTML файлов не найдено в папке.")
        return
    replaced = 0
    skipped = []
    for fn in files:
        path = os.path.join(HTML_DIR, fn)
        ok = replace_header_in_file(path, new_header)
        if ok:
            print(f"✅ Обновлён: {fn}")
            replaced += 1
        else:
            print(f"— Пропущен (header не найден): {fn}")
            skipped.append(fn)
    print(f"\nГотово. Обновлено: {replaced}. Пропущено: {len(skipped)}.")


if __name__ == "__main__":
    main()

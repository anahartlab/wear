#!/usr/bin/env python3
# replace_foothead.py

import os, re, shutil, datetime

HTML_DIR = "."
HEADER_FILE = "header.txt"
FOOTER_FILE = "footer.txt"
BACKUP_SUFFIX = ".bak"


def read_file(path, tag_name):
    if not os.path.exists(path):
        raise SystemExit(f"❌ Не найден {path}")

    txt = open(path, "r", encoding="utf-8").read()

    if f"<{tag_name}" not in txt.lower() or f"</{tag_name}>" not in txt.lower():
        raise SystemExit(f"❌ {path} должен содержать тег <{tag_name}>...</{tag_name}>")

    return txt


def backup_path(path):
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{path}{BACKUP_SUFFIX}.{ts}"


def replace_block(txt, tag, replacement):
    pattern = re.compile(rf"(?is)(<{tag}\b.*?>).*?(</{tag}>)")
    return pattern.sub(replacement, txt, count=1)


def process_file(path, header, footer):
    txt = open(path, "r", encoding="utf-8").read()

    original = txt

    header_pattern = re.compile(r"(?is)(<header\b.*?>).*?(</header>)")
    footer_pattern = re.compile(r"(?is)(<footer\b.*?>).*?(</footer>)")

    changed = False

    if header_pattern.search(txt):
        txt = header_pattern.sub(header, txt, count=1)
        changed = True

    if footer_pattern.search(txt):
        txt = footer_pattern.sub(footer, txt, count=1)
        changed = True

    if not changed:
        return False

    shutil.copy2(path, backup_path(path))

    open(path, "w", encoding="utf-8").write(txt)

    return True


def main():
    header = read_file(HEADER_FILE, "header")
    footer = read_file(FOOTER_FILE, "footer")

    files = [
        f
        for f in os.listdir(HTML_DIR)
        if f.lower().endswith(".html") and os.path.isfile(os.path.join(HTML_DIR, f))
    ]

    if not files:
        print("⚠️ HTML файлов не найдено")
        return

    replaced = 0
    skipped = []

    for fn in files:
        path = os.path.join(HTML_DIR, fn)

        ok = process_file(path, header, footer)

        if ok:
            print(f"✅ Обновлён: {fn}")
            replaced += 1
        else:
            print(f"— Пропущен (header/footer не найден): {fn}")
            skipped.append(fn)

    print(f"\nГотово. Обновлено: {replaced}. Пропущено: {len(skipped)}.")


if __name__ == "__main__":
    main()

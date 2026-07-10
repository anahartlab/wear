import os
import csv
import sys
import random
from bs4 import BeautifulSoup

repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_root)

# === Параметры ===
theway = "fullprint"
csv_path = f"{theway}.csv"
html_path = f"{theway}.html"
images_dir = "images"
valid_exts = {".jpg", ".jpeg", ".png"}

# === Проверка HTML-файла ===
if not os.path.exists(html_path):
    print(f"❌ HTML-файл {html_path} не найден.")
    exit()

# === Читаем текущий HTML ===
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()


# === Парсим HTML для удаления навигации ===
soup = BeautifulSoup(html_content, "html.parser")

# === Удаляем весь контент между </header> и <footer> ===
header_end = html_content.lower().find("</header>")
footer_start = html_content.lower().find("<footer")
if header_end != -1 and footer_start != -1:
    html_content = (
        html_content[: header_end + len("</header>")] + html_content[footer_start:]
    )
# После очистки страница собирается заново из всех строк CSV.
# Поэтому существующие секции товаров больше не удаляются по id.

insert_index = html_content.lower().find("<footer")
if insert_index == -1:
    print("❌ Не найден <footer> в {html_content}")
    exit()

# === Читаем CSV ===
with open(csv_path, newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile, delimiter=",")
    # normalize headers to lowercase
    reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

    for row in reader:
        # normalize each key to lowercase
        row = {
            k.strip().lower(): (v.strip() if v is not None else "")
            for k, v in row.items()
        }

        name = row.get("name", "")

        # --- Получаем seo_name строго из SEO_url ---
        seo_name = (
            row.get("seo_url", "")
            or row.get("SEO_url", "")
            or row.get("Seo_Url", "")
            or ""
        ).strip()

        title = row.get("title", "")
        description = row.get("description", "")
        stock = row.get("stock", "")

        if not name:
            continue

        folder_path = os.path.join(images_dir, name)

        if not os.path.isdir(folder_path):
            print(f"⚠️  Пропущен '{name}' — папка '{folder_path}' не найдена.")
            continue

        all_images = [
            f
            for f in sorted(os.listdir(folder_path))
            if os.path.isfile(os.path.join(folder_path, f))
            and os.path.splitext(f)[1].lower() in valid_exts
        ]

        if not all_images:
            print(f"⚠️  Пропущен '{name}' — нет изображений.")
            continue

        # Если есть main.jpg или main.jpeg — оно всегда первое
        main_image = None
        for img in all_images:
            if img.lower() in ("main.jpg", "main.jpeg"):
                main_image = img
                break

        if main_image:
            remaining = [img for img in all_images if img != main_image]

            if len(remaining) > 7:
                remaining = random.sample(remaining, 7)

            images = [main_image] + remaining
        else:
            # Если main нет — первая картинка остается первой
            if len(all_images) > 8:
                first = all_images[0]
                remaining = random.sample(all_images[1:], 7)
                images = [first] + remaining
            else:
                images = all_images

        # Используем полностью уникальный id карусели.
        # Обрезание до 8 символов может приводить к совпадениям.
        carousel_base = seo_name if seo_name else name
        carousel_base = carousel_base.replace(' ', '-').replace('/', '-').replace('\\', '-')
        carousel_id = f"carousel-{carousel_base}"
        carousel_indicators = ""
        carousel_items = ""

        for i, img_name in enumerate(images):
            active_class = "u-active" if i == 0 else ""
            indicator_li = f'<li data-u-target="#{carousel_id}" data-u-slide-to="{i}" class="{active_class} u-grey-70 u-shape-circle" style="width: 10px; height: 10px;"></li>'
            carousel_indicators += "                          " + indicator_li + "\n"

            item_div = f"""\
                          <div class="{active_class} u-carousel-item u-gallery-item u-carousel-item-{i+1}" data-image-width="960" data-image-height="1280">
                            <div class="u-back-slide">
                              <img class="u-back-image u-expanded" src="images/{name}/{img_name}">
                            </div>
                            <div class="u-align-center u-over-slide u-shading u-valign-bottom u-over-slide-{i+1}"></div>
                            <style data-mode="XL"></style>
                            <style data-mode="LG"></style>
                            <style data-mode="MD"></style>
                            <style data-mode="SM"></style>
                            <style data-mode="XS"></style>
                          </div>"""
            carousel_items += item_div + "\n"

        # Форматируем stock с <br> и "☀️"
        if not stock.strip():
            stock_html = "Цифровая версия. Возможна продажа дизйайна либо изготовлени изделий оптом на заказ."
        else:
            stock_lines = [line.strip() for line in stock.splitlines() if line.strip()]
            stock_html = (
                "В наличии:<br>" + "<br>".join(f"☀️ {line}" for line in stock_lines)
                if stock_lines
                else "Изготовление на заказ. Опт."
            )

        # Защита от дублирующихся id на одной странице.
        while f'id="{carousel_id}"' in html_content:
            carousel_id += "-dup"

        block = f"""
    <section class="u-clearfix u-section-16" id="{seo_name}">
      <div class="u-clearfix u-sheet u-valign-middle-md u-valign-top-lg u-valign-top-xl u-sheet-1">
        <div class="data-layout-selected u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-size-30">
                <div class="u-layout-col">
                  <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-1">
                    <div class="u-container-layout u-valign-middle-lg u-valign-middle-sm u-valign-middle-xs u-container-layout-1" style="display:flex; flex-direction:column; justify-content:center; align-items:center;">
                      <div class="custom-expanded u-carousel u-gallery u-gallery-slider u-layout-carousel u-lightbox u-no-transition u-show-text-none u-gallery-1" data-interval="5000" data-u-ride="carousel" id="{carousel_id}">
                        <ol class="u-absolute-hcenter u-carousel-indicators u-carousel-indicators-1">
{carousel_indicators}                        </ol>
                        <div class="u-carousel-inner u-gallery-inner u-gallery-inner-1" role="listbox">
{carousel_items}                        </div>
                        <a class="u-absolute-vcenter u-carousel-control u-carousel-control-prev u-grey-70 u-icon-circle u-opacity u-opacity-70 u-spacing-10 u-text-white u-carousel-control-1" href="#{carousel_id}" role="button" data-u-slide="prev">
                          <span aria-hidden="true">
                            <svg viewBox="0 0 451.847 451.847"><path d="..."/></svg></span><span class="sr-only">Previous</span>
                        </a>
                        <a class="u-absolute-vcenter u-carousel-control u-carousel-control-next u-grey-70 u-icon-circle u-opacity u-opacity-70 u-spacing-10 u-text-white u-carousel-control-2" href="#{carousel_id}" role="button" data-u-slide="next">
                          <span aria-hidden="true">
                            <svg viewBox="0 0 451.846 451.847"><path d="..."/></svg></span><span class="sr-only">Next</span>
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="u-size-30">
                <div class="u-layout-col">
                  <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-2">
                    <div style="display:flex; flex-direction:column; align-items:center;">
                      <h4 class="u-align-center u-text u-text-1">{title}</h4>
                      <p class="u-align-center u-text u-text-availability"><b> По ссылке ниже можно посмотреть 3D/AR модель через браузер Вашего телефона. <br> Google Chrome (Android) , Safari (iPhone)</b></p>
<p class="u-align-center u-text u-text-availability">
  <a href="https://anahartlab.github.io/ar/{name}.html"
     style="background-color:#4CAF50; color:#000; padding:8px 16px; border-radius:6px; text-decoration:none; display:inline-block;"
     title="{title}">
    Посмотреть 3D/AR модель
  </a>
</p>   
                      <p class="u-align-left u-text u-text-2" style="display:inline-block; text-align:left; max-width:100%;">{description}</p>
                      <p class="u-align-center u-text u-text-availability">{stock_html}</p>
                      <p class="u-align-center u-text u-text-availability"><a href="https://t.me/anahart" class="u-btn u-button-style u-custom-font u-heading-font u-hover-palette-1-light-1 u-palette-1-base u-radius-50 u-btn-1" style="border-radius: 100px;" title="Свяжитесь для уточнения подробностей">Написать автору</a></p>
 
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>"""

        # === Вставка перед <footer> ===
        insert_index = html_content.lower().find("<footer")
        if insert_index == -1:
            raise RuntimeError("Не найден <footer> при вставке товара")

        html_content = (
            html_content[:insert_index] + block + "\n" + html_content[insert_index:]
        )

# === Сохраняем результат ===
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Все товары из CSV добавлены")

import sys

# === Установка рабочей директории (если скрипт запущен не из корня репозитория) ===
repo_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(repo_root)

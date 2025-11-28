from bs4 import BeautifulSoup
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(current_dir, "main.html")

with open(html_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Сохраняем header и footer, удаляем всё остальное
body_tags = list(soup.body.contents)
for tag in body_tags:
    if not (tag.name == "header" or tag.name == "footer"):
        tag.extract()

# Вставляем пустой блок после header для визуального разделения
header_tag = soup.body.find("header")
if header_tag:
    spacer = soup.new_tag("div", **{"style": "height:50px;"})
    header_tag.insert_after(spacer)

# Сохраняем результат
with open(html_path, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("Остались только шапка и футер, меню сохранено, добавлен пустой блок для разделения")
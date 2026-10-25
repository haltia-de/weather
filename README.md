# Погода

Прогноз погоды на одной странице (`haltia-weather`), для любого города.

- Данные — открытый XML-сервис Gismeteo, значки погоды рисуются программой
  по кодам Gismeteo (их картинки не используются).
- Сейчас: температура, «ощущается как», ветер, давление, влажность, вода,
  восход и закат, магнитное поле. Ниже — по дням с шагом 3 часа; нажатие на
  день открывает его подробно.
- Город выбирается в программе (шестерёнка → «Город», поиск по названию) и
  хранится в `~/.config/haltia/weather.conf`.

## Установка

**Ubuntu 24.04, Debian 13** (и elementary OS 8, Linux Mint 22) — из
репозитория apt Haltia:

```
sudo curl -fsSLo /usr/share/keyrings/haltia-archive-keyring.gpg https://haltia-de.github.io/packages/apt/haltia-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/haltia-archive-keyring.gpg] https://haltia-de.github.io/packages/apt $(. /etc/os-release; echo $VERSION_CODENAME) main" | sudo tee /etc/apt/sources.list.d/haltia.list
sudo apt update && sudo apt install haltia-weather
```

**Flatpak** (любой дистрибутив; среда GNOME — с Flathub):

```
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak remote-add --if-not-exists haltia https://haltia-de.github.io/packages/flatpak/haltia.flatpakrepo
flatpak install haltia io.github.haltia_de.Weather
```

В Flatpak настройки лежат в `~/.var/app/io.github.haltia_de.Weather/config/haltia/weather.conf`.

**Alpine и postmarketOS** — пакет `haltia-weather` из
[репозитория apk Haltia](https://github.com/haltia-de/packages).

**Из исходников:** нужны Python 3, GTK 3 и PyGObject.

```
sh install.sh            # в / (нужен root)
sh install.sh /mnt/root  # в другой корень, например при сборке образа
```

`install.sh` кладёт программу в `/usr/local/bin/haltia-weather` (пакет — в
`/usr`), её `.desktop`, значок и описание AppStream. Сборка пакетов:
`debian/` и `packaging/flatpak/`, выпуск по тегу — `haltia-de/ci`.

## Haltia

Программа — часть среды [Haltia](https://github.com/haltia-de): образы
Pertin Haltia ставят её пакетом `haltia-weather`, оболочка показывает её на
домашнем экране. На любом другом рабочем столе с GTK 3 она работает так же:
вне оболочки у окна обычные кнопки, в том числе «Закрыть».

## Лицензия

GPL-2.0 (`LICENSE`).

#!/usr/bin/env python3
"""Fetch real cover images from Internet Archive for game covers.

For each game, downloads the best available image from IA and converts to 300x200 WebP.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

IMAGES_DIR = Path(__file__).resolve().parent.parent / "public" / "images"

# (target_filename, ia_identifier, image_filename, description)
# image_filename=None means "auto-detect best"
# image_filename="__ia_thumb" means use services/img thumbnail
GAMES = [
    ("bloonstd1-cover.webp", "btd1_20220404", "00_coverscreenshot.png", "Bloons TD 1"),
    ("bloonstd2-cover.webp", "bloons_tower_defense_2_flash", "bloons_tower_defense_2_screenshot.png", "Bloons TD 2"),
    ("bloonstd3-cover.webp", "bloons-tower-defense-3", "Btd3a.png", "Bloons TD 3"),
    ("bloonstd4-cover.webp", "bloonstd4exp_flash", "bloonstd4exp_flash_screenshot.png", "Bloons TD 4"),
    ("bloonstd5cover.webp", "btd5_20210115", "00_coverscreenshot.png", "Bloons TD 5"),
    ("fireboy-watergirl-cover.webp", "fireboy-and-watergirl-in-the-forest-temple", "FireboyWatergirl.png", "Fireboy & Watergirl 1"),
    ("fireboy-watergirl-2-cover.webp", "fireboy-and-watergirl-2-in-the-light-temple", "00_A.jpg", "Fireboy & Watergirl 2"),
    ("fireboy-watergirl-3-cover.webp", "fireboy-and-watergirl-3-in-the-ice-temple", "00_A.jpg", "Fireboy & Watergirl 3"),
    ("fireboy-watergirl-4-cover.webp", "fireboy-and-watergirl-4-in-the-crystal-temple", "00_A.jpg", "Fireboy & Watergirl 4"),
    ("sonny-cover.webp", "sonny-flash-game-series.", "sonny_main_menu_patch4.1.png", "Sonny"),
    ("sonny-2-cover.webp", "sonny-flash-game-series.", "sonny_2_main_menu_v2.2.png", "Sonny 2"),
    ("epic-battle-fantasy-3-cover.webp", "epic-battle-fantasy-3.-by-matt-roszak-aka-kupo707", "Epic_Battle_Fantasy_3_Menu_003.png", "Epic Battle Fantasy 3"),
    ("epic-battle-fantasy-5-cover.webp", "epic-battle-fantasy-5-v1.5.4.", "EBF5_Main_Menu_v1.5.4.png", "Epic Battle Fantasy 5"),
    ("gemcraft-cover.webp", "gemcraft-1716", "gemcraft-1716_screenshot.jpg", "GemCraft"),
    ("kingdom-rush-cover.webp", "kingdom-rush-frontie-15717", "00_coverscreenshot.png", "Kingdom Rush"),
    ("the-last-stand-cover.webp", "the-last-stand", "00_coverscreenshot.png", "The Last Stand"),
    ("the-last-stand-2-cover.webp", "the-last-stand-2", "00_coverscreenshot.png", "The Last Stand 2"),
    ("the-last-stand-union-city-cover.webp", "the-last-stand-union-city", "00_coverscreenshot.png", "The Last Stand: Union City"),
    ("desktop-tower-defense-cover.webp", "desktop-tower-defence_flash", "00_coverscreenshot.png", "Desktop Tower Defense"),
    ("knightmare-tower-cover.webp", "knightmare-tower-flash-game", "knightmaretower-gameplay1.png", "Knightmare Tower"),
    ("age-of-war-2-cover.webp", "ageofwar2_202401", "00_coverscreenshot.png", "Age of War 2"),
    ("stick-war-2-cover.webp", "stick-war-2-remix-part-1-official-public-v-1.22", "00_coverscreenshot.png", "Stick War 2"),
    ("raze-2-cover.webp", "raze-2", "00_coverscreenshot.png", "Raze 2"),
    ("swords-and-sandals-3-cover.webp", "swords-and-sandals-3-solo-flash", "00_coverscreenshot.png", "Swords and Sandals 3"),
    ("the-impossible-quiz-cover.webp", "the-impossible-quiz", "__ia_thumb", "The Impossible Quiz"),
    ("crush-the-castle-2-cover.webp", "crush-the-castle-flash-game-series", "CrushtheCastle2-menu.png", "Crush the Castle 2"),
    ("infectonator-cover.webp", "infectonator-flash-game-series.", "Infectonator_menu_v1.5.png", "Infectonator"),
    ("infectonator-2-cover.webp", "infectonator-flash-game-series.", "infectonator2_main_menu_v1.5.png", "Infectonator 2"),
    ("infectonator-hot-chase-cover.webp", "infectonator-flash-game-series.", "infectonator_hot_chase_menu_v1.3.5.png", "Infectonator: Hot Chase"),
    ("infectonator-survivors-cover.webp", "infectonator-flash-game-series.", "infectonator_survivors_menu_alpha_v.051.png", "Infectonator: Survivors"),
    ("warfare-1917-cover.webp", "warfare-1917", "00_coverscreenshot.png", "Warfare 1917"),
    ("mutilate-a-doll-2-cover.webp", "mutilate-a-doll-2_202011", "__ia_thumb", "Mutilate a Doll 2"),
    ("thing-thing-cover.webp", "Thing-Thing-Collection", "Thing Thing Collection.png", "Thing Thing"),
    ("binding-of-isaac-cover.webp", "the-binding-of-isaac_202111", "00_coverscreenshot.png", "The Binding of Isaac"),
    ("meatboy-cover.webp", "flash_meatboy", "flash_meatboy_screenshot.png", "Meat Boy"),
    ("onslaught-cover.webp", "onslaught2_202311", "00_coverscreenshot.png", "Onslaught"),
    ("monsters-den-cover.webp", "monsters-den-book-of-dread", "00_coverscreenshot.png", "Monster's Den: Book of Dread"),
]


def download_and_convert(img_url, output_path):
    tmp_path = None
    try:
        resp = requests.get(img_url, timeout=30, stream=True)
        if resp.status_code != 200:
            return False
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type:
            return False

        suffix = ".jpg" if "jpeg" in content_type else ".png"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name

        result = subprocess.run(
            [
                "convert", tmp_path,
                "-resize", "300x200^",
                "-gravity", "center",
                "-extent", "300x200",
                str(output_path),
            ],
            capture_output=True, timeout=30,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"    convert error: {e}", file=sys.stderr)
        return False
    finally:
        if tmp_path:
            os.unlink(tmp_path)


def main():
    success = 0
    failed = 0
    skipped = 0

    for filename, identifier, image_name, desc in GAMES:
        output_path = IMAGES_DIR / filename
        print(f"  [{desc}] -> {filename}...", end=" ", flush=True)

        if identifier is None:
            print("SKIPPED (no IA identifier)")
            skipped += 1
            continue

        if image_name == "__ia_thumb":
            img_url = f"https://archive.org/services/img/{identifier}"
        elif image_name:
            img_url = f"https://archive.org/download/{identifier}/{image_name}"
        else:
            img_url = f"https://archive.org/services/img/{identifier}"

        if download_and_convert(img_url, output_path):
            size = output_path.stat().st_size
            print(f"OK ({size}B)")
            success += 1
        else:
            print("FAILED")
            if output_path.exists():
                output_path.unlink()
            failed += 1

    print(f"\nDone: {success} succeeded, {failed} failed, {skipped} skipped")


if __name__ == "__main__":
    main()

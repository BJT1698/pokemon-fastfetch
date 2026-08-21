#!/usr/bin/env python3
"""
Pokemon Fastfetch Sprite Generator
Downloads Generation 2 (Crystal) animated sprites from PokeAPI,
extracts dynamic color palettes for each Pokemon, and builds
native Kitty Graphics animation (.raw) files with 1-loop playback.
"""

import urllib.request
import json
import os
import io
import base64
import argparse
import concurrent.futures
from PIL import Image, ImageSequence

POKEAPI_LIST_URL = "https://pokeapi.co/api/v2/pokemon?limit=251"
SPRITE_BASE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-ii/crystal/animated/{url_id}.gif"

def rgb_to_hex(r, g, b):
    return f"{r:02x}{g:02x}{b:02x}"

def is_gray_or_extreme(r, g, b):
    if r < 35 and g < 35 and b < 35:
        return True
    if r > 240 and g > 240 and b > 240:
        return True
    return False

def get_color_saturation(r, g, b):
    mx = max(r, g, b)
    mn = min(r, g, b)
    if mx == 0:
        return 0
    return (mx - mn) / mx

def get_color_brightness(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b

def boost_color(rgb, target_lum=130):
    r, g, b = rgb
    lum = get_color_brightness(r, g, b)
    if lum < 100:
        factor = target_lum / max(lum, 1)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
    return (r, g, b)

def extract_palette(frames):
    pixel_counts = {}
    for f in frames:
        rgba = f.convert("RGBA")
        for p in rgba.get_flattened_data():
            if p[3] > 64:  # non-transparent
                rgb = (p[0], p[1], p[2])
                pixel_counts[rgb] = pixel_counts.get(rgb, 0) + 1

    colored = [c for c in pixel_counts.keys() if not is_gray_or_extreme(*c)]
    if not colored:
        colored = [c for c in pixel_counts.keys() if c != (0, 0, 0) and c != (255, 255, 255)]
    if not colored:
        colored = [(100, 200, 255)]

    readable = []
    for c in colored:
        b = get_color_brightness(*c)
        s = get_color_saturation(*c)
        count = pixel_counts.get(c, 1)
        score = count * (1 + s) * (1 if b > 50 else 0.5)
        readable.append((score, c))

    readable.sort(reverse=True)
    primary = boost_color(readable[0][1], target_lum=140)

    if len(readable) > 1:
        secondary = boost_color(readable[1][1], target_lum=160)
    else:
        secondary = (min(255, primary[0] + 50), min(255, primary[1] + 50), min(255, primary[2] + 50))

    return rgb_to_hex(*primary), rgb_to_hex(*secondary)

def build_kitty_raw(frames, durations, cols=28, rows=14, img_id=999):
    w, h = frames[0].size
    parts = []

    # 1. Base frame (a=T)
    raw1 = frames[0].tobytes()
    b64_1 = base64.b64encode(raw1).decode("ascii")
    z1 = durations[0] if len(durations) > 0 else 100
    parts.append(f"\x1b_Ga=T,f=32,s={w},v={h},c={cols},r={rows},i={img_id},z={z1},q=2;{b64_1}\x1b\\")

    # 2. Subsequent frames (a=f)
    for idx_f, (frame, dur) in enumerate(zip(frames[1:], durations[1:]), start=2):
        raw_f = frame.tobytes()
        fb64 = base64.b64encode(raw_f).decode("ascii")
        parts.append(f"\x1b_Ga=f,i={img_id},f=32,s={w},v={h},z={dur},q=2;{fb64}\x1b\\")

    # 3. Animation control: s=3 (run animation), v=2 (1 loop / play once and stop on last frame)
    parts.append(f"\x1b_Ga=a,i={img_id},s=3,v=2,q=2\x1b\\")

    return "".join(parts)

def process_pokemon(idx_poke, target_dir):
    idx, poke = idx_poke
    poke_id = idx + 1
    name = poke["name"]
    url_id = "201-a" if poke_id == 201 else str(poke_id)
    sprite_url = SPRITE_BASE_URL.format(url_id=url_id)

    try:
        req = urllib.request.Request(sprite_url, headers={"User-Agent": "PokemonFastfetch/1.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        img = Image.open(io.BytesIO(data))

        frames = [f.convert("RGBA") for f in ImageSequence.Iterator(img)]
        durations = [f.info.get("duration", 100) for f in ImageSequence.Iterator(img)]

        p_col, s_col = extract_palette(frames)
        raw_content = build_kitty_raw(frames, durations)

        filename = f"{poke_id:03d}_{name}_{p_col}_{s_col}.raw"
        file_path = os.path.join(target_dir, filename)

        with open(file_path, "w") as f:
            f.write(raw_content)

        return f"[{poke_id:03d}/251] {name}: OK ({p_col}, {s_col})"
    except Exception as e:
        return f"[{poke_id:03d}/251] {name}: ERROR ({e})"

def main():
    parser = argparse.ArgumentParser(description="Generate animated Pokemon sprites for Fastfetch.")
    parser.add_argument(
        "--target-dir",
        default=os.path.expanduser("~/.local/share/pokemon-sprites/animated"),
        help="Target directory to store .raw animation files"
    )
    args = parser.parse_args()

    os.makedirs(args.target_dir, exist_ok=True)
    print(f"Target directory: {args.target_dir}")
    print("Fetching Pokemon list from PokeAPI...")

    req = urllib.request.Request(POKEAPI_LIST_URL, headers={"User-Agent": "PokemonFastfetch/1.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        results = data["results"]

    print(f"Processing {len(results)} Pokemon sprites concurrently...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(process_pokemon, (i, p), args.target_dir) for i, p in enumerate(results)]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if "ERROR" in res:
                print(res)

    count = len([f for f in os.listdir(args.target_dir) if f.endswith(".raw")])
    print(f"\nDone! Generated {count} animated sprites in {args.target_dir}.")

if __name__ == "__main__":
    main()

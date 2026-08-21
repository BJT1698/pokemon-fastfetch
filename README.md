# 🎮 Pokemon Fastfetch

> A dynamic, minimalist, and aesthetic **Fastfetch** configuration featuring **animated Generation 2 (Crystal) Pokémon sprites** with **automatic color-matched system info**, designed for **Fish Shell** and **Kitty Terminal**.

---

## ✨ Features

- 🌟 **251 National Pokédex Animated Sprites**: Covers every Pokémon from Generation 1 and 2 (#001 Bulbasaur to #251 Celebi, including Unown).
- 🎬 **Authentic Single-Loop Crystal Animations**: Plays the original entrance animation once on startup and cleanly settles into the static resting pose.
- 🎨 **Dynamic Color Palette Matching**: Automatically extracts the Pokémon's signature colors to theme the system info labels, titles, and separators dynamically.
- ⚡ **Zero Startup Latency**: Pre-compiled Kitty Graphics Protocol sequences (`.raw`) mean opening a terminal takes ~20ms with 0% CPU overhead.
- 🧼 **Clean & Essential Layout**: Focused on what matters (OS, Kernel, Uptime, Window Manager, Shell, Terminal, Memory, and color palette circles).

---

## 📋 Requirements

- [**Fastfetch**](https://github.com/fastfetch-cli/fastfetch) (v2.0+)
- [**Kitty Terminal**](https://sw.kovidgoyal.net/kitty/) (supports native Kitty Graphics Protocol animations)
- [**Fish Shell**](https://fishshell.com/)
- [**Python 3**](https://www.python.org/) with `Pillow` (used during the initial sprite generation)
- A [**Nerd Font**](https://www.nerdfonts.com/) (e.g. JetBrainsMono Nerd Font, FiraCode Nerd Font) for icons

---

## 🚀 Quick Installation

Clone this repository and run the automated installer:

```bash
git clone https://github.com/BJT1698/pokemon-fastfetch.git
cd pokemon-fastfetch
chmod +x install.sh
./install.sh
```

The installer will:
1. Check dependencies (`fastfetch`, `kitty`, `fish`, `python-pillow`).
2. Download and compile all 251 Crystal animation sequences to `~/.local/share/pokemon-sprites/animated/`.
3. Install the Fastfetch configuration to `~/.config/fastfetch/config.jsonc`.
4. Install the Fish function to `~/.config/fish/functions/fastfetch.fish`.
5. Enable the greeting hook in `~/.config/fish/config.fish`.

---

## 🛠️ Manual Installation

If you prefer to configure manually:

### 1. Generate Sprites
```bash
python3 scripts/generate_sprites.py --target-dir ~/.local/share/pokemon-sprites/animated
```

### 2. Copy Fastfetch Configuration
```bash
mkdir -p ~/.config/fastfetch
cp config/fastfetch/config.jsonc ~/.config/fastfetch/config.jsonc
```

### 3. Copy Fish Function
```bash
mkdir -p ~/.config/fish/functions
cp fish/functions/fastfetch.fish ~/.config/fish/functions/fastfetch.fish
```

### 4. Enable Startup Greeting
Add the following to `~/.config/fish/config.fish`:
```fish
function fish_greeting
    fastfetch
end
```

---

## 🔍 How It Works

1. **Sprite Compilation**: `generate_sprites.py` downloads official Crystal GIF sprites from PokeAPI, extracts the dominant primary and secondary colors, and packs multi-frame Kitty Graphics Protocol escape codes (`a=T`, `a=f`, `a=a,s=3,v=2`).
2. **Runtime Execution**: When `fastfetch` is invoked in `fish`, the wrapper randomly picks a `.raw` sprite, parses the embedded color metadata in `< 1ms`, and launches:
   ```bash
   fastfetch --raw "$sprite" --color-keys "$primary_color" --color-separator "$secondary_color"
   ```
3. **GPU Hardware Animation**: Kitty's compositor plays the multi-frame animation sequence asynchronously and stops on the last frame.

---

## ⚙️ Configuration & Customization

You can customize the displayed modules, icons, or separators in `~/.config/fastfetch/config.jsonc`:

```jsonc
{
    "$schema": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
    "logo": {
        "type": "raw",
        "width": 28,
        "height": 14,
        "padding": {
            "top": 1,
            "right": 3
        }
    },
    "display": {
        "separator": " 󰄾 "
    },
    "modules": [
        "title",
        "separator",
        {
            "type": "command",
            "key": "󰐼 Pokémon",
            "text": "echo -n \"$POKEMON_NAME\""
        },
        "os",
        "kernel",
        "uptime",
        "wm",
        "shell",
        "terminal",
        "memory",
        "break",
        {
            "type": "colors",
            "symbol": "circle"
        }
    ]
}
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).  
Pokémon sprites and trademarks are property of Nintendo, Game Freak, and The Pokémon Company.

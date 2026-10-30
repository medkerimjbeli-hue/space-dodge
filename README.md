# 🚀 Space Dodge

> Survive as long as you can. Dodge the rocks. The longer you last, the faster they get.

**Space Dodge** is a free arcade survival game for Windows, and the first release from **indie-TUN** — *Independent games. Tunisian soul.* 🇹🇳

<!-- Add a screenshot or GIF here, e.g. ![Gameplay](docs/gameplay.gif) -->

## ✨ Features

- Endless survival gameplay with difficulty that scales over time (faster, more rocks)
- Best-time tracking saved between sessions
- Menu, how-to-play and game-over screens built on a proper state machine
- Custom HUD built from sprite assets
- 8-bit sound effects generated from scratch with Python's standard library
- Resizable window and fullscreen toggle

## 🎮 Controls

| Action | Keys |
|---|---|
| Move | `W` `A` `S` `D` or Arrow keys |
| Restart (after game over) | `R` |
| Back to menu | `Esc` |
| Toggle fullscreen | `F11` |

## ▶️ Play

### Option 1: Download the game (Windows)
Grab the latest zip from the [Releases](../../releases) page, extract it, and run **Space Dodge Alpha v0.1.exe**.

### Option 2: Run from source
Requires Python 3.10+.

```bash
git clone https://github.com/medkerimjbeli-hue/space-dodge.git
cd space-dodge
pip install -r requirements.txt
python main.py
```

## 🛠️ Build the executable

```bash
pip install pyinstaller
pyinstaller "Space Dodge Alpha v0.1.spec"
```

The built game appears in `dist/`.

## 🧰 Built with

- Python
- [pygame](https://www.pygame.org/)
- PyInstaller

## 📌 Status

Alpha (v0.1). Bugs are being fixed and the code is being polished as development continues.

## 👤 Author

**Mohamed Kerim Jbeli** — indie-TUN
- GitHub: [@medkerimjbeli-hue](https://github.com/medkerimjbeli-hue)
- Instagram: [@med_kerim_jbeli](https://www.instagram.com/med_kerim_jbeli/)

# Py-Chess Game

A simple chess game made using PyGame

---

Thanks to this awesome tutorial by [CodingSpot](https://www.youtube.com/@codingspot):
[Coding a Complete Chess Game AI With Python (Part 1) | PVP Game Mode](https://www.youtube.com/watch?v=OpL0Gcfn4B4)

# Game Instructions

* Working on AI gamemode...

- Entry point: main.py
- Press 't' to change theme (green, brown, blue, gray)
- Press 'r' to reset the game

# Additional Functions

- Press 'u' to undo last move
- Press 'm' to enable/disable Player vs. AI mode (still under development)
- Press 'Escape' key to exit the game
- Added checkmate detection
- Added stalemate detection
- Added insufficient material rule
- Added three-fold repitition rule
- Added 50 moves rule

# To be fixed
- Player vs. AI mode

# To be added
- Additional UI components
- Change difficulty of the AI
- And more

# Building the game

### Required Modules:

- [PyGame](https://pypi.org/project/pygame/)

```bash
pip install pygame
```

- [CX_Freeze](https://pypi.org/project/cx-Freeze/)

```
pip install cx_Freeze
```

### Build as a python program:
```bash
python src/main.py
```

### Build as a standalone exe
```bash
# Without installer
python src/setup.py build

# With installer (windows)
python src/setup.py bdist_msi
```

Files(`.exe`) will be found inside of `build` folder that will

be generated when you build it as a standalone exe file.

If you built with `bdist_msi`, the installer

will be located at `dist` folder.
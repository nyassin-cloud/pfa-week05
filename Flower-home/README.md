# Flower Home

A flower collects eyeballs, throws them at the Fridge Fiend, and climbs to its
family's vase on top of the refrigerator. Defeat the monster with six eyes, then
reach the vase within seven seconds before it returns and eats you. A countdown
and shrinking bar show the time left. You have three petals (health) and eyes will regrow
after three seconds.

## How to run it

Requires desktop Python 3.10–3.13 and Pygame 2.6.1. Use Python 3.12 for
the tested setup. Install Python from https://www.python.org/downloads/ if needed;
on Windows enable the Python launcher. Internet is needed for the initial Pygame
installation; the game then runs offline. All artwork is drawn in code.

Extract/copy this folder. Open a terminal **inside the folder containing game.py**.
On Windows, open the folder in File Explorer, type `powershell` in its address
bar, and press Enter.

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe game.py
```

If your installed Python uses `python` instead of `py`, use
`python -m venv .venv` for the first command. Using the venv executable directly
avoids PowerShell activation-policy issues. Optional activation:
`.\.venv\Scripts\Activate.ps1`, then `python game.py`.

macOS/Linux (with Python 3.12 installed):

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python game.py
```

On Linux you may need your distribution's Python venv package. If `pip` reports
that no compatible Pygame distribution is available, check that you are using
Python 3.12. Run this on a graphical desktop, not a browser-only Python runner.

Controls: A/D or arrow keys move; Space/W/Up jumps; E throws an eye with
automatic aiming; R restarts only on the win/loss screen; Escape quits. Tap E once for each throw.
Only the green projectiles hurt you. Platforms can be jumped through from below.
Move close to a shelf edge before jumping to the next one. You can stay near
an eye spawn to collect more ammunition, but keep dodging the green projectiles.

## What I made better

I missed the class, so this is a new Pygame project. I chose the concept and requested improvements through playtesting, with coding-agent help. 
- Collectible eyes that regrow, with an ammunition counter.
- A giant monster with a health bar, warning before attacks, and green projectiles.
- Eye throwing with automatic aim at the monster.
- Three health points, brief invulnerability after damage, and a loss screen.
- A family reunion win screen and restart control.
- Quicker movement and shorter jump airtime after playtesting; R cannot reset an active run.
- Faster attacks, a locked vase, and a seven-second escape deadline: the monster eats you if time runs out.
- OUCH hit bubbles, HELP from the family, and a cartoon blood-and-organ explosion.
- A flower character, kitchen shelves, fridge, and family drawn in code.

## How it works

- **`jump`**: The player jumps onto platforms to collect eyes and fight the monster so they can reach their family. This function starts the jump only when the flower is standing on the floor or a platform.
- **`throw_eye`**: Throwing eyes is required to defeat the monster. Press E to throw an eye. The function uses one collected eye and sends it toward the monster.
- **`monster_message`: I typed the function below to give the monster an "OUCH!" message when it is hit.

```python
def monster_message():
    return "OUCH!"
```
## One undo

The agent changed the monster's shooting interval from 1.1 seconds to 3 seconds. I played the game and found it too easy: I could collect eyes and defeat the monster faster than it could hit me. I wanted the faster attacks back.

I checked the change with `git --no-pager diff -- game.py`, then ran `git restore game.py` to discard the experiment and restore the 1.1-second interval. Afterward, `git status` showed "nothing to commit, working tree clean."

To test a fresh installation, copy game.py, check_game.py, requirements.txt, and this README into a new empty folder. Do not copy .venv or __pycache__. Follow the setup commands above from the beginning, then play the game.

# Tamagotchi Pet Project Status

## Project Goal

Build a small Tamagotchi-style virtual pet in Python on Windows first, then eventually deploy it to a Raspberry Pi Zero / Pi Zero 2 W with a Whisplay HAT.

The Windows version is the development prototype. The final Pi version should use the same pet logic but swap the desktop input/display/audio layer for Whisplay HAT hardware support.

## Current Development Environment

* OS: Windows
* Editor: VS Code
* Python: 3.12 virtual environment
* Project root: `A:\Games\Projects\tamagotchi`
* Virtual environment: `.venv`
* Main run command:

```powershell
.venv\Scripts\Activate.ps1
python main.py
```

Important note: Python 3.14 caused pygame install/build problems. Python 3.12 works.

Current key dependency:

```txt
pygame==2.6.1
```

Pillow was also used for sprite cleanup experiments:

```txt
pillow
```

## Save / Editor Workflow Notes

Use **Save All** in VS Code before running because regular `Ctrl+S` only saves the active tab.

Save All shortcut:

```text
Ctrl + K, then S
```

Recommended VS Code setting: enable Auto Save.

Before commits:

```powershell
git status
git add .
git commit -m "Describe change"
```

## Current File Structure

```text
tamagotchi/
├─ main.py
├─ save.json
├─ requirements.txt
├─ PROJECT_STATUS.md
├─ assets/
│  ├─ pet_idle.png
│  ├─ pet_happy.png
│  ├─ pet_sleep.png
│  ├─ pet_hungry.png
│  ├─ pet_dirty.png
│  ├─ pet_tired.png
│  ├─ pet_sad.png
│  ├─ pet_sick.png
│  └─ sounds/
│     ├─ feed.wav
│     ├─ play.wav
│     ├─ clean.wav
│     ├─ sleep.wav
│     ├─ wake.wav
│     ├─ error.wav
│     ├─ menu.wav
│     ├─ select.wav
│     ├─ poop.wav
│     ├─ pee.wav
│     ├─ medicine.wav
│     └─ treat.wav
├─ io_layer/
│  ├─ __init__.py
│  ├─ windows_io.py
│  └─ whisplay_io.py
├─ pet/
│  ├─ __init__.py
│  ├─ state.py
│  ├─ save.py
│  ├─ logic.py
│  ├─ mood.py
│  ├─ sprites.py
│  └─ sounds.py
└─ tools/
   └─ remove_bg.py
```

## Implemented Features

### Core Pet

The pet is named `Bit`.

Current core stats:

```text
hunger: 0-100
happiness: 0-100
cleanliness: 0-100
energy: 0-100
health: 0-100
asleep: bool
```

Additional room accident state:

```text
mess_count: 0-3
time_since_last_mess
pee_count: 0-3
time_since_last_pee
```

Stats are persisted to `save.json`.

Offline progress is applied on startup based on `last_seen`, capped to avoid instant catastrophe after long breaks.

### Controls

Current Windows controls:

```text
Up / W       = move menu cursor up
Down / S     = move menu cursor down
Enter/Space  = select
M            = debug-cycle displayed mood
Esc          = quit
```

`M` is a temporary development/debug feature and should be removed or hidden before production.

### Current Menu Actions

Dynamic menu options include:

```text
Feed
Play
Clean
Sleep/Wake
Meds
Treat
```

Sleep changes to Wake when Bit is asleep.

Medicine appears only when useful / when health is low.

Energy Treat appears when energy is low.

### Care Actions

#### Feed

* Increases hunger
* Slightly decreases cleanliness
* Slightly increases happiness
* Does not work while Bit is asleep

#### Play

* Increases happiness
* Decreases energy
* Decreases hunger
* Decreases cleanliness
* Does not work while asleep
* Fails if Bit is too tired

#### Clean

* If poop or pee is present, clears both
* Resets accident timers
* Increases cleanliness
* Slightly increases happiness
* If no accidents are present, performs normal cleaning

#### Sleep / Wake

* Toggles `pet.asleep`
* While sleeping, energy regenerates faster
* Hunger still drains slowly
* Happiness drains slowly
* Poop/pee timers do not progress while asleep

#### Medicine

* Used when health is low
* Increases health significantly
* Reduces happiness dramatically, currently around half
* Does not work while asleep
* Plays medicine sound

#### Energy Treat

* Boosts energy
* Slightly increases hunger and happiness
* If overused when energy is already high, Bit becomes too wired and loses some happiness/health
* Does not work while asleep

## Mood System

Mood logic is in:

```text
pet/mood.py
```

Mood is deterministic, not random. Stats and room state determine Bit’s mood.

Current moods:

```text
idle
happy
hungry
dirty
tired
sad
sick
asleep
```

Sprite mapping is mood-based:

```text
idle   -> pet_idle.png
happy  -> pet_happy.png
hungry -> pet_hungry.png
dirty  -> pet_dirty.png
tired  -> pet_tired.png
sad    -> pet_sad.png
sick   -> pet_sick.png
asleep -> pet_sleep.png
```

Mood scoring uses a `problems` list and sorts by severity. This was added because simple priority order caused Bit to get stuck on one face.

Current intended accident mood progression:

```text
0-1 accidents = normal mood rules
2-3 accidents = dirty
4 accidents   = sad/upset
5-6 accidents = sick
```

Sick mood should also increase health drain.

## Poop / Pee Mechanics

Poop and pee were added as separate mechanics after the poop sound effect attracted child stakeholder interest.

Current intended behavior:

```text
poop/mess = larger cleanliness and health issue
pee       = faster cleanliness/happiness issue, slightly lighter than poop
```

Each accident causes immediate cleanliness and happiness loss.

A room with many accidents drains cleanliness/happiness faster.

At high total accidents, Bit becomes sad and then sick.

Current test intervals may be short; production intervals should be much longer.

Suggested production values:

```python
MESS_INTERVAL_SECONDS = 60 * 30
PEE_INTERVAL_SECONDS = 60 * 20
```

Suggested testing values:

```python
MESS_INTERVAL_SECONDS = 10
PEE_INTERVAL_SECONDS = 8
```

Important: accident timers only progress while Bit is awake.

## Sound System

Sound code is in:

```text
pet/sounds.py
```

Sounds are generated as simple retro `.wav` files using Python wave generation and pygame mixer.

Current sounds:

```text
feed
play
clean
sleep
wake
error
menu
select
poop
pee
medicine
treat
```

`update_pet()` now returns an event list, for example:

```python
["mess_created"]
["pee_created"]
```

`main.py` plays sounds based on those returned events.

Important defensive pattern in `main.py`:

```python
pet_events = update_pet(pet, dt) or []
```

This prevents crashes if `update_pet()` accidentally returns `None`.

## Sprites / Image Notes

Sprites were generated as pixel-art style images. Some generated images had fake checkerboard backgrounds or white backgrounds and needed cleanup.

There is a cleanup script:

```text
tools/remove_bg.py
```

The best cleanup strategy was border-connected background removal, not global “remove light pixels,” because Bit is mostly white and the naive cleanup ate his body.

Current sprite PNGs are loading successfully.

Future sprite work:

* Consider regenerating cleaner true transparent sprites
* Add 2-frame animations
* Add action sprites such as eating, cleaning, medicated, and playing
* Add evolution stage sprite sets

## UI Notes

Window size:

```python
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 280
FPS = 30
```

This matches the Whisplay HAT display scale target.

Current UI includes:

```text
Pet name
Mood/status label
Sprite
Poop/pee drawings
Stat bars
Dynamic menu
Mood/action message line
```

Known UI quirks:

* Menu gets tight when there are 5+ options.
* Dynamic menu works now, but extra options can crowd the bottom.
* If menu grows further, we may need a one-column scrolling menu or submenus.

## Hardware Direction

The project is intentionally split so that logic is independent from hardware.

Current input:

```text
io_layer/windows_io.py
```

Future input/output:

```text
io_layer/whisplay_io.py
```

Whisplay deployment plan:

* Keep `pet/` logic unchanged
* Replace Windows keyboard input with Whisplay buttons
* Replace pygame display if needed with direct display rendering
* Use Whisplay speaker/audio for generated sounds
* Add systemd autostart on Raspberry Pi

## Current Roadmap

Implemented:

```text
✅ Windows pygame prototype
✅ save/load
✅ offline progress
✅ menu system
✅ sleep/wake
✅ mood system
✅ mood sprites
✅ debug mood cycler
✅ generated sound effects
✅ poop/mess mechanic
✅ pee mechanic
✅ medicine
✅ energy treat
✅ event-based pet sounds
```

Next planned features:

```text
1. Random mood-specific idle messages
2. Better menu layout / possible scrolling menu
3. Mini-game
4. Evolution stages
5. Optional classic death / egg reset mode
6. Pi Zero / Whisplay HAT hardware port
```

Feature ideas to preserve:

```text
Random idle messages:
- Bit pings the void.
- Bit is vibing.
- Bit watches dust move.
- Bit inspected VLAN 10.
- Bit regrets licking the battery contacts.

Mini-game ideas:
- Catch the packet
- Timing/reaction game
- Memory blink game

Evolution ideas:
- Egg
- Blob
- Gremlin
- Cyber Rabbit
- Eldritch Admin
- Dust Bunny if neglected
- Packet Paladin if well cared for
```

## Current Balancing Philosophy

This should eventually be kid-friendly and forgiving by default.

Classic harsh Tamagotchi behavior can be added later as an optional mode.

Suggested modes later:

```text
Kid Mode:
- forgiving health recovery
- no permanent death
- recovery possible with care

Classic Mode:
- health can hit zero
- if health remains zero too long, Bit dies/resets to egg
```

Current recovery tuning should be forgiving enough that a sick Bit can recover once fed, cleaned, rested, and medicated.

## Common Debugging Notes

If imports or changes seem wrong:

1. Use Save All: `Ctrl + K`, then `S`
2. Delete cache if needed:

```powershell
Remove-Item -Recurse -Force .\pet\__pycache__
```

3. Confirm actual imported class/function:

```powershell
python -c "from pet.state import PetState; p=PetState(); print(p)"
```

4. Confirm pygame environment:

```powershell
python main.py
```

5. Confirm venv is active:

```text
(.venv) PS A:\Games\Projects\tamagotchi>
```

## Recent Known Good State

The project currently runs successfully after:

* medicine mechanic
* energy treat mechanic
* poop and pee mechanics
* mood consequences
* sound event system

A recent checkpoint/commit should be made after these changes.

Suggested commit:

```powershell
git add .
git commit -m "Add medicine, energy treat, and accident mechanics"
```
## Current Milestone: Baby Sprite Animation Pipeline

The baby pet sprite system now supports multi-frame mood animations using numbered PNG frames.

Active sprite path:

```text
assets/pets/baby/
```

Current naming convention:

```text
idle_0.png
idle_1.png
idle_2.png

happy_0.png
happy_1.png
happy_2.png

sad_0.png
sad_1.png
sad_2.png

sick_0.png
sick_1.png
sick_2.png

sleep_0.png
sleep_1.png
sleep_2.png

tired_0.png
tired_1.png
tired_2.png
```

The sprite loader automatically loads frames in sequence until a numbered frame is missing. For example, if `idle_0.png`, `idle_1.png`, and `idle_2.png` exist, idle will animate across all three frames.

## Animation System

`pet/animation.py` contains the animation player.

`pet/sprites.py` now loads sprites from:

```text
assets/pets/
```

and supports evolution-stage folders such as:

```text
assets/pets/baby/
assets/pets/child/
assets/pets/teen/
assets/pets/adult/normal/
assets/pets/adult/excellent/
assets/pets/adult/rough/
```

`main.py` now uses:

```python
choose_sprite_frames()
AnimationPlayer
```

instead of the older single-image `choose_sprite()` flow.

## Background Cleanup Tools

Generated sprites should preferably use a solid bright green chroma-key background.

Current cleanup strategy:

```text
remove_chroma_bg.py
```

This tool scans sprite PNGs under:

```text
assets/pets/
```

and removes green/magenta chroma-key backgrounds only when the chroma color touches the image border.

Older white/checkerboard cleanup is risky for Bit because Bit’s body is white. Avoid using white-background cleanup on current pet sprites unless absolutely necessary.

## Recent Asset Work

New 3-frame baby animation sets have been generated or are in progress for:

```text
idle
happy
sad
sick
sleep
tired
```

Dirty animation frames were also expanded using chroma-key backgrounds to show dirt spreading over time.

Next step is to save the generated images into the correct `assets/pets/baby/` filenames, run `remove_chroma_bg.py`, test in-game, then commit the milestone.

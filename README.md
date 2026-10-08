<a href="https://www.buymeacoffee.com/fulger" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 37px !important;width: 170px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

# Halo: Combat Evolved for Android

An Android-focused fork of [cybersecurity/halo-ce-universal](https://github.com/cybersecurity/halo-ce-universal),
with built-in multi-touch controls, direct swipe aiming, optional phone rumble
and gyroscope aiming, and a customizable, portable touch layout.
Repository: [theLlamaNet/halo-ce-android](https://github.com/theLlamaNet/halo-ce-android).

The game runs as an ARM64 app with OpenGL ES 3 and SDL3 audio. It requires
Android 9 (API 28) or later and a 64-bit ARM device. Game data is not included.

## Download and install

Get [the latest Android release](https://github.com/theLlamaNet/halo-ce-android/releases/latest)
or the APK archives from [GitHub Actions](https://github.com/theLlamaNet/halo-ce-android/actions).
Release builds are for playing; debug builds stop on failed game assertions
and are intended for troubleshooting. Release archives contain an APK and
third-party license notices. Install the APK on your device.

On the first launch, select an Xbox Halo: Combat Evolved disc image
(`.iso` or `.xiso`) that you own. The app extracts its `maps/` directory
(approximately 1.8 GB), then starts the game. Copy the image to your device
before opening the file picker. Saved games, maps, logs and `config.toml`
are under `/sdcard/Android/data/com.halo.decomp/files/`.

## Touch controls

You can play without a physical controller. Multiple fingers can hold
movement, aim and action controls at the same time.

| Control | Action |
| --- | --- |
| Left stick | Move |
| Swipe the display | Look, including while holding an action button |
| Fire (left and right) / Grenade | Fire weapon / throw grenade |
| A / Jump | Jump / accept in menus |
| B / Melee | Melee / back in menus |
| X / Reload | Reload / interact |
| Y / Weapon | Switch weapon |
| Crouch / Zoom | Crouch / zoom |
| Light / Gren. type | Flashlight / switch grenade type |
| D-pad | Navigate menus |
| Pause / Back | Controller Start / Back |
| Hide / Touch | Hide / show the gameplay overlay |

Touch controls merge with the first physical controller for player 1.
Bluetooth and USB controllers still work, including additional players.
Touch inputs are released when you hide the controls or leave the app.

### Porting options

The main menu and the game pause menu include **Porting options**, with
**Overlay settings**, **General** and **Cheats**. The main-menu entry replaces
Quit at its original position and size; the pause frame extends below its extra entry.

The overlay uses cyan Halo-style vector icons. **Camera mode** changes camera
mode with one tap and is editable from both menus. In flying mode, **Zoom**
toggles player/camera control; swipe and gyro aim rotate the camera while its
controls are active. Existing version 1–3 layouts migrate to version 4 while
preserving positions and copies.

**Overlay settings** lets you move, hide, add, duplicate and resize controls,
adjust swipe look sensitivity, or select **Disable all overlay**. That toggle
hides every Android overlay, including **Hide/Touch** and FPS. Direct menu
taps and physical controllers remain available; use Porting options to restore
the overlay. Opening the layout editor also restores it for editing.
**Reset all buttons** restores the supplied October 3 layout and sizes.
Existing saved layouts are retained until reset. **Export** and **Import** use
Android's document picker for `.halolayout` files.

**General** contains **Rumble**, **Gyroscope**, independent **Gyroscope
sensitivity**, **FPS counter** and **Field of view (FOV)**. FOV ranges from
55 to 90 degrees (70 by default, measured in the engine's 4:3 camera space);
the wider display expands horizontal view as usual, and weapon zoom is retained.
Rumble defaults on; gyro and FPS default off. Sensitivity sliders range from
0.25x to 4x; control sizes range from 50% to 200%.

**Cheats** in the main menu selects **Startup cheats**. All sixteen start off.
Selections are saved as executable commands in a marked section of
`init.txt` under `/sdcard/Android/data/com.halo.decomp/files/`; other file
contents are preserved. Flags apply when a player spawns at the start of each
map, and selected instant actions run once per map. Teleport waits for a valid
camera. These settings also survive app restarts. In the game pause menu,
Cheats retains its existing live toggles and repeatable instant actions and
never edits `init.txt`. Network clients retain the host's rules.

Version 3 layout exports include positions, visibility, copies, sizes, swipe
and gyro sensitivity, rumble, gyro, FPS, FOV and the global overlay toggle.
Older exports remain supported; missing FOV and overlay settings default to
70 degrees and enabled overlays. Startup cheats stay in `init.txt`, separate
from layout exports. Phone rumble, gyro and final GPU presentation require
verification on Android hardware.

## Build

Install Python, ninja, CMake, JDK 17+, the Android SDK (API 35) and NDK,
and a clang with the `arm64_32` target. The first build downloads musl,
SDL3, Gradle and the Android Gradle Plugin.

On Windows, install Git for Windows too: its Bash runs the native build
commands, and the Windows NDK compiler can build the guest and host.
Set `ANDROID_HOME` to the SDK folder. Linux can also be used as a build host.

```sh
python configure.py --release --pgo=off
ninja android_apk
```

The installable APK is at
`port/android/app/build/outputs/apk/debug/app-debug.apk`. This command uses
the Gradle debug package with a release-mode native engine. For a full
release package matching CI, run:

```sh
python tools/ci_build.py android release
```

Its APK and license notices are collected in `dist/halo-android-release/`.
`python configure.py` builds an engine with assertions; `ninja android`
builds only the native engine and libraries. `ninja` defaults to the APK.
The inherited optimization profile requires clang 22+; `--pgo=off` disables it.

Run the layout, file compatibility and gyroscope regression checks with:

```sh
python tools/test_touch_layout.py
python tools/test_porting_actions.py
python tools/test_menu_touch.py
python tools/test_porting_ui.py
python tools/test_startup_cheats_engine.py
```

## Android-only source layout

The standalone Windows and Linux ports, their build targets and CI jobs
have been removed. `port/shared/` contains the engine compatibility layer,
renderer, networking and game changes that Android needs. Some internal
identifiers retain their upstream `halo_linux` names for compatibility.
The `android_windows_*.py` helpers build Android on a Windows computer;
they do not build a Windows version of the game.

See [Android setup, settings and troubleshooting](port/android/README.md),
[shared engine settings](port/shared/README.md#settings) and
[netcode details](port/shared/NETCODE.md).

## Multiplayer and updates

The inherited system link networking supports LAN play and internet invite
links, and remains compatible with the upstream networking protocol.
Official fork builds check releases of **theLlamaNet/halo-ce-android**.
Local builds without a build number do not check for updates.

GitHub Actions builds Android debug and release packages and keeps the APK
artifacts for 14 days. Tags and GitHub releases are published manually.
Configure the repository's
`ANDROID_KEYSTORE_BASE64` and `ANDROID_KEYSTORE_PASSWORD` secrets to keep a
stable signing key across builds (key alias `halo`). Without them, each CI
runner uses its own debug key, so its APK may not install over an earlier
build. Keep signing keys and game data out of the repository.

## Automatic upstream synchronization

[Sync upstream](https://github.com/theLlamaNet/halo-ce-android/actions/workflows/sync-upstream.yml)
checks `cybersecurity/halo-ce-universal`'s `main` every 30 minutes and can also
be started with **Run workflow**. GitHub may delay scheduled runs. Each run
merges all new upstream commits into a temporary `codex/upstream-sync-*`
branch, preserving the Android changes and the original commit history.
The exact candidate must pass the sync regression tests, touch/gyro tests,
and Android debug and release builds before the bot advances this fork's
`main`. If `main` changes during validation, the next run starts from it.

The policy in [upstream-sync-policy.json](.github/upstream-sync-policy.json)
preserves this fork's workflows, README and sync helper, keeps removed
desktop ports out, and recognizes the `port/linux` to `port/shared` move.
Other code uses normal three-way merging. An unresolved source conflict or
failed build stops the update and leaves `main` unchanged. The Actions run
contains a JSON report; failed build candidates remain available for
inspection. Resolve source conflicts on the fork and run the workflow
again; incompatible source changes cannot safely be merged automatically.

Keep Actions enabled and allow the workflow token to write repository
contents. Branch protection must allow the bot's normal fast-forward push
to `main`; the workflow never force-pushes. No upstream tags are copied,
and neither workflow creates tags or releases.

For a manual release, download the chosen build's APK artifacts and use a
`build-<number>` tag on that exact commit. The number is the full-history
commit count (`git rev-list --count <commit>`), or the `build_number`
override supplied to **Android build / Run workflow**. Use a number greater
than previously published versions. To support the in-app updater, attach
`halo-android-debug.zip` and `halo-android-release.zip`, each containing its
APK and notices at the ZIP root. Create these ZIPs without compression
(stored entries) for compatibility with older updaters; mark the release
as latest. Downloaded Actions artifact ZIPs should be repackaged this way.

## Online multiplayer

Both players must use compatible builds. The host selects **Create Internet
Game**, finishes creating the lobby and shares its current `halo://join/` link.
The other player opens **Direct Link** or **Server Browser** and selects
**PASTE LINK**. Keep the host game open while the guest connects. The connection
status appears below the list; select the host's row once it is discovered.
Your own invitation is for the other player and cannot be used to join yourself.

Server Browser searches LAN games and games reached through invitations. There
is no global public server directory; an empty list without an invitation does
not mean an invite connection has failed.

Direct UDP remains the preferred transport. After a few seconds of failed
hole punching, `network.relay_fallback = true` (default) sends the already
ChaCha20-Poly1305 authenticated game packets through MQTT brokers, allowing
mobile/strict NAT connections without forwarding a port. Session topics use
separate keys for each direction, replay protection remains active, messages
are never retained and queues are bounded. The client keeps probing UDP and
switches to it when available. Set `network.relay_fallback = false` for UDP only.

The default `network.signalling_brokers` are anonymous public testing services,
without a game-service availability or latency guarantee. Sustained play should
use your own reachable MQTT 3.1.1 broker (`host:port`, anonymous TCP supported
by this client), configured identically on both devices. Networks must allow
its TCP port (default 1883). The fallback adds TCP latency and does not create
a public server listing.

Regression checks: `python tools/test_multiplayer.py` runs actual C tunnel,
cryptography, relay topic/queue/reconnection and browser-filter code in wasm.
A real two-device mobile-network gameplay check remains necessary.

## Known limitations

- Bink videos are skipped.
- The native engine requires fixed guest memory addresses below 4 GB.
- Devices using 16 KB kernel pages are currently unsupported.
- A full editor/gameplay test still requires an Android device.

## Credits and license

This fork builds on the Android port in
[cybersecurity/halo-ce-universal](https://github.com/cybersecurity/halo-ce-universal),
which starts from [bnunu/halo-1](https://github.com/bnunu/halo-1), a fork of
[punpckhdq/halo](https://github.com/punpckhdq/halo).
The decompilation is based on Xbox build 2342 (`cachebeta.exe`).
See [LICENSE.md](LICENSE.md) and the notices in `port/third_party/`.

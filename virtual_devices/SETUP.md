# Setting up the virtual camera + microphone

`pyvirtualcam` and `sounddevice` don't create virtual devices themselves -
they write into ones that already exist on the OS. Install the driver for
your platform once, then `pip install -r requirements.txt`.

```
pip install -r requirements.txt
```

## Virtual camera

| OS | Install | Notes |
|---|---|---|
| Windows | Install [OBS Studio](https://obsproject.com/) | Ships a virtual camera driver pyvirtualcam can use directly. Just installing OBS is enough - you don't need to open it. |
| macOS | Install [OBS Studio](https://obsproject.com/) | Same as Windows; OBS's virtual cam works on macOS 26.0+. |
| Linux | `sudo apt install v4l2loopback-dkms` then `sudo modprobe v4l2loopback video_nr=10 card_label="Cue Camera" exclusive_caps=1` | `exclusive_caps=1` is required for apps like Chrome/Meet to detect it as a real webcam. Add the modprobe line to `/etc/modules-load.d/` to persist across reboots. |

**Caveat:** on Windows/macOS, OBS only exposes *one* virtual camera instance. If you also want to run OBS itself at the same time, install [Unity Capture](https://github.com/schellingb/UnityCapture) instead and pass `backend="unitycapture"` to `VirtualCamera`.

## Virtual microphone

| OS | Install | Device name to use |
|---|---|---|
| Windows | Install [VB-CABLE](https://vb-audio.com/Cable/) | Python writes to **"CABLE Input"**; in Meet, pick **"CABLE Output"** as the microphone. |
| macOS | `brew install blackhole-2ch` | Python writes to **"BlackHole 2ch"**; in Meet, pick **"BlackHole 2ch"** as the microphone too (it's a single loopback pair, not two separate devices). |
| Linux | `pactl load-module module-null-sink sink_name=CueMic sink_properties=device.description="Cue_Microphone"` | Python writes to output **"CueMic"**; in Meet, pick the input named **"Monitor of Cue_Microphone"** (run `pactl list sources short` to confirm the exact name). |

If `find_device_index()` in `virtual_microphone.py` can't find your device, run:

```python
from virtual_microphone import list_devices
list_devices()
```

and copy the exact name (or a distinctive substring of it) into `device_name_hint`.

## Using them in Google Meet

1. Run `demo.py` (or your real Cue pipeline) so the virtual devices are actively receiving frames/audio.
2. In Google Meet, click the **Settings gear** → **Video** tab → set Camera to the OBS/v4l2loopback device.
3. Same menu → **Audio** tab → set Microphone to CABLE Output / BlackHole 2ch / Monitor of Cue_Microphone.
4. Meet now sees your processed video and generated audio exactly as if they came from a real webcam and mic.

## Common gotchas

- **Virtual cam shows a black/frozen frame in Meet:** the Python process must be actively calling `send_frame()` - the camera has no image until frames are pushed to it. Chrome also caches the last frame if your script crashes, so restart the script and toggle the camera off/on in Meet.
- **No sound reaches Meet:** double check you selected the *output*-side name in Python (`"CABLE Input"`) but the *input*-side name in Meet (`"CABLE Output"`) - these are two different device names for VB-CABLE specifically.
- **macOS mic permissions:** the first time, macOS will prompt to grant your terminal/Python Microphone access - this is separate from camera permissions.

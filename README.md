# 🧠 CS2 Internal Python Cheat Framework

An internal Counter-Strike 2 cheat written entirely in **Python**, powered by `python3xx.dll`.  
Handles memory, injection, and Python execution inside the CS2 process. Designed to be minimal, modular, and extendable.

> 🚨 No external shit, only internal!

> ⚠️⚠️ DirectX Hooking currently not working! If you know how to fix it, please contact me or open pull request! THANKS ⚠️⚠️

---

## ⚙️ Features

- ✅ Fully internal execution
- ✅ Code injection via Python
- ✅ no fucking ideas, lol

---

## 📁 Project Structure

```
cs2_py/
│
├── main.py              # Entry point: handles execution
├── cs2_loader.py        # Python code executed inside the target process
├── config.json          # Configuration for debug, target and python dll
├── python3x.dll         # Python runtime (needs to be added)
│
├── lib/                 # Core logic
│   ├── config.py        # Handles config loading and access
│   ├── debug.py         # Logging system (auto-respects debug mode)
│   ├── injector.py      # Injects Python-DLL into target process
│   ├── utility.py       # Memory read helpers, module base, export parsing
│   ├── winapi.py        # Win32 + memory functions (VirtualAllocEx, etc.)
│
└── cs2/                 # Future cheat logic
```

---

## 📦 Requirements

- Python 3.x.x installed (needs to be same as dll)
- Requirements installed (install via pip)
- Working `python3x.dll` next to the executable
- Run as Administrator (required for injection)

---

## 🧪 Usage

1. 🧬 **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. 🐍 **Get and copy your Python.dll:**
> if you're to dumb to do that dont waste my time
Go to you Python installation folder and copy out `python3xx.dll` as example for me `python311.dll`.
Paste it in the same folder as main or compiled exe!

3. 🔧 **Edit your config.json:**
```json
{
  "debug": false or true,
  "target_process": "cs2.exe",
  "dll_name": "python3x.dll"
}
```

4. 🚀 **Run the injector:**
```bash
python main.py
```
This will:
- Inject `python3x.dll` into `cs2.exe`
- Execute `cs2_loader.py` inside the target (internal)

---

## 💬 Planned Features

- [ ] Internal DirectX11 hook for true menu/drawing

---

## ⚠ Disclaimer

This software is for educational and research purposes only.  
You are fully responsible for how you use this code.

> 🚫 **Do not use on VAC-secured servers unless you know the risks.**

---

## 🧠 Credits

- Inspired by [GuidedHacking](https://guidedhacking.com/threads/python-game-hacking-tutorial-1-6-first-internal.19100/)  
- Community contributions from UC forums  
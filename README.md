# 🖱️ MacClicker: The Ultimate macOS Auto Clicker

![Platform](https://img.shields.io/badge/Platform-macOS-000000?style=for-the-badge&logo=apple)
![Language](https://img.shields.io/badge/Language-Python_3-3776AB?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**MacClicker** is a high-precision, "Tahoe-style" auto clicker designed specifically for macOS. It features a frameless "Liquid Glass" HUD, high-accuracy timing for up to 100 CPS, and advanced safety features like the "Slide-to-Arm" switch.

---

## ✨ Key Features

* **🚀 High-Speed Engine:** Capable of **100 Clicks Per Second (CPS)** using high-precision `perf_counter` timing.
* **🛡️ Safety Field Technology:** The script intelligently detects the dashboard's position in real-time. It **physically refuses to click** if the mouse is hovering over or near the control panel.
* **💎 Tahoe Liquid HUD:** A beautiful, semi-transparent, frameless interface that blends perfectly with macOS.
* **✋ Hover-to-Pause:** Simply move your mouse over the dashboard to instantly pause clicking.
* **🔒 Slide-to-Arm:** Features a Master Safety Slider. The clicker is physically disconnected until you slide the switch to **ARMED**.
* **⚡️ Auto-Installer:** No need to manually install libraries. The script detects missing dependencies and installs them automatically.

---

## 🛠️ Installation & Usage

You don't need to be a coder to use this. Open your **Terminal** (Command + Space, type "Terminal") and follow these steps.

### 1️⃣ First Time Setup (Install & Run)
Copy and paste this entire command to download, install, and start the app instantly:

```bash
git clone [https://github.com/Kvc899/MacClicker.git](https://github.com/Kvc899/MacClicker.git) && cd MacClicker && python3 clicker.py

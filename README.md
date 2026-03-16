# Eye Help Health 👁️

A lightweight Linux desktop tool that reminds you to **blink and relax your eyes** while working on a computer.

The program periodically **fades the entire screen to black for about one second** every **60–80 seconds**, encouraging you to blink and rest your eyes. This helps reduce **digital eye strain, dryness, and fatigue** caused by long screen usage.

---

# Features

* ⏱️ Automatic reminder every **60–80 seconds**
* 🌑 Smooth **full-screen fade to black**
* 👁️ Encourages blinking and eye relaxation
* 🔔 Desktop **notification alerts**
* 🖥️ **System tray icon** with controls
* ⏯️ Pause / Resume reminders
* ⚙️ Adjustable reminder intervals
* 📏 Optional **20-20-20 eye rule**
* 🚀 **Auto-start on login**

---

# How It Works

1. The application runs in the background.
2. After **60–80 seconds**, the screen gradually fades to black.
3. The screen stays dark for about **1 second**.
4. The screen fades back to normal.
5. A notification reminds the user to blink and relax their eyes.

This small pause helps restore natural blinking and reduce eye strain.

---

# Requirements

### Python

Python **3.8+** recommended.

Check your version:

```
python3 --version
```

---

# System Dependencies

Install required Linux packages:

```
sudo apt install libnotify-bin python3-tk
```

These provide:

* **notify-send** for desktop notifications
* **Tkinter GUI** for screen overlay

---

# Python Dependencies

Install required Python libraries:

```
pip install pystray pillow
```

These are used for:

* **System tray icon**
* **Tray menu controls**

---

# Project Structure

```
eye-help-health/
│
├── blink_reminder.py
├── README.md
└── venv/
```

---

# Running the Program

Navigate to the project folder:

```
cd eye-help-health
```

Run the program:

```
python3 blink_reminder.py
```

The application will start running in the background.

You will see:

* a **tray icon**
* notifications
* screen fade reminders

---

# Run in Background

Run the application in background:

```
python3 blink_reminder.py &
```

Check if it is running:

```
ps aux | grep blink_reminder
```

Stop it:

```
pkill -f blink_reminder.py
```

---

# Auto Start on Login

Install autostart:

```
python3 blink_reminder.py --install
```

This creates:

```
~/.config/autostart/blink_reminder.desktop
```

The application will automatically start when you log into Ubuntu.

---

# Remove Auto Start

Disable autostart:

```
python3 blink_reminder.py --remove
```

---

# Tray Icon Controls

Right-click the tray icon to access options:

* Pause reminder
* Resume reminder
* Blink immediately
* Change reminder interval
* Enable **20-20-20 rule**
* Quit application

---

# 20-20-20 Eye Rule

Optional eye health feature.

Every **20 minutes**:

* Look at something **20 feet away**
* For **20 seconds**

This reduces eye strain from prolonged screen focus.

---

# Keyboard Shortcuts

While the application is running:

```
ESC      Quit program
Ctrl+C   Quit program
```

---

# Health Benefits

This tool helps prevent:

* Dry eyes
* Eye fatigue
* Reduced blinking
* Digital eye strain
* Headaches from screen overuse

Short micro-breaks help keep your eyes **lubricated and relaxed**.

---

# License

MIT License

---

# Author

Rachappa Biradar

Project: **Eye Help Health**

A small open-source tool to improve **eye health during computer usage**.




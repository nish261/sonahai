# Foqos for Android 🎯

**The ultimate focus app for Android - Block apps, websites, and distractions with physical unlock methods.**

<div align="center">

![Foqos Logo](https://via.placeholder.com/120x120?text=F)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Android](https://img.shields.io/badge/Platform-Android-green.svg)](https://www.android.com/)
[![Kotlin](https://img.shields.io/badge/Language-Kotlin-purple.svg)](https://kotlinlang.org/)

</div>

---

## 📖 Table of Contents

- [Features](#-features)
- [Screenshots](#-screenshots)
- [Download](#-download)
- [How It Works](#-how-it-works)
- [Blocking Strategies](#-blocking-strategies)
- [Architecture](#-architecture)
- [Setup & Installation](#-setup--installation)
- [Building from Source](#-building-from-source)
- [Permissions](#-permissions)
- [Tech Stack](#-tech-stack)
- [License](#-license)

---

## ✨ Features

### 🚫 Advanced Blocking
- **App Blocking** - Block any installed app using Accessibility Service
- **Website Blocking** - Filter websites system-wide with local VPN (no data leaves your device)
- **Smart Detection** - Automatically blocks app switches during focus sessions

### 🔓 Physical Unlock Methods
Choose how strict your focus sessions should be:

- **NFC Tag** - Tap a physical NFC tag to end sessions
- **QR Code** - Scan a specific QR code to unlock
- **Manual** - End sessions anytime (flexible mode)
- **Timer-Based** - Automatic sessions based on duration

**Hybrid Strategies:**
- NFC + QR Code
- NFC + Timer
- QR Code + Timer

### 📊 Insights & Analytics
- **Session History** - Track all your focus sessions
- **Streak Tracking** - Build consistency with daily streaks
- **Statistics** - Total time, average duration, longest session
- **Visual Charts** - See your progress over time

### ⏸️ Break System
- **Scheduled Breaks** - Take timed breaks during long sessions
- **Configurable Duration** - 5, 10, 15, or 20-minute breaks
- **Auto-Resume** - Blocking automatically resumes after break ends

### 🎨 Premium UI
- **Material Design 3** - Modern, beautiful interface
- **Dark Mode** - Full dark theme support
- **Smooth Animations** - Delightful user experience
- **Live Timers** - Real-time session duration tracking

### 🔔 Smart Notifications
- **Session Start/End** - Get notified when sessions begin and complete
- **Persistent Notifications** - Always see your active session
- **Quick Actions** - Stop sessions or take breaks from notifications
- **Reminder System** - Optional reminders during focus time

### 🏠 Widgets & Shortcuts
- **Active Session Widget** - See your current session on home screen
- **Quick Start Widget** - Start profiles with one tap
- **Deep Linking** - Share profile links via NFC/QR codes
- **App Shortcuts** - Fast access to common actions

---

## 📱 Screenshots

> Coming soon - Screenshots of the app in action

---

## ⬇️ Download

### Latest Release
Download the latest APK from the [Releases page](https://github.com/nish261/sonahai/releases).

**Direct APK download - no extraction needed!**

### Automatic Builds (Advanced)
Every commit triggers an automatic build. To download:

1. Go to [Actions](https://github.com/nish261/sonahai/actions)
2. Click latest successful workflow
3. Download artifact (it's a ZIP file)
4. **Extract the ZIP** to get the APK
5. Install the APK

> **Important:** GitHub Actions wraps all artifacts in ZIP files. You must extract it first!
- Android 8.0 (Oreo) or higher
- ~15 MB storage space
- NFC hardware (optional, for NFC unlock)
- Camera (optional, for QR code scanning)

---

## 🔧 How It Works

### App Blocking
Foqos uses Android's **AccessibilityService** to monitor which apps you open. When you start a focus session, the service watches for blocked apps and immediately sends you back to the home screen if you try to open them.

**Why AccessibilityService?**
- No root required
- Works across all apps
- System-level monitoring
- Doesn't drain battery

### Website Blocking
Foqos creates a **local VPN connection** to filter web traffic. When you visit a blocked domain, the request is dropped before it reaches the internet.

**Why VPN?**
- Android doesn't have built-in content blocking APIs (unlike iOS)
- Works across all browsers and apps
- Local VPN = your data never leaves your device
- Industry standard used by all focus apps on Android

**Important:** The VPN is 100% local - no data is sent to external servers!

### Physical Unlock
When you create a profile, you can:
1. **Write to NFC Tag** - Store a unique profile link on an NFC sticker
2. **Generate QR Code** - Create a printable QR code
3. **Place Strategically** - Put tags/codes in inconvenient locations (drawer, another room)

To end your session, you must physically go to the tag/code - introducing "friction" that helps you think twice before breaking focus.

---

## 🛡️ Blocking Strategies

### 1. **NFC Blocking** 🏷️
- Most secure option
- Requires physical NFC tag
- Can't be bypassed without the tag

**Use case:** Place NFC tag in another room or give it to someone else

### 2. **QR Blocking** 📷
- Print QR code and place it somewhere inconvenient
- Requires camera permission
- Harder to bypass than manual

**Use case:** Stick QR code inside a book or drawer

### 3. **Manual Blocking** ✋
- Most flexible
- End session anytime with a button
- Good for building the habit

**Use case:** Starting out, or flexible work sessions

### 4. **Timer Blocking** ⏰
- Session ends automatically after set duration
- No manual intervention needed
- Great for Pomodoro-style work

**Use case:** 25-minute work sprints, study sessions

### Hybrid Strategies

#### **NFC + QR Code** 🏷️📷
- Unlock with either method
- Maximum flexibility with physical friction

#### **NFC + Timer** 🏷️⏰
- Session auto-ends after timer OR when you tap NFC tag
- Early exit requires the tag

#### **QR + Timer** 📷⏰
- Session auto-ends after timer OR when you scan QR code
- Early exit requires the code

---

## 🏗️ Architecture

Foqos is built with **Clean Architecture** principles using modern Android development practices:

```
app/
├── data/              # Data layer
│   ├── local/         # Room database, DAOs, entities
│   └── repository/    # Repository implementations
├── domain/            # Business logic
│   ├── model/         # Domain models (BlockingStrategy)
│   └── usecase/       # Use cases (SessionManager)
├── presentation/      # UI layer
│   ├── home/          # Home screen + ViewModel
│   ├── insights/      # Statistics screen
│   ├── profile/       # Profile editing
│   ├── settings/      # Settings screen
│   ├── components/    # Reusable UI components
│   └── theme/         # Material Design 3 theme
├── service/           # Background services
│   ├── AppBlockerAccessibilityService.kt
│   ├── BlockingForegroundService.kt
│   └── WebsiteBlockerVpnService.kt
├── util/              # Utilities
│   ├── NFCReader/Writer
│   ├── QRScanner/Generator
│   └── PermissionHelper
└── di/                # Dependency injection (Hilt)
```

### Tech Highlights
- **MVVM Pattern** - Clean separation of concerns
- **Jetpack Compose** - Modern declarative UI
- **Room Database** - Local data persistence
- **Kotlin Coroutines & Flow** - Reactive programming
- **Dagger Hilt** - Dependency injection
- **Material Design 3** - Latest design system

---

## 🚀 Setup & Installation

### From APK
1. Download the latest APK from [Releases](https://github.com/nish261/sonahai/releases)
2. Enable "Install from Unknown Sources" in Android settings
3. Install the APK
4. Grant required permissions when prompted

### Required Permissions
After installation, you'll need to manually enable:

#### 1. **Accessibility Service** (Critical)
   - Settings → Accessibility → Foqos → Enable
   - Required for app blocking

#### 2. **Usage Access** (Critical)
   - Settings → Apps → Special Access → Usage Access → Foqos
   - Required to detect foreground apps

#### 3. **VPN Permission** (For Website Blocking)
   - Prompted when you start a session with websites
   - Required for website filtering

#### 4. **Overlay Permission** (Optional)
   - For showing blocking overlay screens
   - Settings → Apps → Special Access → Display over other apps

---

## 🛠️ Building from Source

### Prerequisites
- **Android Studio** Hedgehog or newer
- **JDK 17** or higher
- **Android SDK 34** (Android 14)
- **Gradle 8.x**

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/nish261/sonahai.git
   cd sonahai
   ```

2. **Open in Android Studio**
   - File → Open → Select the project directory
   - Wait for Gradle sync to complete

3. **Build the project**
   ```bash
   ./gradlew assembleRelease
   ```

4. **Find the APK**
   ```
   app/build/outputs/apk/release/app-release.apk
   ```

### Debug Build
```bash
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

---

## 🔐 Permissions

Foqos requires several permissions to function:

| Permission | Usage | Required? |
|------------|-------|-----------|
| **Accessibility** | Monitor app launches for blocking | ✅ Yes |
| **Usage Stats** | Detect foreground apps | ✅ Yes |
| **VPN** | Block websites | Only for website blocking |
| **NFC** | Read/write NFC tags | Only for NFC unlock |
| **Camera** | Scan QR codes | Only for QR unlock |
| **Overlay** | Show blocking screens | Optional |
| **Notifications** | Session alerts | Optional but recommended |

**Privacy:** All data stays on your device. Foqos has no analytics, no ads, and no network requests.

---

## 🎯 Tech Stack

### Core
- **Kotlin** - 100% Kotlin codebase
- **Jetpack Compose** - Modern UI toolkit
- **Material Design 3** - Latest design guidelines

### Architecture & Data
- **Room** - Local database for profiles and sessions
- **Dagger Hilt** - Dependency injection
- **Kotlin Coroutines** - Asynchronous programming
- **StateFlow** - Reactive state management

### Android Frameworks
- **AccessibilityService** - App monitoring
- **VPNService** - Website filtering
- **ForegroundService** - Persistent sessions
- **WorkManager** - Scheduled tasks
- **Glance** - App widgets
- **ML Kit** - QR code scanning
- **ZXing** - QR code generation

### Libraries
- **Accompanist** - Compose utilities
- **Coil** - Image loading
- **Kotlinx Serialization** - JSON handling

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

## 📄 License

```
MIT License

Copyright (c) 2026 Nishchal Asri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contact

Created by **Nishchal Asri**

- GitHub: [@nish261](https://github.com/nish261)

---

<div align="center">

**Built with ❤️ using Kotlin & Jetpack Compose**

⭐ Star this repo if you find it useful!

</div>

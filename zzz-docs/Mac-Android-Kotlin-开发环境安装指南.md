# Mac 上 Android / Kotlin 开发环境安装指南（含 VS Code）

## Metadata（元数据）

| 字段 | 内容 |
|------|------|
| 创建时间（Created At） | 2026-08-07 16:48:31 CST |
| 更新时间（Updated At） | 2026-08-07 17:05:00 CST |
| 作者（Author） | Grok |
| 目的（Purpose） | 指导在 macOS 上安装 Android / Kotlin 开发所需环境，以及 VS Code 扩展，便于开发本仓库 `android/` 工程与 mission `bilibili-fanqie-mobile-plugin` |
| 关联仓库或项目（Related Repository / Project） | mine-interest-bilibili-fanqie |
| 关联 mission（Related Mission） | bilibili-fanqie-mobile-plugin（可选关联；本文独立可复用） |
| 当前状态（Status） | 说明文档（Guide） |
| 文档边界（Scope / Boundary） | 安装与自检说明；**不是**产品实现 Plan；**不**替代 Android 官方文档全文 |
| 相对路径 | `zzz-docs/Mac-Android-Kotlin-开发环境安装指南.md` |
| 适用系统 | macOS（Apple Silicon / Intel 通用写法，差异处会注明） |
| 目标编辑器 | VS Code 为主；Android Studio 用于 SDK 配套（可不日常使用） |
| 推荐验收方式 | **真机安装 APK 手工测试**；模拟器可选，非必须 |

---

## 1. 你要装成什么样

本仓库计划中的 App 是 **Kotlin + Android**，不是纯 JVM 命令行程序。

| 组件 | 是否必须 | 作用 |
|------|----------|------|
| Xcode **Command Line Tools** | 建议有（完整 Xcode App **不必**） | Mac 基础工具链；`xcode-select --install` 已提示 installed 即可 |
| JDK 17 | **必须** | 编译 Kotlin / 跑 Gradle |
| Android SDK + Build-Tools | **必须** | 才能打出 APK |
| `adb`（Platform-Tools） | 建议有 | 可选：一键安装 APK、看 logcat；也可用隔空投送拷贝 APK |
| Android Studio | **强烈建议**（装 SDK 最省事） | 拿到 SDK；**不**等于必须用模拟器，也**不**等于必须天天开 Studio |
| Android Emulator（模拟器） | **可选，可不装** | 本指南默认走「真机 APK 手工验收」 |
| VS Code + 扩展 | 可选但本文覆盖 | 日常改代码 |
| 安卓真机 | **推荐作为唯一测试设备** | 安装 APK 后手动点选用 |

### 1.1 本仓库推荐工作流（真机 APK，可不装模拟器）

```text
Mac 写代码（VS Code / 任意编辑器）
    → JDK + Android SDK 构建
    → ./gradlew :app:assembleDebug 得到 APK
    → 传到手机（隔空投送 / 数据线 adb / 网盘）
    → 手机允许「安装未知应用」并安装
    → 自己手动测分享、下载、保存路径
```

**不强制：**

- 安装或启动 Android Emulator  
- 用 Android Studio 点绿色 Run  
- 数据线常插着（无 adb 也能拷 APK）

**仍然需要：**

- 本机能 **编出 APK**（JDK + Android SDK + Gradle）  
- 一部可安装第三方 APK 的安卓手机  

### 1.2 和「完整 Xcode」的区别

| 名称 | 要不要 |
|------|--------|
| **完整 Xcode**（App Store 大 IDE） | 做当前 Android 项目 **不需要** |
| **Xcode Command Line Tools** | 建议有；若提示 already installed 则跳过 |

### 1.3 组件角色一句话

```text
Android Studio  →  主要用来装/更新 SDK（可装完很少打开）
VS Code         →  日常写 Kotlin
终端            →  ./gradlew assembleDebug 打 APK
安卓手机        →  安装 APK 后手工验收（主测试场）
模拟器          →  可选，本指南默认跳过
```

---

## 2. 安装前检查

打开「终端（Terminal）」执行：

```bash
sw_vers
uname -m
```

- `arm64`：Apple Silicon（M 系列）
- `x86_64`：Intel Mac

磁盘建议至少预留 **15GB+**（Studio + SDK + 模拟器镜像会较大）。

---

## 3. 安装 Xcode Command Line Tools（不是完整 Xcode）

```bash
xcode-select --install
```

- 若弹出安装窗口：点安装，完成后检查下方命令。  
- 若提示类似 `Command line tools are already installed`：**已满足，直接跳过**，无需安装完整 Xcode。

检查：

```bash
xcode-select -p
# 常见输出：/Library/Developer/CommandLineTools
```

可选更新（非必须）：

```bash
softwareupdate --list
# 或：系统设置 → 软件更新
```

---

## 4. 安装 JDK 17

### 4.1 推荐：Homebrew + Temurin 17

若尚未安装 Homebrew：

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Apple Silicon 安装后，按提示把 `brew` 加入 PATH（常见为）：

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

安装 JDK：

```bash
brew install --cask temurin@17
```

### 4.2 验证

```bash
java -version
javac -version
/usr/libexec/java_home -V
```

期望：`java -version` 显示 **17** 相关版本。

若系统仍指向旧 JDK，可在 `~/.zshrc` 中固定：

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export PATH="$JAVA_HOME/bin:$PATH"
```

然后：

```bash
source ~/.zshrc
java -version
```

### 4.3 备选

- 不装 Homebrew：从 [Adoptium Temurin](https://adoptium.net/) 下载 macOS JDK 17 安装包。
- 也可仅使用 Android Studio 自带的 **JBR（JetBrains Runtime）**，但命令行 `java` 仍建议单独装好 JDK 17，避免终端构建找不到 Java。

---

## 5. 安装 Android Studio 与 Android SDK

### 5.1 安装 Android Studio

任选其一：

**A. Homebrew**

```bash
brew install --cask android-studio
```

**B. 官网**

- 打开：https://developer.android.com/studio  
- 下载 macOS 版并拖到「应用程序」

### 5.2 首次启动向导

1. 打开 **Android Studio**
2. 选择 **Standard（标准）** 安装（推荐）
3. 等待下载：
   - Android SDK
   - SDK Platform
   - Build-Tools
   - **模拟器相关组件可以不勾选 / 稍后不装**（走真机 APK 验收时不需要）

### 5.3 用 SDK Manager 补齐组件

菜单路径（文案可能随版本微调）：

```text
Android Studio → Settings（或 Preferences）
  → Languages & Frameworks
  → Android SDK
```

在 **SDK Platforms** 至少勾选：

- Android 14.0（API 34）或更新（如 API 35）——与工程 `compileSdk`/`targetSdk` 对齐即可

在 **SDK Tools** 至少勾选：

- Android SDK Build-Tools
- Android SDK Platform-Tools（含 `adb`）
- Android SDK Command-line Tools
- **Android Emulator：可不勾选**（本指南推荐真机测 APK）
- （可选）Google Play services 等

记下页面顶部的 **Android SDK Location**，常见路径：

```text
/Users/<你的用户名>/Library/Android/sdk
```

### 5.4 配置环境变量

编辑 `~/.zshrc`（若用 zsh，默认即是）：

```bash
# Android SDK
export ANDROID_HOME="$HOME/Library/Android/sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$PATH:$ANDROID_HOME/platform-tools"
# 未装模拟器时可去掉下一行
export PATH="$PATH:$ANDROID_HOME/emulator"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin"
```

若 SDK 不在默认路径，把 `ANDROID_HOME` 改成 SDK Manager 里显示的路径。

生效：

```bash
source ~/.zshrc
```

验证：

```bash
echo $ANDROID_HOME
adb version
sdkmanager --version   # 若 cmdline-tools 路径正确
```

`adb version` 能输出版本号即平台工具可用。

---

## 6. 测试设备：默认真机（模拟器可选）

### 6.0 推荐策略

| 策略 | 说明 |
|------|------|
| **默认推荐** | **只使用安卓真机** + 安装 debug APK 手工点测 |
| 模拟器 | 体积大、占磁盘；无真机时再装 |
| USB 调试 | 用 `adb install` 时方便；纯隔空投送装包 **可不开发者选项** |

### 6.1 真机安装 APK（主路径，可不插数据线）

1. 在 Mac 上打出 APK（见第 8 节）  
2. 把 `app-debug.apk` 传到手机，例如：  
   - 隔空投送（AirDrop）  
   - 微信/QQ 传文件给自己  
   - U 盘、网盘、局域网共享  
3. 手机用「文件」或浏览器打开该 APK  
4. 若系统拦截：设置 → 对应应用 → 允许 **安装未知应用**  
5. 安装完成后从桌面打开，按清单手工测（见 8.3）

**说明：** 这种方式 **不需要** 模拟器，也 **不强制** `adb devices` 必须有设备。

### 6.2 真机 + USB / adb（可选，装包更快）

1. 手机：设置 → 关于手机 → 连续点「版本号」打开开发者选项  
2. 打开 **USB 调试**  
3. 数据线连接 Mac，手机点「允许调试」  
4. 终端：

```bash
adb devices
```

应看到 `device` 状态（不是 `unauthorized`）。

若 `unauthorized`：拔线重插，手机点允许，或：

```bash
adb kill-server && adb start-server
adb devices
```

然后：

```bash
adb install -r path/to/app-debug.apk
```

### 6.3 模拟器（Emulator，可选，默认可跳过）

仅在没有真机、或需要自动化截图时再装：

1. SDK Manager → SDK Tools → 勾选 **Android Emulator**  
2. Android Studio → **Device Manager** → Create Device  
3. 下载 **system image**（Apple Silicon 选 **arm64**）  
4. 启动后 `adb devices` 应能看到模拟器  

命令行：

```bash
emulator -list-avds
adb devices
```

---

## 7. VS Code 安装与推荐扩展（插件）

### 7.1 安装 VS Code

```bash
brew install --cask visual-studio-code
```

或官网：https://code.visualstudio.com/

安装命令行拉起（可选，VS Code 内）：

```text
Command Palette → Shell Command: Install 'code' command in PATH
```

之后可用：

```bash
code /path/to/repo
```

### 7.2 推荐扩展（Extensions）

在扩展市场搜索安装（名称以市场显示为准）：

| 扩展建议名 | 用途 | 优先级 |
|------------|------|--------|
| **Kotlin**（常见发布者：fwcd） | Kotlin 语法高亮、基础语言服务 | 必须 |
| **Extension Pack for Java**（Microsoft） | Java/Kotlin 相关语言支持、调试基建常依赖 | 强烈建议 |
| **Gradle for Java**（Microsoft） | Gradle 任务视图、构建辅助 | 建议 |
| **Android** 相关社区扩展（可选） | 部分提供 logcat/补全，质量参差 | 可选 |
| **EditorConfig**（若项目使用） | 统一缩进 | 可选 |
| **GitLens** 或自带 Git | 看 diff | 可选 |
| **Error Lens** | 行内显示诊断 | 可选 |
| **YAML** | 读 `.devflow` / CI 配置 | 可选 |

说明：

1. **VS Code 不能完整替代 Android Studio** 的 Layout 预览、Profiler、一键 Device Manager。  
2. 扩展只解决「写代码舒服」；**编译安装仍靠 JDK + SDK + Gradle**。  
3. 若 Kotlin 扩展报错找不到 JDK：在 VS Code 设置中指定 `java.configuration.runtimes` 或 `java.jdt.ls.java.home` 指向 JDK 17。

### 7.3 VS Code 建议设置（可选）

用户 `settings.json` 片段示例：

```json
{
  "java.configuration.runtimes": [
    {
      "name": "JavaSE-17",
      "path": "/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home",
      "default": true
    }
  ],
  "java.import.gradle.enabled": true,
  "files.exclude": {
    "**/.gradle": true,
    "**/build": true
  },
  "search.exclude": {
    "**/.gradle": true,
    "**/build": true,
    "**/node_modules": true
  }
}
```

`path` 请用本机实际路径：

```bash
/usr/libexec/java_home -v 17
```

把输出路径填进去即可。

### 7.4 用 VS Code 打开本仓库

工程规划中的 Android 根目录为仓库下的 `android/`（按 mission Plan；若尚未创建则先打开整个仓库即可）。

```bash
# 在仓库根目录
code .
# 或仅 Android 工程
code android
```

首次打开 Java/Kotlin 工程时，右下角可能提示导入 Gradle，选允许并等待索引完成。

---

## 8. 打 APK + 真机手工验收（推荐主流程）

本仓库在 Apply 阶段会在 `android/` 生成 Gradle Wrapper（`gradlew`）。  
**环境装好但工程尚未创建时**，下面构建命令会失败，属正常；以 `java -version` / `adb version`（若已配）通过为准。

### 8.1 打包 debug APK

工程存在后，在 Mac 终端：

```bash
cd android
chmod +x gradlew   # 仅需一次
./gradlew :app:assembleDebug
```

期望：`BUILD SUCCESSFUL`。

产物路径（常见）：

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

### 8.2 装到手机（三选一）

**方式 A — 隔空投送 / 文件传输（可不装模拟器、可不插线）**

1. 把 `app-debug.apk` 发到手机  
2. 手机打开文件 → 安装  
3. 允许未知来源  

**方式 B — adb（手机已 USB 调试）**

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

或：

```bash
./gradlew :app:installDebug
```

**方式 C — 网盘 / 局域网**

上传 APK → 手机下载 → 安装（注意各 App「安装未知应用」权限）。

### 8.3 手工验收清单（个人自测）

安装后在真机上按需求点测（对应 mission Align 成功标准，可裁剪）：

| 编号 | 操作 | 期望 |
|------|------|------|
| T1 | 从 B站/番茄 App **分享** 文本到本应用 | 能打开本应用并带入链接 |
| T2 | 复制链接后 **打开本应用** | 可选：提示检测到剪贴板链接 |
| T3 | **手动粘贴** 链接并解析 | 识别 B站或番茄 |
| T4 | B站任务：选 mp3/mp4、目录后开始 | 目标文件夹出现文件或明确失败原因 |
| T5 | 番茄任务：开始下载 | 目标位置出现 TXT 或明确失败原因（如未配置正文端点） |
| T6 | 任务列表 | 能看到进行中 / 成功 / 失败 |

失败时优先看 App 内错误文案；若插着 USB，可辅助：

```bash
adb logcat | grep -i mineinterest
# 包名 / 过滤关键字以实际 applicationId 为准
```

### 8.4 本流程的局限（可接受）

1. 改代码后需重新 `assembleDebug` 再安装，比 IDE 一键 Run 慢半拍  
2. 无 USB 时排查崩溃主要靠界面提示，建议实现期把错误 `message` 显示在任务列表  
3. debug 包仅供自己用；长期分发再考虑 release 签名（非本指南范围）

---

## 9. 一键自检清单（装完请逐项打勾）

在终端执行并确认输出正常：

```bash
# 1) 系统与工具链
xcode-select -p

# 2) Java 17
java -version
javac -version

# 3) Android SDK
echo "$ANDROID_HOME"
ls "$ANDROID_HOME/platform-tools/adb"
adb version

# 4) adb 命令存在即可（真机可不连接）
adb version

# 5) VS Code
code -v
```

| 检查项 | 通过标准 |
|--------|----------|
| `java -version` | 17.x |
| `ANDROID_HOME` | 非空，且目录存在 |
| `adb version` | 有版本号（方便以后 install；隔空投送装包时可不连设备） |
| `adb devices` | **可选**；用 adb 安装时才需要看到 `device` |
| 模拟器 | **可选**；默认可不装、不检查 |
| VS Code Kotlin 扩展 | 打开 `.kt` 有高亮 |
| （工程就绪后）`./gradlew :app:assembleDebug` | 得到 `app-debug.apk` |
| 真机 | 能安装该 APK 并完成第 8.3 节手工项 |

---

## 10. 常见问题（Troubleshooting）

### 10.1 `adb: command not found`

- 未配置 `PATH` 或 `ANDROID_HOME` 错误  
- 重新检查第 5.4 节，并 `source ~/.zshrc`  
- 或直接调用：
  ```bash
  "$HOME/Library/Android/sdk/platform-tools/adb" version
  ```

### 10.2 `JAVA_HOME is not set` / Gradle 报 Java 版本不对

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
java -version
```

确认 Android Studio 的 Gradle JDK 也选 17：

```text
Settings → Build, Execution, Deployment → Build Tools → Gradle → Gradle JDK
```

### 10.3 Apple Silicon 模拟器很慢或无法启动

- 系统镜像选 **ARM 64** 而非过时的 x86 镜像  
- 在 Device Manager 删除错误镜像重建  

### 10.4 VS Code 没有智能提示 / 报错一片红

1. 安装 **Extension Pack for Java** + **Kotlin**  
2. 配置 `java.configuration.runtimes` 指向 JDK 17  
3. 命令面板：`Java: Clean Java Language Server Workspace` 后重载  
4. 确认打开的是含 `settings.gradle.kts` 的工程根（`android/`）

### 10.5 `sdkmanager: command not found`

SDK Command-line Tools 未装或路径不是 `cmdline-tools/latest/bin`。  
在 SDK Manager → SDK Tools 勾选 **Android SDK Command-line Tools**，安装后检查：

```bash
ls "$ANDROID_HOME/cmdline-tools"
```

### 10.6 Homebrew 很慢或失败

- 检查网络 / 代理  
- 改用官网 dmg 安装 Android Studio 与 Temurin  
- 不必强依赖 Homebrew，只是省事  

### 10.7 权限与隐私

首次 `adb` 连接真机需在手机点允许；  
macOS 若拦截 adb，到「系统设置 → 隐私与安全性」允许开发者工具。

---

## 11. 与本仓库 mission 的关系

| 文档 | 路径 |
|------|------|
| 本安装指南 | `zzz-docs/Mac-Android-Kotlin-开发环境安装指南.md` |
| Align | `.devflow/bilibili-fanqie-mobile-plugin/plans/2026-08-07-bilibili-fanqie-mobile-align.md` |
| Plan | `.devflow/bilibili-fanqie-mobile-plugin/plans/2026-08-07-bilibili-fanqie-mobile-plan.md` |
| 产品工程目录（计划） | `android/` |
| 开发分支 | `rin-bilibili-fanqie-mobile/dev` |

环境就绪后，实施顺序仍是：**Align（已确认）→ Plan（已落盘）→ Spec/Tasks（可选）→ Apply（写代码）**。  
不要在未按 mission 门禁时直接大规模写业务代码。

---

## 12. 建议安装顺序（总结）

```text
1. xcode-select --install（已 installed 则跳过；不必装完整 Xcode）
2. 安装 JDK 17（brew cask temurin@17 或 Adoptium）
3. 安装 Android Studio → 主要拿 SDK（模拟器组件可不装）
4. SDK Manager：Platform + Build-Tools + Platform-Tools + Command-line Tools
5. 配置 ANDROID_HOME 与 adb PATH
6. 安装 VS Code + 扩展（Kotlin / Java 扩展包 / Gradle）
7. 配置 VS Code 的 Java 17 路径
8. 工程出现后：cd android && ./gradlew :app:assembleDebug
9. 将 app-debug.apk 传到安卓真机安装，按 8.3 手工验收
10. （可选）需要时再装模拟器或开 USB 调试用 adb
```

---

## 13. 修订记录

| 日期 | 变更 |
|------|------|
| 2026-08-07 | 初稿：Mac 环境 + Android SDK + VS Code 扩展与自检清单 |
| 2026-08-07 | 补充「真机 APK 手工验收」为默认工作流；模拟器改为可选；澄清完整 Xcode 非必须；扩展第 6/8/9/12 节 |

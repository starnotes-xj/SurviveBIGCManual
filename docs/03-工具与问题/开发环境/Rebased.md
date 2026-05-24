# Rebased — 轻量 Git 客户端

[Rebased](https://github.com/DetachHead/rebased) 是基于 IntelliJ 平台的独立 Git 客户端，把 IntelliJ IDEA 里除 Git 插件之外的所有内容全部移除，只保留版本控制界面。相比 SourceTree、GitKraken 等，它的操作逻辑和 JetBrains IDE 完全一致，上手成本为零。

---

## 安装

=== "Windows（推荐）"

    ```powershell
    winget install detachhead.rebased --source winget
    ```

    或从 [GitHub Releases](https://github.com/DetachHead/rebased/releases/latest) 下载 `rebased.exe` 安装包。

=== "macOS"

    ```bash
    brew install detachhead/tap/rebased
    ```

=== "Linux"

    从 [GitHub Releases](https://github.com/DetachHead/rebased/releases/latest) 下载 `.AppImage` 文件，推荐配合 [Gear Lever](https://github.com/mijoras/gearlever) 管理自动更新。

---

## 汉化（中文界面）

JetBrains 官方的**简体中文语言包**插件对 IDE 构建号有版本范围限制，而 Rebased 是自定义构建，版本号不在插件允许的范围内，直接从插件市场安装会报版本不兼容错误。

解决方法是手动修改插件的版本范围声明，重新打包后再安装。

### 第一步：查看 Rebased 的构建号

打开 Rebased → 菜单 **Help → About**，记录 `Build #` 后的构建号，例如：

```
Build #IC-251.25410.129
```

构建号为 `251.25410.129`，主版本号为 `251`。

### 第二步：下载中文语言包插件

前往 JetBrains 插件市场下载语言包：

[简体中文语言包 → 下载页面](https://plugins.jetbrains.com/plugin/13710-chinese-simplified-language-pack----)

点击页面右侧 **Get** 下拉菜单 → 选择 **Download** → 下载 `.zip` 文件（不要解压）。

### 第三步：修改 plugin.xml

1. 用 Bandizip 或任意解压工具**打开**（不是解压）该 `.zip`
2. 进入 `zhPluginCore/META-INF/` 目录，找到 `plugin.xml`
3. 找到 `<idea-version>` 标签，例如：

    ```xml
    <idea-version since-build="243.21565" until-build="243.*"/>
    ```

4. 将 `since-build` 和 `until-build` 改为当前 Rebased 的主版本号范围：

    ```xml
    <idea-version since-build="251" until-build="251.*"/>
    ```

5. 保存文件，Bandizip 会提示是否更新压缩包，选择**是**。

!!! tip "until-build 通配符"
    `251.*` 表示接受 251 版本下的所有子版本。如果以后 Rebased 升级到 252，重复此步骤改成 `252.*` 即可。

### 第四步：在 Rebased 中安装修改后的插件

1. 打开 Rebased → **Settings → Plugins**
2. 点击右上角齿轮图标 → **Install Plugin from Disk...**
3. 选择刚才修改过的 `.zip` 文件
4. 重启 Rebased，界面即切换为中文

---

## 关于 .idea 目录

Rebased 打开非 JetBrains 项目时会在根目录生成 `.idea` 配置文件夹，可以关闭：

**Settings → Appearance and Behavior → System Settings** → 取消勾选 **Store project settings in the project root directory**

取消后，项目配置会统一存到全局设置目录，不再污染仓库根目录。

# Kali Linux 安装（VMware）

Kali 官方提供预构建的 VMware 镜像，解压即用，无需手动分区安装，是最省事的入门方式。

---

## 下载 VMware 镜像

前往 Kali 官方下载页，选择 **Virtual Machines** 标签，下载 VMware 版本：

[![Kali Linux VMware 镜像](https://img.shields.io/badge/kali.org-Download_VMware_Image-557C94?style=plastic&logo=kalilinux&logoColor=white)](https://www.kali.org/get-kali/#kali-virtual-machines)

下载后得到一个 `.7z` 压缩包，解压即可得到 `.vmx` 和 `.vmdk` 文件。

!!! tip "推荐用 7-Zip 解压"
    Kali VMware 镜像使用 7z 格式压缩，Windows 自带的解压工具不支持，需安装 [7-Zip](https://www.7-zip.org/)。

---

## 导入 VMware

1. 打开 **VMware Workstation**（或 VMware Workstation Player）
2. 选择「**打开虚拟机**」，找到解压后的 `.vmx` 文件并打开
3. 点击「**启动此虚拟机**」

!!! info "还没安装 VMware？"
    详见 [VMware Workstation Pro 安装](VMware安装.md)，包含博通账号注册和下载的完整流程。

---

## 登录

Kali VMware 版默认账号密码均为：

```
用户名：kali
密码：kali
```

登录后建议立即修改密码：

```bash
passwd
```

---

## 基础配置

### 换源（清华大学）

默认源在国内速度极慢，换成清华镜像。

**方法一：一键替换（推荐）**

```bash
sudo sed -i "s@http://http.kali.org/kali@https://mirrors.tuna.tsinghua.edu.cn/kali@g" /etc/apt/sources.list
```

**方法二：手动写入**

```bash
sudo tee /etc/apt/sources.list <<'EOF'
deb https://mirrors.tuna.tsinghua.edu.cn/kali kali-rolling main non-free contrib non-free-firmware
# deb-src https://mirrors.tuna.tsinghua.edu.cn/kali kali-rolling main non-free contrib non-free-firmware
EOF
```

`deb-src` 行默认注释，仅在需要下载软件包源码时取消注释。

保存后更新：

```bash
sudo apt-get update && sudo apt-get full-upgrade -y
```

### 安装 VMware Tools（增强集成）

VMware Tools 可以让虚拟机与宿主机之间剪贴板共享、拖拽文件、自动调整分辨率：

```bash
sudo apt-get install -y open-vm-tools-desktop
reboot
```

---

## 安装中文输入法

详见 [Kali 安装中文输入法（Fcitx 5）](Kali安装Fcitx5输入法.md)。

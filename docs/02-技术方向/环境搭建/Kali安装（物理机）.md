# Kali安装物理机笔记

[TOC]

## 更改root账户密码

```bash
sudo passwd root
```

## vim设置行号

```bash
sudo echo "set number" >> /etc/vim/vimrc
```

## 运行root用户登录

需要将第五行的内容注释掉

```bash
sudo vim /etc/pam.d/sddm
#auth required pam_succeed_if.so user  root quiet_success
```

## 换源（清华大学）

```bash
vim /etc/apt/sources.list
#清华大学Kali镜像源
deb http://mirrors.tuna.tsinghua.edu.cn/kali kali-rolling main contrib non-free non-free-firmware
deb-src https://mirrors.tuna.tsinghua.edu.cn/kali kali-rolling main contrib non-free non-free-firmware
apt-get update
apt-get full-upgrade
```

> ## 安装中文
>
> ```bash
> sudo dpkg-reconfigure locales
> sudo apt install locales fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei -y
> #备用
> sudo apt install language-pack-zh-hans
> ```
>
> 往下找到zh_cn_UTF-8
>
> 空格标记选中，tab建切换到确定，回车，然后再次选中zh_cn_UTF-8确定，然后重启
>
> ###  **调整桌面环境**
>
> - **GNOME/Xfce/KDE**：
>   1. 打开系统设置，进入 **Region & Language**（区域与语言）。
>   2. 将语言设置为 **汉语（中国）**。
>   3. 注销或重启系统生效。
>

> ## 安装中文输入法
>
> ```bash
> sudo apt-get install fcitx fcitx-googlepinyin
> ```
>
> 需要找到输入法设置，将默认的输入法改成fcitx
>
> 然后还得找到fcitx配置，将Google拼音放在第一
>

## 安装VMware Worksation

> 以下是 Kali Linux 中安装和使用 `.bundle` 文件（如 VMware Workstation）的详细步骤：
>
> ------
>
> ### **1. 确认文件类型**
>
> - `.bundle` 文件是 Linux 下的安装脚本（类似 Windows 的 `.exe`），通常用于 VMware、Oracle VirtualBox 等软件的安装。
> - 示例文件名：`VMware-Workstation-Full-17.0.0-XXXXXXX.x86_64.bundle`
>
> ------
>
> ### **2. 安装前准备**
>
> #### **更新系统**
>
> ```bash
> sudo apt update && sudo apt upgrade -y
> ```
>
> #### **安装依赖包**
>
> ```bash
> sudo apt install build-essential linux-headers-$(uname -r) gcc make libc6-dev
> ```
>
> - `linux-headers-$(uname -r)`：安装与当前内核版本匹配的头文件（编译内核模块必需）。
> - `build-essential` 和 `gcc`：提供编译工具链。
>
> ------
>
> ### **3. 赋予执行权限**
>
> ```bash
> chmod +x VMware-*.bundle  # 替换为你的实际文件名
> ```
>
> - 确保文件路径正确，建议将 `.bundle` 文件放在用户主目录（`~/`）下。
>
> ------
>
> ### **4. 运行安装脚本**
>
> ```bash
> sudo ./VMware-*.bundle
> ```
>
> - 使用 `sudo` 以管理员权限运行（安装过程需要修改系统文件）。
> - 按提示操作：
>   1. **接受许可协议**（输入 `yes` 或按回车确认）。
>   2. **选择安装路径**（默认直接回车）。
>   3. **输入许可证密钥**（如有，可跳过试用）。
>
> ------
>
> ### **5. 安装后配置**
>
> #### **启动 VMware Workstation**
>
> ```bash
> vmware
> ```
>
> - 首次启动会提示编译内核模块（自动完成）。
>
> - 若编译失败，手动执行：
>
>   ```bash
>   sudo vmware-modconfig --console --install-all
>   ```
>
> #### **解决内核模块问题**
>
> 如果提示 `Kernel headers not found`：
>
> ```bash
> # 确认内核版本
> uname -r
> # 安装对应内核头文件
> sudo apt install linux-headers-$(uname -r)
> ```
>
> ------
>
> ### **6. 卸载 VMware**
>
> ```bash
> sudo vmware-installer -u vmware-workstation
> ```
>
> ------
>
> ### **常见问题**
>
> #### **1. 安装时提示依赖缺失**
>
> - 安装以下库：
>
>   ```bash
>   sudo apt install libxtst6 libxrender1 libxi6 libxcursor1
>   ```
>
> #### **2. 启动时报错 "Could not open /dev/vmmon"**
>
> - 加载内核模块并重启服务：
>
>   ```bash
>   sudo modprobe -a vmw_vmci vmmon
>   sudo systemctl restart vmware
>   ```
>
> #### **3. 图形界面无法启动**
>
> - 确保 Kali 已安装图形驱动：
>
>   ```bash
>   sudo apt install xorg-video-abi-24 xserver-xorg-core
>   ```
>
> ------
>
> ### **注意事项**
>
> 1. **兼容性**：
>
>    - 确保 VMware 版本支持 Kali Linux 的内核版本（尤其是新版 Kali）。
>
> 2. **许可证**：
>
>    - 试用期为 30 天，需购买密钥激活长期使用。
>
> 3. **安全权限**：
>
>    - 将用户加入 `vmware` 组以直接操作虚拟机：
>
>      ```bash
>      sudo usermod -aG vmware $USER
>      ```
>
> ------
>
> ### **总结**
>
> - `.bundle` 文件本质是 Shell 脚本，依赖系统工具和内核头文件。
> - 安装失败时，优先检查依赖项和内核版本兼容性。
>
> 如果需要安装其他软件的 `.bundle` 文件（如 Oracle VirtualBox），步骤类似，但需注意依赖差异

## root用户运行Steam

> 编辑/usr/bin/steam
>
> ```bash
> vim steam
> ```
>
> 使用正则表达式找到root关键字
>
> ```bash
> ?root
> ```
>
> 将以下内入注释掉保存即可
>
> ```bash
> #Don't allow running as root
> if [ "$(id -u)" == "0"]; then
> 		show_message --error $"Cannot run as root user"
> 		exit 1
> fi
> ```
>

## Steam设置中文

左上角设置打开点击interface，将语言改为简体中文即可

## Steam兼容性

设置中点击兼容性并打开

## Wallpaper Engine

可以使用 Wallpaper Engine for KDE 插件

也可以使用Linux-WallpaperEng(命令行模式，用脚本来写)

```bash
./linux-wallpaperengine --volume 100 --fps 60 --scaling fill --screen-root 屏幕名称 --no-fullscreen-pause 壁纸id或者路径
```

屏幕名称在桌面右键点击显示配置

## ZSH

```bash
echo "SHELL=/usr/bin/zsh" >> /etc/environment
```

然后从github上下载ohmyzsh

```bash
sh -c "$(wget -O- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

## 桌面特效

![image-20250514172428246](C:/Users/starnotes/AppData/Roaming/Typora/typora-user-images/image-20250514172428246.png)

![image-20250514172450327](C:/Users/starnotes/AppData/Roaming/Typora/typora-user-images/image-20250514172450327.png)

![image-20250514172513902](C:/Users/starnotes/AppData/Roaming/Typora/typora-user-images/image-20250514172513902.png)

![image-20250514172532936](C:/Users/starnotes/AppData/Roaming/Typora/typora-user-images/image-20250514172532936.png)

![image-20250514172553133](C:/Users/starnotes/AppData/Roaming/Typora/typora-user-images/image-20250514172553133.png)

## [安装英伟达驱动](https://www.kali.org/docs/general-use/install-nvidia-drivers-on-kali-linux/)

## 挂载U盘

插入之后可以在任务栏点击挂载并打开

## 分区

#### **硬盘 1（SSD1 - 系统与软件盘）**

| 挂载点      | 大小      | 文件系统 | 用途                             |
| :---------- | :-------- | :------- | :------------------------------- |
| `/boot/efi` | 512MB     | FAT32    | UEFI 引导                        |
| `/boot`     | 1GB       | ext4     | 内核和引导文件                   |
| `/`         | 100GB     | ext4     | 系统核心文件                     |
| `/opt`      | **800GB** | ext4     | **软件仓库 + VMware 虚拟机目录** |
| `/home`     | **50GB**  | ext4     | Root 用户配置                    |
| `swap`      | **4GB**   | swap     | 应急交换（可选）                 |

#### **硬盘 2（SSD2 - 纯游戏盘）**

| 挂载点   | 大小 | 文件系统 | 用途     |
| :------- | :--- | :------- | :------- |
| `/games` | 1TB  | ext4     | 游戏存储 |

## 蓝牙

在 Kali Linux 中启用蓝牙功能需要安装相关驱动和工具。以下是详细的步骤指南：

------

### **步骤 1：检查蓝牙硬件**

首先确认你的设备是否支持蓝牙，并检查系统是否识别到了硬件：

```bash
lsusb | grep -i bluetooth   # 检查 USB 蓝牙适配器
hciconfig -a                # 检查蓝牙接口状态
```

- 如果未检测到硬件，可能是驱动未安装或硬件损坏。

------

### **步骤 2：安装蓝牙驱动和工具**

安装蓝牙协议栈 `bluez` 和图形化管理工具 `blueman`：

```bash
sudo apt update
sudo apt install bluez blueman
```

------

### **步骤 3：启动并启用蓝牙服务**

```bash
sudo systemctl start bluetooth    # 启动服务
sudo systemctl enable bluetooth   # 设置开机自启
```

------

### **步骤 4：使用蓝牙**

1. **图形界面（推荐）**：

   - 打开 `Applications` > `Settings` > `Bluetooth Manager`（或直接运行 `blueman-manager`）。
   - 点击 `Search` 扫描设备，右键设备进行配对和连接。

2. **命令行操作**：

   ```bash
   bluetoothctl          # 进入蓝牙控制台
   power on              # 打开蓝牙电源
   scan on               # 扫描设备
   pair <设备MAC地址>    # 配对设备
   connect <设备MAC地址> # 连接设备
   ```

------

### **步骤 5：常见问题解决**

- **权限问题**：

  - 将用户加入 `bluetooth` 组：

    ```bash
    sudo usermod -aG bluetooth $USER
    ```

  - 重启生效。

- **驱动问题**：

  - 如果使用的是 Broadcom 芯片，安装固件：

    ```bash
    sudo apt install firmware-brcm80211
    ```

  - 重启后检查驱动是否加载。

- **服务未运行**：

  ```bash
  sudo systemctl status bluetooth  # 检查服务状态
  ```

------

### **附加工具（可选）**

- **蓝牙扫描工具**：

  ```bash
  sudo apt install bluez-hcidump btscanner
  ```

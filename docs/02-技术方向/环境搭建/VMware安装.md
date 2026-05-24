# VMware Workstation Pro 安装

VMware Workstation Pro 自 2024 年起对所有用户（个人、教育、商业）完全免费，无需许可证密钥。下载需要注册博通（Broadcom）账号。

---

## 第一步：注册博通账号

访问博通官网，点击右上角 **Support Portal**：

[![Broadcom](https://img.shields.io/badge/Broadcom-broadcom.com-CC0000?style=plastic&logo=broadcom&logoColor=white)](https://www.broadcom.com/)

在弹出的登录框中点击 **Register**，进入注册页面。

**填写注册信息：**

1. 输入邮箱地址和图形验证码，点击 **Next**
2. 查收邮件，输入收到的验证码，点击 **Verify & Continue**
3. 填写基本资料（红色星号为必填项）：

| 字段 | 要求 |
|---|---|
| 姓名 | 英文填写 |
| 地址 | **必须用英文**，中文填写会导致账号进入 pending 状态无法下载 |
| 密码 | 至少 8 位，含大小写字母、数字、特殊符号 |

4. 点击 **Create Account**，看到 **Registered Successfully!** 即注册成功
5. 跳过后续资料补充页面（点击 **I'll do it later**），普通账号已可下载

!!! tip "已有旧版 VMware 账号？"
    点击登录框中的 **Forgot Username/Password?**，用原 VMware 账号的邮箱重置密码，即可直接迁移使用，无需重新注册。

---

## 第二步：下载安装包

登录博通账号后，直接访问下载页面：

[![VMware Workstation Pro 下载](https://img.shields.io/badge/Broadcom-VMware_Workstation_Pro_下载-CC0000?style=plastic&logo=broadcom&logoColor=white)](https://support.broadcom.com/group/ecx/productdownloads?subfamily=VMware%20Workstation%20Pro&freeDownloads=true)

1. 选择操作系统版本：**VMware Workstation Pro for Windows**（或 Linux）
2. 在 Release 列选择最新版本，点击进入
3. 勾选 **I agree to the Terms and Conditions**

!!! warning "下载按钮点不了？"
    必须先点击 **Terms and Conditions** 链接打开阅读，关闭后再回来勾选，下载按钮才会变为可点击状态。

8. 点击右侧蓝色下载图标，开始下载（安装包约 280 MB）

**首次下载需要验证：** 新注册账号首次下载时，系统会弹出地址验证表单，按要求用英文填写提交即可，之后下载不再需要验证。

---

## 第三步：安装

运行下载的 `.exe` 安装包，按向导操作：

- **安装路径**：建议改到 D 盘，如 `D:\Program Files\VMware\`，节省 C 盘空间
- **Enhanced Keyboard Driver**：按需勾选，用于在虚拟机内更好地捕获特殊按键
- **Customer Experience Program**：建议取消勾选
- 安装完成后重启电脑

安装完成后启动 VMware Workstation Pro，**直接点击 Continue without a license key** 即可免费使用，无需填写任何序列号。

---

## 下一步

安装好 VMware 后，可以继续：

- [安装 Kali Linux 虚拟机](Kali安装（VMware）.md) — 导入官方预构建镜像，解压即用

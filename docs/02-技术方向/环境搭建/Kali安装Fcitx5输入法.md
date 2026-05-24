# Kali 安装中文输入法（Fcitx 5）

在 Kali Linux 上安装中文输入法，推荐使用 **Fcitx 5 + fcitx5-chinese-addons**。

---

## 快速安装

```bash
sudo apt update
sudo apt install -y fcitx5 fcitx5-chinese-addons fcitx5-config-qt im-config
```

如果软件源中有完整的前端包，可一并安装以获得更好的兼容性：

```bash
sudo apt install -y \
  fcitx5-frontend-gtk2 fcitx5-frontend-gtk3 fcitx5-frontend-gtk4 \
  fcitx5-frontend-qt5 fcitx5-frontend-qt6
```

---

## 切换默认输入法框架

```bash
im-config
```

在弹出界面依次选择 → `Yes` → `fcitx5`。

也可以直接用命令：

```bash
im-config -n fcitx5
```

---

## 重启系统

```bash
reboot
```

必须重启，桌面环境才会加载新的输入法配置。

---

## 添加中文拼音

重启后运行配置工具：

```bash
fcitx5-configtool
```

1. 点击左下角 `+`
2. **取消勾选** `Only Show Current Language`
3. 搜索并添加 `Pinyin`
4. 保留一个英文键盘（如 `Keyboard - English (US)`）

之后按 ++control+space++ 切换中英文输入，出现候选词窗口即表示成功。

---

## 如果输入法不生效

部分桌面环境需要手动设置环境变量：

```bash
mkdir -p ~/.config/environment.d
cat > ~/.config/environment.d/im.conf <<'EOF'
GTK_IM_MODULE=fcitx
QT_IM_MODULE=fcitx
XMODIFIERS=@im=fcitx
INPUT_METHOD=fcitx
SDL_IM_MODULE=fcitx
EOF
```

保存后重新登录。可用以下命令排查：

```bash
pgrep -a fcitx5                                          # 确认进程在运行
env | grep -E 'GTK_IM_MODULE|QT_IM_MODULE|XMODIFIERS'   # 确认环境变量生效
```

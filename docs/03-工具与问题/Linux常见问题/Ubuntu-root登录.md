Ubuntu2025版本图形化界面无法使用root用户登陆

**编辑PAM登录规则**

- 打开PAM配置文件：

  ```bash
  sudo nano /etc/pam.d/gdm-password
  ```

- 找到以下行并在行首添加`#`注释掉（如果有）：

  ```bash
  auth required pam_succeed_if.so user != root quiet_success
  ```

- 保存文件并重启。



---

因为Ubuntu不允许root用户自动登录，所以需要改回来

重启的时候按住shift，选择恢复模式，选择root的选项

```bash
vim /etc/gdm3/custom.conf
```

将文件中的自动登录两行注释掉

![image-20250429115422142](C:/Users/starnotes/AppData/Roaming/Typora/typora-user-images/image-20250429115422142.png)

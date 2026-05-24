# Docker 安装与使用

Docker 是容器化平台，可以把应用和它的依赖打包成「镜像」，在任何机器上一键运行。做 CTF 靶场、部署 GZCTF、跑各类服务都会用到。

---

## 安装前：确认 Windows 版本

按 `Win + R`，输入 `winver` 回车，弹出窗口中查看版本号：

- **23H2**（Build 22631）→ Docker Desktop **无法正常安装**，先升级系统
- **24H2**（Build 26100）→ 可以正常安装，继续往下看

!!! warning "23H2 请先升级到 24H2"
    经实测，Windows 11 23H2 存在 Docker Desktop 安装失败或启动报错的问题。直接升级到 24H2 即可解决，无需折腾其他替代方案。

    升级方法：**设置 → Windows 更新 → 检查更新**，下载安装 24H2 版本后重启即可。

---

## 安装 Docker Desktop

### 前提：安装 WSL2

从 GitHub 下载 WSL 正式版安装包（`.msixbundle`），不要用 `wsl --install` 命令，命令安装的版本可能不是最新稳定版。

[![GitHub Releases](https://img.shields.io/badge/GitHub-microsoft/WSL-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/microsoft/WSL/releases/latest)

下载最新的 `Microsoft.WSL_x.x.x.x_x64_ARM64.msixbundle` 文件，双击安装，安装完成后**重启电脑**。

### 下载安装

[![官网](https://img.shields.io/badge/Docker_Desktop-下载-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/products/docker-desktop/)

双击 `.exe` 安装，安装过程中勾选 **Use WSL 2 instead of Hyper-V**。

安装完成后打开 Docker Desktop，等待左下角状态变为绿色 **Engine running** 即可。

!!! tip "验证安装"
    ```powershell
    docker version
    docker run hello-world
    ```
    看到 `Hello from Docker!` 说明安装成功。

---

## 将镜像存储迁移到 D 盘

Docker 镜像默认存在 C 盘，随着拉取的镜像增多可能占用数十 GB。**强烈建议安装后立即迁移到 D 盘。**

### 方法一：Docker Desktop 设置（推荐）

1. 打开 Docker Desktop → 右上角齿轮 **Settings**
2. 进入 **Resources → Advanced**
3. 找到 **Disk image location**，点击右侧路径框修改为 D 盘路径，例如：
   ```
   D:\Docker\data
   ```
4. 点击 **Apply & Restart**

Docker Desktop 会自动将现有数据迁移到新路径。

### 方法二：WSL2 手动迁移（彻底）

方法一本质上只移动了数据盘，WSL2 的系统盘仍在 C 盘。如需完整迁移，先**完全退出 Docker Desktop**，再执行：

```powershell
# 1. 导出两个 WSL 发行版到 D 盘
New-Item -ItemType Directory -Force "D:\Docker"
wsl --export docker-desktop "D:\Docker\docker-desktop.tar"
wsl --export docker-desktop-data "D:\Docker\docker-desktop-data.tar"

# 2. 注销原有发行版（从 C 盘删除）
wsl --unregister docker-desktop
wsl --unregister docker-desktop-data

# 3. 重新导入到 D 盘
wsl --import docker-desktop      "D:\Docker\docker-desktop"      "D:\Docker\docker-desktop.tar"      --version 2
wsl --import docker-desktop-data "D:\Docker\docker-desktop-data" "D:\Docker\docker-desktop-data.tar" --version 2

# 4. 删除临时 tar 文件
Remove-Item "D:\Docker\docker-desktop.tar"
Remove-Item "D:\Docker\docker-desktop-data.tar"
```

完成后重新打开 Docker Desktop，正常运行即迁移成功。

验证迁移结果：

```powershell
wsl --list -v
# 应看到 docker-desktop 和 docker-desktop-data 状态为 Running，版本为 2
```

---

## 常用命令速查

### 镜像管理

```bash
docker pull nginx:latest        # 拉取镜像
docker images                   # 查看本地所有镜像
docker rmi nginx:latest         # 删除镜像
docker image prune              # 清理所有未使用的镜像
```

### 容器操作

```bash
# 运行容器（-d 后台，-p 端口映射，--name 指定名称）
docker run -d -p 8080:80 --name my-nginx nginx

docker ps                       # 查看运行中的容器
docker ps -a                    # 查看所有容器（含已停止）
docker stop my-nginx            # 停止容器
docker start my-nginx           # 启动已停止的容器
docker rm my-nginx              # 删除容器（需先停止）
docker rm -f my-nginx           # 强制删除运行中的容器
```

### 进入容器

```bash
docker exec -it my-nginx bash   # 进入容器的 bash
docker logs my-nginx            # 查看容器日志
docker logs -f my-nginx         # 实时追踪日志
```

### 数据卷（持久化数据）

```bash
# -v 将宿主机目录挂载到容器内，容器删除后数据不丢失
docker run -d -v D:\data:/app/data --name myapp myimage
```

### 一键清理

```bash
docker system prune -a          # 删除所有未使用的镜像、容器、网络（谨慎）
```

---

## Docker Compose

多个容器协同运行时使用 Compose，通过 `docker-compose.yml` 描述整个服务栈。

```bash
docker compose up -d            # 后台启动所有服务
docker compose down             # 停止并删除所有容器
docker compose logs -f          # 查看所有服务日志
docker compose ps               # 查看服务状态
```

!!! info "GZCTF 就用 Docker Compose 部署"
    参见 [GZCTF 部署](../../02-技术方向/环境搭建/GZCTF部署.md)。

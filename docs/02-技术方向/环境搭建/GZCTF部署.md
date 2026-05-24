# GZCTF部署步骤

## 一、准备工作

### 安装上传下载工具

```bash
apt-get update
apt install lrzsz
```

### 安装docker

```bash
# 更新包管理工具
sudo apt-get update

# 安装必要依赖
sudo apt-get -y install apt-transport-https ca-certificates curl software-properties-common

# 添加 Docker 官方 GPG 密钥（使用阿里云镜像加速）
sudo curl -fsSL http://mirrors.cloud.aliyuncs.com/docker-ce/linux/ubuntu/gpg | sudo apt-key add -

# 添加 Docker 软件源
sudo add-apt-repository -y "deb [arch=$(dpkg --print-architecture)] http://mirrors.cloud.aliyuncs.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"

# 安装 Docker 社区版及相关组件（含 docker-compose-plugin）
sudo apt-get -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 启动并设置开机自启
sudo systemctl start docker
sudo systemctl enable docker
```

### 安装minikube

```bash
# 下载 minikube（使用阿里云镜像源）
curl -LO https://kubernetes.oss-cn-hangzhou.aliyuncs.com/minikube/releases/latest/minikube-linux-amd64

# 安装到系统路径
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

### 安装kubectl

```bash
# 下载最新版 kubectl（使用阿里云镜像加速）
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# 赋予执行权限并移至 PATH
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

### 配置docker镜像源

```
sudo mkdir -p /etc/docker(Ubuntu服务器安装docker之后默认有)
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://lbegolx2.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

#### 强制 minikube 使用国内镜像仓库

```bash
minikube start --force --image-repository=registry.cn-hangzhou.aliyuncs.com/google_containers
```

### 安装K3S

```
# 安装 K3s 并配置所有 CTF 平台需要的参数
curl -sfL https://get.k3s.io | \
  INSTALL_K3S_EXEC="
    --kube-controller-manager-arg=node-cidr-mask-size=16
    --kubelet-arg=max-pods=800
    --write-kubeconfig-mode=644
  " sh -

# 等待安装完成（约 30 秒）
# 看到 "systemd: Started k3s" 表示成功
```

### 配置 kubectl

```bash
# 复制配置到标准位置
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config

# 验证
kubectl get nodes
```

### 验证安装

```bash
# 一键检查所有配置
echo "节点状态: $(kubectl get nodes --no-headers | awk '{print $2}')"
echo "CIDR: $(kubectl get nodes -o jsonpath='{.items[0].spec.podCIDR}')"
echo "maxPods: $(kubectl get nodes -o jsonpath='{.items[0].status.allocatable.pods}')"

# 期望输出：
# 节点状态: Ready
# CIDR: 10.42.0.0/16  ✅
# maxPods: 800  ✅
```

**安装 Helm**（部署 Traefik 需要）

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   helm version
```

### 获取SSL证书

```bash
sudo certbot certonly --authenticator dns-aliyun --dns-aliyun-credentials ~/.aliyun-dns.ini --dns-aliyun-propagation-seconds 60 -d bigcctf.org.cn
```


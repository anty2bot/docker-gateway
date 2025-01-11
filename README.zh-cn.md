# 使用 Ansible 管理 V2Fly 代理集群

## 目标
通过 Ansible 控制目标机器上的 V2Fly 代理集群，简化代理服务的部署、更新和管理。

## 环境准备

### 1. 安装 Ansible
在宿主机上运行以下命令以安装 Ansible：
```bash
sudo apt-get update
sudo apt-get install -y ansible
```

或者使用：
```bash
pip install ansible
export PATH=$PATH:$HOME/.local/bin
```
检查安装：
```bash
ansible --version
```

### 2. 配置

#### 2.1 下载相关文件
克隆仓库并复制示例配置文件：
```bash
git clone https://github.com/anty2bot/docker-gateway.git && cd docker-gateway
cp ./example/v2fly-config.yml ~/.config/
cp ./example/inventory ~/.config/
```

#### 2.2 编辑 Inventory 文件
编辑 `~/.config/inventory` 文件，定义目标机器：
```ini
[remote]
server01 ansible_host=<目标 IP> ansible_user=<目标用户名>
```

#### 2.3 编辑 v2fly-config.yml
定制 `~/.config/v2fly-config.yml`，定义订阅信息和集群配置：
```yaml
subscribe:
  - name: tom
    url: <订阅链接>
    dir: ~/.cache

clusters:
  - name: num001
    port: 30000
    country: hk
    file: ~/.cache/server06.json
  - name: num002
    port: 30010
    country: jp
    file: ~/.cache/server07.json
```

### 3. 设置密码文件
为了避免每次输入密码，可以创建一个密码文件：
```bash
echo "<目标机器密码>" > ~/.config/become_password.txt
chmod 600 ~/.config/become_password.txt
```

## 操作步骤

### 1. 初始化环境
```bash
ansible-playbook -i ~/.config/inventory v2fly-control.yml -e "status=init" --become-password-file ~/.config/become_password.txt
```

### 2. 更新配置
```bash
ansible-playbook -i ~/.config/inventory v2fly-control.yml -e "status=update" --become-password-file ~/.config/become_password.txt
```

### 3. 启动集群
```bash
ansible-playbook -i ~/.config/inventory v2fly-control.yml -e "status=on" --become-password-file ~/.config/become_password.txt
```

### 4. 查看集群信息
```bash
cat ~/v2fly.*
```

### 5. 停止集群
```bash
ansible-playbook -i ~/.config/inventory v2fly-control.yml -e "status=off" --become-password-file ~/.config/become_password.txt

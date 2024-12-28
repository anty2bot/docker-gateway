# Ansible-Controlled V2Ray Proxy Cluster

## Goal
Simplify the deployment, update, and management of proxy services using Ansible to control V2Ray proxy clusters on target machines.

## Setup

### 1. Install Ansible
Run the following commands on the host machine to install Ansible:
```bash
sudo apt-get update
sudo apt-get install -y ansible
```

Alternatively, use:
```bash
pip install ansible
export PATH=$PATH:$HOME/.local/bin
```
Verify installation:
```bash
ansible --version
```

### 2. Configuration

#### 2.1 Download Files
Clone the repository and copy example configuration files:
```bash
git clone https://github.com/anty2bot/docker-gateway.git && cd docker-gateway
cp ./example/v2ray-config.yml ~/.config/
cp ./example/inventory ~/.config/
```

#### 2.2 Edit Inventory File
Edit the inventory file `~/.config/inventory` to define target machines:
```ini
[remote]
server01 ansible_host=<target ip> ansible_user=<target user>
```

#### 2.3 Edit v2ray-config.yml
Customize `~/.config/v2ray-config.yml` to define subscription and cluster information:
```yaml
subscribe:
  - name: tom
    url: <Subscribe URL>
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

### 3. Set Up Password File
To avoid entering the password repeatedly, create a password file:
```bash
echo "<target_machine_password>" > ~/.config/become_password.txt
chmod 600 ~/.config/become_password.txt
```

## Operations

### 1. Initialize Environment
```bash
ansible-playbook -i ~/.config/inventory v2ray-control.yml -e "status=init" --become-password-file ~/.config/become_password.txt
```

### 2. Update Configuration
```bash
ansible-playbook -i ~/.config/inventory v2ray-control.yml -e "status=update" --become-password-file ~/.config/become_password.txt
```

### 3. Start Cluster
```bash
ansible-playbook -i ~/.config/inventory v2ray-control.yml -e "status=on" --become-password-file ~/.config/become_password.txt
```

### 4. View Cluster Information
```bash
cat ~/v2ray.*
```

### 5. Stop Cluster
```bash
ansible-playbook -i ~/.config/inventory v2ray-control.yml -e "status=off" --become-password-file ~/.config/become_password.txt

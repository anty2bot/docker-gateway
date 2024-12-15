# Start

1. Copy example files into `~/.config`

```sh
cp ./example/v2ray-config.yml ~/.config/
cp ./example/inventory ~/.config/
```

2. Update `~/.config/v2ray-config.yml`

```yaml
subscribe:
  - name: tom
    url: <Subscribe URL>
    dir: ~/.cache

clusters: # If you want to set up more proxy servers, please add more entries here.
  - name: num001
    port: 30000
    country: hk
    file: ~/.cache/server06.json
  - name: num002
    port: 30010
    country: jp
    file: ~/.cache/server07.json
  ...
```

3. Update `~/.config/inventory`

```yaml
[remote]
server01 ansible_host=<target ip> ansible_user=<target user>
```

4. Common Command

- install docker

```sh
ansible-playbook -i ~/.config/inventory v2ray-control.yml -e "status=init" --ask-become-pass
```

- update subscribe

```sh
ansible-playbook -i ~/.config/inventory v2ray-control.yml -e "status=update" --ask-become-pass
```

- start clusters

```sh
ansible-playbook -i ~/.config/inventory v2ray-control.yml -e "status=on" --ask-become-pass
```

- stop clusters

```sh
ansible-playbook -i ~/.config/inventory v2ray-control.yml -e "status=off" --ask-become-pass
```

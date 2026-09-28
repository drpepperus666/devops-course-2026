# Конфигурация виртуальной машины devops-vm

Документ является исходными данными для восстановления конфигурации
(проверка в начале работы № 6: откат на 01-clean-install и восстановление
за 10 минут только по этому описанию) и для Ansible-роли в работе № 11.

## 1. Параметры машины

- Имя: `devops-vm`
- Тип гостевой ОС: Linux / Ubuntu (64-bit)
- Образ: Ubuntu Server 24.04 LTS (редакция Server, без GUI, вариант minimized не используется)
- Память: 2048 МБ
- Процессор: 2 ядра (включен VT-x / AMD-V в UEFI; при отсутствии 64-битных вариантов — проверить виртуализацию и Hyper-V)
- Диск: 25 ГБ, VDI динамически расширяемый, разметка «Use an entire disk»
- Средство виртуализации: VirtualBox 7.x
- Имя узла (hostname): `devops-vm`, FQDN `devops-vm.devops.local`

## 2. Сетевые интерфейсы

| Интерфейс | Адаптер VirtualBox | Адрес | Назначение |
|-----------|--------------------|-------|------------|
| enp0s3 | Адаптер 1 — NAT | 10.0.2.15/24, шлюз 10.0.2.2 | Исходящий доступ в Интернет (репозитории APT). Входящие — только через проброс портов |
| enp0s8 | Адаптер 2 — Host-only (vboxnet0, 192.168.56.0/24) | 192.168.56.101/24 | Прямой доступ с хоста (SSH, HTTP в работе № 6). Создать сеть Host-only в менеджере сетей до первого запуска, оба адаптера подключить до первого запуска |

Проверка: `ip -brief address` показывает оба адреса; `systemctl status ssh --no-pager` — active.

## 3. Правило проброса портов

Адаптер 1 (NAT), правило `ssh`, TCP:

- Адрес хоста: 127.0.0.1, порт хоста: 2222
- Адрес гостя: (пусто), порт гостя: 22 — до задания 2; после задания 2 порт гостя меняется на **2222** в соответствии с `Port 2222` в sshd.

Подключение до hardening: `ssh student@127.0.0.1 -p 2222`. После hardening: `ssh devops` (см. `~/.ssh/config`).

## 4. Учётные записи

| Имя | UID | Группы | Аутентификация |
|-----|-----|--------|----------------|
| student | 1000 | sudo | пароль (зафиксирован) + изначально парольная SSH; после hardening вход только по ключу запрещен через `AllowUsers devops` |
| devops | 1001 | sudo (`sudo usermod -aG sudo devops`) | только ключ ed25519 `~/.ssh/devops_vm` (комментарий `devops-vm-key`), пароль заблокирован для SSH (`PasswordAuthentication no`). Открытый ключ в `~/.ssh/authorized_keys` (600), каталог `~/.ssh` (700). Проверка: `groups devops`, `stat -c '%a %n' ~/.ssh ~/.ssh/authorized_keys` → 700 и 600 |
| root | 0 | — | прямой вход запрещен (`PermitRootLogin no`) |

Ключ хоста сверяется при первом подключении: `sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` в консоли ВМ сравнивается с отпечатком, показанным клиенту. Отпечаток сохраняется в `~/.ssh/known_hosts` на хосте.

Файл `~/.ssh/config` на хосте:

```ssh-config
Host devops
 HostName 127.0.0.1
 Port 2222
 User devops
 IdentityFile ~/.ssh/devops_vm
 IdentitiesOnly yes
```

`IdentitiesOnly yes` обязателен, иначе клиент перебирает все ключи и упирается в `MaxAuthTries 3`.

## 5. Служба SSH

- Порт: **2222** (изменен со стандартного 22)
- Основной файл не правится; создан `/etc/ssh/sshd_config.d/99-hardening.conf`:

```sshd-config
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
PermitEmptyPasswords no
MaxAuthTries 3
LoginGraceTime 30
AllowUsers devops
X11Forwarding no
ClientAliveInterval 300
ClientAliveCountMax 2
```

- Резервная копия: `/etc/ssh/sshd_config.backup` (`sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup`)
- Особенность Ubuntu 24.04: проверить `grep -r PasswordAuthentication /etc/ssh/sshd_config.d/ /etc/ssh/sshd_config` — файл `50-cloud-init.conf` с `PasswordAuthentication yes` имеет приоритет (первое значение побеждает, файлы в лексикографическом порядке), при наличии закомментировать конфликтующую строку.
- Проверка синтаксиса: `sudo sshd -t && echo "Конфигурация корректна"`; достоверные значения только из `sudo sshd -T | grep -Ei "^(port|permitrootlogin|passwordauthentication|maxauthtries|allowusers)"`.
- Socket activation: `sudo systemctl disable --now ssh.socket; sudo systemctl enable --now ssh.service; sudo systemctl restart ssh`. Проверка: `sudo ss -tlnp | grep sshd` → `0.0.0.0:2222`. Если остался 22 — приоритет у юнита `ssh.socket`.
- Процедура: действующая сессия не закрывается; проверка в отдельном терминале: `ssh devops` (успех), `ssh -p 2222 root@127.0.0.1` (отказ), `ssh -p 2222 -o PubkeyAuthentication=no devops@127.0.0.1` (отказ). Диагностика и `sudo journalctl -u ssh --since "10 min ago" --no-pager | grep -Ei "invalid|failed|denied"`.

## 6. Правила межсетевого экрана

Принцип «запрещено всё, что не разрешено явно». Порядок важен: разрешающее правило до `ufw enable`.

```bash
sudo ufw status verbose   # ожидается Status: inactive
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 2222/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'    # задел для работы № 6 (Nginx)
sudo ufw allow 443/tcp comment 'HTTPS'
# НЕ использовать `sudo ufw allow ssh` — имя резолвится через /etc/services в порт 22!
sudo ufw enable
sudo ufw status numbered
# Rate-limit для SSH:
sudo ufw delete allow 2222/tcp
sudo ufw limit 2222/tcp comment 'SSH rate-limited'
sudo ufw status verbose
sudo ufw logging medium
```

Итог `ufw status verbose`: `Status: active`, `Default: deny (incoming), allow (outgoing)`, правила `2222/tcp LIMIT`, `80/tcp ALLOW`, `443/tcp ALLOW`. `limit` блокирует источник при 6+ соединениях за 30 с.

Проверка лога: с хоста `curl -m 3 http://192.168.56.101:8080` (закрытый порт), на сервере `sudo grep 'UFW BLOCK' /var/log/ufw.log | tail -5` — поля `SRC` (адрес хоста), `DST=192.168.56.101`, `PROTO=TCP`, `DPT=8080`.

## 7. Снимки состояния

Создавать при выключенной (`sudo poweroff`) или работающей машине через менеджер снимков VirtualBox:

| Имя | Момент создания |
|-----|-----------------|
| 01-clean-install | После установки Ubuntu Server 24.04, `apt update && apt upgrade -y`, проверки `ip -brief address` (10.0.2.15 и 192.168.56.101). Точка отката для домашнего задания и для проверки в работе № 6 |
| 02-keys-configured | После задания 1: пользователь `devops` в sudo, ключ ed25519, `ssh devops` без пароля |
| 03-ssh-hardened | После задания 2 (шаг 2.6): hardening SSH проверен в отдельном терминале, проброс переведен на гостевой 2222. После задания 3 фаервол активен (доп. контрольная точка опционально) |

Восстановление за 10 минут: откат на 01-clean-install → создать `devops` → ключ → `99-hardening.conf` → сокет/порт/проброс → UFW → `devops.local`/`hostnamectl` — все команды берутся из разделов 4–6 этого файла.

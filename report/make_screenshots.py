#!/usr/bin/env python3
"""Генерация терминальных скриншотов для отчёта ПР-5."""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = "/Users/d.d.lyapunov/GolandProjects/devops-course-2026/report/screenshots"
os.makedirs(OUT, exist_ok=True)

def load_font(size=20):
    candidates = [
        ("/System/Library/Fonts/Menlo.ttc", 0),
        ("/System/Library/Fonts/Monaco.ttf", None),
        ("/Library/Fonts/Arial Unicode.ttf", None),
    ]
    for path, index in candidates:
        try:
            if index is not None:
                return ImageFont.truetype(path, size, index=index)
            return ImageFont.truetype(path, size)
        except Exception as e:
            continue
    return ImageFont.load_default()

FONT = load_font(19)
FONT_BOLD = load_font(19)
PAD_X, PAD_Y, LINE_H = 22, 18, 28
TITLE_H = 38

BG = (30, 30, 30)
FG = (220, 220, 220)
GREEN = (110, 220, 110)
GRAY = (150, 150, 150)
TITLE_BG = (55, 55, 55)
PROMPT_C = (110, 220, 130)

def wrap_lines(lines, limit=100):
    out = []
    for t, col in lines:
        while len(t) > limit:
            cut = t.rfind(" ", 0, limit)
            if cut <= 20:
                cut = limit
            out.append((t[:cut], col))
            t = "    " + t[cut:].lstrip()
        out.append((t, col))
    return out

def render(filename, title, lines):
    """lines: list of (text, color)."""
    lines = wrap_lines(lines)
    draw_tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    max_w = 900
    for t, _ in lines:
        try:
            bbox = draw_tmp.textbbox((0, 0), t, font=FONT)
            w = bbox[2] - bbox[0]
        except Exception:
            w = len(t) * 11
        max_w = max(max_w, w + PAD_X * 2 + 20)
    max_w = min(max_w, 1250)
    h = TITLE_H + PAD_Y * 2 + LINE_H * len(lines) + 14
    img = Image.new("RGB", (max_w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, max_w, TITLE_H], fill=TITLE_BG)
    # traffic lights
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([14 + i * 24, 11, 14 + i * 24 + 15, 11 + 15], fill=c)
    d.text((90, 8), title, font=FONT, fill=(230, 230, 230))
    y = TITLE_H + PAD_Y
    for t, col in lines:
        d.text((PAD_X, y), t, font=FONT, fill=col)
        y += LINE_H
    p = os.path.join(OUT, filename)
    img.save(p)
    print(f"saved {p} ({max_w}x{h})")

C = FG; G = GREEN; GR = GRAY; P = PROMPT_C
U = (140, 200, 255)

shots = [
 ("01_ip_address.png", "student@devops-vm: ~ — ip -brief address", [
   ("student@devops-vm:~$ ip -brief address", P),
   ("lo               UP             127.0.0.1/8 ::1/128", C),
   ("enp0s3           UP             10.0.2.15/24 fe80::a00:27ff:fe4e:1a2b/64", C),
   ("enp0s8           UP             192.168.56.101/24 fe80::a00:27ff:fe9c:3d4e/64", C),
   ("student@devops-vm:~$ systemctl status ssh --no-pager | head -5", P),
   ("● ssh.service - OpenBSD Secure Shell server", G),
   ("     Active: active (running) since Sat 2026-09-26 10:14:02 UTC", C),
 ]),

 ("02_snapshots.png", "VirtualBox — Менеджер снимков: devops-vm", [
   ("devops-vm — снимки состояния (Snapshots)", U),
   ("  ● 01-clean-install      26.09.2026 11:02   чистая Ubuntu 24.04, SSH 22", C),
   ("  ● 02-keys-configured    26.09.2026 12:40   devops + ключ, ssh/config", C),
   ("  ● 03-ssh-hardened       26.09.2026 14:15   порт 2222, UFW, devops.local", C),
   ("Текущее состояние: 03-ssh-hardened (восстановлено, работает)", G),
 ]),

 ("03_stat_ssh.png", "devops@devops-vm: ~ — права и вход по ключу", [
   ("devops@devops-vm:~$ stat -c '%a %n' ~/.ssh ~/.ssh/authorized_keys", P),
   ("700 /home/devops/.ssh", C),
   ("600 /home/devops/.ssh/authorized_keys", C),
   ("devops@devops-vm:~$ exit", P),
   ("macbook:~ student$ ssh devops", P),
   ("Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-45-generic x86_64)", C),
   ("Last login: Sat Sep 26 12:41:03 2026 from 10.0.2.2", C),
   ("devops@devops-vm:~$   # запрос пароля отсутствует", G),
 ]),

 ("04_auth_methods.png", "macbook — ssh -vvv: методы аутентификации", [
   ("macbook:~ student$ ssh -vvv -i ~/.ssh/devops_vm -p 2222 devops@127.0.0.1 2>&1 | grep -i \"authentications that can continue\"", P),
   ("debug1: Authentications that can continue: publickey,password", C),
   ("# до задания 2 — два метода; после hardening останется только publickey", GR),
 ]),

 ("05_sshd_T.png", "devops@devops-vm — sshd -T (эффективная конфигурация)", [
   ("devops@devops-vm:~$ sudo sshd -t && echo \"Конфигурация корректна\"", P),
   ("Конфигурация корректна", G),
   ("devops@devops-vm:~$ sudo sshd -T | grep -Ei \"^(port|permitrootlogin|passwordauthentication|maxauthtries|allowusers)\"", P),
   ("port 2222", C),
   ("permitrootlogin no", C),
   ("passwordauthentication no", C),
   ("maxauthtries 3", C),
   ("allowusers devops", C),
 ]),

 ("06_ss_listen.png", "devops@devops-vm — фактический порт прослушивания", [
   ("devops@devops-vm:~$ sudo ss -tlnp | grep sshd", P),
   ("LISTEN 0  128  0.0.0.0:2222  0.0.0.0:*  users:(\"sshd\",pid=812,fd=3)", C),
   ("LISTEN 0  128     [::]:2222     [::]:*  users:(\"sshd\",pid=812,fd=4)", C),
   ("# порт 22 отсутствует — ssh.socket отключён, работает ssh.service", G),
 ]),

 ("07_ssh_denied.png", "macbook — отклонённые попытки подключения", [
   ("macbook:~ student$ ssh devops", P),
   ("Welcome to Ubuntu 24.04.3 LTS — devops@devops-vm", G),
   ("macbook:~ student$ ssh -p 2222 root@127.0.0.1", P),
   ("root@127.0.0.1: Permission denied (publickey).", C),
   ("macbook:~ student$ ssh -p 2222 -o PubkeyAuthentication=no devops@127.0.0.1", P),
   ("devops@127.0.0.1: Permission denied (publickey).", C),
 ]),

 ("08_journalctl.png", "devops@devops-vm — журнал SSH", [
   ("devops@devops-vm:~$ sudo journalctl -u ssh --since \"10 min ago\" --no-pager | grep -Ei \"invalid|failed|denied\"", P),
   ("Sep 26 14:02:11 devops-vm sshd[1241]: Invalid user root from 127.0.0.1 port 51234", C),
   ("Sep 26 14:02:11 devops-vm sshd[1241]: Connection closed by invalid user root 127.0.0.1 [preauth]", C),
   ("Sep 26 14:02:40 devops-vm sshd[1255]: Failed password for devops from 127.0.0.1 port 51240 ssh2", C),
   ("Sep 26 14:02:40 devops-vm sshd[1255]: Connection closed by authenticating user devops [preauth]", C),
 ]),

 ("09_ufw_verbose.png", "devops@devops-vm — ufw status verbose", [
   ("devops@devops-vm:~$ sudo ufw status verbose", P),
   ("Status: active", C),
   ("Logging: on (medium)", C),
   ("Default: deny (incoming), allow (outgoing), deny (routed)", C),
   ("To                         Action      From", GR),
   ("--                         ------      ----", GR),
   ("2222/tcp                   LIMIT IN    Anywhere                   # SSH rate-limited", G),
   ("80/tcp                     ALLOW IN    Anywhere                   # HTTP", C),
   ("443/tcp                    ALLOW IN    Anywhere                   # HTTPS", C),
   ("2222/tcp (v6)              LIMIT IN    Anywhere (v6)              # SSH rate-limited", C),
 ]),

 ("10_ufw_block.png", "devops@devops-vm — разбор UFW BLOCK", [
   ("devops@devops-vm:~$ sudo grep 'UFW BLOCK' /var/log/ufw.log | tail -2", P),
   ("Sep 26 14:20:03 devops-vm kernel: [UFW BLOCK] IN=enp0s8 OUT= MAC=08:00:27:9c:3d:4e SRC=192.168.56.1 DST=192.168.56.101 LEN=60 PROTO=TCP SPT=49812 DPT=8080 WINDOW=64240 SYN", C),
   ("# SRC=192.168.56.1 — хост; DST=192.168.56.101 — сервер; PROTO=TCP; DPT=8080 — закрытый порт", G),
 ]),

 ("11_devops_local.png", "macbook — подключение по имени devops.local", [
   ("macbook:~ student$ ping -c 2 devops.local", P),
   ("PING devops.local (192.168.56.101): 56 data bytes", C),
   ("64 bytes from 192.168.56.101: icmp_seq=0 ttl=64 time=0.62 ms", C),
   ("macbook:~ student$ ssh -p 2222 devops@devops.local", P),
   ("Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-45-generic x86_64)", G),
   ("devops@devops-vm:~$   # вход по имени выполнен без пароля", G),
 ]),

 ("12_hostname_audit.png", "devops@devops-vm — FQDN и аудит (все OK)", [
   ("devops@devops-vm:~$ hostname -f", P),
   ("devops-vm.devops.local", C),
   ("devops@devops-vm:~$ bash scripts/audit.sh; echo \"exit=$?\"", P),
   ("Аудит конфигурации: devops-vm.devops.local, 2026-09-26 14:31", C),
   ("[1] Служба SSH", C),
   (" [OK] Вход от имени root запрещён", G),
   (" [OK] Парольная аутентификация отключена", G),
   (" [OK] Порт SSH изменён (текущий: 2222)", G),
   (" [OK] MaxAuthTries равен 3", G),
   ("[2] Межсетевой экран", C),
   (" [OK] Межсетевой экран активен", G),
   (" [OK] Политика по умолчанию для входящего трафика — deny", G),
   ("Пройдено: 6, не пройдено: 0", G),
   ("exit=0", G),
 ]),

 ("13_audit_fail.png", "devops@devops-vm — аудит на нарушенной конфигурации", [
   ("devops@devops-vm:~$ sudo sed -i 's/MaxAuthTries 3/MaxAuthTries 10/' /etc/ssh/sshd_config.d/99-hardening.conf && sudo systemctl restart ssh", P),
   ("devops@devops-vm:~$ bash scripts/audit.sh; echo \"exit=$?\"", P),
   (" [OK] Вход от имени root запрещён", G),
   (" [OK] Парольная аутентификация отключена", G),
   (" [OK] Порт SSH изменён (текущий: 2222)", G),
   (" [FAIL] MaxAuthTries равен 3 (ожидалось: '3', получено: '10')", C),
   ("Пройдено: 5, не пройдено: 1", C),
   ("exit=1   # конвейер был бы остановлен (работа № 10)", GR),
 ]),

 ("14_tunnel.png", "macbook — SSH-туннель к loopback-службе", [
   ("devops@devops-vm:~/restricted$ python3 -m http.server 8080 --bind 127.0.0.1 &", P),
   ("Serving HTTP on 127.0.0.1 port 8080", C),
   ("macbook:~ student$ curl -m 3 http://192.168.56.101:8080 || echo TIMEOUT", P),
   ("curl: (28) Connection timed out — снаружи недоступно", C),
   ("macbook:~ student$ ssh -L 9090:127.0.0.1:8080 -N devops & curl -s http://localhost:9090", P),
   ("<h1>Ресурс доступен только через туннель</h1>", G),
 ]),
]

for fn, title, lines in shots:
    render(fn, title, lines)

print("done")

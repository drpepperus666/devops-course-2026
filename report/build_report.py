#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка отчёта ПР-5 в .docx (ГОСТ 7.32-2017, Times New Roman, 14, 1.5)."""
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

BASE = "/Users/d.d.lyapunov/GolandProjects/devops-course-2026"
SHOT = os.path.join(BASE, "report/screenshots")
OUT = os.path.join(BASE, "report/PR5_SSH_UFW_DNS_Report.docx")

doc = Document()

# --- Page setup A4, GOST margins ---
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin, sec.right_margin = Cm(3.0), Cm(1.0)
sec.top_margin, sec.bottom_margin = Cm(2.0), Cm(2.0)
sec.header_distance, sec.footer_distance = Cm(1.0), Cm(1.25)

# --- Base styles ---
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(14)
style.font.color.rgb = RGBColor(0, 0, 0)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
pf = style.paragraph_format
pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
pf.space_after = Pt(0)
pf.space_before = Pt(0)
pf.first_line_indent = Cm(1.25)
pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

for i in (1, 2, 3):
    hs = doc.styles[f"Heading {i}"]
    hs.font.name = "Times New Roman"
    hs.font.color.rgb = RGBColor(0, 0, 0)
    hs.font.bold = True
    hs.font.size = Pt(14 if i == 1 else 14)
    hs.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    hpf = hs.paragraph_format
    hpf.space_before = Pt(12)
    hpf.space_after = Pt(6)
    hpf.first_line_indent = Cm(0)
    hpf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    hpf.keep_with_next = True

# footer page number
footer = sec.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run()
fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
r._r.append(fld1)
r2 = fp.add_run()
instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
r2._r.append(instr)
r3 = fp.add_run()
fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
r3._r.append(fld2)
for rr in fp.runs:
    rr.font.name = "Times New Roman"; rr.font.size = Pt(12)

fig_no = [0]
def p(text, bold=False, italic=False, align=None, indent=True, size=None, space_after=None):
    par = doc.add_paragraph()
    if align is not None: par.alignment = align
    if not indent: par.paragraph_format.first_line_indent = Cm(0)
    if space_after is not None: par.paragraph_format.space_after = Pt(space_after)
    run = par.add_run(text)
    run.bold = bold; run.italic = italic
    if size: run.font.size = Pt(size)
    return par

def p_mixed(parts, align=None, indent=True):
    """parts: list of (text, {bold, italic})"""
    par = doc.add_paragraph()
    if align is not None: par.alignment = align
    if not indent: par.paragraph_format.first_line_indent = Cm(0)
    for t, fmt in parts:
        r = par.add_run(t)
        r.bold = fmt.get("bold", False); r.italic = fmt.get("italic", False)
    return par

def h1(text):
    return doc.add_heading(text, level=1)

def h2(text):
    return doc.add_heading(text, level=2)

def code_block(lines):
    for ln in lines:
        par = doc.add_paragraph()
        par.paragraph_format.first_line_indent = Cm(0)
        par.paragraph_format.space_after = Pt(0)
        par.paragraph_format.space_before = Pt(0)
        par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        r = par.add_run(ln)
        r.font.name = "Consolas"; r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)
        pPr = par._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "F2F2F2")
        pPr.append(shd)

def table_caption(text):
    cap = doc.add_paragraph()
    cap.paragraph_format.first_line_indent = Cm(0)
    cap.paragraph_format.space_after = Pt(4)
    cap.paragraph_format.space_before = Pt(12)
    r = cap.add_run(text)
    r.font.size = Pt(12)

def table(headers, rows, widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    for j, hh in enumerate(headers):
        c = t.cell(0, j)
        c.text = ""
        par = c.paragraphs[0]
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.first_line_indent = Cm(0)
        r = par.add_run(hh); r.bold = True; r.font.size = Pt(12); r.font.name = "Times New Roman"
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            c = t.cell(i, j)
            c.text = ""
            par = c.paragraphs[0]
            par.paragraph_format.first_line_indent = Cm(0)
            par.paragraph_format.space_after = Pt(2)
            r = par.add_run(val); r.font.size = Pt(12); r.font.name = "Times New Roman"
    # caption spacing
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return t

def fig(path, caption):
    fig_no[0] += 1
    par = doc.add_paragraph()
    par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    par.paragraph_format.first_line_indent = Cm(0)
    run = par.add_run()
    # fit width max 15 cm
    run.add_picture(path, width=Cm(15.0))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.first_line_indent = Cm(0)
    cap.paragraph_format.space_after = Pt(12)
    r = cap.add_run(f"Рисунок {fig_no[0]} – {caption}")
    r.font.size = Pt(12); r.italic = False
    return fig_no[0]

def page_break():
    doc.add_page_break()

# ================= PLACEHOLDER TITLE =================
box = p("МЕСТО ДЛЯ ТИТУЛЬНОГО ЛИСТА", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, size=16)
p("Титульный лист вставляется сюда перед печатью / сдачей. Данный лист-заглушка при оформлении заменяется титульным листом вуза (ИПТИП, кафедра Индустриального программирования, дисциплина «Инструменты девопс», практическая работа № 5, студент Ляпунов Д. Д., группа ЭФБО-04-24, преподаватель Гиматдинов Д. М., 2026/2027). Нумерация страниц начинается со следующего листа.",
  italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=False, size=12)
p("Служебная информация: отчёт подготовлен по методическим указаниям DEV_5.md от 26.09.2026. Репозиторий: devops-course-2026 (scripts/audit.sh, docs/server-setup.md).",
  indent=False, size=12)
page_break()

# ================= СОДЕРЖАНИЕ =================
h1("Содержание")
toc_items = [
    "Введение (цель и задачи работы)",
    "1 Подготовка к занятию: виртуальная машина",
    "2 Задание 1. Учётная запись и ключевая аутентификация",
    "3 Задание 2. Усиление защиты службы SSH",
    "4 Задание 3. Межсетевой экран UFW",
    "5 Задание 4. Локальное доменное имя",
    "6 Факультативное задание. SSH-туннель",
    "7 Самостоятельная работа: audit.sh и server-setup.md",
    "8 Ответы на контрольные вопросы",
    "9 Контроль перед сдачей (таблица 7)",
    "Заключение",
    "Список использованных источников",
    "Приложение А. Ссылка на репозиторий",
]
for it in toc_items:
    q = doc.add_paragraph()
    q.paragraph_format.first_line_indent = Cm(0)
    q.paragraph_format.space_after = Pt(2)
    q.add_run(it).font.size = Pt(13)
page_break()

# ================= ВВЕДЕНИЕ =================
h1("Введение")
p("Целью работы было получить на практике базовые навыки первичной защиты удалённого Linux-сервера: поднять свою виртуальную машину, разобраться с доверием в SSH, закрыть лишнее фаерволом и привязать к серверу локальное имя. Тема кажется простой только на первый взгляд — на деле почти каждое действие здесь может отрезать доступ к машине, поэтому методичка отдельно предупреждает о снимках состояния. Я это прочувствовал уже на этапе hardening SSH.")
p("Для достижения цели делал по шагам: развернуть Ubuntu Server 24.04 в VirtualBox и настроить связность «хост — гость»; разобраться в модели доверия SSH (ключи хоста, known_hosts, authorized_keys); выполнить hardening sshd без потери управления; настроить UFW по принципу «запрещено всё, кроме явно разрешённого»; сопоставить серверу имя devops.local и понять порядок разрешения имён в Linux.")
p("Созданная машина devops-vm в дальнейшем используется в работах № 6 (Nginx), № 7 (Docker), № 11 (Ansible) и № 14 (Prometheus и Grafana), поэтому удалять её после занятия нельзя. Все команды я фиксировал — часть из них потом ляжет в Ansible-плейбук.")
p("Хостовая система: macOS на ARM (MacBook Air), VirtualBox 7.x. Гостевая система: Ubuntu Server 24.04 LTS, 2048 МБ ОЗУ, 2 vCPU, диск 25 ГБ (динамический). Пользователи: student (парольный, установочный) и devops (ключевой, рабочий). Итоговое состояние: SSH только по ключу на порту 2222, root запрещён, UFW активен с правилом LIMIT, имя devops.local разрешается.")

# ================= 1 =================
h1("1 Подготовка к занятию: виртуальная машина")
p("Подготовку я делал заранее, как и требуют указания: одна только установка с загрузкой образа на 2,5 ГБ занимает от получаса. Поставил VirtualBox 7.x, скачал Ubuntu Server 24.04 LTS именно в редакции Server — без графики. Это осознанное условие: на боевом сервере графики тоже нет, и привыкать работать через консоль и SSH нужно сразу.")
h2("1.1 Параметры машины и сети")
table_caption("Таблица 1 – Параметры виртуальной машины devops-vm")
table(["Параметр", "Значение"],
    [["Имя", "devops-vm"],
     ["Тип гостевой ОС", "Linux / Ubuntu (64-bit)"],
     ["Память", "2048 МБ"],
     ["Процессор", "2 ядра"],
     ["Диск", "25 ГБ, динамически расширяемый, Use an entire disk"],
     ["Адаптер 1", "NAT (доступ в Интернет, apt)"],
     ["Адаптер 2", "Host-only (связка с хостом, будущий Nginx)"]])
p("Оба адаптера я подключил до первого запуска. С сетью Host-only пришлось повозиться: её не было в списке, создал вручную через менеджер сетей VirtualBox (подсеть 192.168.56.0/24). Если в списке версий нет 64-битных вариантов — это выключенный VT-x/AMD-V или мешающий Hyper-V, но на моём Mac такой проблемы не возникло.")
h2("1.2 Проброс портов и установка")
p("Для адаптера NAT задал правило ssh: TCP, 127.0.0.1:2222 (хост) → порт 22 (гость). Адрес гостя оставил пустым, как в таблице 3 указаний. Позже, после переноса sshd на 2222, порт гостя поменял на 2222.")
p("При установке выбрал: язык English, тип Ubuntu Server (не minimized), разметка Use an entire disk, имя узла devops-vm, пользователь student, OpenSSH server — обязательно, Featured snaps — ничего. Пароль student записал отдельно — он ещё понадобится для sudo.")
p("После перезагрузки вошёл в консоль ВМ и обновил систему:")
code_block(["sudo apt update && sudo apt upgrade -y", "ip -brief address"])
fig(os.path.join(SHOT, "01_ip_address.png"), "вывод ip -brief address: интерфейсы NAT (10.0.2.15) и Host-only (192.168.56.101), служба SSH запущена")
p("В выводе нас интересуют два адреса: 10.0.2.15 — сегмент NAT, и 192.168.56.101 — сегмент Host-only. Второй я зафиксировал: он будет именем devops.local и адресом веб-сервера в следующей работе.")
h2("1.3 Снимок 01-clean-install")
p("Выключил гостя командой sudo poweroff и сделал снимок 01-clean-install (рисунок 2). Это точка отката: если запру sshd_config или закрою себе доступ фаерволом, восстанавливаюсь сюда, а не переустанавливаю всё заново.")
fig(os.path.join(SHOT, "02_snapshots.png"), "менеджер снимков: три контрольные точки работы")
p("Проверку готовности (таблица 5 указаний) прошёл за пару минут: машина грузится, оба адреса на месте, sshd активен, ssh student@127.0.0.1 -p 2222 подключается, снимок создан.")

# ================= 2 =================
h1("2 Задание 1. Учётная запись и ключевая аутентификация")
p("Идея задания — уйти от общего пользователя student к персональному devops с входом по ключу. Отдельный ключ именно под эту ВМ я сделал осознанно: не хотел тащить сюда ключ от репозиториев из работы № 1 — если уведут ключ с учебного стенда, за ним потянется и доступ к коду.")
h2("2.1 Создание пользователя и сверка отпечатка")
code_block(["ssh student@127.0.0.1 -p 2222", "sudo adduser devops", "sudo usermod -aG sudo devops", "groups devops"])
p("Перед первым подтверждением отпечатка сверил то, что показывает клиент, с реальным ключом хоста — командой sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub в консоли ВМ. На удалённом сервере это вообще единственный способ убедиться, что подключаешься к своему узлу, а не к «человеку посередине». Отпечатки сошлись, подтверждение дал.")
h2("2.2 Ключ и authorized_keys")
code_block(['ssh-keygen -t ed25519 -C "devops-vm-key" -f ~/.ssh/devops_vm',
            "ssh-copy-id -i ~/.ssh/devops_vm.pub -p 2222 devops@127.0.0.1"])
fig(os.path.join(SHOT, "03_stat_ssh.png"), "права 700/600 и вход командой ssh devops без запроса пароля")
p("Проверку делал в лоб: ssh -i ~/.ssh/devops_vm -p 2222 devops@127.0.0.1 — пароля спросить не должно. И сразу stat -c '%a %n' ~/.ssh ~/.ssh/authorized_keys: жду 700 на каталог и 600 на файл. Если права шире, sshd молча отклоняет ключ (в логе — bad ownership or modes), а клиент просто снова просит пароль. У меня с первого раза было 700/600, задержек не возникло.")
h2("2.3 Методы аутентификации и ssh/config")
code_block(['ssh -vvv -i ~/.ssh/devops_vm -p 2222 devops@127.0.0.1 2>&1 | grep -i "authentications that can continue"'])
fig(os.path.join(SHOT, "04_auth_methods.png"), "строка Authentications that can continue до hardening: publickey,password")
p("До усиления защиты сервер предлагает оба метода — publickey,password. После задания 2 здесь останется только publickey, это и будет доказательством отключения паролей. Зафиксировал строку как есть.")
p("Файл ~/.ssh/config на хосте собрал по образцу из указаний (Host devops, HostName 127.0.0.1, Port 2222, User devops, IdentityFile, IdentitiesOnly yes). Директива IdentitiesOnly здесь не для красоты: без неё клиент перебирает все ключи подряд, а при MaxAuthTries 3 легко исчерпать лимит раньше, чем дойдёт до нужного ключа. Проверил командой ssh devops — заходит сразу. После этого сделал снимок 02-keys-configured.")

# ================= 3 =================
h1("3 Задание 2. Усиление защиты службы SSH")
p("Самое ответственное задание. Главное правило, которое я соблюдал буквально: рабочую сессию не закрывать до конца, все проверки — из второго терминала. Иначе одна опечатка в конфиге — и Connection refused без шансов зайти обратно. На учебном стенде это лечится откатом на снимок, в проде — только через консоль провайдера.")
h2("3.1 Конфигурация через drop-in файл")
p("Основной sshd_config я не правил, а создал дополняющий файл /etc/ssh/sshd_config.d/99-hardening.conf — так делают современные дистрибутивы, и Ansible потом работает так же. Перед этим сохранил эталон: sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.")
code_block(["Port 2222", "PermitRootLogin no", "PasswordAuthentication no", "PubkeyAuthentication yes",
            "PermitEmptyPasswords no", "MaxAuthTries 3", "LoginGraceTime 30", "AllowUsers devops",
            "X11Forwarding no", "ClientAliveInterval 300", "ClientAliveCountMax 2"])
p("Нюанс Ubuntu 24.04, на котором я споткнулся: в каталоге уже лежал 50-cloud-init.conf с PasswordAuthentication yes. Файлы читаются по алфавиту, и действует первое встреченное значение — то есть мой 99-й файл парольную аутентификацию не переопределял. Проверяется это командой grep -r \"PasswordAuthentication\" /etc/ssh/sshd_config.d/ /etc/ssh/sshd_config. Конфликтную строку в 50-cloud-init.conf закомментировал, иначе весь hardening был бы фикцией. В отчёте пишу об этом специально — это и есть та самая «фактически допущенная ошибка», которую методичка просит не скрывать.")
h2("3.2 Проверка эффективной конфигурации")
code_block(['sudo sshd -t && echo "Конфигурация корректна"',
            'sudo sshd -T | grep -Ei "^(port|permitrootlogin|passwordauthentication|maxauthtries|allowusers)"'])
fig(os.path.join(SHOT, "05_sshd_T.png"), "вывод sshd -T: действующие значения директив")
p("Важный вывод, который я для себя зафиксировал: верить нужно только sshd -T, а не тексту конфигов. Конфиги могут переопределять друг друга (как в случае с cloud-init), а sshd -T показывает то, с чем реально запустится демон.")
h2("3.3 Сокет-активация и порт прослушивания")
code_block(["sudo systemctl disable --now ssh.socket", "sudo systemctl enable --now ssh.service",
            "sudo systemctl restart ssh", "sudo ss -tlnp | grep sshd  # ожидается 0.0.0.0:2222"])
fig(os.path.join(SHOT, "06_ss_listen.png"), "вывод ss: sshd слушает порт 2222")
p("Если после рестарта в ss всё ещё висит 22 — значит, параметры юнита ssh.socket перебивают директиву Port. Лечится как раз отключением сокета и включением сервиса. У меня после этой последовательности встал 0.0.0.0:2222. Затем поменял в VirtualBox правило проброса: порт гостя 22 → 2222.")
h2("3.4 Негативные проверки и журнал")
code_block(["ssh devops                                             # ожидается успех",
            "ssh -p 2222 root@127.0.0.1                            # ожидается отказ",
            "ssh -p 2222 -o PubkeyAuthentication=no devops@127.0.0.1  # ожидается отказ"])
fig(os.path.join(SHOT, "07_ssh_denied.png"), "две отклонённые попытки подключения")
p("Разница в диагностике такая. Попытка под root отбивается из-за AllowUsers devops и PermitRootLogin no — сервер отвечает Permission denied (publickey), в журнале это invalid user root / Connection closed by invalid user. Попытка с PubkeyAuthentication=no отбивается иначе по смыслу: клиент запретил себе ключ, а пароль сервер больше не принимает — итог тот же Permission denied (publickey), но в журнале — Failed password / Connection closed by authenticating user. То есть внешне сообщения похожи, а причина разная: в первом случае «вам сюда нельзя», во втором — «так сюда нельзя».")
code_block(['sudo journalctl -u ssh --since "10 min ago" --no-pager | grep -Ei "invalid|failed|denied"'])
fig(os.path.join(SHOT, "08_journalctl.png"), "записи системного журнала SSH")
p("После проверок сделал снимок 03-ssh-hardened. Сессию, к слову, так и не закрывал до самого конца задания.")

# ================= 4 =================
h1("4 Задание 3. Межсетевой экран UFW")
p("Принцип настройки — «запрещено всё, что не разрешено явно». Порядок здесь критичен: сначала разрешающее правило для управляющего порта, потом enable. Если сделать наоборот (default deny → enable → allow), соединение рвётся прямо на команде enable, и дальше работаешь уже через консоль ВМ, а не по SSH.")
h2("4.1 Политики и правила")
code_block(["sudo ufw status verbose   # ожидается Status: inactive",
            "sudo ufw default deny incoming", "sudo ufw default allow outgoing",
            "sudo ufw allow 2222/tcp comment 'SSH'", "sudo ufw allow 80/tcp comment 'HTTP'",
            "sudo ufw allow 443/tcp comment 'HTTPS'"])
p("Порты 80 и 443 открываю заделом под работу № 6 (Nginx). А вот команду ufw allow ssh осознанно не использую: имя ssh резолвится через /etc/services в порт 22, и после переезда sshd на 2222 такое правило висит в статусе для красоты, а доступа не даёт. Это классическая ловушка, в которую легко попасть.")
code_block(["sudo ufw enable", "sudo ufw status numbered"])
p("Включил фаервол, не закрывая сессию, и из второго терминала проверил, что ssh devops всё ещё подключается. Подключился — значит, правило для 2222 встало корректно.")
h2("4.2 Rate-limit и логирование")
code_block(["sudo ufw delete allow 2222/tcp", "sudo ufw limit 2222/tcp comment 'SSH rate-limited'",
            "sudo ufw status verbose"])
fig(os.path.join(SHOT, "09_ufw_verbose.png"), "ufw status verbose: политики по умолчанию и правило LIMIT")
p("Действие limit — это тот же allow, но с защитой от перебора: шесть и более соединений за 30 секунд с одного адреса — и источник блокируется. В статусе такое правило помечено словом LIMIT. Для SSH-порта это уместно: сканеры стучатся в 22-й (а теперь и в 2222-й) постоянно.")
code_block(["sudo ufw logging medium",
            "# с хоста: curl -m 3 http://192.168.56.101:8080",
            "sudo grep 'UFW BLOCK' /var/log/ufw.log | tail -5"])
fig(os.path.join(SHOT, "10_ufw_block.png"), "запись UFW BLOCK и разбор её полей")
p("Разбор записи: SRC=192.168.56.1 — адрес моей хостовой машины в сегменте Host-only; DST=192.168.56.101 — адрес сервера; PROTO=TCP — протокол; DPT=8080 — порт назначения, который закрыт, поэтому пакет и отброшен. Поля SPT (исходный порт хоста), IN=enp0s8 (входящий интерфейс) и флаг SYN дополнительно подтверждают, что это была попытка установки TCP-соединения, а не какой-то фоновый шум.")

# ================= 5 =================
h1("5 Задание 4. Локальное доменное имя")
p("Чтобы не держать в голове IP, привязал к серверу имя devops.local. Запись внёс в hosts именно хостовой системы (на macOS — /etc/hosts, на Windows это был бы C:\\Windows\\System32\\drivers\\etc\\hosts):")
code_block(["192.168.56.101 devops.local"])
code_block(["ping devops.local", "ssh -p 2222 devops@devops.local"])
fig(os.path.join(SHOT, "11_devops_local.png"), "подключение по имени devops.local")
p("Имя разрешилось, пинг пошёл на 192.168.56.101, SSH по имени зашёл без пароля. На Windows после правки hosts иногда нужен ipconfig /flushdns, на macOS у меня всё подхватилось сразу.")
code_block(["sudo hostnamectl set-hostname devops-vm",
            "sudo sed -i 's/^127.0.1.1.*/127.0.1.1 devops-vm.devops.local devops-vm/' /etc/hosts",
            "hostname -f"])
fig(os.path.join(SHOT, "12_hostname_audit.png"), "вывод hostname -f и успешный прогон audit.sh")
p("Полное имя узла теперь devops-vm.devops.local — команда hostname -f это подтверждает. Запись 127.0.1.1 в /etc/hosts поправил аккуратно через sed, чтобы не сломать резолвинг самого себя.")

# ================= 6 =================
h1("6 Факультативное задание. SSH-туннель")
p("Задание необязательное, но я его сделал — оно хорошо показывает, чем туннель отличается от открытого порта. Поднял на сервере игрушечный HTTP с привязкой только к loopback:")
code_block(["mkdir -p ~/restricted && cd ~/restricted",
            'echo "<h1>Ресурс доступен только через туннель</h1>" > index.html',
            "python3 -m http.server 8080 --bind 127.0.0.1"])
p("С хоста curl -m 3 http://192.168.56.101:8080 ожидаемо висит и падает по таймауту: служба слушает только 127.0.0.1, а порт 8080 фаерволом не открыт. Затем построил туннель:")
code_block(["ssh -L 9090:127.0.0.1:8080 -N devops"])
fig(os.path.join(SHOT, "14_tunnel.png"), "недоступность службы извне и доступ через localhost:9090")
p("Смысл ключа -L такой: слушать порт 9090 на хосте и всё, что туда приходит, переправлять на 127.0.0.1:8080 уже в адресном пространстве сервера. Адрес 127.0.0.1 здесь интерпретируется сервером, а не хостом — это ключевой момент. Ключ -N просто не запускает shell, нужен только проброс.")
p("Почему фаервол не мешает? Потому что извне на порт 8080 никто не стучится. Весь трафик идёт внутри уже установленного SSH-соединения на порт 2222, который разрешён и rate-limited. Для UFW это обычный разрешённый SSH-трафик, а что внутри него едет HTTP — фаервол не видит. Фактически данные передавались через порт 2222.")

# ================= 7 =================
h1("7 Самостоятельная работа: audit.sh и server-setup.md")
h2("7.1 Теоретическая подготовка (кратко)")
p("К работе № 6 повторил три темы по документации Ubuntu Server и паре статей с Хабра. Nginx — легковесный веб-сервер и обратный прокси: отдаёт статику, балансирует, терминирует TLS; база — server-блоки в sites-available. С прокси разница такая: прямой (forward) стоит возле клиента и ходит в Интернет за него — пример корпоративный фильтр; обратный (reverse) стоит перед серверами и принимает запросы за них — пример Nginx перед приложением. Про TLS главное: сервер предъявляет сертификат, клиент проверяет цепочку до доверенного УЦ и имя хоста. У самоподписанного цепочки нет, поэтому браузер и предупреждает — отличить его от подделки он не может.")
h2("7.2 Скрипт scripts/audit.sh")
p("Скрипт дополнил по трём TODO. Первая проверка — порт sshd отличен от 22 (беру из sshd -T, сравниваю «не равно»). Вторая — MaxAuthTries равен 3. Третья — политика входящего по умолчанию deny (парсю sudo ufw status verbose | grep Default). Остальные проверки оставил как в шаблоне. Скрипт возвращает 0, только если все проверки прошли, — иначе 1, это потом используется для остановки CI-конвейера в работе № 10.")
p("Проверял двумя прогонами. На корректной конфигурации — все шесть проверок зелёные, код 0 (рисунок 12). Затем временно поставил MaxAuthTries 10 и перезапустил sshd — скрипт честно упал с FAIL по этой проверке и кодом 1 (рисунок 14). После вернул 3 обратно и перезапустил службу.")
fig(os.path.join(SHOT, "13_audit_fail.png"), "прогон аудита на намеренно нарушенной конфигурации (exit 1)")
h2("7.3 Документ docs/server-setup.md")
p("Документ заполнил по семи разделам из указаний: параметры машины, интерфейсы, проброс портов, пользователи, SSH, UFW, снимки. Главный критерий — по нему можно за 10 минут восстановить всё после отката на 01-clean-install. Поэтому туда вынесены не только значения, но и готовые команды по шагам, включая ловушки с cloud-init и ssh.socket. Лежит в docs/server-setup.md, скрипт — в scripts/audit.sh, оба закоммичены по Conventional Commits.")

# ================= 8 =================
h1("8 Ответы на контрольные вопросы")
qs = [
 ("1. NAT и Host-only.",
  "При NAT гость сидит за транслятором гипервизора в сети 10.0.2.0/24. У него нет адреса, видимого снаружи, исходящие соединения NATит гипервизор, а входящие возможны только через явно заданный проброс портов. Поэтому без проброса зайти извне нельзя. При Host-only гипервизор создаёт общий изолированный сегмент (у нас 192.168.56.0/24), где и хост, и гости имеют адреса из одной сети и видят друг друга напрямую — входящие соединения возможны без проброса, но Интернета в этом сегменте нет. Потому в работе и используются оба адаптера."),
 ("2. known_hosts и authorized_keys.",
  "Файл ~/.ssh/known_hosts лежит на клиенте (хостовой системе) и хранит отпечатки ключей серверов, к которым уже подключались, — защита от MITM: при смене ключа клиент бьёт тревогу. Файл ~/.ssh/authorized_keys лежит на сервере в домашнем каталоге того пользователя, под которым заходят, и содержит открытые ключи, которым разрешён вход. Перепутать их — частая ошибка: первый отвечает на вопрос «тот ли это сервер?», второй — «этому ли ключу можно войти?»."),
 ("3. Почему ключ лучше пароля, если канал и так шифрован.",
  "Шифрование канала защищает от перехвата, но не от подбора и утечек. Пароль сервер должен проверить, а значит, его можно перебирать (словари, брутфорс), он может утечь из баз, его вводят с клавиатуры. При ключевой аутентификации закрытый ключ вообще не покидает клиент: клиент лишь доказывает владение им криптографически (подписывает вызов сервера). Подобрать ed25519-ключ перебором нереально, фишингом его не выманить, а скомпрометированный ключ отзывается удалением одной строки из authorized_keys."),
 ("4. ufw allow и ufw limit.",
  "allow просто разрешает трафик, подпадающий под правило. limit разрешает тоже, но включает защиту от флуда: если источник открывает шесть и более соединений за 30 секунд, он временно блокируется. В статусе такое правило помечено LIMIT. Для SSH использую limit, для веба (80/443) достаточно allow."),
 ("5. Закрыл сессию после правок — Connection refused.",
  "Нарушена процедура, а не обязательно конфигурация: проверять новую конфигурацию нужно новым соединением, не закрывая старое. Тогда при ошибке остаётся рабочая сессия для отката. Исключили бы исход две команды: sudo sshd -t (синтаксический контроль до рестарта) и проверочное подключение из второго терминала (ssh devops) до закрытия текущей сессии. Дополнительно — sudo sshd -T для сверки эффективных значений."),
 ("6. deny → enable → allow: что будет.",
  "Результат — самоблокировка: разрыв SSH-соединения наступает на команде ufw enable, потому что политика deny incoming уже активна, а разрешающего правила для управляющего порта ещё нет. Все последующие команды по этому же SSH выполнить уже нельзя. Правильный порядок: ufw default deny incoming → ufw default allow outgoing → ufw allow 2222/tcp (и остальные) → ufw enable."),
 ("7. ufw allow ssh после смены порта.",
  "Утилита берёт номер порта из файла /etc/services, а не из sshd_config. Там имени ssh соответствует порт 22, поэтому правило откроет 22-й, а sshd уже слушает 2222-й. В ufw status правило будет красоваться, а соединения не будет. Лечится указанием номера явно: ufw allow 2222/tcp."),
 ("8. Смена порта — security through obscurity?",
  "Тезис наполовину верен. Сканирование действительно находит реальный порт за минуты, так что от целенаправленной атаки смена порта не защищает — эту задачу она не решает. А решает она другую, вполне практическую: срезает вал автоматического сканирования и перебора по 22-му порту, который идёт непрерывно. Меньше шума в логах, меньше нагрузка и меньше шансов, что слабый пароль подберёт очередной бот. Как единственный барьер — бесполезна, как гигиена вместе с ключами и fail2ban/limit — полезна."),
 ("9. REMOTE HOST IDENTIFICATION HAS CHANGED.",
  "Три причины: сервер переустановлен и сгенерировал новые ключи хоста (штатно); сервер тот же, но зашли по другому адресу/через NAT, и сопоставление в known_hosts не совпало; атака MITM — кто-то подставил свой ключ. Разграничение — только через независимый канал: сверить отпечаток с sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub на сервере (консоль ВМ, консоль провайдера), уточнить у команды, не пересоздавали ли узел. Безусловный ssh-keygen -R плох тем, что стирает и след атаки тоже: вместо проверки просто «затыкает предупреждение», и при реальном MITM пользователь добровольно отдаётся в руки атакующему."),
 ("10. Клиент ругается на права закрытого ключа.",
  "Клиент проверяет, что ключ доступен только владельцу (обычно 600), потому что файл лежит в многопользовательской системе. Если права шире (например, 644), ключ может прочитать другой пользователь этой же машины, скопировать себе и входить от вашего имени — при этом ни сеть, ни сервер этого не заметят. Это защита от локального класса угроз: любопытный сосед по хосту, скомпрометированный соседний аккаунт, бэкапы с чужими правами. Поэтому SSH проще отказаться от «незащищённого» ключа, чем рисковать."),
 ("11. ping myapp.local работает, а dig — пусто.",
  "Противоречия нет: ping и dig ходят разными путями. Порядок по /etc/nsswitch.conf (директива hosts:): сначала /etc/hosts (статика, без TTL и кэша), затем systemd-resolved (127.0.0.53, кэш), затем внешние DNS. ping идёт через весь этот порядок (NSS) и находит запись в /etc/hosts. dig обращается напрямую к DNS-серверу, минуя /etc/hosts и NSS, и про локальное имя ничего не знает — потому и пусто. Полный порядок: /etc/hosts → systemd-resolved → вышестоящие DNS (DHCP/статика), с учётом TTL на DNS-ответы."),
 ("12. ssh -L 9090:127.0.0.1:8080.",
  "Адрес 127.0.0.1 интерпретируется в адресном пространстве сервера: это его собственная петля. Поэтому служба, слушающая только loopback, для туннеля доступна. Фаервол не мешает, потому что на порт 8080 снаружи никто не подключается — весь трафик идёт внутри SSH-соединения на порт 2222, который разрешён. UFW видит легитимный SSH, а не внутренний HTTP."),
 ("13. sudo пишет кто и что, но есть sudo su -.",
  "Логирования команды после sudo su - уже нет детализации: в журнале останется сам факт перехода в root, а дальнейшие команды исполняются от root без привязки к человеку — расследовать, кто именно что сломал, нельзя. Лечится комплексно: запретить неограниченный su/shell (в sudoers только конкретные команды), писать расширенный аудит (auditd, snoopy, sudosh / запись сессий), централизованно хранить логи (чтобы root не мог их затереть), по возможности — персональные учётки без общего root."),
 ("14. Три недостатка ручной настройки (не видны на одном узле).",
  "Первое — невоспроизводимость и дрейф: руками два одинаковых сервера не собрать, опечатки и пропущенные шаги накапливаются. Второе — отсутствие истории и ревью: нет диффа, непонятно, что и зачем менялось. Третье — масштаб и скорость: на десятках узлов руками это часы и ошибки, а плейбуком — минуты и идемпотентность. Плюс из ручной настройки трудно сделать откат и тесты (тот же audit.sh в CI)."),
]
for title, body in qs:
    h2(title)
    p(body)

# ================= 9 =================
h1("9 Контроль перед сдачей (таблица 7)")
p("Итоговую сверку по таблице 7 методических указаний свёл в таблицу 2: каждая строка подтверждается скриншотом или командой из текста выше.")
table_caption("Таблица 2 – Контроль выполнения условий перед сдачей отчёта")
table(["№", "Условие", "Подтверждение"],
    [["1", "Вход по ключу без пароля", "ssh devops — без запроса пароля (рисунок 3)"],
     ["2", "Вход root запрещён", "sshd -T | grep permitrootlogin → no (рисунок 5)"],
     ["3", "Парольная аутентификация отключена", "sshd -T | grep passwordauth → no (рисунок 5)"],
     ["4", "SSH на нестандартном порту", "ss -tlnp | grep sshd → 0.0.0.0:2222 (рисунок 6)"],
     ["5", "UFW активен, deny, LIMIT", "ufw status verbose (рисунок 9)"],
     ["6", "devops.local разрешается", "ssh -p 2222 devops@devops.local (рисунок 11)"],
     ["7", "Три снимка ВМ", "менеджер снимков (рисунок 2)"],
     ["8", "Скрипт и документация в репозитории", "scripts/audit.sh, docs/server-setup.md (приложение А)"]])
p("Все восемь условий выполнены. Скрипт audit.sh на финальной конфигурации завершается с кодом 0, на намеренно нарушенной (MaxAuthTries 10) — с кодом 1, то есть пригоден для автоматизации.")

# ================= Заключение =================
h1("Заключение")
p("Главное для меня: машина не просто поднялась, а пережила hardening без потери доступа — SSH только по ключу на порту 2222, без root и паролей, с лимитами и таймаутами. Фаервол работает по deny-by-default с rate-limit, имя devops.local резолвится, скрипт и документация лежат в репозитории. Три снимка состояния созданы и проверены.")
p("Из затруднений отмечу три. Первое — конфликт PasswordAuthentication с 50-cloud-init.conf: мой 99-й файл его не переопределял, и без grep по каталогу я бы сдал конфигурацию с фактически включёнными паролями. Второе — ssh.socket против sshd_config: пока не отключил сокет-активацию, порт не менялся. Третье — чуть не включил UFW до разрешающего правила на тестовом прогоне в голове; спасло правило «сначала allow, потом enable» и второй терминал. Все три эпизода разобраны в тексте выше — считаю их полезной частью результата, а не браком.")
p("Для следующих работ важно, что машина и документ восстановления готовы: по server-setup.md конфигурация поднимается из 01-clean-install за десять минут, а audit.sh даёт быстрый ответ, всё ли на месте.")

# ================= Источники =================
h1("Список использованных источников")
srcs = [
 "Oracle VM VirtualBox. User Manual. Chapter 6. Virtual Networking [Электронный ресурс]. URL: https://www.virtualbox.org/manual/ch06.html (дата обращения: 14.09.2026).",
 "Ubuntu Server Documentation [Электронный ресурс]. URL: https://documentation.ubuntu.com/server (дата обращения: 14.09.2026).",
 "OpenSSH. sshd_config: руководство по конфигурационному файлу [Электронный ресурс]. URL: https://man.openbsd.org/sshd_config (дата обращения: 14.09.2026).",
 "Firewalls. Ubuntu Server Documentation [Электронный ресурс]. URL: https://documentation.ubuntu.com/server/how-to/security/firewalls (дата обращения: 14.09.2026).",
 "Get Ubuntu Server [Электронный ресурс]. URL: https://ubuntu.com/download/server (дата обращения: 14.09.2026).",
 "systemd-resolved.service: системный резолвер имён [Электронный ресурс]. URL: https://www.freedesktop.org/software/systemd/man/systemd-resolved.html (дата обращения: 14.09.2026).",
 "Как работает DNS [Электронный ресурс] // Хабр. URL: https://habr.com/ru/companies/ruvds/articles/583148 (дата обращения: 14.09.2026).",
 "Туннелирование средствами SSH [Электронный ресурс] // Хабр. URL: https://habr.com/ru/companies/first/articles/568020 (дата обращения: 14.09.2026).",
 "SSH Essentials: Working with SSH Servers, Clients, and Keys [Электронный ресурс] // DigitalOcean. URL: https://www.digitalocean.com/community/tutorials/ssh-essentials-working-with-ssh-servers-clients-and-keys (дата обращения: 14.09.2026).",
]
for i, s in enumerate(srcs, 1):
    par = doc.add_paragraph()
    par.paragraph_format.first_line_indent = Cm(0)
    par.paragraph_format.left_indent = Cm(0)
    r = par.add_run(f"{i}. {s}")
    r.font.size = Pt(12)

h1("Приложение А. Ссылка на репозиторий")
p("Репозиторий: devops-course-2026 — https://github.com/ddlyapunov/devops-course-2026. Файлы работы № 5: scripts/audit.sh (скрипт контроля с тремя реализованными проверками), docs/server-setup.md (восстановление за 10 минут), report/PR5_SSH_UFW_DNS_Report.docx (данный отчёт), report/screenshots/ (копии экрана). Коммиты оформлены по Conventional Commits.", indent=False)
code_block(["git log --oneline", "feat: add PR5 SSH hardening audit script and server docs"])

doc.save(OUT)
print(f"saved {OUT}")

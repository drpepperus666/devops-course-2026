#!/usr/bin/env bash
set -uo pipefail
PASS=0; FAIL=0
check() {
 local desc="$1" expected="$2" actual="$3"
 if [[ "$actual" == "$expected" ]]; then
 echo " [OK] $desc"; ((PASS++))
 else
 echo " [FAIL] $desc (ожидалось: '$expected', получено: '$actual')";
((FAIL++))
 fi
}
echo "Аудит конфигурации: $(hostname -f), $(date '+%Y-%m-%d %H:%M')"
echo "[1] Служба SSH"
check "Вход от имени root запрещён" "no" "$(sudo sshd -T 2>/dev/null | awk '/^permitrootlogin/{print $2}')"
check "Парольная аутентификация отключена" "no" "$(sudo sshd -T 2>/dev/null | awk '/^passwordauthentication/{print $2}')"
# TODO 1: проверить, что значение параметра port отлично от 22
ssh_port="$(sudo sshd -T 2>/dev/null | awk '/^port/{print $2}')"
if [[ -n "$ssh_port" && "$ssh_port" != "22" ]]; then
 echo " [OK] Нестандартный порт SSH (port=$ssh_port)"; ((PASS++))
else
 echo " [FAIL] Нестандартный порт SSH (ожидалось: отлично от '22', получено: '$ssh_port')"; ((FAIL++))
fi
# TODO 2: проверить, что значение параметра maxauthtries равно 3
check "MaxAuthTries равен 3" "3" "$(sudo sshd -T 2>/dev/null | awk '/^maxauthtries/{print $2}')"
echo "[2] Межсетевой экран"
check "Межсетевой экран активен" "active" "$(sudo ufw status 2>/dev/null | awk '/^Status:/{print $2}')"
# TODO 3: проверить, что политика по умолчанию для входящего трафика равна deny
# источник данных: sudo ufw status verbose | grep Default
# Пример строки: "Default: deny (incoming), allow (outgoing), disabled (routed)"
default_line="$(sudo ufw status verbose 2>/dev/null | grep -i '^Default')"
incoming_policy="$(echo "$default_line" | sed -n 's/.*: *\([A-Za-z]*\) *(incoming).*/\1/p' | tr '[:upper:]' '[:lower:]')"
check "Политика по умолчанию для входящего трафика — deny" "deny" "$incoming_policy"
echo "[3] Учётные записи"
awk -F: '$3>=1000 && $3<65534 {printf " %s (uid=%s)\n",$1,$3}' /etc/passwd
echo "Пройдено: $PASS, не пройдено: $FAIL"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1

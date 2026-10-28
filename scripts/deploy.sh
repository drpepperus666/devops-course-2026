#!/usr/bin/env bash
# Доставка статического ресурса на devops-vm
# Использование: scripts/deploy.sh [--dry-run]
set -euo pipefail

REMOTE="devops"                # псевдоним из ~/.ssh/config (ПР № 5, шаг 1.6)
REMOTE_DIR="/var/www/devops-site"
SITE_URL="https://devops.local"
SITE_RESOLVE="--resolve devops.local:443:127.0.0.1"   # на macOS-хосте без записи /etc/hosts: явный адрес
CA_CERT="${HOME}/devops.crt"
LOCAL_DIR="$(git rev-parse --show-toplevel)/site/"
RSYNC="/opt/homebrew/bin/rsync"   # системный rsync macOS (openrsync) не поддерживает --chmod

# 1. Разбор аргумента --dry-run
DRY_RUN=""
if [[ "${1:-}" == "--dry-run" ]]; then
    DRY_RUN="--dry-run"
elif [[ -n "${1:-}" ]]; then
    echo "Ошибка: неизвестный аргумент '$1'" >&2
    exit 1
fi

# 2. Проверки по требованиям 4 и 5
if [[ ! -f "${LOCAL_DIR}index.html" ]]; then
    echo "Ошибка: файл ${LOCAL_DIR}index.html не найден, доставка отменена" >&2
    exit 1
fi
if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
    echo "Ошибка: в репозитории есть незафиксированные изменения, доставка отменена" >&2
    exit 1
fi

# 3. Синхронизация каталога site/ на сервер (одна команда = одно SSH-соединение,
#    приводим права к модели «владелец пишет, веб-сервер читает»)
rsync_flags=(-avz --delete --chmod=D755,F644 -e "ssh -o BatchMode=yes -o ConnectTimeout=5")
if ! "$RSYNC" "${rsync_flags[@]}" ${DRY_RUN:+"${DRY_RUN}"} "${LOCAL_DIR}" "${REMOTE}:${REMOTE_DIR}/"; then
    echo "Ошибка: rsync завершился с ошибкой (ключ непригоден или сервер недоступен)" >&2
    exit 1
fi

# 4. При --dry-run — завершение без проверки доступности
if [[ -n "$DRY_RUN" ]]; then
    echo "--dry-run: состояние сервера не изменялось"
    exit 0
fi

# 5. Проверка доступности ресурса с проверкой сертификата
COMMIT="$(git rev-parse --short HEAD)"
if curl -f --cacert "${CA_CERT}" -s -o /dev/null ${SITE_RESOLVE} "${SITE_URL}"; then
    echo "Деплой успешен: доставлен коммит ${COMMIT}"
    exit 0
else
    echo "Ошибка: ресурс ${SITE_URL} недоступен после доставки" >&2
    exit 1
fi

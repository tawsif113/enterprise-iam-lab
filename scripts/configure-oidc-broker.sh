#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
COMPOSE_FILE="${ROOT_DIR}/infrastructure/docker-compose.yml"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}. Copy .env.example to .env first."
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

compose() {
  docker compose --env-file "${ENV_FILE}" -f "${COMPOSE_FILE}" "$@"
}

echo "Starting main and external Keycloak..."
compose up -d keycloak external-keycloak

echo "Waiting for main Keycloak admin API..."
READY=false
for _ in $(seq 1 45); do
  if compose exec -T keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user "${KEYCLOAK_ADMIN}" --password "${KEYCLOAK_ADMIN_PASSWORD}" >/dev/null 2>&1; then
    READY=true
    break
  fi
  sleep 2
done

if [[ "${READY}" != "true" ]]; then
  echo "Main Keycloak did not become ready in time."
  exit 1
fi

compose exec -T keycloak /opt/keycloak/bin/kcadm.sh get realms/enterprise-lab >/dev/null

if compose exec -T keycloak /opt/keycloak/bin/kcadm.sh get identity-provider/instances/corporate-oidc -r enterprise-lab >/dev/null 2>&1; then
  echo "Updating existing corporate-oidc identity provider..."
  compose exec -T keycloak /opt/keycloak/bin/kcadm.sh update identity-provider/instances/corporate-oidc -r enterprise-lab -f /opt/keycloak/data/import/corporate-oidc-provider.json
else
  echo "Creating corporate-oidc identity provider..."
  compose exec -T keycloak /opt/keycloak/bin/kcadm.sh create identity-provider/instances -r enterprise-lab -f /opt/keycloak/data/import/corporate-oidc-provider.json
fi

MAPPERS="$(compose exec -T keycloak /opt/keycloak/bin/kcadm.sh get identity-provider/instances/corporate-oidc/mappers -r enterprise-lab 2>/dev/null || true)"
if grep -q "corporate-users-are-employees" <<<"${MAPPERS}"; then
  echo "Employee role mapper already exists."
else
  echo "Creating employee role mapper..."
  compose exec -T keycloak /opt/keycloak/bin/kcadm.sh create identity-provider/instances/corporate-oidc/mappers -r enterprise-lab -f /opt/keycloak/data/import/corporate-oidc-employee-mapper.json
fi

echo
echo "OIDC broker configured."
echo "Main Keycloak:   http://localhost:8080"
echo "Corporate IdP:   http://localhost:8180"
echo "Employee Portal: http://localhost:9001"
echo "Demo user:       external-alice"

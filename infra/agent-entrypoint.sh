#!/bin/bash
set -e

# Registrar el agente con el manager
sed -i "s/MANAGER_IP/${WAZUH_MANAGER}/" /var/ossec/etc/ossec.conf 2>/dev/null || true

/var/ossec/bin/agent-auth -m "${WAZUH_MANAGER}" -A "${WAZUH_AGENT_NAME}" 2>/dev/null || true

# Arrancar el agente Wazuh y el daemon SSH
/var/ossec/bin/wazuh-control start
exec /usr/sbin/sshd -D

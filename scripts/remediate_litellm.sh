#!/usr/bin/env bash
# =============================================================================
# Co-Op Platform — LiteLLM Supply Chain Remediation Script
# CVE-2026-33634 | March 24, 2026
#
# Usage:
#   chmod +x scripts/remediate_litellm.sh
#   ./scripts/remediate_litellm.sh
#
# What this script does:
#   1. Checks if a compromised LiteLLM version is installed
#   2. Searches for the malicious .pth file
#   3. Checks for persistence backdoors
#   4. Removes compromised packages and purges caches
#   5. Reinstalls the last known-clean version (1.82.6)
#   6. Verifies the clean install
#   7. Outputs a summary of secrets you need to rotate
#
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

COMPROMISED_VERSIONS=("1.82.7" "1.82.8")
SAFE_VERSION="1.82.6"
MALICIOUS_PTH="litellm_init.pth"
BACKDOOR_SCRIPT="$HOME/.config/sysmon/sysmon.py"
BACKDOOR_SERVICE="$HOME/.config/systemd/user/sysmon.service"
EXFIL_DOMAIN="models.litellm.cloud"

COMPROMISED=false

print_header() {
  echo ""
  echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
  echo -e "${BLUE}  $1${NC}"
  echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
}

print_ok()   { echo -e "  ${GREEN}✅ $1${NC}"; }
print_warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }
print_err()  { echo -e "  ${RED}🚨 $1${NC}"; }
print_info() { echo -e "  ${BLUE}ℹ️  $1${NC}"; }

# ─────────────────────────────────────────────────────────────────────────────
print_header "STEP 1 — Check installed LiteLLM version"
# ─────────────────────────────────────────────────────────────────────────────

if command -v pip &>/dev/null; then
  INSTALLED_VERSION=$(pip show litellm 2>/dev/null | grep "^Version:" | awk '{print $2}' || echo "not_installed")
elif command -v uv &>/dev/null; then
  INSTALLED_VERSION=$(uv pip show litellm 2>/dev/null | grep "^Version:" | awk '{print $2}' || echo "not_installed")
else
  INSTALLED_VERSION="not_installed"
fi

echo "  Installed version: $INSTALLED_VERSION"

for V in "${COMPROMISED_VERSIONS[@]}"; do
  if [[ "$INSTALLED_VERSION" == "$V" ]]; then
    print_err "COMPROMISED VERSION DETECTED: litellm==$V"
    print_err "Your machine may have had credentials exfiltrated."
    COMPROMISED=true
    break
  fi
done

if [[ "$COMPROMISED" == "false" && "$INSTALLED_VERSION" != "not_installed" ]]; then
  print_ok "Version $INSTALLED_VERSION is not in the compromised list."
fi

# ─────────────────────────────────────────────────────────────────────────────
print_header "STEP 2 — Search for malicious .pth file"
# ─────────────────────────────────────────────────────────────────────────────

PTH_FOUND=()

while IFS= read -r -d '' f; do
  PTH_FOUND+=("$f")
done < <(find \
  "$HOME/.cache/uv" \
  "$HOME/.local/lib" \
  /usr/local/lib \
  ./venv \
  ./.venv \
  2>/dev/null \
  -name "$MALICIOUS_PTH" -print0 || true)

if [[ ${#PTH_FOUND[@]} -gt 0 ]]; then
  print_err "Malicious .pth file found in ${#PTH_FOUND[@]} location(s):"
  for f in "${PTH_FOUND[@]}"; do
    echo "    → $f"
  done
  COMPROMISED=true
else
  print_ok "No $MALICIOUS_PTH found in scanned directories."
fi

# ─────────────────────────────────────────────────────────────────────────────
print_header "STEP 3 — Check for persistence / backdoors"
# ─────────────────────────────────────────────────────────────────────────────

if [[ -f "$BACKDOOR_SCRIPT" ]]; then
  print_err "Backdoor script found: $BACKDOOR_SCRIPT"
  print_err "Removing it now..."
  rm -f "$BACKDOOR_SCRIPT"
  rmdir --ignore-fail-on-non-empty "$(dirname "$BACKDOOR_SCRIPT")" 2>/dev/null || true
  print_warn "Removed. Check the file contents manually if you need forensic evidence first."
  COMPROMISED=true
else
  print_ok "No backdoor script at $BACKDOOR_SCRIPT"
fi

if [[ -f "$BACKDOOR_SERVICE" ]]; then
  print_err "Backdoor systemd service found: $BACKDOOR_SERVICE"
  print_err "Stopping and removing..."
  systemctl --user stop sysmon.service 2>/dev/null || true
  systemctl --user disable sysmon.service 2>/dev/null || true
  rm -f "$BACKDOOR_SERVICE"
  systemctl --user daemon-reload 2>/dev/null || true
  COMPROMISED=true
else
  print_ok "No backdoor systemd service at $BACKDOOR_SERVICE"
fi

# Check for active outbound connections to the exfiltration domain
if command -v ss &>/dev/null; then
  if ss -tnp 2>/dev/null | grep -q "$EXFIL_DOMAIN"; then
    print_err "Active connection to $EXFIL_DOMAIN detected! Kill it immediately."
  fi
fi

# Kubernetes check
if command -v kubectl &>/dev/null; then
  print_info "Kubernetes detected — checking kube-system for suspicious pods..."
  SUSPICIOUS_PODS=$(kubectl get pods -n kube-system --no-headers 2>/dev/null | grep "node-setup-" || true)
  if [[ -n "$SUSPICIOUS_PODS" ]]; then
    print_err "Suspicious pods found in kube-system:"
    echo "$SUSPICIOUS_PODS"
    print_warn "Delete them with: kubectl delete pod -n kube-system <pod-name>"
  else
    print_ok "No suspicious node-setup-* pods found in kube-system."
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
print_header "STEP 4 — Remove compromised package and purge caches"
# ─────────────────────────────────────────────────────────────────────────────

UNINSTALLED=false

for V in "${COMPROMISED_VERSIONS[@]}"; do
  if [[ "$INSTALLED_VERSION" == "$V" ]]; then
    print_info "Uninstalling litellm==$V..."

    if command -v pip &>/dev/null; then
      pip uninstall litellm -y 2>/dev/null && print_ok "pip uninstall done."
      pip cache purge 2>/dev/null && print_ok "pip cache purged."
    fi

    if command -v uv &>/dev/null; then
      uv pip uninstall litellm 2>/dev/null && print_ok "uv uninstall done."
    fi

    if [[ -d "$HOME/.cache/uv" ]]; then
      rm -rf "$HOME/.cache/uv"
      print_ok "uv cache at ~/.cache/uv removed."
    fi

    UNINSTALLED=true
    break
  fi
done

if [[ "$UNINSTALLED" == "false" ]]; then
  print_info "LiteLLM was not a compromised version; skipping uninstall."
  # Still purge uv cache to be safe if .pth file was found
  if [[ ${#PTH_FOUND[@]} -gt 0 ]]; then
    print_warn "Malicious .pth was found in cache — purging uv cache anyway."
    rm -rf "$HOME/.cache/uv" 2>/dev/null || true
    print_ok "uv cache purged."
  fi
fi

# ─────────────────────────────────────────────────────────────────────────────
print_header "STEP 5 — Reinstall safe version (1.82.6)"
# ─────────────────────────────────────────────────────────────────────────────

if [[ "$UNINSTALLED" == "true" ]]; then
  print_info "Installing litellm==$SAFE_VERSION..."

  if command -v uv &>/dev/null; then
    uv pip install "litellm==$SAFE_VERSION"
  else
    pip install "litellm==$SAFE_VERSION"
  fi

  print_ok "litellm==$SAFE_VERSION installed."
fi

# ─────────────────────────────────────────────────────────────────────────────
print_header "STEP 6 — Verify clean install"
# ─────────────────────────────────────────────────────────────────────────────

FINAL_VERSION=$(pip show litellm 2>/dev/null | grep "^Version:" | awk '{print $2}' || echo "not_installed")
echo "  Current litellm version: $FINAL_VERSION"

# Confirm no .pth file in newly installed package
SITE_PACKAGES=$(python3 -c "import site; print(site.getsitepackages()[0])" 2>/dev/null || echo "")
if [[ -n "$SITE_PACKAGES" ]]; then
  if find "$SITE_PACKAGES" -name "$MALICIOUS_PTH" 2>/dev/null | grep -q .; then
    print_err "Malicious .pth file STILL present in site-packages! Manual intervention required."
    exit 1
  else
    print_ok "No $MALICIOUS_PTH in site-packages. Install is clean."
  fi
fi

for V in "${COMPROMISED_VERSIONS[@]}"; do
  if [[ "$FINAL_VERSION" == "$V" ]]; then
    print_err "Still on compromised version $V after remediation! Aborting."
    exit 1
  fi
done

print_ok "Version check passed."

# ─────────────────────────────────────────────────────────────────────────────
print_header "STEP 7 — Summary & Credential Rotation Checklist"
# ─────────────────────────────────────────────────────────────────────────────

if [[ "$COMPROMISED" == "true" ]]; then
  echo ""
  print_err "YOUR MACHINE WAS LIKELY COMPROMISED."
  echo ""
  echo -e "  ${RED}You MUST rotate the following credentials immediately:${NC}"
  echo ""
  echo "  [ ] SSH keys            → ssh-keygen -t ed25519; revoke old public keys"
  echo "  [ ] OpenAI API key      → platform.openai.com → API Keys"
  echo "  [ ] Anthropic API key   → console.anthropic.com → API Keys"
  echo "  [ ] AWS access keys     → IAM → Security credentials"
  echo "  [ ] GCP credentials     → gcloud auth revoke; create new service account key"
  echo "  [ ] Database passwords  → ALTER ROLE in PostgreSQL"
  echo "  [ ] Redis password      → Update requirepass + all .env files"
  echo "  [ ] Kubernetes secrets  → kubectl delete secret / recreate"
  echo "  [ ] MinIO credentials   → MinIO console → Service Accounts"
  echo "  [ ] Telegram bot token  → @BotFather → /revoke"
  echo "  [ ] Any .env API keys   → Rotate all providers present in .env"
  echo ""
  print_warn "After rotating, update your .env file and restart all services:"
  echo "  docker compose down && docker compose up -d"
else
  echo ""
  print_ok "No compromise indicators found on this machine."
  print_info "Recommended: still run 'pip-audit' and 'pnpm audit' as a precaution."
fi

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Remediation script complete.${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

#!/usr/bin/env python3
"""Build a kubeconfig for an EdgeFlow/CloudFlow appliance from the tenant's
Rancher credential, so reaching an appliance needs no pre-existing local file.

usage: appliance-kubeconfig.py <tenant_id> <gateway_id> [--out PATH]
                               [--kubectl PATH] [--no-verify] [--print-path]

The tenant record carries `edgeflow_rancher_user_token` and
`edgeflow_rancher_endpoint`. Rancher proxies the appliance's Kubernetes API at
https://<rancher>/k8s/clusters/<cluster_id>, and the token is the bearer
credential for it - so a kubeconfig is just those two values in a template.
There is no need to call generateKubeconfig.

Clusters are named ef-<tenant_id>-<gateway_id>, which is how a gateway id is
resolved to a cluster id.

By default this verifies that the credential can actually exec into a pod.
Reading pods and streaming logs is a *different* Kubernetes permission from
`create` on `pods/exec`, and a Rancher read-only project role grants the first
while denying the second. Checking up front turns a confusing Forbidden in the
middle of a long sampling run into a clear message before it starts.

The written file contains a live credential. It is created 0600, and you should
delete it when finished. Never commit it.
"""

import argparse
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

KUBECONFIG_TEMPLATE = """apiVersion: v1
kind: Config
clusters:
- name: "{name}"
  cluster:
    server: "{server}"
users:
- name: "{name}"
  user:
    token: "{token}"
contexts:
- name: "{name}"
  context:
    user: "{name}"
    cluster: "{name}"
current-context: "{name}"
"""


def tenant_record(tenant):
    """Read the tenant record via the cogniac CLI."""
    p = subprocess.run(["cogniac", "--tenant", tenant, "tenant", "get"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"cogniac tenant get failed: {p.stderr.strip()[:200]}")
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        sys.exit(f"unexpected output from cogniac: {p.stdout[:200]}")


def rancher_get(base, token, path):
    r = urllib.request.Request(base + path)
    r.add_header("Authorization", "Bearer " + token)
    r.add_header("Accept", "application/json")
    # Full TLS verification: the token is sent on every request.
    try:
        with urllib.request.urlopen(r, timeout=40,
                                    context=ssl.create_default_context()) as f:
            return json.load(f)
    except urllib.error.HTTPError as e:
        sys.exit(f"rancher {path} -> HTTP {e.code}: "
                 f"{e.read()[:160].decode(errors='replace')}")
    except Exception as e:
        sys.exit(f"rancher {path} -> {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tenant")
    ap.add_argument("gateway")
    ap.add_argument("--out", help="where to write (default: alongside samples)")
    ap.add_argument("--kubectl", default=os.environ.get("KUBECTL", "kubectl"))
    ap.add_argument("--no-verify", action="store_true",
                    help="skip the exec capability check")
    ap.add_argument("--print-path", action="store_true",
                    help="print only the kubeconfig path, for use in a shell var")
    a = ap.parse_args()

    log = (lambda *m: None) if a.print_path else \
          (lambda *m: print(*m, file=sys.stderr))

    rec = tenant_record(a.tenant)
    token = rec.get("edgeflow_rancher_user_token")
    endpoint = rec.get("edgeflow_rancher_endpoint")
    if not token or not endpoint:
        sys.exit(f"tenant {a.tenant} has no edgeflow_rancher_user_token / "
                 f"edgeflow_rancher_endpoint; ask an operator for a kubeconfig")

    base = endpoint.rstrip("/")
    if not base.startswith("http"):
        base = "https://" + base

    cluster_name = f"ef-{a.tenant}-{a.gateway}"
    data = rancher_get(base, token, f"/v3/clusters?name={cluster_name}").get("data", [])
    if not data:
        sys.exit(f"no Rancher cluster named {cluster_name}. Check the gateway id, "
                 f"and that this credential can see that cluster.")
    cluster = data[0]
    server = f"{base}/k8s/clusters/{cluster['id']}"
    log(f"cluster {cluster_name} -> {cluster['id']} (state: {cluster.get('state')})")

    out = a.out or f"kubeconfig-{a.gateway}.yaml"
    # create 0600 before writing: the file holds a live credential
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(KUBECONFIG_TEMPLATE.format(name=cluster_name, server=server,
                                           token=token))

    if not a.no_verify:
        env = dict(os.environ, KUBECONFIG=os.path.abspath(out))

        def kc(*args):
            return subprocess.run([a.kubectl, *args], env=env,
                                  capture_output=True, text=True, timeout=90)

        p = kc("get", "pods", "-n", "default")
        if p.returncode != 0:
            os.remove(out)
            sys.exit(f"credential cannot list pods on {cluster_name}:\n"
                     f"  {p.stderr.strip()[:300]}")
        pods = [l.split()[0] for l in p.stdout.splitlines()
                if l.startswith("rabbitmq-") and " Running " in l]
        log(f"can list pods: yes ({len(p.stdout.splitlines())-1} pods)")

        p = kc("auth", "can-i", "create", "pods/exec", "-n", "default")
        verdict = p.stdout.strip()
        log(f"can create pods/exec: {verdict or '?'}")
        if verdict.startswith("no"):
            os.remove(out)
            sys.exit(
                f"This credential can read pods on {cluster_name} but cannot exec "
                f"into them, so it cannot run rabbitmqctl.\n"
                f"Reading pods and streaming logs is a different Kubernetes "
                f"permission from create on pods/exec.\n"
                f"Ask an operator either to widen this tenant's Rancher role, or "
                f"for a kubeconfig with exec rights.")
        if not pods:
            log("warning: no running rabbitmq pod found in namespace default")

    print(os.path.abspath(out) if a.print_path
          else f"wrote {out} (mode 0600) - contains a live credential; "
               f"delete it when done, never commit it")


if __name__ == "__main__":
    main()

#!/bin/bash
# Sample RabbitMQ queue depths on one EdgeFlow/CloudFlow appliance.
#
# usage: sample-queues.sh <gateway_id> <kubeconfig> [duration_s] [interval_s]
#          duration_s  default 1200 (20 min)
#          interval_s  default 20
#
# Writes depths-<gateway_id>.tsv in $OUTDIR (default: current directory):
#
#   <epoch>\t<queue_name>\t<messages>     one line per queue holding messages
#   <epoch>\t__total__\t<n>               summed depth over all queues
#   <epoch>\t__nqueues__\t<n>             queues on the broker
#   <epoch>\t__error__\t1                 a sample that failed
#   <epoch>\t__start__\t<duration>        run markers, so a relaunch extends
#   <epoch>\t__stop__\t0                    a series rather than replacing it
#
# Read-only. Runs `rabbitmqctl list_queues` and nothing else. In particular it
# never calls DELETE /api/reset, which would blank the broker's stats database.
#
# For a run longer than your session, detach it:
#   (nohup ./sample-queues.sh gw1 /path/cfg 18000 20 > gw1.log 2>&1 &)
# `setsid` is Linux-only and absent on macOS; nohup in a subshell is enough.

set -u

GW=${1:?usage: sample-queues.sh <gateway_id> <kubeconfig> [duration_s] [interval_s]}
CFG=${2:?usage: sample-queues.sh <gateway_id> <kubeconfig> [duration_s] [interval_s]}
DURATION=${3:-1200}
INTERVAL=${4:-20}

KUBECTL=${KUBECTL:-kubectl}
OUTDIR=${OUTDIR:-.}
NS=${NS:-default}

export KUBECONFIG=$CFG
OUT=$OUTDIR/depths-$GW.tsv
ERR=$OUTDIR/sample-$GW.err

[ -r "$CFG" ] || { echo "cannot read kubeconfig: $CFG" >&2; exit 2; }

resolve_pod() {
    "$KUBECTL" get pods -n "$NS" 2>>"$ERR" \
      | awk '/^rabbitmq-[0-9a-f]/ && $3=="Running" {print $1; exit}'
}

POD=$(resolve_pod)
if [ -z "$POD" ]; then
    echo "no running rabbitmq pod in namespace $NS on $GW" >&2
    echo "check: KUBECONFIG=$CFG $KUBECTL get pods -n $NS | grep rabbitmq" >&2
    exit 3
fi

start=$(date +%s)
printf '%s\t__start__\t%s\n' "$start" "$DURATION" >> "$OUT"
echo "$(date -u +%FT%TZ) start gw=$GW pod=$POD dur=$DURATION int=$INTERVAL" >> "$ERR"

fails=0
while :; do
    now=$(date +%s)
    [ $(( now - start )) -ge "$DURATION" ] && break

    snap=$("$KUBECTL" exec -n "$NS" "$POD" -- \
             /opt/rabbitmq/sbin/rabbitmqctl list_queues name messages 2>>"$ERR")

    if [ -n "$snap" ]; then
        fails=0
        # Select rows by "messages is numeric" rather than by line offset:
        # rabbitmqctl prints its "Timeout:" banner only on a TTY, so a fixed
        # `tail -n +3` drops a real queue row when the banner is absent and
        # counts the header as a queue when it is present.
        echo "$snap" | awk -F'\t' -v t="$now" '
            $2 ~ /^[0-9]+$/ {
                n++
                sum += $2
                if ($2 > 0) print t "\t" $1 "\t" $2
            }
            END { print t "\t__total__\t" sum+0; print t "\t__nqueues__\t" n+0 }' >> "$OUT"
    else
        printf '%s\t__error__\t1\n' "$now" >> "$OUT"
        fails=$(( fails + 1 ))
        # Two misses in a row usually means the pod was replaced. Re-resolving
        # keeps a long run from silently flat-lining after a broker restart.
        if [ "$fails" -ge 2 ]; then
            newpod=$(resolve_pod)
            if [ -n "$newpod" ] && [ "$newpod" != "$POD" ]; then
                echo "$(date -u +%FT%TZ) pod changed $POD -> $newpod" >> "$ERR"
                POD=$newpod
            fi
            fails=0
        fi
    fi

    # sleep to the next tick, accounting for how long the exec took
    sleep_for=$(( now + INTERVAL - $(date +%s) ))
    [ "$sleep_for" -gt 0 ] && sleep "$sleep_for"
done

printf '%s\t__stop__\t0\n' "$(date +%s)" >> "$OUT"
echo "DONE $(date +%s)" >> "$OUT"

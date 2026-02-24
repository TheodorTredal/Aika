#!/bin/bash
# -----------------------------------------
# killChord.sh – Stopp alle CHORD-noder oppført i activehostport.txt
# -----------------------------------------

ACTIVE_FILE="data/activehostport.txt"
REMOTE_PROJECT_PATH="/mnt/users/$USER/3200-a2/src"
FORCE=false

# Bruk: ./killChord.sh [--force]
# --force = bruk SIGKILL i stedet for SIGTERM

if [[ "$1" == "--force" ]]; then
    FORCE=true
fi


echo "Stopper alle CHORD-noder fra $ACTIVE_FILE..."
mapfile -t NODES < "$ACTIVE_FILE"

for NODE in "${NODES[@]}"; do
    HOST=$(echo "$NODE" | cut -d':' -f1)
    PORT=$(echo "$NODE" | cut -d':' -f2)

    echo "Stopper node på $HOST:$PORT ..."

    if [[ "$FORCE" == true ]]; then
        # Hard kill med -9
        ssh -n "$USER@$HOST" "ps -ef | grep 'python3 startChordNode.py $HOST $PORT' | grep -v grep | awk '{print \$2}' | xargs -r kill -9" >/dev/null 2>&1
    else
        # Myk kill (SIGTERM)
        ssh -n "$USER@$HOST" "ps -ef | grep 'python3 startChordNode.py $HOST $PORT' | grep -v grep | awk '{print \$2}' | xargs -r kill" >/dev/null 2>&1
    fi

    echo "Node $HOST:$PORT stoppet (hvis den kjørte)"
done

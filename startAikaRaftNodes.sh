#!/bin/bash

# =============================================================================
# Startup script for the Aika distributed image labelling system
# =============================================================================

if [ -z "$1" ]; then
    echo "Usage: $0 <number_of_cluster_controllers>"
    exit 1
fi

TOTAL_CLUSTER_CONTROLLERS=$1
MAX_LOAD=0.4
BIN_DIR="./bin"
CMD_DIR="./cmd"
# Sørg for at denne stien er korrekt for din bruker
REMOTE_PROJECT_PATH="/mnt/users/$USER/Aika/src" 

# --- Clean up ----------------------------------------------------------------
echo "Cleaning up..."
rm -f data/logs/*.log
rm -f data/wal/*.wal
rm -f data/result.json
> data/activehostport.txt
echo "Done."

# --- Compile -----------------------------------------------------------------
echo "Compiling binaries..."
# Fix for Go module error:
# if [ ! -f "go.mod" ]; then
#     go mod init aika 2>/dev/null || true
# fi

go build -o "$BIN_DIR/inf_3203_initial_agent" "$CMD_DIR/initial-agent/main.go"
go build -o "$BIN_DIR/inf_3203_worker_agent" "$CMD_DIR/worker-agent/main.go"
go build -o "$BIN_DIR/inf_3203_final_agent" "$CMD_DIR/final-agent/main.go"
go build -o "$BIN_DIR/inf_3203_local_controller" "$CMD_DIR/local_controller/main.go"
echo "Done."

# --- Find available nodes ----------------------------------------------------
echo "Finding available nodes..."
get_available_nodes() {
    local hosts
    hosts="$(shuf /share/compute-nodes.txt)"
    local filtered=()
    for H in $hosts; do
        [[ "$H" =~ ^c6- ]] && continue
        grep -qF "$H" /share/exclude-nodes.txt 2>/dev/null && continue
        filtered+=("$H")
    done

    for H in "${filtered[@]}"; do
        ssh -o ConnectTimeout=1 -o ConnectionAttempts=1 -x "$H" \
            "cat /proc/loadavg /proc/sys/kernel/hostname | tr '\n' ' ' | awk -v max_load=$MAX_LOAD '\$1+0 < max_load {printf \"%s %s\n\", \$1, \$6}'" 2>/dev/null &
    done | sort -n | awk '{print $2}' | sed 's/.ifi.uit.no//'
    wait
}

readarray -t AVAILABLE_NODES < <(get_available_nodes)

# --- Port Check Function -----------------------------------------------------
check_port_availability() {
    local node="$1"
    local port
    while :; do
        port=$(shuf -i 49631-65535 -n 1)
        if ! ssh -o ConnectTimeout=1 "$node" "nc -z localhost $port" >/dev/null 2>&1; then
            echo "$port"
            return
        fi
    done
}

# --- Phase 1: Identify Nodes and Ports ---
echo "Identifying $TOTAL_CLUSTER_CONTROLLERS nodes and ports..."
SELECTED_NODES=()
COUNT=0

for node in "${AVAILABLE_NODES[@]}"; do
    if [ "$COUNT" -ge "$TOTAL_CLUSTER_CONTROLLERS" ]; then
        break
    fi

    port=$(check_port_availability "$node")
    if [ -n "$port" ]; then
        SELECTED_NODES+=("$node:$port")
        echo "  Found: $node:$port"
        ((COUNT++))
    fi
done

# Lagre til fil for senere bruk
printf "%s\n" "${SELECTED_NODES[@]}" > data/activehostport.txt


# --- Phase 2: Start Raft Nodes ---
echo "Starting $TOTAL_CLUSTER_CONTROLLERS Raft nodes..."

for i in "${!SELECTED_NODES[@]}"; do
    # Den nåværende noden som skal startes (hentet fra de utvalgte med port)
    CURRENT_STR="${SELECTED_NODES[$i]}"
    HOST=$(echo "$CURRENT_STR" | cut -d':' -f1)
    PORT=$(echo "$CURRENT_STR" | cut -d':' -f2)

    # ---------------------------------------------------------
    # Bygg peer-liste fra ALLE tilgjengelige noder (AVAILABLE_NODES)
    # UNNTATT den vi starter akkurat nå.
    # ---------------------------------------------------------
    LOCAL_CONTROLLERS=()
    for potential_peer in "${AVAILABLE_NODES[@]}"; do
        # Vi sjekker mot HOST (navnet), siden AVAILABLE_NODES ikke har porter ennå
        if [ "$potential_peer" != "$HOST" ]; then
            LOCAL_CONTROLLERS+=("$potential_peer")
        fi
    done
    
    LOCAL_CONTROLLERS_STRING="${LOCAL_CONTROLLERS[*]}"

    echo "Launching Raft controller on $HOST:$PORT..."
    
    ssh -n "$USER@$HOST" "
        cd $REMOTE_PROJECT_PATH &&
        nohup python3 inf3203_startupRaftNodes.py \
            $HOST \
            $PORT \
            $LOCAL_CONTROLLERS_STRING \
        > node.log 2>&1 < /dev/null &
    " &
done

wait
echo "Done. $TOTAL_CLUSTER_CONTROLLERS nodes started."
'''Print all raft nodes, used for debugging purposes.'''


'''Må åpne filen hente ut alle aktive raft noder og printe deres status ved bruk av curl eller api kall eller whatever.'''

import requests
import time
import os
from rich.console import Console
from rich.table import Table
from rich.live import Live



def AllRaftNodeStatus():
    '''USED FOR DEBUGGING, find out if the nodes are follower, leader or candidate. '''

    path = "../data/activehostport.txt"

    last_modified = os.path.getmtime(path)

    with open(path, "r") as file:

        # Keep the script running during the RAFT protocol
        while True:
            current_mtime = os.path.getmtime(path)

            if current_mtime == os.path.getmtime(path):
                print("File changed!")

            print("\033[H\033[J", end="")

            print("=== RAFT CLUSTER STATUS ===")

            file.seek(0)
            for node_addr in file:
                r = requests.get(
                    f"http://{node_addr.strip()}/raft-myVote"
                )
                print(node_addr.strip(), "->", r.json()["state"])

            time.sleep(0.5)




console = Console()

tick = 0 # global timer

def build_table(nodes, tick):
    table = Table(title=f"RAFT Cluster Status — Tick {tick}")

    table.add_column("Server", style="cyan")
    table.add_column("State")
    table.add_column("Term")
    table.add_column("Voted For")
    table.add_column("Votes")

    for node in nodes:
        try:
            r = requests.get(
                f"http://{node}/raft-myVote",
                timeout=1
            )
            data = r.json()

            table.add_row(
                data["server_id"],
                data["state"],
                str(data["term"]),
                str(data["VotedFor"]),
                str(data["myVotes"]),
            )

        except Exception:
            table.add_row(node, "DOWN", "-", "-", "-", str(tick))

    return table


def show_raft_grid():
    path = "../data/activehostport.txt"

    with open(path) as file:
        nodes = [line.strip() for line in file]

    tick = 0

    with Live(build_table(nodes, tick),
              console=console,
              refresh_per_second=2) as live:

        while True:
            tick += 1
            live.update(build_table(nodes, tick))
            time.sleep(3)  # halve sekund mellom oppdateringer


if __name__ == "__main__":
    show_raft_grid()
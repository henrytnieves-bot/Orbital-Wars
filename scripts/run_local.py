#!/usr/bin/env python3
"""
Run a local Orbit Wars game with the Producer agent.

Usage:
    python scripts/run_local.py                          # Producer vs random
    python scripts/run_local.py --opponent agents/sniper.py  # vs sniper
    python scripts/run_local.py --players 4              # 4-player FFA
    python scripts/run_local.py --seed 42                # reproducible seed
    python scripts/run_local.py --render                 # render HTML replay
"""

import argparse
import os
import sys

# Ensure project root is importable
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(description="Run a local Orbit Wars game")
    parser.add_argument(
        "--opponent", "-o",
        default="random",
        help="Opponent agent: 'random', or a path to a .py file (default: random)",
    )
    parser.add_argument(
        "--players", "-p",
        type=int,
        default=2,
        choices=[2, 4],
        help="Number of players (default: 2)",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--render",
        action="store_true",
        help="Save an HTML replay file after the game",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Override max episode steps (default: use game default of 500)",
    )
    args = parser.parse_args()

    try:
        from kaggle_environments import make
    except ImportError:
        print("ERROR: kaggle-environments is not installed.")
        print("Install it with: pip install 'kaggle-environments>=1.28.0'")
        sys.exit(1)

    # Build configuration
    config = {}
    if args.seed is not None:
        config["seed"] = args.seed
    if args.steps is not None:
        config["episodeSteps"] = args.steps

    main_agent = os.path.join(PROJECT_ROOT, "main.py")

    # Build player list
    if args.opponent == "random":
        opponent = "random"
    else:
        opponent = os.path.join(PROJECT_ROOT, args.opponent)
        if not os.path.isfile(opponent):
            print(f"ERROR: Opponent file not found: {opponent}")
            sys.exit(1)

    if args.players == 2:
        players = [main_agent, opponent]
    else:
        # 4-player: Producer + 3 opponents
        players = [main_agent, opponent, opponent, opponent]

    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║  Orbit Wars — Local Game                                ║")
    print(f"╠══════════════════════════════════════════════════════════╣")
    print(f"║  Players: {args.players:<46}║")
    print(f"║  Agent:   Producer Lite (main.py){' ' * 22}║")
    print(f"║  Opponent: {str(args.opponent):<45}║")
    if args.seed is not None:
        print(f"║  Seed:    {args.seed:<46}║")
    print(f"╚══════════════════════════════════════════════════════════╝")
    print()

    env = make("orbit_wars", configuration=config, debug=True)
    env.run(players)

    # Print results
    final = env.steps[-1]
    print()
    print("=" * 50)
    print("  RESULTS")
    print("=" * 50)

    results = []
    for i, step in enumerate(final):
        label = "Producer" if i == 0 else f"Opponent {i}"
        reward = step.reward if hasattr(step, "reward") else step.get("reward", "?")
        status = step.status if hasattr(step, "status") else step.get("status", "?")
        results.append((label, reward, status))
        print(f"  Player {i} ({label}): reward={reward}, status={status}")

    print("=" * 50)

    # Determine winner
    rewards = [(r[1], r[0]) for r in results if isinstance(r[1], (int, float))]
    if rewards:
        winner = max(rewards, key=lambda x: x[0])
        print(f"\n  🏆 Winner: {winner[1]} (reward: {winner[0]})")

    # Render HTML replay if requested
    if args.render:
        replay_path = os.path.join(PROJECT_ROOT, "replay.html")
        html = env.render(mode="html", width=800, height=600)
        with open(replay_path, "w") as f:
            f.write(html)
        print(f"\n  📺 Replay saved to: {replay_path}")


if __name__ == "__main__":
    main()

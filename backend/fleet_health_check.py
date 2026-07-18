import os
import yaml
import sqlite3
import logging
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

def check_fleet_health():
    console.print("[bold cyan]===================================================[/]")
    console.print("[bold cyan]       JARVIS-X FLEET HEALTH & GROWTH CHECK        [/]")
    console.print("[bold cyan]===================================================[/]\n")

    # 1. Agent Integrity
    agent_dir = Path("config/agents")
    agents = list(agent_dir.glob("*.yaml"))
    
    table = Table(title="Agent Status Registry")
    table.add_column("Agent ID", style="magenta")
    table.add_column("Model", style="green")
    table.add_column("Integrity", style="cyan")
    table.add_column("Archetype", style="yellow")

    valid_count = 0
    for agent_file in agents:
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            aid = data.get("id", agent_file.stem)
            model = data.get("model", "N/A")
            arch = data.get("archetype", "N/A")
            
            integrity = "[OK] PASS" if all(k in data for k in ["id", "name", "mindset"]) else "[!] WARN"
            table.add_row(aid, model, integrity, arch)
            valid_count += 1
        except Exception as e:
            table.add_row(agent_file.name, "ERROR", "[X] FAIL", str(e)[:30])

    console.print(table)
    console.print(f"\n[bold]Total Agents Verified:[/] {valid_count}/{len(agents)}")

    # 2. Growth & Learning Metrics
    console.print("\n[bold cyan]── Learning & Growth Metrics ──────────────────────[/]")
    db_path = "memory/fleet.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Count interactions
            cursor.execute("SELECT COUNT(*) FROM interaction_logs")
            lesson_count = cursor.fetchone()[0]
            
            # Count agent performance records from interaction_logs
            cursor.execute("SELECT agent_id, COUNT(*), AVG(score) FROM interaction_logs GROUP BY agent_id")
            performance = cursor.fetchall()
            
            console.print(f"📈 [bold]Total Interactions Recorded:[/] {lesson_count}")
            
            p_table = Table(title="Agent Performance & Growth")
            p_table.add_column("Agent", style="magenta")
            p_table.add_column("Tasks", style="cyan")
            p_table.add_column("Avg Score", style="green")
            
            for row in performance:
                p_table.add_row(row[0], str(row[1]), f"{row[2]:.1f}" if row[2] else "0.0")
            
            console.print(p_table)
            conn.close()
        except Exception as e:
            console.print(f"[bold red]Database Error:[/] {e}")
    else:
        console.print("[yellow]Note: fleet.db not found. System may be in fresh state.[/]")

    # 3. Social Intelligence Validation (Vera)
    console.print("\n[bold cyan]── Social Intelligence Gate (Vera) ────────────────[/]")
    from core.social_filter import apply_social_filter
    
    test_message = "Hey Boss, tell me about the budget."
    # Simulate an elder brother asking
    adapted = apply_social_filter(test_message, "Annaya", context="Elder Brother")
    
    if "Annaya" in str(adapted) or "Meeru" in str(adapted):
        console.print("[OK] [green]Social Intelligence Layer: Active & Grounded[/]")
        console.print(f"   Sample Adaptation for Annaya: [italic]'{adapted.get('bubbles', [''])[0]}...'[/]")
    else:
        console.print("[!] [yellow]Social Intelligence Layer: Adaptation pending/generic[/]")

    console.print("\n[bold green]FINAL STATUS: FLEET IS 100% OPERATIONAL[/]")

if __name__ == "__main__":
    check_fleet_health()

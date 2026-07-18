import os
import glob
import sys
import subprocess

def review_proposals():
    proposal_dir = "proposals"
    if not os.path.exists(proposal_dir):
        print("No proposals directory found.")
        return

    proposals = glob.glob(os.path.join(proposal_dir, "*.py"))
    if not proposals:
        print("No pending proposals.")
        return

    print("--- PENDING AGENT PROPOSALS ---")
    for i, prop in enumerate(proposals):
        print(f"[{i}] {prop}")

    choice = input("\nEnter the number of the proposal to review (or 'q' to quit): ")
    if choice.lower() == 'q':
        return

    try:
        idx = int(choice)
        target = proposals[idx]
        
        print("\n--- CODE PREVIEW ---")
        with open(target, "r", encoding="utf-8") as f:
            print(f.read())
            
        print("\n--------------------")
        action = input("Options: [A]pprove and run, [D]elete, [I]gnore: ").strip().upper()
        
        if action == 'A':
            print(f"Running {target}...")
            # For this MVP, we just execute it. In a robust system, it could copy it to a target module.
            subprocess.run([sys.executable, target])
            print("Execution finished.")
        elif action == 'D':
            os.remove(target)
            print(f"Deleted {target}.")
            
    except (ValueError, IndexError):
        print("Invalid selection.")

if __name__ == "__main__":
    review_proposals()

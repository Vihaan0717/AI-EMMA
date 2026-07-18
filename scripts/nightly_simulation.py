import asyncio
from backend.brain.agents.critic_agent import CriticAgent

async def run_simulation():
    print("Starting Nightly Simulation Loop...")
    critic = CriticAgent()
    
    # In a real system, these would be fetched from daily failure logs
    dummy_failed_tasks = [
        {
            "task": "Login to portal X",
            "error": "TimeoutError: Could not find element with id 'submit-btn'. The UI seems to have changed to a React hashed class."
        }
    ]
    
    for task_info in dummy_failed_tasks:
        print(f"Reflecting on failed task: {task_info['task']}")
        lesson_file = await critic.reflect_on_failure(task_info['task'], task_info['error'])
        print(f"Generated Lesson Learned: {lesson_file}")
        
if __name__ == "__main__":
    asyncio.run(run_simulation())

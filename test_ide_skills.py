import os
from nexus_master import NexusMaster

def test_ide_skills():
    print("Testing IDE Skills...\n")
    master = NexusMaster()
    
    # Test 1: Write file
    test_file_path = os.path.abspath("test_file.txt")
    print(f"1. Testing ide_write_file to {test_file_path}")
    call_str = f'<CALL: ide_write_file("{test_file_path}", "Hello from Nexus IDE skills!")>'
    tool, result = master.parse_and_execute_tool(call_str)
    print(f"Tool: {tool}, Result: {result}")
    
    # Test 2: Read file
    print("\n2. Testing ide_read_file")
    call_str = f'<CALL: ide_read_file("{test_file_path}")>'
    tool, result = master.parse_and_execute_tool(call_str)
    print(f"Tool: {tool}, Result: {result}")
    
    # Test 3: List directory
    current_dir = os.path.abspath(".")
    print(f"\n3. Testing ide_list_directory on {current_dir}")
    call_str = f'<CALL: ide_list_directory("{current_dir}")>'
    tool, result = master.parse_and_execute_tool(call_str)
    print(f"Tool: {tool}, Result: {result[:100]}... (truncated)")
    
    # Test 4: Run command
    print("\n4. Testing ide_run_command")
    call_str = '<CALL: ide_run_command("echo IDE_TEST_SUCCESS")>'
    tool, result = master.parse_and_execute_tool(call_str)
    print(f"Tool: {tool}, Result: {result.strip()}")

    # Cleanup
    if os.path.exists(test_file_path):
        os.remove(test_file_path)

if __name__ == "__main__":
    test_ide_skills()

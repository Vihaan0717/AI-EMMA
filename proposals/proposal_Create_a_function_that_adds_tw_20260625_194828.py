# Proposal: Create a function that adds two numbers together
# Status:   VERIFIED
# Sandbox:  Docker
# Output:   15
30.7
# Generated: 20260625_194828

def add_numbers(a, b):
    """
    Adds two numbers together.

    Args:
        a (int or float): The first number.
        b (int or float): The second number.

    Returns:
        int or float: The sum of a and b.
    """
    return a + b

# Example usage:
print(add_numbers(5, 10))  # Output: 15
print(add_numbers(10.5, 20.2))  # Output: 30.7
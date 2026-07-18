import subprocess
import json
from typing import Optional, List, Dict

class GmailAgent:
    """
    A wrapper around the Himalaya CLI to manage Gmail (IMAP/SMTP).
    """

    def __init__(self):
        # We assume himalaya is in the system PATH
        self.cli_cmd = "himalaya"

    def _run_command(self, args: List[str]) -> str:
        """Run a Himalaya command and return the output."""
        try:
            # We use --output json to make it parseable where possible
            command = [self.cli_cmd] + args
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error executing himalaya: {e.stderr}"

    def list_emails(self, folder: str = "inbox", limit: int = 10) -> str:
        """List emails in a specific folder."""
        # Note: --output json might not be fully supported on all himalaya commands depending on version, 
        # but we'll stick to standard text output for broad compatibility unless JSON is needed.
        return self._run_command(["envelope", "list", folder, "--max-width", "100", "--page-size", str(limit)])

    def search_emails(self, query: str, folder: str = "inbox") -> str:
        """Search emails matching a query."""
        # e.g., query = "from alice@example.com subject invoice"
        args = ["envelope", "list", folder] + query.split()
        return self._run_command(args)

    def read_email(self, email_id: str, folder: str = "inbox") -> str:
        """Read the content of a specific email by ID."""
        return self._run_command(["message", "read", email_id, folder])

    def send_email(self, to: str, subject: str, body: str) -> str:
        """Send an email."""
        # Himalaya typically uses MML (Mail Markup Language) or standard stdin for writes.
        # This is a simplified wrapper. For complex messages, himalaya template write might be better.
        try:
            # We construct a simple MIME message and pass to himalaya message send
            email_content = f"To: {to}\nSubject: {subject}\n\n{body}\n"
            command = [self.cli_cmd, "message", "send"]
            result = subprocess.run(command, input=email_content, capture_output=True, text=True, check=True)
            return "Email sent successfully."
        except subprocess.CalledProcessError as e:
            return f"Failed to send email: {e.stderr}"

    def delete_email(self, email_id: str, folder: str = "inbox") -> str:
        """Delete an email."""
        return self._run_command(["message", "delete", email_id, folder])

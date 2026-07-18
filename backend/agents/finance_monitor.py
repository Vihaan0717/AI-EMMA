import logging
import re
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger("Nexus.FinanceMonitor")

class FinanceMonitor:
    """
    Automated Financial Monitoring Agent.
    Scans messages for transaction patterns and stores them.
    """
    def __init__(self, db_path: str = "memory/finance.db"):
        self.db_path = db_path
        self._init_db()
        
        # Regex patterns for common transaction notifications
        self.patterns = [
            r"(?:Rs|INR)\.?\s*([\d,]+\.?\d*)\s*(?:debited|paid|spent|sent|spent to)",
            r"(?:spent|paid)\s*(?:Rs|INR)\.?\s*([\d,]+\.?\d*)",
            r"(?:Rs|INR)\.?\s*([\d,]+\.?\d*)\s*(?:credited|received|added)",
        ]

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      amount REAL,
                      type TEXT, -- 'DEBIT' or 'CREDIT'
                      purpose TEXT,
                      raw_text TEXT,
                      timestamp DATETIME)''')
        conn.commit()
        conn.close()

    async def scan_message(self, text: str) -> Optional[Dict[str, Any]]:
        """Scans a single message for financial data."""
        text_lower = text.lower()
        
        # 1. Detect if it's a financial message
        is_financial = any(re.search(p, text_lower) for p in self.patterns) or \
                       any(w in text_lower for w in ["debited", "credited", "transaction", "bank", "upi", "spent"])
        
        if not is_financial:
            return None

        # 2. Extract Amount
        amount = 0.0
        for p in self.patterns:
            match = re.search(p, text_lower)
            if match:
                try:
                    amount = float(match.group(1).replace(",", ""))
                    break
                except: continue

        # 3. Detect Type
        trans_type = "DEBIT"
        if any(w in text_lower for w in ["credited", "received", "added", "income", "salary"]):
            trans_type = "CREDIT"

        # 4. Extract Purpose (Heuristic)
        purpose = "Miscellaneous"
        # Look for "to [Name]" or "at [Store]"
        p_match = re.search(r"(?:to|at|for)\s+([a-zA-Z0-9\s]{3,20})", text)
        if p_match:
            purpose = p_match.group(1).strip()

        # 5. Store in DB
        self._store_transaction(amount, trans_type, purpose, text)
        
        return {
            "amount": amount,
            "type": trans_type,
            "purpose": purpose,
            "timestamp": datetime.now().isoformat()
        }

    def _store_transaction(self, amount: float, t_type: str, purpose: str, raw: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO transactions (amount, type, purpose, raw_text, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (amount, t_type, purpose, raw, datetime.now()))
        conn.commit()
        conn.close()
        logger.info(f"Financial record saved: {t_type} {amount} for {purpose}")

    def get_summary(self, period: str = "daily") -> Dict[str, Any]:
        """Returns a summary of spending."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Simple daily summary for now
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='DEBIT' AND date(timestamp) = date('now')")
        daily_spent = c.fetchone()[0] or 0.0
        
        c.execute("SELECT SUM(amount) FROM transactions WHERE type='CREDIT' AND date(timestamp) = date('now')")
        daily_income = c.fetchone()[0] or 0.0
        
        conn.close()
        return {
            "daily_spent": daily_spent,
            "daily_income": daily_income,
            "net": daily_income - daily_spent
        }

if __name__ == "__main__":
    import asyncio
    async def test():
        fm = FinanceMonitor()
        res = await fm.scan_message("Rs. 500 debited from your account for Amazon")
        print(res)
        print(fm.get_summary())
    asyncio.run(test())

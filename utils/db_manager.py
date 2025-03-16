import json
import os
import time
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)

class UserData:
    def __init__(self):
        self.data_file = "userdata.json"
        self.data = self._load_data()
        logger.info("UserData initialized")

    def _load_data(self) -> Dict:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error("Failed to decode userdata.json")
                return {}
        return {}

    def _save_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save data: {e}")

    def _init_user(self, user_id: int) -> None:
        user_id_str = str(user_id)  # Convert to string for JSON storage
        if user_id_str not in self.data:
            self.data[user_id_str] = {
                "balance": 1000,      # Wallet balance
                "bank": 0,            # Bank balance
                "last_work": 0,       # Last work timestamp
                "last_daily": 0,      # Last daily claim
                "last_weekly": 0,     # Last weekly claim
                "daily_streak": 0,    # Current daily streak
                "warnings": []        # Warning list
            }
            self._save_data()
            logger.info(f"Initialized new user data for user {user_id}")

    def get_balance(self, user_id: int) -> int:
        self._init_user(user_id)
        return self.data[str(user_id)]["balance"]

    def get_bank_balance(self, user_id: int) -> int:
        self._init_user(user_id)
        return self.data[str(user_id)]["bank"]

    def add_balance(self, user_id: int, amount: int) -> None:
        self._init_user(user_id)
        user_id_str = str(user_id)
        self.data[user_id_str]["balance"] += amount
        self._save_data()
        logger.debug(f"Added {amount} to user {user_id}'s balance")

    def remove_balance(self, user_id: int, amount: int) -> None:
        self._init_user(user_id)
        user_id_str = str(user_id)
        self.data[user_id_str]["balance"] = max(0, self.data[user_id_str]["balance"] - amount)
        self._save_data()
        logger.debug(f"Removed {amount} from user {user_id}'s balance")

    def transfer_balance(self, from_user: int, to_user: int, amount: int) -> None:
        self._init_user(from_user)
        self._init_user(to_user)

        from_user_str = str(from_user)
        to_user_str = str(to_user)

        # Remove from source user
        self.data[from_user_str]["balance"] = max(0, self.data[from_user_str]["balance"] - amount)
        # Add to target user
        self.data[to_user_str]["balance"] += amount
        self._save_data()
        logger.info(f"Transferred {amount} from user {from_user} to user {to_user}")

    def deposit(self, user_id: int, amount: int) -> None:
        self._init_user(user_id)
        user_id_str = str(user_id)

        # Remove from wallet
        self.data[user_id_str]["balance"] -= amount
        # Add to bank
        self.data[user_id_str]["bank"] += amount
        self._save_data()
        logger.debug(f"User {user_id} deposited {amount} into bank")

    def withdraw(self, user_id: int, amount: int) -> None:
        self._init_user(user_id)
        user_id_str = str(user_id)

        # Remove from bank
        self.data[user_id_str]["bank"] -= amount
        # Add to wallet
        self.data[user_id_str]["balance"] += amount
        self._save_data()
        logger.debug(f"User {user_id} withdrew {amount} from bank")

    def can_claim_daily(self, user_id: int) -> Tuple[bool, int]:
        self._init_user(user_id)
        user_id_str = str(user_id)

        last_daily = self.data[user_id_str]["last_daily"]
        current_time = int(time.time())
        cooldown = 86400  # 24 hours in seconds

        if current_time - last_daily >= cooldown:
            return True, 0

        return False, cooldown - (current_time - last_daily)

    def can_claim_weekly(self, user_id: int) -> Tuple[bool, int]:
        self._init_user(user_id)
        user_id_str = str(user_id)

        last_weekly = self.data[user_id_str]["last_weekly"]
        current_time = int(time.time())
        cooldown = 604800  # 7 days in seconds

        if current_time - last_weekly >= cooldown:
            return True, 0

        return False, cooldown - (current_time - last_weekly)

    def increment_daily_streak(self, user_id: int) -> int:
        self._init_user(user_id)
        user_id_str = str(user_id)

        # Store the previous claim time before updating
        current_time = int(time.time())
        prev_claim = self.data[user_id_str]["last_daily"]

        # Update the last claim time
        self.data[user_id_str]["last_daily"] = current_time

        # Check if the last claim was within 48 hours (24h + 24h grace period)
        if current_time - prev_claim <= 172800:  # 48 hours in seconds
            self.data[user_id_str]["daily_streak"] += 1
            logger.debug(f"User {user_id} increased daily streak to {self.data[user_id_str]['daily_streak']}")
        else:
            self.data[user_id_str]["daily_streak"] = 1
            logger.debug(f"User {user_id} daily streak reset to 1")

        self._save_data()
        return self.data[user_id_str]["daily_streak"]

    def get_daily_streak(self, user_id: int) -> int:
        self._init_user(user_id)
        return self.data[str(user_id)]["daily_streak"]

    def can_work(self, user_id: int) -> Tuple[bool, int]:
        """Check if user can work and return cooldown time remaining"""
        self._init_user(user_id)
        user_id_str = str(user_id)

        last_work = self.data[user_id_str]["last_work"]
        current_time = int(time.time())
        cooldown = 3600  # 1 hour in seconds

        if current_time - last_work >= cooldown:
            return True, 0

        return False, cooldown - (current_time - last_work)

    def add_work_reward(self, user_id: int, amount: int) -> None:
        """Add work reward to user's balance and update work timestamp"""
        self._init_user(user_id)
        user_id_str = str(user_id)

        self.data[user_id_str]["balance"] += amount
        self.data[user_id_str]["last_work"] = int(time.time())
        self._save_data()
        logger.debug(f"User {user_id} earned {amount} from work")

    def add_warning(self, user_id: int, reason: str, mod_id: int) -> None:
        """Add a warning to a user's record"""
        self._init_user(user_id)
        user_id_str = str(user_id)

        warning = {
            "reason": reason,
            "mod_id": mod_id,
            "timestamp": int(time.time())
        }

        self.data[user_id_str]["warnings"].append(warning)
        self._save_data()
        logger.info(f"Warning added to user {user_id} by moderator {mod_id}")

    def get_warnings(self, user_id: int) -> List[Dict]:
        """Get all warnings for a user"""
        self._init_user(user_id)
        return self.data[str(user_id)]["warnings"]

    def clear_warnings(self, user_id: int) -> int:
        """Clear all warnings for a user and return the number of warnings cleared"""
        self._init_user(user_id)
        user_id_str = str(user_id)

        num_warnings = len(self.data[user_id_str]["warnings"])
        self.data[user_id_str]["warnings"] = []
        self._save_data()
        logger.info(f"Cleared {num_warnings} warnings for user {user_id}")

        return num_warnings
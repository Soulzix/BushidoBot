import json
import os
import time
from typing import Dict, Tuple
from utils.constants import WORK_COOLDOWN

class UserData:
    def __init__(self):
        self.data_file = "userdata.json"
        self.data = self._load_data()

    def _load_data(self) -> Dict:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def _save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def _init_user(self, user_id: str) -> None:
        if user_id not in self.data:
            self.data[user_id] = {
                "balance": 1000,  # Starting balance
                "last_work": 0    # Timestamp of last work command
            }
            self._save_data()

    def get_balance(self, user_id: int) -> int:
        user_id = str(user_id)
        self._init_user(user_id)
        return self.data[user_id]["balance"]

    def can_work(self, user_id: int) -> Tuple[bool, int]:
        """Check if user can work and return cooldown time remaining"""
        user_id = str(user_id)
        self._init_user(user_id)

        last_work = self.data[user_id]["last_work"]
        current_time = int(time.time())
        time_passed = current_time - last_work

        if time_passed >= WORK_COOLDOWN:
            return True, 0

        return False, WORK_COOLDOWN - time_passed

    def add_work_reward(self, user_id: int, amount: int) -> None:
        """Add work reward to user's balance and update work timestamp"""
        user_id = str(user_id)
        self._init_user(user_id)

        self.data[user_id]["balance"] += amount
        self.data[user_id]["last_work"] = int(time.time())
        self._save_data()
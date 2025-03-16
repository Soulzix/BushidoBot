WEAPON_STATS = {
    "katana": {
        "damage": 50,
        "speed": "Fast",
        "description": "A swift blade perfect for quick strikes."
    },
    "longsword": {
        "damage": 70,
        "speed": "Medium",
        "description": "A balanced weapon with good reach and power."
    },
    "dagger": {
        "damage": 30,
        "speed": "Very Fast",
        "description": "Small but deadly, perfect for quick successive attacks."
    }
}

# Work-related constants
WORK_COOLDOWN = 86400  # 24 hours in seconds
WORK_REWARDS = {
    "office_work": {"min": 100, "max": 300, "messages": [
        "You worked hard at the office today! Earned {} Yen! 💼",
        "Another day at the 9-5 grind. Earned {} Yen! 👔",
        "Completed those TPS reports! Earned {} Yen! 📊"
    ]},
    "delivery": {"min": 150, "max": 250, "messages": [
        "Made some speedy deliveries! Earned {} Yen! 🚚",
        "Delivered packages all around town. Earned {} Yen! 📦",
        "Rain or shine, you delivered! Earned {} Yen! 🛵"
    ]},
    "freelance": {"min": 50, "max": 400, "messages": [
        "Completed a freelance gig! Earned {} Yen! 💻",
        "Your creative work paid off! Earned {} Yen! 🎨",
        "Finished a client project! Earned {} Yen! ✍️"
    ]}
}
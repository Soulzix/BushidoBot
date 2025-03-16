# Weapon-related constants
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
    "office_work": {
        "min": 100,
        "max": 300,
        "messages": [
            "You worked hard at the office today! Earned {} Yen! 💼",
            "Another day at the 9-5 grind. Earned {} Yen! 👔",
            "Completed those TPS reports! Earned {} Yen! 📊"
        ],
        "emoji": "💼"
    },
    "delivery": {
        "min": 150,
        "max": 250,
        "messages": [
            "Made some speedy deliveries! Earned {} Yen! 🚚",
            "Delivered packages all around town. Earned {} Yen! 📦",
            "Rain or shine, you delivered! Earned {} Yen! 🛵"
        ],
        "emoji": "📦"
    },
    "freelance": {
        "min": 50,
        "max": 400,
        "messages": [
            "Completed a freelance gig! Earned {} Yen! 💻",
            "Your creative work paid off! Earned {} Yen! 🎨",
            "Finished a client project! Earned {} Yen! ✍️"
        ],
        "emoji": "💻"
    },
    "chef": {
        "min": 200,
        "max": 450,
        "messages": [
            "Your culinary skills earned you {} Yen! 👨‍🍳",
            "The restaurant was packed! Made {} Yen in tips! 🍽️",
            "Your special dish was a hit! Earned {} Yen! 🥘"
        ],
        "emoji": "👨‍🍳"
    },
    "streamer": {
        "min": 75,
        "max": 500,
        "messages": [
            "Your stream was a huge success! Earned {} Yen! 🎮",
            "Got lots of donations today! Made {} Yen! 🎥",
            "Your viewers loved the content! Earned {} Yen! 🎬"
        ],
        "emoji": "🎮"
    }
}
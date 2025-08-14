#!/usr/bin/env python3
"""
Gamification System for StudyMate
Transforms learning into an engaging, competitive experience with points, badges, and achievements
"""

import json
import os
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import random

class GameificationManager:
    """Manages the gamification system for StudyMate."""
    
    def __init__(self):
        self.user_progress_file = "user_progress.json"
        self.leaderboard_file = "leaderboard.json"
        self.badges_file = "badges_config.json"
        self.initialize_badges()
    
    def initialize_badges(self):
        """Initialize the badge system with predefined badges."""
        badges_config = {
            "accuracy_badges": {
                "Perfect Score": {"threshold": 100, "icon": "🏆", "description": "Score 100% on any quiz", "points": 200},
                "Excellence": {"threshold": 90, "icon": "⭐", "description": "Score 90%+ on a quiz", "points": 100},
                "Good Job": {"threshold": 80, "icon": "👍", "description": "Score 80%+ on a quiz", "points": 50},
                "Getting There": {"threshold": 70, "icon": "📈", "description": "Score 70%+ on a quiz", "points": 25}
            },
            "subject_badges": {
                "Math Wizard": {"subject": "mathematics", "threshold": 5, "icon": "🧮", "description": "Complete 5 math quizzes", "points": 150},
                "Science Genius": {"subject": "science", "threshold": 5, "icon": "🔬", "description": "Complete 5 science quizzes", "points": 150},
                "History Buff": {"subject": "history", "threshold": 5, "icon": "📚", "description": "Complete 5 history quizzes", "points": 150},
                "Language Master": {"subject": "language", "threshold": 5, "icon": "📝", "description": "Complete 5 language quizzes", "points": 150},
                "Bio Expert": {"subject": "biology", "threshold": 3, "icon": "🌿", "description": "Complete 3 biology quizzes", "points": 100},
                "Physics Pro": {"subject": "physics", "threshold": 3, "icon": "⚛️", "description": "Complete 3 physics quizzes", "points": 100},
                "Chemistry Champion": {"subject": "chemistry", "threshold": 3, "icon": "🧪", "description": "Complete 3 chemistry quizzes", "points": 100}
            },
            "streak_badges": {
                "On Fire": {"streak": 5, "icon": "🔥", "description": "5-day study streak", "points": 100},
                "Unstoppable": {"streak": 10, "icon": "💪", "description": "10-day study streak", "points": 250},
                "Legend": {"streak": 20, "icon": "👑", "description": "20-day study streak", "points": 500}
            },
            "speed_badges": {
                "Lightning Fast": {"time_threshold": 30, "icon": "⚡", "description": "Complete quiz in under 30 seconds", "points": 75},
                "Quick Thinker": {"time_threshold": 60, "icon": "🏃", "description": "Complete quiz in under 1 minute", "points": 50},
                "Speedy": {"time_threshold": 120, "icon": "🚀", "description": "Complete quiz in under 2 minutes", "points": 25}
            },
            "special_badges": {
                "First Steps": {"condition": "first_quiz", "icon": "🎯", "description": "Complete your first quiz", "points": 50},
                "Comeback Kid": {"condition": "improvement", "icon": "📊", "description": "Improve score by 20%+", "points": 100},
                "Night Owl": {"condition": "late_study", "icon": "🦉", "description": "Study after 10 PM", "points": 25},
                "Early Bird": {"condition": "early_study", "icon": "🐦", "description": "Study before 7 AM", "points": 25},
                "Weekend Warrior": {"condition": "weekend_study", "icon": "⚔️", "description": "Study on weekends", "points": 50}
            }
        }
        
        if not os.path.exists(self.badges_file):
            with open(self.badges_file, 'w') as f:
                json.dump(badges_config, f, indent=2)
    
    def load_user_progress(self, user_id: str) -> Dict:
        """Load user progress data."""
        try:
            if os.path.exists(self.user_progress_file):
                with open(self.user_progress_file, 'r') as f:
                    all_progress = json.load(f)
                    return all_progress.get(user_id, self.create_new_user_progress())
            return self.create_new_user_progress()
        except:
            return self.create_new_user_progress()
    
    def create_new_user_progress(self) -> Dict:
        """Create new user progress structure."""
        return {
            "total_points": 0,
            "level": 1,
            "current_streak": 0,
            "best_streak": 0,
            "quizzes_completed": 0,
            "total_questions_answered": 0,
            "correct_answers": 0,
            "badges_earned": [],
            "quiz_history": [],
            "subject_stats": {},
            "last_activity": None,
            "rank": "Novice Scholar",
            "achievements": []
        }
    
    def save_user_progress(self, user_id: str, progress: Dict):
        """Save user progress data."""
        try:
            all_progress = {}
            if os.path.exists(self.user_progress_file):
                with open(self.user_progress_file, 'r') as f:
                    all_progress = json.load(f)
            
            all_progress[user_id] = progress
            
            with open(self.user_progress_file, 'w') as f:
                json.dump(all_progress, f, indent=2)
        except Exception as e:
            st.error(f"Error saving progress: {e}")
    
    def calculate_quiz_score(self, correct: int, total: int, time_taken: int, previous_best: int = 0) -> Dict:
        """Calculate comprehensive quiz score with bonuses."""
        accuracy = (correct / total) * 100 if total > 0 else 0
        base_points = correct * 10
        
        # Accuracy bonus
        accuracy_bonus = 0
        if accuracy >= 100:
            accuracy_bonus = 100
        elif accuracy >= 90:
            accuracy_bonus = 50
        elif accuracy >= 80:
            accuracy_bonus = 25
        
        # Speed bonus (based on time taken)
        speed_bonus = 0
        if time_taken <= 30:
            speed_bonus = 75
        elif time_taken <= 60:
            speed_bonus = 50
        elif time_taken <= 120:
            speed_bonus = 25
        
        # Improvement bonus
        improvement_bonus = 0
        if previous_best > 0 and accuracy > previous_best:
            improvement = accuracy - previous_best
            if improvement >= 20:
                improvement_bonus = 100
            elif improvement >= 10:
                improvement_bonus = 50
            elif improvement >= 5:
                improvement_bonus = 25
        
        total_points = base_points + accuracy_bonus + speed_bonus + improvement_bonus
        
        return {
            "base_points": base_points,
            "accuracy_bonus": accuracy_bonus,
            "speed_bonus": speed_bonus,
            "improvement_bonus": improvement_bonus,
            "total_points": total_points,
            "accuracy": accuracy
        }
    
    def check_new_badges(self, user_progress: Dict, quiz_result: Dict) -> List[Dict]:
        """Check for newly earned badges."""
        new_badges = []
        
        with open(self.badges_file, 'r') as f:
            badges_config = json.load(f)
        
        earned_badge_names = [badge["name"] for badge in user_progress.get("badges_earned", [])]
        
        # Check accuracy badges
        accuracy = quiz_result.get("accuracy", 0)
        for badge_name, badge_info in badges_config["accuracy_badges"].items():
            if badge_name not in earned_badge_names and accuracy >= badge_info["threshold"]:
                new_badges.append({
                    "name": badge_name,
                    "icon": badge_info["icon"],
                    "description": badge_info["description"],
                    "points": badge_info["points"],
                    "category": "accuracy"
                })
        
        # Check speed badges
        time_taken = quiz_result.get("time_taken", 999)
        for badge_name, badge_info in badges_config["speed_badges"].items():
            if badge_name not in earned_badge_names and time_taken <= badge_info["time_threshold"]:
                new_badges.append({
                    "name": badge_name,
                    "icon": badge_info["icon"],
                    "description": badge_info["description"],
                    "points": badge_info["points"],
                    "category": "speed"
                })
        
        # Check streak badges
        current_streak = user_progress.get("current_streak", 0)
        for badge_name, badge_info in badges_config["streak_badges"].items():
            if badge_name not in earned_badge_names and current_streak >= badge_info["streak"]:
                new_badges.append({
                    "name": badge_name,
                    "icon": badge_info["icon"],
                    "description": badge_info["description"],
                    "points": badge_info["points"],
                    "category": "streak"
                })
        
        # Check special badges
        if user_progress.get("quizzes_completed", 0) == 0:  # First quiz
            if "First Steps" not in earned_badge_names:
                badge_info = badges_config["special_badges"]["First Steps"]
                new_badges.append({
                    "name": "First Steps",
                    "icon": badge_info["icon"],
                    "description": badge_info["description"],
                    "points": badge_info["points"],
                    "category": "special"
                })
        
        return new_badges
    
    def get_rank_from_points(self, points: int) -> str:
        """Determine user rank based on total points."""
        if points >= 10000:
            return "Grandmaster Scholar 👑"
        elif points >= 5000:
            return "Master Scholar 🎓"
        elif points >= 2500:
            return "Expert Scholar 📚"
        elif points >= 1000:
            return "Advanced Scholar ⭐"
        elif points >= 500:
            return "Intermediate Scholar 📖"
        elif points >= 100:
            return "Apprentice Scholar 🌟"
        else:
            return "Novice Scholar 🎯"
    
    def get_motivational_message(self, performance: Dict, user_progress: Dict) -> str:
        """Generate motivational messages based on performance."""
        accuracy = performance.get("accuracy", 0)
        points_gained = performance.get("total_points", 0)
        
        messages = {
            "excellent": [
                "🔥 Absolutely crushing it! You're on fire!",
                "⭐ Outstanding work! You're a true scholar!",
                "🚀 Phenomenal performance! Keep soaring!",
                "💎 Brilliant! You're shining bright today!",
                "🏆 Champion-level performance! Incredible!"
            ],
            "good": [
                "👏 Great job! You're making solid progress!",
                "📈 Nice improvement! Keep up the momentum!",
                "💪 Strong performance! You're getting stronger!",
                "🎯 Well done! You're hitting your targets!",
                "⚡ Good energy! Keep that focus going!"
            ],
            "okay": [
                "📚 Good effort! Every step counts!",
                "🌱 You're growing! Keep practicing!",
                "🎪 Nice try! Learning is a journey!",
                "💫 Progress is progress! Keep going!",
                "🔄 Keep pushing! You've got this!"
            ],
            "needs_work": [
                "🌟 Don't give up! Every expert was once a beginner!",
                "💪 Challenges make you stronger! Try again!",
                "🎯 Practice makes perfect! You're improving!",
                "🚀 Ready for takeoff? Let's try another round!",
                "📈 Growth mindset! You're learning and improving!"
            ]
        }
        
        if accuracy >= 90:
            category = "excellent"
        elif accuracy >= 75:
            category = "good"
        elif accuracy >= 60:
            category = "okay"
        else:
            category = "needs_work"
        
        return random.choice(messages[category])
    
    def generate_next_challenge(self, user_progress: Dict) -> Dict:
        """Generate personalized challenges for the user."""
        challenges = [
            {
                "title": "Perfect Score Challenge",
                "description": "Score 100% on your next quiz",
                "reward": "200 bonus XP + 'Perfectionist' badge",
                "icon": "🎯",
                "difficulty": "Hard"
            },
            {
                "title": "Speed Demon",
                "description": "Complete a quiz in under 1 minute",
                "reward": "150 bonus XP + 'Lightning Fast' badge",
                "icon": "⚡",
                "difficulty": "Medium"
            },
            {
                "title": "Consistency King",
                "description": "Study for 3 days in a row",
                "reward": "100 bonus XP + streak multiplier",
                "icon": "🔥",
                "difficulty": "Easy"
            },
            {
                "title": "Subject Master",
                "description": "Score 85%+ in 3 different subjects",
                "reward": "300 bonus XP + 'Versatile Scholar' badge",
                "icon": "🌟",
                "difficulty": "Hard"
            }
        ]
        
        return random.choice(challenges)

    def update_leaderboard(self, user_id: str, username: str, points: int):
        """Update the global leaderboard."""
        try:
            leaderboard = {}
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    leaderboard = json.load(f)

            leaderboard[user_id] = {
                "username": username,
                "points": points,
                "last_updated": datetime.now().isoformat()
            }

            with open(self.leaderboard_file, 'w') as f:
                json.dump(leaderboard, f, indent=2)
        except Exception as e:
            st.error(f"Error updating leaderboard: {e}")

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get the top users from leaderboard."""
        try:
            if not os.path.exists(self.leaderboard_file):
                return []

            with open(self.leaderboard_file, 'r') as f:
                leaderboard = json.load(f)

            # Sort by points descending
            sorted_users = sorted(
                leaderboard.items(),
                key=lambda x: x[1]["points"],
                reverse=True
            )

            return [
                {
                    "user_id": user_id,
                    "username": data["username"],
                    "points": data["points"],
                    "rank": idx + 1
                }
                for idx, (user_id, data) in enumerate(sorted_users[:limit])
            ]
        except:
            return []

    def get_user_rank(self, user_id: str) -> int:
        """Get user's current rank on leaderboard."""
        leaderboard = self.get_leaderboard(100)  # Get more entries to find rank
        for entry in leaderboard:
            if entry["user_id"] == user_id:
                return entry["rank"]
        return len(leaderboard) + 1


# Global gamification manager
game_manager = GameificationManager()

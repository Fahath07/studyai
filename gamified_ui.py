#!/usr/bin/env python3
"""
Gamified UI Components for StudyMate
Beautiful, engaging interfaces for the gamification system
"""

import streamlit as st
from gamification import game_manager
from datetime import datetime
import time

def render_gamification_styles():
    """Render CSS styles for gamification components."""
    st.markdown("""
    <style>
    /* Gamification Styles */
    .game-header {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
        border: 2px solid rgba(255, 215, 0, 0.4);
    }
    
    .game-header h2 {
        color: #1a1a1a;
        margin: 0;
        font-size: 2rem;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .points-display {
        background: linear-gradient(135deg, #00D4AA, #0099CC);
        border-radius: 20px;
        padding: 15px;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 1.5rem;
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.4);
        margin: 10px 0;
    }
    
    .badge-container {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 165, 0, 0.1));
        border: 2px solid rgba(255, 215, 0, 0.3);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    
    .badge-item {
        display: inline-block;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 25px;
        padding: 10px 15px;
        margin: 5px;
        color: #1a1a1a;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
        animation: badgeGlow 2s infinite alternate;
    }
    
    @keyframes badgeGlow {
        from { box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3); }
        to { box-shadow: 0 6px 20px rgba(255, 215, 0, 0.6); }
    }
    
    .leaderboard-card {
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.95), rgba(22, 33, 62, 0.95));
        border: 2px solid rgba(0, 212, 170, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .leaderboard-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 10px;
        background: rgba(0, 212, 170, 0.1);
        border: 1px solid rgba(0, 212, 170, 0.2);
    }
    
    .leaderboard-item.current-user {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 165, 0, 0.2));
        border: 2px solid rgba(255, 215, 0, 0.5);
        font-weight: bold;
    }
    
    .rank-badge {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #1a1a1a;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .challenge-card {
        background: linear-gradient(135deg, rgba(255, 99, 132, 0.1), rgba(255, 159, 64, 0.1));
        border: 2px solid rgba(255, 99, 132, 0.3);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
    }
    
    .progress-bar {
        background: rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        height: 20px;
        overflow: hidden;
        margin: 10px 0;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #00D4AA, #0099CC);
        height: 100%;
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    .streak-fire {
        font-size: 2rem;
        animation: fireFlicker 1s infinite alternate;
    }
    
    @keyframes fireFlicker {
        from { transform: scale(1) rotate(-2deg); }
        to { transform: scale(1.1) rotate(2deg); }
    }
    
    .achievement-popup {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: #1a1a1a;
        font-weight: bold;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.5);
        animation: achievementBounce 0.6s ease-out;
    }
    
    @keyframes achievementBounce {
        0% { transform: scale(0.3) rotate(-10deg); opacity: 0; }
        50% { transform: scale(1.1) rotate(5deg); opacity: 1; }
        100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)

def display_quiz_results_gamified(correct: int, total: int, time_taken: int, subject: str = "General"):
    """Display gamified quiz results with points, badges, and motivation."""
    render_gamification_styles()
    
    # Get user data
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('user_id', 'demo_user')
    username = user_data.get('username', 'Student')
    
    # Load user progress
    user_progress = game_manager.load_user_progress(user_id)
    
    # Calculate previous best for this subject
    subject_stats = user_progress.get('subject_stats', {})
    previous_best = subject_stats.get(subject, {}).get('best_accuracy', 0)
    
    # Calculate score
    score_data = game_manager.calculate_quiz_score(correct, total, time_taken, previous_best)
    
    # Check for new badges
    quiz_result = {
        "accuracy": score_data["accuracy"],
        "time_taken": time_taken,
        "subject": subject
    }
    new_badges = game_manager.check_new_badges(user_progress, quiz_result)
    
    # Update user progress
    old_points = user_progress["total_points"]
    user_progress["total_points"] += score_data["total_points"]
    user_progress["quizzes_completed"] += 1
    user_progress["total_questions_answered"] += total
    user_progress["correct_answers"] += correct
    
    # Update subject stats
    if subject not in user_progress["subject_stats"]:
        user_progress["subject_stats"][subject] = {"quizzes": 0, "best_accuracy": 0, "total_points": 0}
    
    user_progress["subject_stats"][subject]["quizzes"] += 1
    user_progress["subject_stats"][subject]["best_accuracy"] = max(
        user_progress["subject_stats"][subject]["best_accuracy"],
        score_data["accuracy"]
    )
    user_progress["subject_stats"][subject]["total_points"] += score_data["total_points"]
    
    # Update streak
    today = datetime.now().date().isoformat()
    if user_progress.get("last_activity") != today:
        user_progress["current_streak"] += 1
        user_progress["best_streak"] = max(user_progress["best_streak"], user_progress["current_streak"])
        user_progress["last_activity"] = today
    
    # Add new badges
    for badge in new_badges:
        user_progress["badges_earned"].append(badge)
        user_progress["total_points"] += badge["points"]
    
    # Update rank
    user_progress["rank"] = game_manager.get_rank_from_points(user_progress["total_points"])
    
    # Save progress
    game_manager.save_user_progress(user_id, user_progress)
    
    # Update leaderboard
    game_manager.update_leaderboard(user_id, username, user_progress["total_points"])
    
    # Display results
    st.markdown(f"""
    <div class="game-header">
        <h2>🎯 Quiz Results – {subject}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Score breakdown
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="points-display">
            ✅ Score: {correct}/{total}<br>
            📊 {score_data['accuracy']:.1f}%
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="points-display">
            ⚡ Time: {time_taken}s<br>
            🏃 Speed Bonus: +{score_data['speed_bonus']}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="points-display">
            💎 Points Earned<br>
            +{score_data['total_points']}
        </div>
        """, unsafe_allow_html=True)
    
    # Points breakdown
    st.markdown("### 📈 Points Breakdown")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Base Points", f"+{score_data['base_points']}", help="10 points per correct answer")
    with col2:
        st.metric("Accuracy Bonus", f"+{score_data['accuracy_bonus']}", help="Bonus for high accuracy")
    with col3:
        st.metric("Speed Bonus", f"+{score_data['speed_bonus']}", help="Bonus for quick completion")
    with col4:
        st.metric("Improvement", f"+{score_data['improvement_bonus']}", help="Bonus for beating previous best")
    
    # New badges
    if new_badges:
        st.markdown("### 🏆 New Badges Unlocked!")
        badge_html = ""
        for badge in new_badges:
            badge_html += f"""
            <div class="badge-item">
                {badge['icon']} {badge['name']}<br>
                <small>{badge['description']}</small><br>
                <strong>+{badge['points']} points</strong>
            </div>
            """
        
        st.markdown(f'<div class="badge-container">{badge_html}</div>', unsafe_allow_html=True)
        st.balloons()
    
    # Total progress
    st.markdown(f"""
    <div class="points-display">
        💎 Total Points: {old_points} → {user_progress['total_points']} 
        (+{user_progress['total_points'] - old_points})
    </div>
    """, unsafe_allow_html=True)
    
    # Current rank and streak
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1)); border-radius: 10px; margin: 10px 0;">
            <h4 style="color: #00D4AA; margin: 0;">🎖️ Current Rank</h4>
            <p style="font-size: 1.2rem; margin: 5px 0; color: #EAEAEA;">{user_progress['rank']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        streak_icon = "🔥" if user_progress['current_streak'] >= 5 else "📅"
        st.markdown(f"""
        <div style="text-align: center; padding: 15px; background: linear-gradient(135deg, rgba(255, 99, 132, 0.1), rgba(255, 159, 64, 0.1)); border-radius: 10px; margin: 10px 0;">
            <h4 style="color: #FF6384; margin: 0;">{streak_icon} Study Streak</h4>
            <p style="font-size: 1.2rem; margin: 5px 0; color: #EAEAEA;">{user_progress['current_streak']} days</p>
        </div>
        """, unsafe_allow_html=True)

def display_leaderboard():
    """Display the gamified leaderboard."""
    render_gamification_styles()
    
    st.markdown("### 🏆 Leaderboard")
    
    # Get leaderboard data
    leaderboard = game_manager.get_leaderboard(10)
    user_data = st.session_state.get('user_data', {})
    current_user_id = user_data.get('user_id', 'demo_user')
    
    if not leaderboard:
        st.info("🎯 Be the first to appear on the leaderboard! Complete a quiz to get started.")
        return
    
    # Display leaderboard
    leaderboard_html = '<div class="leaderboard-card">'
    
    for entry in leaderboard:
        if entry["username"] == "rohith@123":
            continue  # Skip this user
        is_current_user = entry["user_id"] == current_user_id
        user_class = "current-user" if is_current_user else ""
        # Rank emoji
        rank_emoji = ""
        if entry["rank"] == 1:
            rank_emoji = "👑"
        elif entry["rank"] == 2:
            rank_emoji = "🥈"
        elif entry["rank"] == 3:
            rank_emoji = "🥉"
        leaderboard_html += f"""
        <div class="leaderboard-item {user_class}">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div class="rank-badge">{entry['rank']}</div>
                <span style="font-size: 1.2rem;">{rank_emoji}</span>
                <strong style="color: {'#FFD700' if is_current_user else '#EAEAEA'};">
                    {entry['username']} {'(You)' if is_current_user else ''}
                </strong>
            </div>
        </div>
        """
    
    leaderboard_html += '</div>'
    st.markdown(leaderboard_html, unsafe_allow_html=True)

def display_next_challenge():
    """Display the next challenge for the user."""
    render_gamification_styles()
    
    user_data = st.session_state.get('user_data', {})
    user_id = user_data.get('user_id', 'demo_user')
    user_progress = game_manager.load_user_progress(user_id)
    
    challenge = game_manager.generate_next_challenge(user_progress)
    
    st.markdown(f"""
    <div class="challenge-card">
        <h3 style="color: #FF6384; margin-top: 0;">🎯 Next Challenge</h3>
        <div style="font-size: 2rem; margin: 10px 0;">{challenge['icon']}</div>
        <h4 style="color: #EAEAEA; margin: 10px 0;">{challenge['title']}</h4>
        <p style="color: #EAEAEA; opacity: 0.9; margin: 10px 0;">{challenge['description']}</p>
        <div style="background: rgba(255, 215, 0, 0.2); border-radius: 10px; padding: 10px; margin: 10px 0;">
            <strong style="color: #FFD700;">🎁 Reward: {challenge['reward']}</strong>
        </div>
        <div style="font-size: 0.9rem; color: #EAEAEA; opacity: 0.7;">
            Difficulty: {challenge['difficulty']}
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_motivational_message(performance: dict, user_progress: dict):
    """Display motivational message based on performance."""
    message = game_manager.get_motivational_message(performance, user_progress)
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 212, 170, 0.1), rgba(0, 153, 204, 0.1)); 
                border: 2px solid rgba(0, 212, 170, 0.3); 
                border-radius: 15px; 
                padding: 20px; 
                text-align: center; 
                margin: 20px 0;">
        <h3 style="color: #00D4AA; margin-top: 0;">💬 StudyMate Says:</h3>
        <p style="font-size: 1.2rem; color: #EAEAEA; margin: 0; font-style: italic;">
            "{message}"
        </p>
    </div>
    """, unsafe_allow_html=True)

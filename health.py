import streamlit as st
import pandas as pd
import random
import io
import requests
import matplotlib.pyplot as plt
from transformers import pipeline
from streamlit_lottie import st_lottie

# Page config
st.set_page_config(page_title="Healia - AI Herbal & Mental Health Assistant", layout="centered", page_icon="🌿")

# Load Lottie animation (cached)
@st.cache_resource
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_mental = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json")
if lottie_mental:
    st_lottie(lottie_mental, height=200, key="mental")
else:
    st.warning("⚠️ Could not load animation. Check your internet.")

# Title & description
st.title("🌿 Healia: AI-Powered Herbal & Mental Health Assistant")
st.markdown("Empowering whole-person wellness by combining traditional healing with modern AI.")

# Sidebar with welcome message and inputs
with st.sidebar:
    st.markdown("## 🌿 Welcome to Healia!")
    st.markdown(
        """
        This app combines AI-powered mental health check-ins  
        with herbal remedy suggestions to support your wellbeing.
        
        Use the form below to share how you're feeling today.
        """
    )

    # Mental health input widgets in sidebar
    user_input = st.text_area("Describe your current emotional state:", height=150)
    mood = st.radio("🌡️ Rate your current mood:", ["😃 Happy", "😐 Neutral", "😔 Sad", "😰 Anxious", "😤 Angry"], horizontal=True)
    analyze_button = st.button("🧠 Analyze Mood")

# Tabs
tabs = st.tabs(["🧠 Mental Health Copilot", "🌿 Herbal Remedy Finder"])

# Load sentiment model (cached)
@st.cache_resource
def load_sentiment_model():
    return pipeline("sentiment-analysis")

sentiment_model = load_sentiment_model()

def analyze_sentiment(text):
    if "happy" in text.lower():
        return {"label": "POSITIVE", "score": 0.99}
    elif "sad" in text.lower():
        return {"label": "NEGATIVE", "score": 0.99}
    else:
        return {"label": "NEUTRAL", "score": 0.5}

# Initialize mood log in session state
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# --- Mental Health Copilot Tab ---
with tabs[0]:
    st.header("🧠 Mental Health Check-In")
    st.markdown("Tell us how you're feeling today. Our AI will try to understand and support you.")

    if analyze_button:
        if user_input.strip():
            result = [analyze_sentiment(user_input)]

            label = result[0]["label"]
            score = result[0]["score"]

            st.session_state.mood_log.append((mood, user_input))

            # Visual feedback
            if label == "POSITIVE":
                st.success(f"You seem to be feeling **positive** today! 🌞 Confidence: {score:.2f}")
                st.balloons()
                st.info("💬 Healia says: *\"That's wonderful to hear! Keep nurturing those good vibes.\"*")
            elif label == "NEGATIVE":
                st.warning(f"You may be experiencing some negative emotions. 💭 Confidence: {score:.2f}")
                st.snow()
                st.warning("💬 Healia says: *\"I hear you. It's okay to feel this way. Take a deep breath — you’re not alone.\"*")
                st.markdown("[🧘 Try this 5-minute guided breathing](https://www.youtube.com/watch?v=inpok4MKVLM)")
            else:
                st.info("Your emotions are complex today. Consider reflecting or journaling.")
        else:
            st.error("Please enter your feelings to continue.")

    # Journal Prompt Generator
    st.markdown("### ✍️ Need help starting a journal?")
    if st.button("🎯 Get a Journal Prompt"):
        journal_prompts = [
            "What is one thing you’re grateful for today?",
            "Describe a moment today that made you smile.",
            "Write about a challenge and how you’re coping.",
            "What emotions have you felt most strongly today?",
            "What’s one self-care action you can do right now?"
        ]
        st.info(random.choice(journal_prompts))

    # Show mood log and visualizations if any entries
    if st.session_state.mood_log:
        st.markdown("### 📝 Mood Log")
        for i, (m, txt) in enumerate(st.session_state.mood_log, 1):
            st.markdown(f"**Entry {i}:** {m} — _\"{txt}\"_")

        # Create dataframe for visualizations
        df = pd.DataFrame(st.session_state.mood_log, columns=["Mood", "Entry"])
        mood_scores = {"😃 Happy": 5, "😐 Neutral": 3, "😔 Sad": 2, "😰 Anxious": 1, "😤 Angry": 1}
        df["MoodScore"] = df["Mood"].map(mood_scores)

        # Line chart for mood scores over time
        st.subheader("📈 Mood Score Over Time")
        st.line_chart(df["MoodScore"], use_container_width=True)

        # Bar chart of mood frequency
        st.subheader("📊 Mood Frequency")
        mood_counts = df["Mood"].value_counts()
        st.bar_chart(mood_counts)

        # Pie chart for mood distribution
        st.subheader("🧁 Mood Distribution")
        fig, ax = plt.subplots()
        ax.pie(mood_counts, labels=mood_counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)

        # Download option
        if st.button("📥 Download Mood Log CSV"):
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button("Download CSV", csv_buffer.getvalue(), file_name="mood_log.csv", mime="text/csv")

# --- Herbal Remedy Finder Tab ---
with tabs[1]:
    st.header("🌿 Personalized Herbal Remedy Finder")
    st.markdown("Select your symptom or condition to receive AI-powered herbal suggestions.")

    herbal_data = {
        "headache": ["Ginger tea", "Willow bark", "Peppermint oil"],
        "anxiety": ["Chamomile", "Ashwagandha", "Valerian root"],
        "insomnia": ["Lavender", "Lemon balm", "Passionflower"],
        "indigestion": ["Peppermint", "Ginger", "Fennel seeds"],
        "cold": ["Echinacea", "Ginger", "Elderberry"]
    }

    herbal_tips = {
        "Ginger tea": "Ginger helps reduce inflammation and ease nausea.",
        "Willow bark": "Often called ‘natural aspirin’, good for relieving pain.",
        "Peppermint oil": "Used for headaches and digestive relief.",
        "Chamomile": "Chamomile is commonly used to relax the mind and aid sleep.",
        "Ashwagandha": "An adaptogen that helps the body cope with stress.",
        "Valerian root": "Promotes relaxation and can help with sleep.",
        "Lavender": "Lavender can reduce anxiety and promote calm.",
        "Lemon balm": "A calming herb, often used for anxiety and sleep.",
        "Passionflower": "Used for insomnia, anxiety, and nervous disorders.",
        "Fennel seeds": "Great for relieving bloating and indigestion.",
        "Echinacea": "Boosts the immune system and fights infections.",
        "Elderberry": "Popular for fighting cold and flu symptoms."
    }

    condition = st.selectbox("Choose a condition:", [""] + list(herbal_data.keys()))
    if condition:
        remedies = herbal_data[condition]
        suggestion = random.choice(remedies)
        st.success(f"✅ Suggested remedy for **{condition}**: **{suggestion}**")

        if suggestion in herbal_tips:
            st.info(f"🧪 Herbal Insight: {herbal_tips[suggestion]}")

        st.markdown("🔍 *Always consult a healthcare professional before starting herbal treatments.*")

    # Q&A about herbs
    st.markdown("### 💬 Ask about an herb")
    herb_query = st.text_input("Herb name:")
    if herb_query:
        tip = herbal_tips.get(herb_query.title())
        if tip:
            st.info(f"🌿 {herb_query.title()}: {tip}")
        else:
            st.warning("No info found. Try another herb.")

# --- Personalized Wellness Plan ---
st.markdown("## 📅 Your Personalized Wellness Plan")

# Determine current mood and condition for customized plan
current_mood = mood if 'mood' in locals() else None
current_condition = condition if 'condition' in locals() else None

def generate_wellness_plan(mood, condition):
    plan = []
    # Mood-based suggestions
    if mood in ["😃 Happy", "😐 Neutral"]:
        plan.append("🌞 Maintain your positive energy with 10 minutes of morning sunlight.")
        plan.append("🧘 Practice mindfulness or meditation for 5 minutes today.")
    elif mood in ["😔 Sad", "😰 Anxious", "😤 Angry"]:
        plan.append("🧘 Try deep breathing exercises or a short walk to ease tension.")
        plan.append("📓 Write down 3 things you are grateful for.")
    else:
        plan.append("💡 Take time to reflect on your emotions today.")
    
    # Condition-based herbal tips
    if condition:
        condition_tips = {
            "headache": "💧 Stay hydrated and try ginger tea or peppermint oil.",
            "anxiety": "🌿 Consider chamomile tea or ashwagandha supplements.",
            "insomnia": "🌙 Use lavender essential oil or lemon balm before bed.",
            "indigestion": "🍵 Drink fennel seed tea after meals.",
            "cold": "🍯 Take elderberry syrup and rest well."
        }
        tip = condition_tips.get(condition, "")
        if tip:
            plan.append(tip)
    
    return plan

# Generate and show plan if user has provided input
if analyze_button or condition:
    plan_items = generate_wellness_plan(current_mood, current_condition)
    if plan_items:
        for item in plan_items:
            st.markdown(f"- {item}")

    # Motivational Quote
    quotes = [
        "“You don’t have to control your thoughts. You just have to stop letting them control you.” — Dan Millman",
        "“Self-care is how you take your power back.” — Lalah Delia",
        "“The greatest wealth is health.” — Virgil",
        "“Healing takes time, and asking for help is a courageous step.” — Mariska Hargitay"
    ]
    st.markdown(f"### 💡 Motivational Quote\n> {random.choice(quotes)}")

    # Progress tracker using session state
    if "days_used" not in st.session_state:
        st.session_state.days_used = 0
    st.session_state.days_used += 1
    st.markdown(f"⏳ You’ve used Healia for **{st.session_state.days_used}** days. Keep going! 🎉")

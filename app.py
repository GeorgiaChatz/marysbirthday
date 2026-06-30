import time
import uuid
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Birthday Quiz", page_icon="🎉", layout="centered")

QUESTIONS = [
    {
        "q": "What is Maria's favourite drink?",
        "options": ["Aperol Spritz", "Wine", "Gin & Tonic", "Espresso Martini"],
        "answer": "Aperol Spritz",
    },
    {
        "q": "Which country would Maria choose?",
        "options": ["Greece", "Austria", "Switzerland", "Italy"],
        "answer": "Greece",
    },
]

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

GAME_ID = "birthday_game_1"


def get_game():
    res = supabase.table("games").select("*").eq("game_id", GAME_ID).execute()
    if not res.data:
        supabase.table("games").insert({
            "game_id": GAME_ID,
            "current_q": 0,
            "locked": False,
            "winner": "",
            "started": False
        }).execute()
    return supabase.table("games").select("*").eq("game_id", GAME_ID).execute().data[0]


def update_game(data):
    supabase.table("games").update(data).eq("game_id", GAME_ID).execute()


def add_player(name):
    existing = supabase.table("players").select("*").eq("game_id", GAME_ID).eq("name", name).execute()
    if not existing.data:
        supabase.table("players").insert({
            "game_id": GAME_ID,
            "name": name,
            "score": 0
        }).execute()


def get_players():
    return supabase.table("players").select("*").eq("game_id", GAME_ID).order("score", desc=True).execute().data


def add_point(name):
    player = supabase.table("players").select("*").eq("game_id", GAME_ID).eq("name", name).execute().data[0]
    supabase.table("players").update({
        "score": player["score"] + 1
    }).eq("id", player["id"]).execute()


st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #fff1f7 0%, #fffafc 100%);
}
.big-title {
    text-align: center;
    font-size: 36px;
    font-weight: 800;
    color: #d63384;
}
.card {
    background: white;
    padding: 22px;
    border-radius: 22px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🎉 Birthday Quiz</div>', unsafe_allow_html=True)

if "name" not in st.session_state:
    st.session_state.name = ""

name = st.text_input("Your name", value=st.session_state.name)

if st.button("Join game"):
    if name.strip():
        st.session_state.name = name.strip()
        add_player(st.session_state.name)
        st.success(f"Joined as {st.session_state.name}")

game = get_game()

st.divider()

if st.session_state.name == "HOST":
    st.subheader("Host controls")

    if st.button("Start game"):
        update_game({"started": True, "current_q": 0, "locked": False, "winner": ""})
        st.rerun()

    if st.button("Next question"):
        next_q = min(game["current_q"] + 1, len(QUESTIONS) - 1)
        update_game({"current_q": next_q, "locked": False, "winner": ""})
        st.rerun()

    if st.button("Reset game"):
        supabase.table("players").delete().eq("game_id", GAME_ID).execute()
        update_game({"current_q": 0, "locked": False, "winner": "", "started": False})
        st.rerun()

if not game["started"]:
    st.info("Waiting for the host to start the game...")
else:
    q = QUESTIONS[game["current_q"]]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(f"Question {game['current_q'] + 1}/{len(QUESTIONS)}")
    st.write(f"### {q['q']}")

    choice = st.radio("Choose your answer:", q["options"], key=f"q_{game['current_q']}")

    if st.button("Submit answer", disabled=game["locked"]):
        fresh_game = get_game()

        if not fresh_game["locked"]:
            is_correct = choice == q["answer"]

            if is_correct:
                add_point(st.session_state.name)
                update_game({
                    "locked": True,
                    "winner": st.session_state.name
                })
                st.success("Correct! You were first 🎉")
                st.balloons()
            else:
                update_game({
                    "locked": True,
                    "winner": f"{st.session_state.name} answered wrong"
                })
                st.error("Wrong answer! Question locked 😅")

            time.sleep(1)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    game = get_game()

    if game["locked"]:
        st.warning(f"Locked! {game['winner']}")

st.divider()

st.subheader("🏆 Leaderboard")
players = get_players()

for p in players:
    st.write(f"**{p['name']}** — {p['score']} points")

st.caption("Tip: use name HOST to control the game.")

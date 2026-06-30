import time
import uuid
import streamlit as st
from supabase import create_client

st.set_page_config(page_title="Birthday Quiz", page_icon="🎉", layout="centered")

QUESTIONS = [
    {
        "q": "Ποιο είναι το αγαπημένο ποτό της Μαρίας;",
        "options": ["Aperol", "Paloma", "Gin", "Ρούμι Cola"],
        "answer": "Ρούμι Cola",
    },
    {
        "q": "Αν η Μαρία δεν ήταν οδοντίατρος, τι θα ήταν;",
        "options": [
            "Κάπου στα βουνά θα τη ψάχναμε",
            "Σε νησί σερβιτόρα",
            "Γιατρός",
            "Όλα τα παραπάνω",
        ],
        "answer": "Όλα τα παραπάνω",
    },
    {
        "q": "Πού ξοδεύει τα περισσότερα λεφτά της η Μαρία;",
        "options": [
            "Φαγητό",
            "Τσιγάρα",
            "Μασάζ",
            "Φαγητό & Laser",
        ],
        "answer": "Φαγητό & Laser",
    },
    {
        "q": "Ποιο είναι το πιο όμορφο σημείο της Μαρίας;",
        "options": [
            "Ακατάλληλη απάντηση 😂",
            "Το πρόσωπό της",
            "Τα άκρα της",
        ],
        "answer": "Το πρόσωπό της",
    },
    {
        "q": "Τι πιστεύει η Μαρία για τον εαυτό της;",
        "options": [
            "Χάλια, χάλια, χάλια",
            "Παιδί σάντουιτς",
            "Ντάξει, καλή είμαι κάποιες φορές",
            "Όλα τα παραπάνω",
        ],
        "answer": "Όλα τα παραπάνω",
    },
    {
        "q": "Πόσο απέχει η Μαρία από τα πρώτα -άντα;",
        "options": [
            "Χα-χα... έρχεται!",
            "Έχουμε ακόμα",
            "Αργεί πολύ ακόμα",
        ],
        "answer": "Χα-χα... έρχεται!",
    },
    {
        "q": "Τι κάνει η Μαρία για να ξεχαστεί από άσχημες σκέψεις;",
        "options": [
            "Βλέπει τουρκικά",
            "Παίζει παιχνίδια στο κινητό",
            "Κοιμάται",
        ],
        "answer": "Βλέπει τουρκικά",
    },
    {
        "q": "Ποιο ήταν το πιο πετυχημένο γκομενάκι της Μαρίας;",
        "options": [
            "Ασχολίαστο",
            "Οι Γιωργήδες",
            "Αλέξης",
        ],
        "answer": "Οι Γιωργήδες",
    },
    {
        "q": "Τι θα προτιμούσε να φάει;",
        "options": [
            "Ιταλικό",
            "Σουβλάκια",
            "Μοσχαράκι γιουβέτσι",
        ],
        "answer": "Ιταλικό",
    },
    {
        "q": "Ποιο ήταν το χειρότερο ιατρείο που έχει βρεθεί μέχρι σήμερα;",
        "options": [
            "Κυρία Ιωάννα δαγκωτό",
            "Κυρία Ιωάννα, κι ας είχε και τα καλά της",
            "Μπορεί η κυρία Ιωάννα",
        ],
        "answer": "Κυρία Ιωάννα, κι ας είχε και τα καλά της",
    },
    {
        "q": "Αν άνοιγε δικό της ιατρείο, τι θα της άρεσε περισσότερο;",
        "options": [
            "Η επιλογή υπαλλήλων",
            "Η επιλογή εργαλείων",
            "Η επιλογή επίπλων & design",
        ],
        "answer": "Η επιλογή επίπλων & design",
    },
    {
        "q": "Αν έπαιρνε τον ίδιο μισθό σε όλες αυτές τις χώρες, πού θα πήγαινε;",
        "options": [
            "Ελβετία",
            "Στρασβούργο",
            "Καλή είναι κι η Ελλαδίτσα",
            "Ισπανία",
        ],
        "answer": "Ισπανία",
    },
    {
        "q": "Πόσους έρπητες βγάζει η Μαρία τον τελευταίο καιρό κάθε μήνα;",
        "options": [
            "Πολλούς",
            "Πάρα πολλούς",
            "Αρκετούς",
        ],
        "answer": "Πολλούς",
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

import streamlit as st
from pyvis.network import Network
import requests

st.set_page_config(page_title="My Streamlit App", layout="wide")

tab_names = ["Beginner", "Advanced", "Challenge"]
tabs = st.tabs(tab_names)

def get_shortest_path(algorithm, start_word, end_word, banned_words):
    url = f"http://localhost:5000/shortest-path/{algorithm}"  # Adjust if hosted elsewhere
    payload = {
        "start_word": start_word,
        "target_word": end_word,
        "banned_words": banned_words
    }

    try:
        response = requests.get(url, json=payload)
        response_data = response.json()

        if response.status_code == 200:
            return response_data
        else:
            return {"error": "Failed to retrieve data", "details": response_data}
        
    except requests.exceptions.RequestException as e:
        return {"error": "Request failed", "details": str(e)}

def start_game(difficulty, game_state_name):
    if game_state_name not in st.session_state:
        api_url = f"http://127.0.0.1:5000/start-game/{difficulty}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()

            st.session_state[game_state_name] = {
                "start_word": data["start_word"],
                "end_word": data["end_word"]
            }

            if "banned_words" in data:
                st.session_state[game_state_name]["banned_words"] = data["banned_words"]
            else:
                st.session_state[game_state_name]["banned_words"] = []
        else:
            st.session_state[game_state_name] = None

def validate_word(game_state_name, input_variable):

    if game_state_name not in st.session_state:
        st.error("Game state not initialized properly.")
        return

    if not st.session_state[game_state_name]["current_word"] or not st.session_state[input_variable] or len(st.session_state[game_state_name]["current_word"]) != len(st.session_state[input_variable]):
        st.error("Please enter a valid word.")
        return

    if st.session_state[game_state_name]["current_word"] == st.session_state[input_variable] and st.session_state[input_variable] != st.session_state[game_state_name]["end_word"]:
        st.error(f"❌ '{st.session_state[input_variable]}' is the same as current word!")
        return

    api_url = "http://127.0.0.1:5000/validate-move"
    payload = {
        "current_word": st.session_state[game_state_name]["current_word"],
        "target_word": st.session_state[input_variable],
        "banned_words": st.session_state[game_state_name]["banned_words"]
    }
    response = requests.post(api_url, json=payload)

    if response.status_code == 200:
        data = response.json()

        if data.get("valid"):
            st.session_state[game_state_name]["guessed_words"].append(st.session_state[input_variable])  # Add to list
            st.success(f"✅ '{st.session_state[input_variable]}' is a valid move!")
            st.session_state[game_state_name]["current_word"] = st.session_state[input_variable]
            st.rerun()
        else:
            st.error(f"❌ '{st.session_state[input_variable]}' is not a valid move!")

    if st.session_state[input_variable] == st.session_state[game_state_name]["end_word"]:
        st.success(f"✅ You reached the end word in only {len(st.session_state[game_state_name]["guessed_words"])}!")

def create_graph(words_dict):
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    
    for word, neighbors in words_dict.items():
        if word not in net.get_nodes():
            net.add_node(word, label=word, title=word)

        for neighbor in neighbors:
            if neighbor not in net.get_nodes():
                net.add_node(neighbor, label=neighbor, title=neighbor)
            net.add_edge(word, neighbor)
    
    # Generate the graph HTML
    net.show_buttons(filter_=["physics"])
    return net

def display_graph(depth, start_word):
    response = requests.get(f"http://localhost:5000/graph/{depth}", json={"start_word": start_word})
    
    if response.status_code == 200:
        words_dict = response.json()
        print(words_dict)
        
        net = create_graph(words_dict)

        graph_html = net.generate_html()
        st.components.v1.html(graph_html, height=600)
    else:
        st.error("Error fetching graph data from API.")

def tab_container(state_name, input_name, difficulty, tabName):
    st.subheader(tabName)

    # state_name = "beginner_game_state"
    # input_name = "beginner_user_input"

    # start_game("beginner", state_name)
    start_game(difficulty, state_name)

    if st.session_state[state_name] is not None:
        start_word = st.session_state[state_name]["start_word"]
        end_word = st.session_state[state_name]["end_word"]
        banned_words = st.session_state[state_name]["banned_words"]



        if "guessed_words" not in st.session_state[state_name]:
            st.session_state[state_name]["guessed_words"] = []

        st.write(f"**Start Word:** {st.session_state[state_name]["start_word"]}")
        st.write(f"**End Word:** {st.session_state[state_name]["end_word"]}")

        if "shortest_paths" not in st.session_state[state_name]:
            st.session_state[state_name]["shortest_paths"] = {
                "bfs": get_shortest_path("bfs", start_word, end_word, banned_words),
                "ucs": get_shortest_path("ucs", start_word, end_word, banned_words),
                "astar": get_shortest_path("astar", start_word, end_word, banned_words)
            }

        shortest_paths = st.session_state[state_name]["shortest_paths"]

        st.write(f"**Shortest path with bfs:** {shortest_paths['bfs']}")
        st.write(f"**Shortest path with ucs:** {shortest_paths['ucs']}")
        st.write(f"**Shortest path with astar:** {shortest_paths['astar']}")

        if "banned_words" in st.session_state[state_name]:
            st.write(f"🚫 **Banned Words:** {', '.join(st.session_state[state_name]["banned_words"])}")

        if "current_word" not in st.session_state[state_name]:
            st.session_state[state_name]["current_word"] = st.session_state[state_name]["start_word"]

        st.write(f"**Current Word:** {st.session_state[state_name]["current_word"]}")

        with st.form(key=f"{difficulty}_form"):
            st.subheader("🔡 Enter a Word")
            user_input = st.text_input("Type your word:", key=input_name).strip()

            submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            validate_word(state_name, input_name)

        if st.session_state[input_name] and len(st.session_state[input_name]) > 0:
            if len(st.session_state[input_name]) == len(st.session_state[input_name]):
                st.success("✅ Word length is correct!")
            else:
                st.error(f"❌ Word must be exactly {len(st.session_state[state_name]["start_word"])} letters long!")

        if st.session_state[state_name]["guessed_words"]:
            st.write("✅ **Guessed Moves:**")
            for word in st.session_state[state_name]["guessed_words"]:
                st.write(f"- {word}")
    
        display_graph(2, start_word)

    else:
        st.error("Error fetching data. Please reload!")

for tab, name in zip(tabs, tab_names):
    with tab:
        tab_container(f"{name.lower()}_game_state", f"{name.lower()}_user_input", f"{name.lower()}", name)
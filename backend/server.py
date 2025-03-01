from flask import Flask, render_template, request, jsonify
import random
from enum import Enum
from collections import defaultdict

from ucs_module import ucs
from astar_module import astar

app = Flask(__name__)

def remove_backslash_n(words_list): #removes /n at end of word
    for i in range(len(words_list)):
        words_list[i] = words_list[i][0:len(words_list[i])-1]

def length(word): # gets length of word
    return len(word)

def is_one_letter_diff(word1,word2):
    if( len(word1) != len(word1) ):
        return False
    count = 0
    for i in range(len(word1)):
        if word1[i] != word2[i]:
            count += 1
        if count == 2:
            return False
    if count == 1:
        return True

def check_valid_move(start_word,target_word,words_graph):
    visited = set()
    queue = [start_word]
    while queue:
        child_node = queue.pop(0)
        visited.add(child_node)
        for word in words_graph[child_node]:
            if word not in visited:
                queue.append(word)
        if target_word in visited:
            return True

    return False

def get_two_connected_words(words_graph, length, max_retries=10):
    valid_words = [word for word in words_graph.keys() if len(word) == length]

    if len(valid_words) < 2:
        return (None, None)
    
    for _ in range(max_retries):
        start_word, end_word = random.sample(valid_words, 2)

        if check_valid_move(start_word, end_word, words_graph):
            return (start_word, end_word)
    
    return (None, None)

def get_banned_words(words_graph, start_word, end_word, iterations=5):
    words = []
    for _ in range(iterations):
        words = words + ucs(words_graph, start_word, end_word, words)[1:-1]
        print(words)

    return words

def get_words_list(fileName):
    # this gets the words from file and stores in list
    words_file = open(fileName,'r')
    words_list = words_file.readlines()
    words_list = list(filter(lambda x: (len(x)>=4 and len(x)<=6),words_list))
    remove_backslash_n(words_list)
    words_list.sort(reverse=False,key=length)
    return words_list

# Group words by their length
def categorize_words_by_length(words_list):
    length_dict = defaultdict(list)
    for word in words_list:
        length_dict[len(word)].append(word)
    return length_dict

# Build the graph using words that differ by exactly one letter
def build_graph(words_list):
    words_graph = defaultdict(list)
    
    # Categorize words by length
    length_dict = categorize_words_by_length(words_list)

    # Now, only compare words of the same length
    for words_of_same_length in length_dict.values():
        for word in words_of_same_length:
            for word2 in words_of_same_length:
                if word != word2:  # Don't compare the same word
                    count = 0
                    # Compare character by character
                    for i in range(len(word)):
                        if word[i] != word2[i]:
                            count += 1
                        if count > 1:
                            break
                    if count == 1:
                        words_graph[word].append(word2)

    return dict(words_graph)

# search by bfs
def bfs(words_graph, start_word, target_word, banned_words=[]):
    visited = set()
    queue = [start_word]
    path =dict()
    path[start_word] = None
    while queue:
        child_node = queue.pop(0)
        if child_node in banned_words:
            continue
        visited.add(child_node)
        for word in words_graph.get(child_node, []):
            if word not in visited:
                queue.append(word)
                path[word] = child_node
        if target_word in visited:
            actual_path = []
            end = target_word
            while end:
                actual_path.append(end)
                end = path[end]
            actual_path.reverse()
            return actual_path

    return []

words_list = get_words_list('words_alpha.txt')
words_graph = build_graph(words_list)
# words_graph = dict()

@app.route("/start-game/<difficulty>", methods=["GET"])
def getStartingWords(difficulty):
    try:
        print(f"Received difficulty: {difficulty}")

        if difficulty == "beginner":
            start_word, end_word = get_two_connected_words(words_graph, 3, 5)
            if start_word is None:
                return jsonify({"error": "No words found for this difficulty"}), 400
            else:
                return jsonify({
                    "start_word": start_word,
                    "end_word": end_word,
                    "banned_words": []
                }), 200

        elif difficulty == "advanced":
            start_word, end_word = get_two_connected_words(words_graph, random.sample([4,5], 1)[0], 5)
            if start_word is None:
                return jsonify({"error": "No words found for this difficulty"}), 400
            else:
                return jsonify({
                    "start_word": start_word,
                    "end_word": end_word,
                    "banned_words": []  # Send empty banned words
                }), 200

        elif difficulty == "challenge":
            start_word, end_word = get_two_connected_words(words_graph, random.sample([4,5,6,7], 1)[0], 5)
            banned_words = get_banned_words(words_graph, start_word, end_word, 2)
            if start_word is None:
                return jsonify({"error": "No words found for this difficulty"}), 400
            else:
                return jsonify({
                    "start_word": start_word,
                    "end_word": end_word,
                    "banned_words": banned_words
                }), 200

        else:
            return "Invalid difficulty"
    except ValueError:
        return jsonify({"error": "Invalid difficulty level"}), 400

@app.route("/validate-move", methods=["POST"])
def validate_move():
    data = request.get_json()
    current_word = data.get("current_word")
    target_word = data.get("target_word")
    banned_words = data.get("banned_words",[])

    if not current_word or not target_word:
        return jsonify({
            "message": "current_word or next_word is not in body"
        })

    if target_word in banned_words:
        return jsonify({
            "message": "This word is banned",
            "valid": False
        })

    isvalid = is_one_letter_diff(current_word, target_word) and check_valid_move(current_word, target_word, words_graph)
    return jsonify({
        "valid": isvalid
    })

@app.route('/shortest-path/<algorithm>', methods=["GET"])
def run_bfs(algorithm):
    data = request.get_json()
    start_word = data.get("start_word")
    target_word = data.get("target_word")
    banned_words = data.get("banned_words",[])

    if not start_word or not target_word:
        return jsonify({
            "message": "current_word or next_word is not in body"
        })

    if target_word in banned_words:
        return jsonify({
            "message": "This word is banned",
            "valid": False
        })

    if algorithm == "bfs":
        return bfs(words_graph, start_word, target_word, banned_words)
    elif algorithm == "ucs":
        return ucs(words_graph, start_word, target_word, banned_words)
    elif algorithm == "astar":
        return astar(words_graph, start_word, target_word, banned_words)
    else:
        return jsonify({
            "message": "Invalid algorithm"
        }), 400


@app.route('/graph/<int:depth>', methods=['GET'])
def get_graph_dict(depth):
    data = request.get_json()
    start_word = data.get("start_word")

    from collections import deque

    words_at_depth = {}
    queue = deque([(start_word, 0)])  # (word, current_depth)
    visited = set()

    while queue:
        word, current_depth = queue.popleft()

        if current_depth > depth:
            return words_at_depth  # No need to continue processing

        if word in visited:
            continue  # Skip already visited words
        
        visited.add(word)
        
        # Add the word and its neighbors to the dictionary
        if current_depth <= depth:
            words_at_depth[word] = words_graph.get(word, [])

        # Add neighbors to the queue to continue exploring
        for neighbor in words_graph.get(word, []):
            if neighbor not in visited:
                queue.append((neighbor, current_depth + 1))
    
    return jsonify(words_at_depth)



if __name__ == '__main__':
    app.run(debug=True)
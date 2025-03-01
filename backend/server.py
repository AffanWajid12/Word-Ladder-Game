from flask import Flask, render_template, request, jsonify
import random
from enum import Enum
from collections import defaultdict

from ucs_module import ucs

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

words_list = get_words_list('words_alpha.txt')
words_graph = build_graph(words_list)
# words_graph = dict()

# the algorithms
# the graph itself
# if in graph check the next one
# beginner 3 words, advanced anywhere between 4 and 5
# greater than six with banned words
# 

@app.route("/start-game/<difficulty>", methods=["GET"])
def getStartingWords(difficulty):
    try:
        print(f"Received difficulty: {difficulty}")

        if difficulty == "beginner":
            start_word, end_word = get_two_connected_words(words_graph, 3, 5)
            if start_word is None:
                return jsonify({"error": "No words found for this difficulty"}), 400
            else:
                return jsonify({"start_word": start_word, "end_word": end_word})

        elif difficulty == "advanced":
            start_word, end_word = get_two_connected_words(words_graph, random.sample([4,5], 1)[0], 5)
            if start_word is None:
                return jsonify({"error": "No words found for this difficulty"}), 400
            else:
                return jsonify({"start_word": start_word, "end_word": end_word})

        elif difficulty == "challenge":
            start_word, end_word = get_two_connected_words(words_graph, random.sample([4,5,6,7], 1)[0], 5)
            banned_words = get_banned_words(words_graph, start_word, end_word, 2)
            return jsonify({
                "start_word": start_word,
                "end_word": end_word,
                "banned_words": banned_words
            })

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

@app.route('/')
def home():
    return "Hello, Flask is running!"

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "This is an API endpoint!"})

if __name__ == '__main__':
    app.run(debug=True)
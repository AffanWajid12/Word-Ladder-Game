
class WNode:
    def __init__(self,word_name,parent,cost):
        self.word_name = word_name
        self.parent = parent
        self.cost = cost
def remove_backslash_n(words_list):
    for i in range(len(words_list)):
        words_list[i] = words_list[i][0:len(words_list[i])-1]

def length(word):
    return len(word)

words_file = open('words_alpha.txt','r')
words_list = words_file.readlines()
words_list = list(filter(lambda x: (len(x)>=4 and len(x)<=6),words_list))
remove_backslash_n(words_list)
words_list.sort(reverse=False,key=length)



# Now we got the whole words in a list
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

words_graph = dict()
for word in words_list:
    words_graph[word] = []
    for word2 in words_list:
        if len(word) == len(word2):
            count = 0
            for i in range(len(word)):
                if word[i] != word2[i]:
                    count += 1
                if count == 2:
                    break
            if count == 1:
                words_graph[word].append(word2)
        else:
            break

print(words_graph)

# Now we got the whole words of list inside a graph. Each word is connected with an another word whose letter difference is by one letter only.

#Bfs to make the word ladder from one word to the next by seeing if they both have a connection of some sort
def bfs(start_word,target_word,words_graph):
    visited = set()
    queue = [start_word]
    path =dict()
    path[start_word] = None
    while queue:
        child_node = queue.pop(0)
        visited.add(child_node)
        for word in words_graph[child_node]:
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

print(bfs('cat','big',words_graph))

print("Welcome to the game")
while True:
    starting_word = input("Enter the starting word: ")
    ending_word = input("Enter the starting word: ")
    if starting_word not in words_graph or ending_word not in words_graph or not check_valid_move(starting_word,ending_word,words_graph):
        print("Seems like there is no path between these two words. Might wanna try a different word or something")
    else:
        print("Ok there is a path so lets play!")
        break

while starting_word != ending_word:
    possible_word = input("Enter the next word. Remember you can only change one letter from {0}: ".format(starting_word))
    if possible_word not in words_graph or not is_one_letter_diff(starting_word,possible_word) or not check_valid_move(possible_word,ending_word,words_graph):
        print(is_one_letter_diff(starting_word,possible_word))
        print("Nope choose again!")
    else:
        print("Good job! Lets get to the next ones!")
        starting_word = possible_word

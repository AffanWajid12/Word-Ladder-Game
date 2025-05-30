import heapq

class _PriorityQueue:
    def __init__(self):
        self.pq = []

    def enqueue(self, new_element):
        heapq.heappush(self.pq, new_element)

    def dequeue(self):
        return heapq.heappop(self.pq)

    def isEmpty(self):
        return len(self.pq) == 0

def _getFullPath(visited, word):
    path = []

    while word is not None:
        path.insert(0, word)
        word = visited.get(word, (None, None))[1]
    return path

def ucs(words_graph, start_word, end_word, banned_words=[]):
    queue = _PriorityQueue()

    queue.enqueue((0, start_word, None))
    visited = {}

    while not queue.isEmpty():
        curr_cost, curr_word, curr_parent = queue.dequeue()

        if curr_word in visited and visited[curr_word][0] <= curr_cost:
            continue

        visited[curr_word] = (curr_cost, curr_parent)

        if (curr_word == end_word):
            return _getFullPath(visited, curr_word)

        for neighbour in words_graph.get(curr_word, []):
            if neighbour in banned_words:
                continue

            new_cost = curr_cost + 1 #each edge is of one cost
            if neighbour not in visited or new_cost < visited[neighbour][0]:
                queue.enqueue((new_cost, neighbour, curr_word))
        
    return []



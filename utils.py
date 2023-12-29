class DFS():
    def __init__(self,adjacency_list):
        self.adjacency_list = adjacency_list
        self.nodes = len(adjacency_list)
        self.visited = [False for _ in range(self.nodes+1)]
        self.clusters = {}
        self.count = 0 
    def get_connected_component(self):
        for node in self.adjacency_list.keys():
            if self.visited[node] == False:
                self.count+=1
                self.clusters.update({self.count:[]})
                self.dfs(node)
        return self.clusters
    def dfs(self,start_node):
        self.clusters[self.count].append(start_node)
        self.visited[start_node] = True
        for i in range(len(self.adjacency_list[start_node])):
            next_node = self.adjacency_list[start_node][i]
            # print("start_node: ",start_node," next_node: ",next_node)
            if self.visited[next_node] == False:
                self.dfs(next_node)

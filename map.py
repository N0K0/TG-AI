import math
from collections import deque
from random import shuffle


class MapManager:
    # noinspection PyUnboundLocalVariable
    def calculate_player_value(self, player_dangerous, enemy_dangerous):
        if player_dangerous and enemy_dangerous:
            value = 0

        elif not player_dangerous and enemy_dangerous:
            value = -10

        elif player_dangerous and not enemy_dangerous:
            value = 10

        elif not player_dangerous and not enemy_dangerous:
            value = -2

        return value

    def print_map(self):
        for line in self.map:
            for tile in line:
                if tile.current_shortest < 100000:
                    print("{:^2}".format(str(tile.current_shortest)), end='')
                else:
                    print("{:^2}".format(str(tile)), end='')

            print('')

    def get_tile(self, x, y, map=None):

        if map is None:
            map = self.map
        tile = map[y]
        tile = tile[x]
        return tile

    def get_neighbors(self, x, y):
        """
        Helperfunction for figuring out what is the neighboring tiles.
        This deals with the wrap around needed for the open edges
        :param x: Pos x
        :param y: Pos y
        :return: Returns four tiles in a list
        """

        height = len(self.map)
        width = len(self.map[0])

        tiles = [self.get_tile((x + 1) % width, (y + 0) % height),
                 self.get_tile((x - 1) % width, (y - 0) % height),
                 self.get_tile((x + 0) % width, (y + 1) % height),
                 self.get_tile((x - 0) % width, (y - 1) % height)]
        shuffle(tiles)
        return tiles

    def get_walkable_neighbors(self, x, y, check_visit = False):
        tiles = self.get_neighbors(x, y)

        temp = []
        for tile in tiles:
            if check_visit and tile.visited:
                continue
            if tile.passable:
                temp.append(tile)

        return temp

    def reduce_tile_by_enemies(self,clusters, init_reduction = 0.8,reduction_delta = 0):
        print("Reducing values")
        """
        Filter / fixes the score for tiles in close proximity to an enemy, so that we don't case after an other ghosts clusters for no reason.
        It does this by doing an limited width search search and reduce the value of nodes close to the enemy.
        :return:
        """

        def reduce_values(point,dist_left, reduction, reduction_delta):
            if dist_left == 0:
                return

            x,y = point
            tile = self.get_tile(x,y)
            if tile.reduced:
                return

            tile.reduced = True
            tile.value = max(0,tile.value - reduction)

            # God fuck. How 2 maek pretty plz?
            reduce_values(((x + 1) % width,(y + 1) % height), dist_left - 1, reduction-reduction_delta,reduction_delta)
            reduce_values(((x + 1) % width,(y - 1) % height), dist_left - 1, reduction-reduction_delta,reduction_delta)
            reduce_values(((x - 1) % width,(y + 1) % height), dist_left - 1, reduction-reduction_delta,reduction_delta)
            reduce_values(((x - 1) % width,(y - 1) % height), dist_left - 1, reduction-reduction_delta,reduction_delta)

        height = len(self.map)
        width = len(self.map[0])

        x_player = self.you.get('x')
        y_player = self.you.get('y')
        player_point = (x_player,y_player)

        prune = math.floor(len(clusters)/3)
        clusters = clusters[0:prune]

        for enemy in self.others:
            x = enemy.get('x')
            y = enemy.get('y')
            enemy_point = (x,y)
            for cluster in clusters:
                dist_enemy = len(self.shortest_path(enemy_point,cluster))
                dist_player = len(self.shortest_path(player_point,cluster))


                if dist_enemy < dist_player: # The enemy is closer than us. The cluster thus loses value
                    reduce_values(enemy_point,dist_player,init_reduction,reduction_delta)

    def sort_clusters(self, clusters):
        """
        Takes an list of clusters and sorts them based on highest value.
        :param clusters: A list of
        """
        return sorted(clusters,key = self.calculate_cluster_value,reverse=True)

    def calculate_cluster_value(self, cluster):
        # TODO: Figure out the value of clusters and sort them accordingly
        x,y = self.you.get('x'), self.you.get('y')
        player_dist = len(self.shortest_path((x,y),cluster))
        self.reset_map()
        total = 0
        for point in cluster:
            tile = self.get_tile(point[0],point[1])
            total += tile.get_value()
        return total + (8 - max(player_dist,0))

    def find_clusters(self, value_map):
        print("Finding clusters")
        """
        Will try to find clusters of pellets
        Returns a list of coordinates

        1. Start in a corner
        2. Checkin the tile
        3. Check if neighbors got pellets too
        4. Repeate 2-3
        5. Check for more pellets
        6. Reapeat 2-3 for new cluster

        :return:
        """

        def fetch_and_set_tile(x, y, map):
            val = map[y][x]
            if val > 0:
                map[y][x] = 0
                return True
            return False

        def get_next_pellet():
            for y, line in enumerate(temp_map):
                for x, tile in enumerate(line):
                    if tile > 0:
                        temp_map[y][x] = 0
                        return x, y
            return None

        def cluster_entry():
            clusters = []

            while True:
                current_cluster = []
                point = get_next_pellet()
                if point is None:  # There is no more untaken pellets
                    print('Done')
                    return clusters

                queue.append(point)

                while len(queue):
                    point = queue.popleft()
                    current_cluster.append(point)

                    x, y = point

                    # Check all the neigboring tiles
                    if fetch_and_set_tile(x, (y + 1) % height, temp_map):
                        queue.append((x, (y + 1) % height))

                    if fetch_and_set_tile(x, (y - 1) % height, temp_map):
                        queue.append((x, (y - 1) % height))

                    if fetch_and_set_tile((x - 1) % width, y, temp_map):
                        queue.append(((x - 1) % width, y))

                    if fetch_and_set_tile((x + 1) % width, y, temp_map):
                        queue.append(((x + 1) % width, y))

                clusters.append(current_cluster)

        queue = deque()
        temp_map = value_map[:]
        height = len(temp_map)
        width = len(temp_map[0])
        clusters = cluster_entry()
        print(len(clusters))
        return clusters

    def generate_heat_map(self):
        print("Heatmapping")
        """
        Will try a approach where a tiles value is based on how likely it is for me to take it versus an enemy
        :return:
        """

        heatmap = []
        for line in self.map:
            temp_line = []
            for tile in line:
                temp_line.append(tile.get_value())
            heatmap.append(temp_line)

        clusters = self.find_clusters(heatmap)

        clusters = self.sort_clusters(clusters)
        self.reduce_tile_by_enemies(clusters)

        for cluster in clusters:
            print(self.calculate_cluster_value(cluster))

        return clusters


    def shortest_path(self, point_from, point_to_lst, num=1, enemy = False):
        """
        :param point_to_lst: A list of points we are looking for
        :param point_from: The point we are going from
        :param num: A number of nodes to return.
        :return: the shortest path to the target location
        """
        #print("Shortest path")


        def point_in_list(point, lst):
            for p in lst:
                if point == p:
                    return True
            return False

        self.reset_map()

        temp_map = self.map[:]
        queue = deque()
        queue.append(point_from)
        x, y = point_from
        tile = self.get_tile(x, y, temp_map)
        tile.current_shortest = 0

        if enemy:
            x, y = point_to_lst
            tile = self.get_tile(x, y)
            tile.passable = True

        while len(queue):
            # self.print_map()
            x, y = queue.popleft()
            tile = self.get_tile(x, y)
            tile.visited = True

            if point_in_list((x, y), point_to_lst):
                tile.current_path.append(tile)

                self.reset_map()

                return tile.current_path

            next_nodes = self.get_walkable_neighbors(x, y, check_visit=False)

            # Lets do some dijkstra bullshit
            for n in next_nodes:
                if n.current_shortest > tile.current_shortest + tile.cost:  # If we are making a shorter path than what we got, add it to the list
                    n.current_shortest = tile.current_shortest + tile.cost
                    n.current_path = tile.current_path[:]
                    n.current_path.append(tile)

                    #print("Current path for next node: ", n.current_path)
                    #print("Adding node")
                    queue.append(n.point)

        raise ValueError("There is no valid path to the destination. Map might be broken")

    def create_plan(self, clusters):
        """
        Creates a plan
        :param clusters: The clusters we are going to use for a base of the next plan.
        :return: A plan: IE, a path to follow for the next X number of ticks. X should be something like 1/2 of the fastest way to the closest cluster
        """
        you_x = self.you.get('x')
        you_y = self.you.get('y')
        plan  = self.shortest_path((you_x, you_y), clusters[0])

        return plan,3

    def set_map(self, state_object):
        # print("Setting map")
        self.state_object = state_object
        gamestate = state_object.get('gamestate')
        map_obj = gamestate.get('map')
        map_content = map_obj['content']

        overview = []
        for y, line in enumerate(map_content):
            temp_line = []
            for x, char in enumerate(line):
                temp_line.append(self.map_object_factory(char, (x, y)))
            overview.append(temp_line)

        self.map = overview[:]

    def set_players(self, state_object):
        print('Setting players')
        gamestate = state_object.get('gamestate')
        self.others = gamestate.get('others')
        self.you = gamestate.get('you')

        for ghost in self.others:
            x = ghost.get('x')
            y = ghost.get('y')
            tile = self.get_tile(x, y)

            if self.you.get('isdangerous') and ghost.get('isdangerous'):
                tile.passable = False
            elif not self.you.get('isdangerous') and ghost.get('isdangerous'):
                tile.passable = False
            elif self.you.get('isdangerous') and not ghost.get('isdangerous'):
                tile.passable = True
            elif not self.you.get('isdangerous') and not ghost.get('isdangerous'):
                tile.passable = False

    def map_object_factory(self, char, point):
        """
        This function generates fitting objects from the char supplied.
        Note that this is only the map, not the players at this time.
        :param point: The (x,y) coord of a char
        :param char: A character to use as base
        :return:
        """
        tile = Tile(char, point)
        return tile

    def reset_map(self):
        self.set_map(self.state_object)

    def __init__(self):
        self.state_object = None
        self.map = []
        self.others = None
        self.you = None
        pass


class MapObject:
    def __init__(self, point):
        self.cost = 0
        self.value = 0
        self.passable = False
        self.content = 'X'
        self.visited = False
        self.point = point
        self.current_shortest = 100000
        self.current_path = []
        self.reduced = False

    def __str__(self):
        return self.content

    def get_value(self):
        return self.value

    def cost(self):
        return self.cost

    def passable(self):
        return self.passable


class Tile(MapObject):
    def __init__(self, char, point):

        super().__init__(point)
        self.content = char

        if char == '_':  # Blank floor
            self.cost = 1
            self.value = 0
            self.passable = True

        elif char == '|':  # Wall tile
            self.cost = -1
            self.value = 0
            self.passable = False

        elif char == '-':  # Door tile, basically floor
            self.value = 0
            self.passable = True
            self.cost = 1

        elif char == '.':  # Pellet <3
            self.passable = True
            self.value = 1
            self.cost = 1

        elif char == 'o':  # Super Pellet <4
            self.passable = True
            self.value = 9
            self.cost = 1

        else:
            raise ValueError(char)


class Enemy(MapObject):
    def __init(self, enemy_object, point):
        super().__init__(point)

        self.content = enemy_object.get('id', None)
        self.dangerous = enemy_object.get('isdangerous', None)
        self.value = 10

    def dangerous(self):
        return self.dangerous

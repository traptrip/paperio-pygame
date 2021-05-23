import networkx as nx
from config import CONSTS
from helpers import (in_polygon,
                     get_neighboring_points,
                     get_vert_and_horiz_neighbours)


class Territory:
    def __init__(self, x, y, color):
        self.color = color
        self.points = {(x, y), *get_neighboring_points((x, y))}
        self.changed = True

    def get_boundary(self):
        """
        :return: The boundary of player's territory
        """
        boundary = []
        for point in self.points:
            if any([neighboring not in self.points for neighboring in get_neighboring_points(point)]):
                boundary.append(point)
        return boundary

    @staticmethod
    def __get_siblings(point, boundary):
        return [sibling for sibling in get_neighboring_points(point) if sibling in boundary]

    def get_graph(self, boundary):
        graph = nx.Graph()
        for index, point in enumerate(boundary):
            siblings = self.__get_siblings(point, boundary)  # adjacent boundary points
            for sibling in siblings:
                graph.add_edge(index, boundary.index(sibling), weight=1)
        return graph

    @staticmethod
    def _get_start_points(point, boundary):
        res = []
        for neighbour in [point, *get_neighboring_points(point)]:
            if neighbour in boundary:
                res.append(neighbour)
        return res

    def _capture(self, boundary):
        poligon_x_arr = [x for x, _ in boundary]
        poligon_y_arr = [y for _, y in boundary]

        max_x = max(poligon_x_arr)
        max_y = max(poligon_y_arr)
        min_x = min(poligon_x_arr)
        min_y = min(poligon_y_arr)

        captured = []
        for x in range(max_x, min_x, -1):
            for y in range(max_y, min_y, -1):
                if (x, y) not in self.points and in_polygon(x, y, poligon_x_arr, poligon_y_arr):
                    captured.append((x, y))
        return captured

    @staticmethod
    def is_siblings(p1, p2):
        return p2 in get_vert_and_horiz_neighbours(p1)

    def get_voids_between_player_line_and_territory(self, line_points):
        boundary = self.get_boundary()  # get boundary of current territory
        graph = self.get_graph(boundary)  # get graph representation of territory
        voids = []
        for idx_lp1, line_point1 in enumerate(line_points):
            for neighbouring_point in get_neighboring_points(line_point1):
                if neighbouring_point in boundary:
                    prev_point = None
                    for line_point2 in line_points[:idx_lp1 + 1]:
                        start_points = self._get_start_points(line_point2, boundary)
                        for start_point in start_points:
                            if prev_point and (self.is_siblings(prev_point, start_point) or prev_point == start_point):
                                prev_point = start_point
                                continue
                            end_index = boundary.index(neighbouring_point)
                            start_index = boundary.index(start_point)

                            try:
                                path = nx.shortest_path(graph, end_index, start_index, weight='weight')
                            except (nx.NetworkXNoPath, nx.NodeNotFound):
                                continue

                            if len(path) > 1 and path[0] == path[-1]:
                                path = path[1:]

                            path = [boundary[index] for index in path]
                            lines_path = line_points[line_points.index(line_point2):idx_lp1 + 1]

                            voids.append(lines_path + path)
                            prev_point = start_point
        return voids

    # def capture_voids_between_lines(self, lines):
    #     captured = []
    #     for index, cur in enumerate(lines):
    #         for point in get_neighboring_points(cur):
    #             if point in lines:
    #                 end_index = lines.index(point)
    #                 path = lines[index:end_index + 1]
    #                 if len(path) >= 8:
    #                     captured.extend(self._capture(path))
    #     return captured

    def capture(self, line_points):
        captured = set()
        if len(line_points) > 1:
            if line_points[-1] in self.points:

                # capture unfilled area between player line and territory
                voids = self.get_voids_between_player_line_and_territory(line_points)

                # captured.update(self.capture_voids_between_lines(line_points))

                # capture player lines
                for line_point in line_points:
                    if line_point not in self.points:
                        captured.add(line_point)

                for void in voids:
                    captured.update(self._capture(void))
        if len(captured) > 0:
            self.changed = True
        return captured



    def remove_points(self, points):
        removed = []
        for point in points:
            if point in self.points:
                self.points.discard(point)
                removed.append(point)

        if len(removed) > 0:
            self.changed = True
        return removed

    def split(self, line, direction, player):
        removed = []
        l_point = line[0]

        if any([point in self.points for point in line]):
            for point in list(self.points):
                if direction in [CONSTS.UP, CONSTS.DOWN]:
                    if player.x < l_point[0]:
                        if point[0] >= l_point[0]:
                            removed.append(point)
                            self.points.discard(point)
                    else:
                        if point[0] <= l_point[0]:
                            removed.append(point)
                            self.points.discard(point)

                if direction in [CONSTS.LEFT, CONSTS.RIGHT]:
                    if player.y < l_point[1]:
                        if point[1] >= l_point[1]:
                            removed.append(point)
                            self.points.discard(point)
                    else:
                        if point[1] <= l_point[1]:
                            removed.append(point)
                            self.points.discard(point)

        if len(removed) > 0:
            self.changed = True
        return removed

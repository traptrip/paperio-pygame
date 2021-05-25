import networkx as nx
from config import CONSTS
from helpers import (in_polygon,
                     get_neighboring_points,
                     get_vert_and_horiz_neighbours)
import numpy as np


class Territory:
    def __init__(self, x, y, color):
        self.color = color
        self.points = {(x, y), *get_neighboring_points((x, y))}
        self.changed = True

    def get_boundary(self):
        """
        Return the boundary of player's territory
        """
        boundary = []
        for point in self.points:
            if any([neighboring not in self.points for neighboring in get_neighboring_points(point)]):
                boundary.append(point)
        return boundary

    @staticmethod
    def __get_boundary_siblings(point, boundary):
        return [sibling for sibling in get_neighboring_points(point) if sibling in boundary]

    def get_boundary_graph(self, boundary):
        graph = nx.Graph()
        for index, point in enumerate(boundary):
            siblings = self.__get_boundary_siblings(point, boundary)  # adjacent boundary points
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
        polygon_x_arr = [x for x, _ in boundary]
        polygon_y_arr = [y for _, y in boundary]

        max_x = max(polygon_x_arr)
        max_y = max(polygon_y_arr)
        min_x = min(polygon_x_arr)
        min_y = min(polygon_y_arr)

        captured = []
        for x in range(max_x, min_x, -1):
            for y in range(max_y, min_y, -1):
                if (x, y) not in self.points and in_polygon(x, y, polygon_x_arr, polygon_y_arr):
                    captured.append((x, y))
        return captured

    @staticmethod
    def is_siblings(p1, p2):
        return p2 in get_vert_and_horiz_neighbours(p1)

    def get_voids(self, line_points):
        boundary = self.get_boundary()  # get boundary of current territory
        boundary_graph = self.get_boundary_graph(boundary)  # get graph representation of boundary

        end_index = boundary.index(line_points[-1])
        start_point = self.__get_boundary_siblings(line_points[0], boundary)
        start_index = boundary.index(start_point[0])
        try:
            path = nx.shortest_path(boundary_graph, end_index, start_index, weight='weight')
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            path = []
        path = [boundary[index] for index in path]
        
        return line_points + path

    def capture(self, line_points):
        captured = set()
        if len(line_points) > 1:
            if line_points[-1] in self.points:

                # capture unfilled area between player line and territory
                unfilled_area = self.get_voids(line_points)

                # capture player lines
                for line_point in line_points:
                    if line_point not in self.points:
                        captured.add(line_point)

                captured.update(self._capture(unfilled_area))

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

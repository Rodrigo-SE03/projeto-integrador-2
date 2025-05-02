from typing import List, Tuple, Sequence, Callable
from dataclasses import dataclass
from loguru import logger
import numpy as np
import math

EARTH_RADIUS_KM = 6371
# ----- Coordenate Validation -----
def validate_coords(lat: float, lon: float):
    '''
    Validate latitude and longitude values.
    '''
    if not -90 <= lat <= 90:
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    if not -180 <= lon <= 180:
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
    

@dataclass
class Coords:
    latitude: float
    longitude: float

    def __post_init__(self):
        validate_coords(self.latitude, self.longitude)
        self.latitude = math.radians(self.latitude)
        self.longitude = math.radians(self.longitude)


# ----- Haversine Function -----
def haversine(coords1:Tuple[float, float], coords2:Tuple[float, float]) -> float: 
    '''
    Calculate the great circle distance in kilometers between two points on the earth (specified in decimal degrees)
    using the Haversine formula.

    Args:
        coords1 (Tuple[float, float]): 
            Latitude and longitude of the first point.

        coords2 (Tuple[float, float]): 
            Latitude and longitude of the second point.

    Returns:
        float: 
            Distance between the two points in kilometers.
    '''

    c1 = Coords(coords1[0], coords1[1])
    c2 = Coords(coords2[0], coords2[1])   
    delta_phi = c2.latitude - c1.latitude
    delta_lambda = c2.longitude - c1.longitude

    a = math.sin(delta_phi/2)**2 + math.cos(c1.latitude) * math.cos(c2.latitude) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_KM  * c


# ----- Distance Calculation -----
def route_distance(route: Sequence[int], points: Sequence[Tuple[float, float]], origin: Tuple[float, float],
                   distance_func: Callable[[Tuple[float, float], Tuple[float, float]], float] = haversine) -> float:
    '''
    Calculate the total distance of a route.

    Args:
        route (Sequence[int]): 
            List of indices representing the order of points in the route.

        points (Sequence[Tuple[float, float]]): 
            List of coordinates for all points.

        origin (Tuple[float, float]): 
            Coordinates of the starting point.

    Returns:
        float: 
            Total distance of the route in kilometers.
    '''
    route = np.array(route, dtype=int)
    if route.size == 0: 
        return 0.0
   
    path = [origin] + [points[i] for i in route] + [origin]
    return sum(distance_func(path[i], path[i+1]) for i in range(len(path)-1))



# ----- Optimazed haversine to routes -----
def precompute_distance_matrix(points: Sequence[Tuple[float, float]], origin: Tuple[float, float]) -> np.ndarray:
    '''
    Precompute the distance matrix for a set of points and an origin using the Haversine formula.
    
    Args:
        points (Sequence[Tuple[float, float]]): 
            List of coordinates for all points.

        origin (Tuple[float, float]): 
            Coordinates of the starting point.
    
    Returns:
        np.ndarray:
            A 2D numpy array representing the distance matrix.
    '''
    all_points = [origin] + list(points)
    lat_lons = np.radians(np.array(all_points))

    lat = lat_lons[:, 0][:, np.newaxis]
    lon = lat_lons[:, 1][:, np.newaxis]

    delta_lat = lat - lat.T
    delta_lon = lon - lon.T

    a = np.sin(delta_lat / 2) ** 2 + np.cos(lat) * np.cos(lat.T) * np.sin(delta_lon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return EARTH_RADIUS_KM * c


def route_distance_matrix(route: Sequence[int], dist_matrix: np.ndarray) -> float:
    '''
    Calculate the total distance of a route using a precomputed distance matrix.

    Args:
        route (Sequence[int]): 
            List of indices representing the order of points in the route.

        dist_matrix (np.ndarray): 
            Precomputed distance matrix.

    Returns:
        float:
            Total distance of the route in kilometers.
    '''
    if not route:
        return 0.0
    path = np.array([0] + [r + 1 for r in route] + [0])
    return dist_matrix[path[:-1], path[1:]].sum()



# ----- Nearest Neighbor Algorithm -----
def nearest_neighbor(origin: Tuple[float, float], points: List[Tuple[float, float]], 
                     distance_func: Callable[[Tuple[float, float], Tuple[float, float]], float] = haversine) -> List[int]:
    '''
    Nearest Neighbor Algorithm: A simple heuristic for the Traveling Salesman Problem.
    
    Args:
        origin (Tuple[float, float]): 
            Coordinates of the starting point.
        
        points (List[Tuple[float, float]]): 
            List of coordinates for all points.
        
        distance_func (Callable[[Tuple[float, float], Tuple[float, float]], float]): 
            Function that computes the distance between two coordinates.

    Returns:
        List[int]: 
            A list of indices representing the order of points in the route.
    '''

    if not callable(distance_func):
        raise ValueError("distance_func must be a callable that accepts two coordinates.")
    validate_coords(origin[0], origin[1])

    if not points:
        return []
    
    unvisited = set(range(len(points)))
    current_pos = origin
    route = []

    while unvisited:
        nearest = min(unvisited, key=lambda idx: distance_func(current_pos, points[idx]))
        unvisited.remove(nearest)
        route.append(nearest)
        current_pos = points[nearest]

    return route


# ----- Two-Opt Algorithm -----
def two_opt(route: Sequence[int], points: Sequence[Tuple[float, float]], origin: Tuple[float, float],
            route_distance: Callable[[Sequence[int], Sequence[Tuple[float, float]], Tuple[float, float]], float]=route_distance, 
            max_iterations=-1, verbose:bool=False) -> List[int]:
    '''
    Two-opt algorithm for optimizing a route.

    Args:
        route (Sequence[int]): 
            List of indices representing the order of points in the route.
        
        points (Sequence[Tuple[float, float]]): 
            List of coordinates for all points.
        
        origin (Tuple[float, float]): 
            Coordinates of the starting point.
 
        route_distance (Callable[[Sequence[int], Sequence[Tuple[float, float]], Tuple[float, float]], float]): 
            Function that computes the distance of a route.

        max_iterations (int): 
            Maximum number of iterations to perform. Default is -1 for unlimited.

        verbose (bool):
            If True, prints the distance at each iteration. Default is False.

    Returns:
        List[int]: 
            Optimized route.
    '''

    if not points or not route: return []

    if len(route) < 2:
        raise ValueError("A rota deve ter pelo menos dois pontos.")
    
    validate_coords(origin[0], origin[1])

    best = np.array(route)
    best_distance = route_distance(best, points, origin)
    iteration = 0
    improved = True

    while improved and (max_iterations < 0 or iteration < max_iterations):
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best)):
                if j - i == 1:
                    continue  # vizinhos, pular

                new_route = np.concatenate([best[:i], best[i:j+1][::-1], best[j+1:]])
                new_distance = route_distance(new_route, points, origin)

                if new_distance < best_distance:
                    best = new_route
                    best_distance = new_distance
                    improved = True
                    break # Interrompe a busca após uma melhoria ser encontrada para acelerar a convergência.

            if improved:
                break

        if verbose:
            logger.info(f"Iter {iteration}: Distance = {best_distance:.2f}")

        iteration += 1

    return best

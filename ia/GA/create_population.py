import random
from typing import List, Optional, Tuple
from .routing_utils import nearest_neighbor


def create_population(population_size: int, num_points: int, seeding_route:Optional[List[int]]=None, use_nn: bool = False, start_node:Tuple[float, float]=None, points:List[Tuple[float, float]]=None) -> List[List[int]]:
    '''
    Generate an initial population of random routes for a genetic algorithm.

    Args:
        population_size (int): 
            Number of routes to generate.
        
        num_points (int): 
            Total number of points (cities) in the problem.

        seeding_route (Optional[List[int]]):
            An optional route to seed the population. If provided, the first route will be this exact route,
            and the remaining routes will be shuffled variations of it.

        use_nn (bool): 
            If True, use the nearest neighbor algorithm to generate the seeding route.

        start_node (Tuple[float, float]):
            Coordinates of the starting point for the nearest neighbor algorithm. Required if use_nn is True.
        
        points (List[Tuple[float, float]]):
            List of coordinates for all points (cities) to visit. Required if use_nn is True.
        

    Returns:
        List[List[int]]: 
            A list of routes, where each route is a randomized list of point indices.
    '''
    if population_size <= 0:
        raise ValueError("Population size must be greater than zero.")
    
    if num_points <= 0:
        raise ValueError("Number of points must be greater than zero.")
    
    if seeding_route is not None and len(seeding_route) != num_points:
        raise ValueError("Seeding route length must match the number of points.")
    
    population = []

    if use_nn:
        assert start_node is not None, "start_node must be provided if use_nn is True."
        assert points is not None, "points must be provided if use_nn is True."
        seeding_route = nearest_neighbor(start_node, points)  # Obtenha a rota do NN

    if seeding_route is not None:
        population.append(seeding_route.copy())

        while len(population) < population_size:
            new_route = seeding_route.copy()
            random.shuffle(new_route)
            population.append(new_route)

    else:
        base_route = list(range(num_points))
        population = [random.sample(base_route, len(base_route)) for _ in range(population_size)]

    return population

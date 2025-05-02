from typing import List, Tuple, Dict, Callable, Optional
import numpy as np
import enum


def pmx_crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    Partially Mapped Crossover (PMX): Creates offspring by partially mapping genes from both parents.
    """
    size = len(parent1)
    child = np.full(size, -1)
    start, end = sorted(np.random.choice(size, 2, replace=False))
    child[start:end] = parent1[start:end]

    p1_pos = {val: idx for idx, val in enumerate(parent1)}
    used = set(child[start:end])
    
    for i in range(size):
        if child[i] == -1:
            gene = parent2[i]
            while gene in used:
                gene = parent2[p1_pos[gene]]
            child[i] = gene
            used.add(gene)
    return child


def ox_crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    Order Crossover (OX): Creates offspring by preserving the order of genes from both parents.
    """
    size = len(parent1)
    child = np.full(size, -1)
    start, end = sorted(np.random.choice(size, 2, replace=False))
    child[start:end] = parent1[start:end]

    used = set(child[start:end])
    p2_filtered = [gene for gene in parent2 if gene not in used]

    idx = 0
    for i in range(size):
        if child[i] == -1:
            child[i] = p2_filtered[idx]
            idx += 1
    return child


def cx_crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    Cycle Crossover (CX): Creates offspring by forming cycles between the two parents.
    """
    size = len(parent1)
    child = np.full(size, -1)
    p2_pos = {val: idx for idx, val in enumerate(parent2)}
    visited = set()
    start = 0

    while len(visited) < size:
        if parent1[start] in visited:
            start += 1
            continue
        idx = start
        while True:
            child[idx] = parent1[idx]
            visited.add(parent1[idx])
            idx = p2_pos[parent1[idx]]
            if idx == start:
                break
    return child


def erx_crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    Edge Recombination Crossover (ERX): Creates offspring by preserving edges between genes.
    """
    size = len(parent1)
    child = np.full(size, -1)
    edges = {int(gene): set() for gene in parent1}

    for i in range(size):
        edges[int(parent1[i])].add(int(parent2[i]))
        edges[int(parent2[i])].add(int(parent1[i]))

    used = set()
    current = int(np.random.choice(parent1))
    child[0] = current
    used.add(current)

    for i in range(1, size):
        for e in edges.values():
            e.difference_update(used)
        neighbors = edges[current]
        if neighbors:
            next_gene = min(neighbors, key=lambda x: len(edges[x]))
        else:
            next_gene = next(g for g in parent1 if g not in used)
        child[i] = next_gene
        used.add(next_gene)
        current = next_gene

    return child


def pos_crossover(parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
    """
    Position-Based Crossover (POS): Creates offspring by selecting genes based on their positions in the parents.
    """
    size = len(parent1)
    child = np.full(size, -1)
    selected = np.random.choice(size, size // 2, replace=False)

    child[selected] = parent1[selected]

    p2_iter = iter(g for g in parent2 if g not in child)
    for i in range(size):
        if child[i] == -1:
            child[i] = next(p2_iter)
    return child


class CROSSOVER_STRATEGY(enum.Enum):
    PMX = "Partially Mapped Crossover"
    OX = "Order Crossover"
    CX = "Cycle Crossover"
    ERX = "Edge Recombination Crossover"
    POS = "Position-Based Crossover"



_crossover_selection: Dict[CROSSOVER_STRATEGY, Callable[[np.ndarray, np.ndarray], np.ndarray]] = {
    CROSSOVER_STRATEGY.PMX: pmx_crossover,
    CROSSOVER_STRATEGY.OX: ox_crossover,
    CROSSOVER_STRATEGY.CX: cx_crossover,
    CROSSOVER_STRATEGY.ERX: erx_crossover,
    CROSSOVER_STRATEGY.POS: pos_crossover,
}


def crossover(parent1: List[int], parent2: List[int], strategy: CROSSOVER_STRATEGY, seed:Optional[int]=None) -> np.ndarray:
    """
    Performs crossover between two parents using the specified crossover strategy.

    Args:
        parent1 (List[int]): 
            The first parent.

        parent2 (List[int]): 
            The second parent.
            
        strategy (CROSSOVER_STRATEGY): 
            The crossover strategy to use. Options:
                - PMX: Partially Mapped Crossover, Creates offspring by partially mapping genes from both parents.
                - OX: Order Crossover, Creates offspring by preserving the order of genes from both parents.
                - CX: Cycle Crossover, Creates offspring by forming cycles between the two parents.
                - ERX: Edge Recombination Crossover, Creates offspring by preserving edges between genes.
                - POS: Position-Based Crossover, Creates offspring by selecting genes based on their positions in the parents.

        seed (int, optional): 
            Random seed for reproducibility.

    Returns:
        Tuple[List[int], List[int]]: 
            Two offspring created from the parents using the specified crossover strategy.
    """

    if strategy not in _crossover_selection:
        raise ValueError(f"Invalid crossover strategy: {strategy}")

    if len(parent1) != len(parent2):
        raise ValueError("Parents must have the same length")


    if seed is not None:
        np.random.seed(seed)

    p1, p2 = np.array(parent1), np.array(parent2)
    child1 = _crossover_selection[strategy](p1, p2)
    child2 = _crossover_selection[strategy](p2, p1)
    return child1, child2


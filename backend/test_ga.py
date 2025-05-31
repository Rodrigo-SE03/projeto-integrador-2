import numpy as np
import time
from tabulate import tabulate
import matplotlib.pyplot as plt
from ia.GA.model import genetic_algorithm
from ia.GA.utils import nearest_neighbor, two_opt, route_distance
from tqdm import tqdm


# Coordenada de Goiânia
GOIANIA = (-16.6869, -49.2648)

def generate_random_points(n, center=GOIANIA, spread=0.2):
    lat_center, lon_center = center
    latitudes = lat_center + np.random.uniform(-spread, spread, n)
    longitudes = lon_center + np.random.uniform(-spread, spread, n)
    return list(zip(latitudes, longitudes))

def test_algorithms(min_points=10, max_points=50, step=1):
    results, r_values = [], []
    x_points = []
    y_nn, y_2opt, y_ga = [], [], []

    print(f"Testing algorithms with points from {min_points} to {max_points} in steps of {step}...")
    with tqdm(total=(max_points - min_points) // step + 1) as pbar:    
        for n_points in range(min_points, max_points + 1, step):
            points = generate_random_points(n_points)
            x_points.append(n_points)

            # --- NN
            start = time.time()
            nn_route, dist_matrix = nearest_neighbor(GOIANIA, np.array(points))
            nn_distance = route_distance(nn_route, dist_matrix)
            nn_time = time.time() - start

            # --- NN + 2-Opt
            start = time.time()
            opt_route = two_opt(nn_route, dist_matrix)
            opt_distance = route_distance(opt_route, dist_matrix)
            opt_time = time.time() - start + nn_time

            # --- GA
            start = time.time()
            ga_route, ga_distance = genetic_algorithm(points, GOIANIA)
            ga_time = time.time() - start

            # --- Porcentagens de melhora
            opt_improvement = 100 * (nn_distance - opt_distance) / nn_distance
            ga_improvement = 100 * (nn_distance - ga_distance) / nn_distance

            y_nn.append(nn_distance)
            y_2opt.append(opt_distance)
            y_ga.append(ga_distance)

            results.append([
                n_points,
                f"{nn_distance:.2f}", f"{nn_time:.2f}s",
                f"{opt_distance:.2f}", f"{opt_time:.2f}s", f"{opt_improvement:.1f}%",
                f"{ga_distance:.2f}", f"{ga_time:.2f}s", f"{ga_improvement:.1f}%"
            ])
            r_values.append([nn_distance, nn_time, 
                             opt_distance, opt_time, opt_improvement, 
                             ga_distance, ga_time, ga_improvement])
            pbar.update(1)

    results.append([
        "Média",
        f"{np.mean([r[0] for r in r_values]):.2f}", f"{np.mean([r[1] for r in r_values]):.2f}s",
        f"{np.mean([r[2] for r in r_values]):.2f}", f"{np.mean([r[3] for r in r_values]):.2f}s", f"{np.mean([r[4] for r in r_values]):.1f}%",
        f"{np.mean([r[5] for r in r_values]):.2f}", f"{np.mean([r[6] for r in r_values]):.2f}s", f"{np.mean([r[7] for r in r_values]):.2f}%"   
    ])

    headers = [
        "N Points",
        "NN Dist", "NN Time",
        "2Opt Dist", "2Opt Time", "2Opt %↓",
        "GA Dist", "GA Time", "GA %↓"
    ]
    print(tabulate(results, headers=headers, tablefmt="grid"))

    # --- Gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(x_points, y_nn, label='NN', marker='o')
    plt.plot(x_points, y_2opt, label='2-Opt', marker='o')
    plt.plot(x_points, y_ga, label='GA', marker='o')
    plt.xlabel('Número de Pontos')
    plt.ylabel('Distancia Total')
    plt.title('Comparação de distâncias: NN vs 2-Opt vs GA')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    points = generate_random_points(3)
    ga_route, ga_distance = genetic_algorithm(points, GOIANIA)
    test_algorithms()

import json

import os.path as op


def calculate_loads(
    base_directory: str, directory: str, load_points_filter: str = ""
) -> dict[str, float]:
    base_path = op.join(base_directory, directory)
    load_points_num = get_number_of_load_points(base_path)
    nodes_num = get_number_of_nodes(base_path)
    node_pairs_num = nodes_num * (nodes_num - 1)

    traffic_path = op.join(base_directory, directory, "traffic")
    if not op.exists(traffic_path):
        raise FileNotFoundError(f"Arquivo 'traffic' não encontrado em {traffic_path}")

    try:
        with open(traffic_path, "r") as f:
            traffic = json.load(f)
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo de tráfego:\n{e}")

    filtered_req_gen = filter_request_generators(traffic)

    arrival_rate_sum = 0
    arrival_rate_increase_sum = 0
    for req_gen in filtered_req_gen:
        arrival_rate_sum += req_gen["arrivalRate"]
        arrival_rate_increase_sum += req_gen["arrivalRateIncrease"]

    hold_rate = filtered_req_gen[0]["holdRate"]

    load_1_to_2 = arrival_rate_sum / hold_rate
    load = node_pairs_num * load_1_to_2
    total_loads = [round(load)]
    increment = arrival_rate_increase_sum * node_pairs_num
    for i in range(1, load_points_num):
        load = total_loads[i - 1] + increment
        total_loads.append(round(load))

    filtered_loads = filter_loads(total_loads, load_points_num, load_points_filter)
    return filtered_loads


def get_number_of_load_points(base_path: str):
    """
    Retrieves the number of load points from the simulation file in the specified base path.
    Args:
        base_path (str): The base directory path where the simulation file is located.
    Returns:
        int: The number of load points.
    """
    simulation_path = op.join(base_path, "simulation")
    if not op.exists(simulation_path):
        raise FileNotFoundError(
            f"Arquivo 'simulation' não encontrado em {simulation_path}"
        )
    with open(simulation_path, "r") as f:
        simulation = json.load(f)
        load_point_num = simulation["loadPoints"]
    return load_point_num


def get_number_of_nodes(base_path: str):
    """
    Retrieves the number of nodes from the network file in the specified base path.
    Args:
        base_path (str): The base directory path where the network file is located.
    Returns:
        int: The number of nodes.
    """
    network_path = op.join(base_path, "network")
    if not op.exists(network_path):
        raise FileNotFoundError(f"Arquivo 'network' não encontrado em {network_path}")
    with open(network_path, "r") as f:
        network = json.load(f)
        node_num = len(network["nodes"])
    return node_num


def filter_request_generators(traffic: dict):
    """
    Filters request generators from the traffic data based on specific criteria.\\
    This function checks if the source node is "1" and the destination node is "2".
    Args:
        traffic (dict): The traffic data containing request generators.
    Returns:
        list: Filtered request generators.
    """
    filtered_req_gen = []
    for req_gen in traffic["requestGenerators"]:
        if req_gen["source"] == "1" and req_gen["destination"] == "2":
            filtered_req_gen.append(req_gen)
        else:
            break
    if not filtered_req_gen:
        raise ValueError(
            "Nenhum gerador de requisições válido encontrado nos dados de tráfego."
        )
    return filtered_req_gen


def filter_loads(
    total_loads: list, load_points_num: int, load_points_filter: str
) -> dict:
    """
    Filters the load points based on the provided filter string.
    Args:
        total_loads (list): List of load points.
        load_points_num (int): Total number of load points.
        load_points_filter (str): Filter string specifying which load points to include.
    Returns:
        dict: Filtered dictionary of load points.
    """
    if load_points_filter:
        try:
            indices = []
            for part in load_points_filter.split(","):
                part = part.strip()
                if "-" in part:
                    start_end = part.split("-")
                    if len(start_end) != 2:
                        raise ValueError(f"Formato de intervalo inválido: {part}")
                    if start_end[0] == "" and start_end[1] == "":
                        raise ValueError(f"Intervalo inválido: {part}")
                    if start_end[0] == "":
                        if indices:
                            raise ValueError(
                                f"Intervalo '-i' só permitido no início: {part}"
                            )
                        start = 0
                        end = int(start_end[1])
                    elif start_end[1] == "":
                        if part != load_points_filter.split(",")[-1].strip():
                            raise ValueError(
                                f"Intervalo 'i-' só permitido no final ou sozinho: {part}"
                            )
                        start = int(start_end[0])
                        end = load_points_num - 1
                    else:
                        start = int(start_end[0])
                        end = int(start_end[1])
                    if start < 0 or end >= load_points_num or start > end:
                        raise ValueError(
                            f"Intervalo de pontos de carga inválido: {start}-{end}."
                        )
                    indices.extend(range(start, end + 1))
                else:
                    idx = int(part)
                    if idx < 0 or idx >= load_points_num:
                        raise ValueError(f"Índice de ponto de carga inválido: {idx}.")
                    indices.append(idx)
            return {str(i): total_loads[i] for i in indices}
        except ValueError as e:
            raise ValueError(f"Erro ao analisar filtro de pontos de carga:\n{e}")

    return {str(i): total_loads[i] for i in range(len(total_loads))}

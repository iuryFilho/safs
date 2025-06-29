import glob
import os
import os.path as op


def get_simulations_dirs_paths(base_directory: str) -> list[str]:
    """
    Retrieves the simulation directories from the base directory.
    Args:
        base_directory (str): The base directory to search for directories.
    Returns:
        list: A list of simulation directories found in the directory.
    """
    if not op.isdir(base_directory):
        raise FileNotFoundError(
            f"The base directory '{base_directory}' does not exist."
        )
    entries = [op.join(base_directory, d) for d in os.listdir(base_directory)]
    dirs = [op.normpath(d) for d in entries if op.isdir(d)]
    return dirs


def get_full_paths(base_directory: str, directories: list[str]) -> list[str]:
    """
    Retrieves the full paths of the directories by joining them with the base directory.
    Args:
        base_directory (str): The base directory to join with the directories.
        directories (list[str]): List of directory names to be joined with the base directory.
    Returns:
        list: A list of full paths for the directories.
    """
    return [op.join(base_directory, d) for d in directories]


def get_csv_paths(simulation_directories: list[str], metric_group: str) -> list[str]:
    """
    Retrieves the csv file paths from the simulation directories based on the given metric group.
    Args:
        simulation_directories (list[str]): The simulation directories to search for files.
        metric_group (str): The file name pattern to search for.
    Returns:
        list: A list of csv file paths matching the given pattern.
    """
    file_paths = []
    empty_directories = []
    for simulation_directory in simulation_directories:
        if not op.isdir(simulation_directory):
            raise FileNotFoundError(f"O diretório '{simulation_directory}' não existe.")
        pattern = f"{simulation_directory}/*_{metric_group}.csv"
        file_paths_glob = glob.glob(pattern)
        if not file_paths_glob:
            empty_directories.append(simulation_directory)
            continue
        file_paths.append(op.normpath(file_paths_glob[0]))
    if empty_directories and len(empty_directories) != len(simulation_directories):
        raise FileNotFoundError(
            f"Nenhum arquivo CSV encontrado para o grupo '{metric_group}' "
            f"nos diretórios: {', '.join(empty_directories)}."
        )
    if not file_paths:
        raise FileNotFoundError(
            f"Nenhum arquivo CSV encontrado para o grupo '{metric_group}'."
        )
    return file_paths


def get_basename(path: str) -> str:
    """
    Returns the base name of a given path.
    Args:
        path (str): The path from which to extract the base name.
    Returns:
        str: The base name of the path.
    """
    return op.basename(op.normpath(path))


def ensure_unique_filename(filename: str, extension: str, overwrite: bool) -> str:
    """
    Ensures that the filename is unique by appending a number if necessary.
    Args:
        filename (str): The base filename to check.
        extension (str): The file extension to use.
        overwrite (bool): Whether to overwrite existing files.
    Returns:
        str: A unique filename, potentially modified with an appended number.
    """
    if not overwrite and op.exists(f"{filename}.{extension}"):
        i = 0
        while True:
            new_filename = f"{filename}_{i}"
            if op.exists(f"{new_filename}.{extension}"):
                i += 1
            else:
                filename = new_filename
                break
    return filename

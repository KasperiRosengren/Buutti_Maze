from queue import PriorityQueue
import argparse
import sys
import logging
import os
from typing import Optional


class InvalidMazeCharacter(Exception):
    '''Raised when the program encounters character that is not ^, E, ' ', or # '''
    
    def __init__(self, row, column, character) -> None:
        self.character=character
        self.row=row
        self.column=column
        self.message = f"Found unrecognized character {self.character} at: ({self.row}, {self.column})"
        super().__init__(self.message)
        
class MultipleStartingPoints(Exception):
    '''Raised when the program finds second starting point from a maze'''
    
    def __init__(self) -> None:
        self.message = "Found more than one starting point."
        super().__init__(self.message)
        
class NoStartingPointFound(Exception):
    '''Raised if the program did not find any starting points (^) in the maze'''
    
    def __init__(self) -> None:
        self.message = "Did not find starting point."
        super().__init__(self.message)
        
class NoEndingPointFound(Exception):
    '''Raised if the program did not find any ending points (E) in the maze'''
    
    def __init__(self) -> None:
        self.message = "Did not find any ending points."
        super().__init__(self.message)

class ResultHandler:
    printing_to_terminal = False
    file_to_print = None
    
    def set_file_to_print(file_name):
        logging.info(f"Setting to print results to file: {file_name}")
        if os.path.isfile(file_name):
            logging.info(f"File {file_name} already exist. Overwriting")
            with open(file_name, "w") as file:
                file.write("")
        ResultHandler.file_to_print = file_name   
    
    def print_result(result):
        if ResultHandler.printing_to_terminal:
            print(result)
        if ResultHandler.file_to_print is not None:
            with open(ResultHandler.file_to_print, 'a') as file:
                file.write(f"{result}\n")             
        

class Node:
    nodeTypes = {
        "#": "wall",
        "E": "ending",
        "^": "start",
        " ": "open",
        "x": "closed",
        "O": "path"
    }
    
    def get_character(wanted_type):
        for character, this_type in Node.nodeTypes.items():
            if wanted_type == this_type:
                return character
    
    def __init__(self, row, column, character, row_length, col_length) -> None:
        self.row = row
        self.column = column
        self.row_length = row_length
        self.col_length = col_length
        
        self.neighbors = []
        self.nodeType = Node.nodeTypes[character]
    
    def is_open(self):
        return self.nodeType == "open"
    
    def is_wall(self):
        return self.nodeType == "wall"
    
    def is_ending(self):
        return self.nodeType == "ending"
    
    def is_start(self):
        return self.nodeType == "start"

    
    def make_open(self):
        self.nodeType = "open"
    
    def make_ending(self):
        self.nodeType = "ending"
    
    def make_start(self):
        self.nodeType = "start"
        
    def make_path(self):
        self.nodeType = "path"
        
    def get_position(self):
        return self.row, self.column
    
    def update_neighbor(self, difference, maze):
        dif_y, dif_x = difference
        neighbor_y = self.row + dif_y
        neighbor_x = self.column + dif_x
        try:
            if not maze[neighbor_y][neighbor_x].is_wall():
                self.neighbors.append(maze[neighbor_y][neighbor_x])
        except IndexError as IE:
            logging.debug(f"Node does not exist: y: {neighbor_y}, x: {neighbor_x}")
        
    def update_neighbors(self, maze):
        self.neighbors = []
        self.update_neighbor((-1, 0), maze) #Node above the current one
        self.update_neighbor((0, 1), maze) #Node right of the current one
        self.update_neighbor((1, 0), maze) #Node under the current one
        self.update_neighbor((0, -1), maze) #Node left of the current one
    
def calculate_distance(nodePosition:tuple, endingPosition:tuple):
    node_y, node_x = nodePosition
    ending_y, ending_x = endingPosition
    
    return abs(node_y - ending_y) + abs(node_x - ending_x)

def readMazeFile(fileName):
    try:
        with open(fileName, 'r') as file:
            maze = [list(line.strip()) for line in file]        
    except FileNotFoundError:
        logging.error(f"File {fileName} not found")
        return None
    else:
        return maze
        
def make_maze(maze:list) -> dict:
    """_summary_

    Args:
        maze (list): _description_

    Raises:
        MultipleStartingPoints: _description_
        InvalidMazeCharacter: _description_
        NoStartingPointFound: _description_
        NoEndingPointFound: _description_

    Returns:
        dict: _description_
    """
    if maze is None:
        return None
    grid = []
    start = None
    endings = []
    try:
        for row_idx, row in enumerate(maze):
            grid.append([])
            row_length = len(row)
            for col_idx, col in enumerate(maze[row_idx]):
                col_length = len(maze[row_idx])
                node = Node(row_idx, col_idx, col, row_length, col_length)
                grid[row_idx].append(node)
                if node.is_ending():
                    endings.append(node)
                elif node.is_start():
                    if start is not None:
                        raise MultipleStartingPoints
                    else:
                        start = (node)
                elif not node.is_wall() and not node.is_open():
                    raise InvalidMazeCharacter(row_idx, col_idx, col)
    except MultipleStartingPoints as MSP:
        logging.error(MSP)
        ResultHandler.print_result(MSP)
    except InvalidMazeCharacter as IMC:
        logging.error(IMC)
        ResultHandler.print_result(IMC)
    else:
        if start is None:
            raise NoStartingPointFound
        if len(endings) == 0:
            raise NoEndingPointFound 
        return {"grid":grid, "start":start, "endings":endings}

def generate_path(came_from:dict, current_node:Node) -> tuple:
    """Generate the walked path from start node to exit node

    Args:
        came_from (dict): _description_
        current_node (Node): The ending point of the path
        
    The path needs to be reversed, since the came_from has been filled from start to finish
    and this reads it from last element to first element.

    Returns:
        tuple:
            First: The length of the path: int
            Second: The path itself: list of tuples
    """
    path_length = 0
    path = []
    while current_node in came_from:
        path_length += 1
        path.append(current_node.get_position())
        current_node = came_from[current_node]
        current_node.make_path()
    
    path.reverse()
    
    return path_length, path
        
def print_grid(grid:list):
    """Print the grid using the ResultHandler class.

    Args:
        grid (list): Matrix filled with printable maze characters. Commonly comes from get_printable_maze()
    """
    printable_grid = []
    for row_idx, row in enumerate(grid):
        printable_grid.append([])
        for node in row:
            printable_grid[row_idx].append(node)
        ResultHandler.print_result(printable_grid[row_idx])

def get_printable_maze(grid:list) -> list:
    """Generate matrix showing the maze.
    Given list is filled with Node objects and this returns the same maze filled with the maze characters

    Args:
        grid (list): Matrix filled with Node objects: [[Node,Node,Node],[Node,Node,Node],[Node,Node,Node]]
    
    Get each Nodes type and get the character representing that type from the Node class
    Create new matrix and fill it with the characters
    
    Returns:
        list: Matrix filled with maze characters: [["#","E","#"],["#"," ","#"],["#","^","#"]]
    """
    printable_grid = []
    for row_idx, row in enumerate(grid):
        printable_grid.append([])
        for node in row:
            printable_grid[row_idx].append(Node.get_character(node.nodeType))
    return printable_grid
      
def solve_ending(start:Node, this_ending:Node, grid:list) -> Optional[dict]: #The actual algorithm, A*
    """Uses the A* pathfinding algorithm to find the shortest path to the end point
    
    To find more about A* algorithm, you can look at:
        - https://brilliant.org/wiki/a-star-search/ 
        - http://theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html#the-a-star-algorithm/ 
    
    

    Args:
        start (Node): Node that is the start point for this maze
        this_ending (Node): Node that is the wanted ending
        grid (list): Matrix with Node object elements

    Returns:
        Optional[dict]: Keys: path_length (how many steps in path) and path (the steps taken to reach ending
                        does not include start node. [(0,1),(0,2),(0,3)])
    """
    count = 0   #Just a running number, in case the f_score is equal on at least two nodes.
    open_set = PriorityQueue()
    open_set.put((0, count, start)) #Start node is the first node
    open_set_hash = {start} #Used for checking if PriorityQueue already has node in it, since it does not have any easy way for it
    
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0   
    
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = calculate_distance(start.get_position(), this_ending.get_position())
    
    while not open_set.empty():
        current_node = open_set.get()[2]
        open_set_hash.remove(current_node)
        
        if current_node == this_ending:
            logging.info(f"Found the endig")
            path_length, path = generate_path(came_from, current_node)
            this_ending.make_ending()
            start.make_start()
            
            return {"path_length": path_length, "path": path}
        
        for neighbor in current_node.neighbors:
            temp_g_score = g_score[current_node] + 1
            
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + calculate_distance(neighbor.get_position(), this_ending.get_position())
                
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()
                    
            
    return None
      
def solve_maze(maze:dict):
    start = maze['start']
    endings = maze['endings']
    grid = maze['grid']
    results = {}
    is_any_ending_solvable = False
    for ending_idx, ending in enumerate(endings):
        ending_name = f"E_{ending_idx}"
        results[ending_name] = {}
        this_result = solve_ending(start, ending, grid)
        if this_result is not None:
            results[ending_name]["result"] = True
            results[ending_name]["path_length"] = this_result['path_length']
            results[ending_name]["path"] = this_result['path']
            results[ending_name]["solved_grid"] = get_printable_maze(grid)
            is_any_ending_solvable = True
        else:
            results[ending_name]["result"] = False
    
    return is_any_ending_solvable, results
        

def maze_main(file_name:str, max_steps:list):
    try:
        maze = make_maze(readMazeFile(file_name))
    except NoStartingPointFound as NSP:
        logging.error(NSP)
        ResultHandler.print_result(NSP)
    except NoEndingPointFound as NEP:
        logging.error(NEP)
        ResultHandler.print_result(NEP)
    else:
        if maze is not None:     
            logging.info(f"Start: {maze['start'].get_position()} Endings: {[ending.get_position() for ending in maze['endings']]}")
            for row in maze['grid']:
                for node in row:
                    node.update_neighbors(maze["grid"])
            
            ResultHandler.print_result("Given maze grid:")
            print_grid(get_printable_maze(maze["grid"]))
            is_maze_solvable, ending_results = solve_maze(maze)
            if is_maze_solvable:
                shortest_ending = None
                for ending_name, values in ending_results.items():
                    if values['result']:
                        logging.info(f"Results for ending: {ending_name}")
                        logging.info(f"Path length: {values['path_length']}")
                        logging.info(f"Taken path: {values['path']}")
                        
                        #ResultHandler.print_result(f"Result for ending: {ending_name}")
                        #ResultHandler.print_result(f"Path length: {values['path_length']}")
                        #ResultHandler.print_result(f"Taken path: {values['path']}")
                        #ResultHandler.print_result("Path taken on grid view:")                        
                        if shortest_ending is not None:
                            if values['path_length'] < shortest_ending['path_length']:
                                shortest_ending = ending_results[ending_name]
                                logging.info(f"Found new shortest path: {ending_name} with length: {values['path_length']}")
                        else:
                            shortest_ending = ending_results[ending_name]
                            logging.info(f"Found first path: {ending_name} with length: {values['path_length']}")
                    else:
                        logging.info(f"Ending: {ending_name} is unsolvable")
                        #ResultHandler.print_result(f"Ending: {ending_name} is unsolvable")
                
                for max_step in max_steps:
                    if max_step is None:
                        ResultHandler.print_result(f"Shortest path took {shortest_ending['path_length']} steps. The path used: {shortest_ending['path']}")
                        print_grid(shortest_ending['solved_grid'])
                    elif max_step > shortest_ending['path_length']:
                        ResultHandler.print_result(f"Was able to solve the maze under {max_step} steps")
                        #ResultHandler.print_result(f"Path taken: {shortest_ending['path']}")
                        #print_grid(shortest_ending['solved_grid'])
                    else:
                        ResultHandler.print_result(f"Was not able to solve the maze under {max_step} steps")
            else:
                logging.info(f"The maze is unsolvable")
                ResultHandler.print_result("The maze is unsolvable")
            
if __name__=="__main__":
    parser = argparse.ArgumentParser(
        prog='Maze solver',
        description='''
        Maze solver is used to find out if the given maze is solvable at all or if it can even be solved in 200, 150, or 25 moves.
        
        Used A* pathfinding algorithm to find the shortest path.
        
        Maze objects are as follow:\n
            # = Wall
            ^ = Start, also known as Pentti
            E = Ending/Exit
            white space = Walkable path
            O = Is the path taken in the grid view result
            
        Endings are named E_0, E_1 ... and each of them is checked if they are solvable
        
        If there is no starting point or any ending points, the error is logged, but nothing is printed on results.
        
        '''
    )
    
    parser.add_argument('-f', '--file', help='Give the name of the maze you want to solve. Either this or -d flag MUST be used')
    parser.add_argument('-d', '--directory', help='Give directory name where your maze files are stored. The files MUST be in .txt format and they MUST be in the root of the folder. Either this or -f flag MUST be used')
    parser.add_argument('-l', '--log-level', help='Set the log level', choices=['error', 'info', 'debug'], default='error')
    parser.add_argument('--log-file', help='Set the log file name', default='maze_solver.log')
    parser.add_argument('--result-terminal', help='Set if you want to print results to terminal', action='store_true')
    parser.add_argument('--result-file', help='Set the filename where you want the results to be stored, can be used with the -t flag')
    
    arguments = parser.parse_args()
    
    wanted_log_level = arguments.log_level
    if wanted_log_level == "error":
        log_level = logging.ERROR
    elif wanted_log_level == "info":
        log_level = logging.INFO
    elif wanted_log_level == "debug":
        log_level = logging.DEBUG
        
    """Format for logging:
    2023-08-30 22:06:14,735:INFO:"Path length: 169"
    when looped line by line can be stripped in the future with:
        line.split("\"") -> ['2023-08-30 22:06:14,735:INFO:', 'Path length: 169', '']
        info, *message, ending = test.split("\"") ->
            info = '2023-08-30 22:06:14,735:INFO:'
            message = 'Path length: 169' -> If includes ", will be splitted in to a list
            ending = ''
        info.split(":")[-2] gets the Log level, INFO, DEBUG...
        info.split(" ")[0] get the date
        info.split(" ")[1].split(":")[:3] get the hours, minutes and seconds (includes ms)
    """
    logging.basicConfig(
        filename=arguments.log_file,
        format='%(asctime)s:%(levelname)s:"%(message)s"', 
        filemode='w',
        level=log_level
    )
    
    maze_files = []
    
    if arguments.file is None and arguments.directory is None:
        logging.critical('No file or directory given.')
        sys.exit()
    else:
        file_name = arguments.file
        if file_name is not None:
            logging.info(f"Given maze file name: {file_name}")
            maze_files.append(file_name)
        else:
            logging.info(f"No file name given")
        
        directory_name = arguments.directory
        if directory_name is not None:
            logging.info(f"Given maze directory name: {directory_name}")
            file_names = os.listdir(directory_name)
            for file in file_names:
                if file.lower().endswith('.txt'):   #Any file without .txt is skipped
                    logging.info(f"Found file {file}")
                    maze_files.append(f"{directory_name}/{file}")
        else:
            logging.info(f"No directory name name given")
        
    if arguments.result_terminal is not None:
        ResultHandler.printing_to_terminal = True
    if arguments.result_file is not None:
        ResultHandler.set_file_to_print(arguments.result_file)
    
    max_steps = [20, 150, 200, None]    #None finds shortest route
    for file_name in maze_files:
        logging.info(f"Given maze file: {file_name}")
        ResultHandler.print_result(20*"-" + f" {file_name} " + 20*"-")
        maze_main(file_name, max_steps)
        ResultHandler.print_result("")

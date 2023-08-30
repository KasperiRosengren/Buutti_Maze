# Buutti_Maze
 
Used command when testing:
```bash 
python maze_solver.py -f Instructions/maze-task-second.txt -d Mazes -l debug --result-terminal --result-file result.txt
```
<H4>Where the flags did the following:</H4>
-f FILENAME, single file to be read for solving the maze<br>
-d DIRECTORY, directory name where multiple mazes are located, and each of them is solved (Only reads files with .txt ending)<br>
-l LOG_LEVEL, sets the logging level to DEBUG, did not use --log-file flag, so default log file used (maze_solver.log)<br>
--result-terminal, prints the results in real time to the terminal, default is false<br>
--result-file RESULT_FILENAME, prints the results in real time to the provided file (result.txt)<br>
<br>
Used A* as search algorithm to find optimal path, some resources I used to learn about it:<br>
<a href=\"https://brilliant.org/wiki/a-star-search/\">Brilliant - A star search</a>: https://brilliant.org/wiki/a-star-search/<br>
<a href=\"http://theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html#the-a-star-algorithm/\">Stanford.edu - A star comparison</a>: http://theory.stanford.edu/~amitp/GameProgramming/AStarComparison.html#the-a-star-algorithm/<br>
<a href=\"https://www.youtube.com/watch?v=ySN5Wnu88nE&t=409s&ab_channel=Computerphile\">Youtube - ComputerPhile - A* (A Star) Search Algorithm</a>: https://www.youtube.com/watch?v=ySN5Wnu88nE&t=409s&ab_channel=Computerphile\

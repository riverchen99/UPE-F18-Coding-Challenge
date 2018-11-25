import requests
import datetime
import sys

def dirToString(d):
	if d[0] == -1:
		return "LEFT"
	elif d[0] == 1:
		return "RIGHT"
	elif d[1] == -1:
		return "UP"
	elif d[1] == 1:
		return "DOWN"

def prettyPrint(maze):
	for i in range(len(maze)):
		for j in range(len(maze[i])):
			print(maze[i][j], end = "")
		print()

def solve(maze, currentPos, visited, bounds):
	#visited[currentPos[0]][currentPos[1]] = 1
	for direction in directions:# [[-1, 0], [0, -1], [1, 0], [0, 1]]:
		if (currentPos[0]+direction[0] in range(bounds[0]) and
			currentPos[1]+direction[1] in range(bounds[1]) and
			#visited[currentPos[0]+direction[0]][currentPos[1]+direction[1]] == 0 and
			maze[currentPos[0]+direction[0]][currentPos[1]+direction[1]] == "?"):
			#print("MOVING ", dirToString(direction), "FROM ", currentPos)
			r = requests.post(url + "/game", params = {"token" : token}, data = {"action" : dirToString(direction)})
			result = r.json()["result"]
			#print("RESULT: ", result)
			#prettyPrint(maze)
			if result == "WALL":
				maze[currentPos[0]+direction[0]][currentPos[1]+direction[1]] = "X"
			elif result == "SUCCESS":
				maze[currentPos[0]+direction[0]][currentPos[1]+direction[1]] = " "
				currentPos = [currentPos[0]+direction[0], currentPos[1]+direction[1]]
				###visited[currentPos[0]+direction[0]][currentPos[1]+direction[1]] = 1
				finalResult = solve(maze, currentPos, visited, bounds)
				if (finalResult):
					return True
				else:
					requests.post(url + "/game", params = {"token" : token}, data = {"action" : dirToString([direction[0]*-1, direction[1]*-1])})
					currentPos = [currentPos[0]-direction[0], currentPos[1]-direction[1]] # undo
					###visited[currentPos[0]+direction[0]][currentPos[1]+direction[1]] = 0
			elif result == "END":
				print("FOUND THE END")
				return True
			elif result == "OUT_OF_BOUNDS":
				print("OUT OF BOUNDS!")
			else:
				print("ERR")
	#print("BACKTRACKING")
	#visited[currentPos[0]][currentPos[1]] = 0
	return False

	
url = "http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com"
token = requests.post(url + "/session", data = {"uid" : sys.argv[1]}).json()["token"]
print(token)
startTime = datetime.datetime.now();
print(startTime)
solvedCount = 0
while True:
	r = requests.get(url + "/game", params = {"token" : token}).json()
	print(r)
	if (r["status"] == "FINISHED"):
		print("DONE!")
		break
	visited = [[0 for i in range(r["maze_size"][1])] for i in range(r["maze_size"][0])]
	maze = [["?" for i in range(r["maze_size"][1])] for i in range(r["maze_size"][0])]
	currentPos = r["current_location"]
	#visited[currentPos[0]][currentPos[1]] = 1
	bounds = r["maze_size"]
	print("BOUNDS", bounds)

	directions = [] # heuristic
	if (currentPos[0] < bounds[0]/2):
		directions.append([1, 0])
	else:
		directions.append([-1, 0])

	if (currentPos[1] < bounds[1]/2):
		directions.append([0, 1])
	else:
		directions.append([0, -1])
	directions.append([directions[0][0]*-1, directions[0][1]*-1])
	directions.append([directions[0][1]*-1, directions[1][1]*-1])

	solve(maze, currentPos, visited, bounds)
	solvedCount += 1
	print("SOLVED", solvedCount)
	timeDiff = datetime.datetime.now()-startTime
	print(timeDiff.seconds//60, timeDiff.seconds%60)
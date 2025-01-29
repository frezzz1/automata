import re
import sys
import csv
from collections import deque

def format_result(result):
    formatted_result = []

    for row in result:
        formatted_row = []
        for element in row:
            if isinstance(element, list) and len(element) == 2:
                formatted_element = f"{element[0]}/{element[1]}"
            else:
                formatted_element = element
            formatted_row.append(formatted_element)
        formatted_result.append(formatted_row)

    return formatted_result


def writeToFile(outFile, result):
    formatted_result = format_result(result)
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(formatted_result)

def getOriginalMealy(infile):
    f = open(inFile, 'r')
    original = []
    lineCount = 0

    for line in f:
        splited = line.split(';')
        original.append([0] * len(splited))
        for i in range(len(splited)):
            item = splited[i].strip('\n').strip('\t')
            if lineCount == 0 or (i == 0 and lineCount != 0):
                original[lineCount][i] = item
            else:
                a = splited[i].split('\')
                a[1] = a[1].strip('\n').strip('\t')
                original[lineCount][i] = a

        lineCount += 1

    print("Original")
    for i in range(len(original)):
        print(original[i])
    print()

    return original

def getStatesForMealy(min):
    currState = 0
    d = dict()

    first = []
    for i in range(2, len(min)-1):
        first.append(min[i][1][1])

    min[0][1] = "A" + str(currState)
    d[tuple(first)] = "A" + str(currState)
    currState += 1

    for j in range(2, len(min[0])):
        curr = []
        for i in range(2, len(min) - 1):
            curr.append(min[i][j][1])
            if i == len(min) - 2:
                a = d.get(tuple(curr))
                if a != None:
                    min[0][j] = a
                else:
                    min[0][j] = "A" + str(currState)
                    d[tuple(curr)] = "A" + str(currState)
                    currState += 1

    print("StatesForMealy")
    for i in range(len(min)):
        print(min[i])
    print()

    return

def removeUnreachebleMealy(arr):
    reachable_states = set()

    queue = deque([arr[0][1]])

    reachable_states.add(arr[0][1])

    while queue:
        current_state = queue.popleft()

        try:
            index = arr[0].index(current_state)
        except ValueError:
            continue

        for i in range(1, len(arr)):
            next_state = arr[i][index][0]

            if next_state not in reachable_states:
                reachable_states.add(next_state)
                queue.append(next_state)

    i = 1
    while i < len(arr[0]):
        if arr[0][i] not in reachable_states:
            for j in range(len(arr)):
                arr[j].pop(i)
        else:
            i += 1

    print("remove unreachble")
    for i in range(len(arr)):
        print(arr[i])
    print()

    return


def minimizeMealy(original, arr):
    start = set()
    end = set()

    for i in range(1, len(arr[0])):
        start.add(arr[0][i])


    for i in range(1, len(original[0])):
        for j in range(1, len(original)):
            id = arr[1].index(original[j][i][0])
            arr[j + 1][i] = arr[0][id]

    while (len(start) != len(end)):
        start.clear()
        end.clear()
        for i in range(1, len(arr[0])):
            start.add(arr[0][i])

        grouped = {arr[1][i]: arr[0][i] for i in range(1, len(arr[0]))}

        currNum = 0
        currCh = re.sub(r'[^a-zA-Z]', '', arr[0][1])
        nextCh = chr(ord(currCh) + 1)

        for i in range(1, len(original[0])):
            for j in range(1, len(original)):
                id = arr[1].index(original[j][i][0])
                arr[j + 1][i] = arr[0][id]

        s = {}
        for j in range(1, len(arr[0])):
            curr = []

            for i in range(2, len(arr) - 1):
                curr.append((arr[i][j], grouped.get(arr[1][j], '')))


            curr_tuple = tuple(curr)
            if curr_tuple in s:
                arr[-1][j] = s[curr_tuple]
            else:
                arr[-1][j] = f"{nextCh}{currNum}"
                s[curr_tuple] = arr[-1][j]
                end.add(arr[-1][j])
                currNum += 1

        arr[0] = arr[-1][:]

    print("Minimize")
    for i in range(len(arr)):
        print(arr[i])
    print()

    return


def groupMealy(original, arr):
    states = []
    out = dict()
    s = set()
    for i in range(1, len(arr[0])):
        if arr[0][i] not in s:
            states.append([arr[0][i], arr[1][i]])
            s.add(arr[0][i])

    for i in range(1, len(arr[1])):
        out[arr[1][i]] = arr[0][i]

    result = [['' for _ in range(len(states)+1)] for _ in range(len(arr) - 2)]
    for i in range(1, len(states)+1):
        result[0][i] = states[i-1][0]

    for i in range(1, len(arr)-2):
        result[i][0] = arr[i+1][0]

    for i in range(len(states)):
        idx = original[0].index(states[i][1])
        for j in range(1, len(original)):
            result[j][i+1] = [out.get(original[j][idx][0]), original[j][idx][1]]

    return result

def mealy(inFile, outFile):
    original = getOriginalMealy(inFile)

    removeUnreachebleMealy(original)

    minimization = [['' for _ in range(len(original[0]))] for _ in range(len(original) + 2)]

    for i in range(len(original)):
        for j in range(len(original[i])):
            minimization[i+1][j] = original[i][j]

    getStatesForMealy(minimization)

    minimizeMealy(original, minimization)
    result = groupMealy(original, minimization)

    print("Result")
    for i in range(len(result)):
        print(result[i])
    print()
    writeToFile(outFile, result)

    return


def getOriginalMoore(inFile):
    f = open(inFile, 'r')
    original = []
    lineCount = 0

    for line in f:
        splited = line.split(';')
        original.append([0] * len(splited))
        for i in range(len(splited)):
            item = splited[i].strip('\n').strip('\t')
            original[lineCount][i] = item

        lineCount += 1

    return original

def removeUnreachebleMoore(arr):
    reachable_states = set()

    queue = deque([arr[1][1]])
    reachable_states.add(arr[1][1])

    while queue:
        current_state = queue.popleft()

        try:
            index = arr[1].index(current_state)
        except ValueError:
            continue

        for i in range(2, len(arr)):
            next_state = arr[i][index]

            if next_state not in reachable_states:
                reachable_states.add(next_state)
                queue.append(next_state)

    i = 1
    while i < len(arr[0]):
        if arr[1][i] not in reachable_states:
            for j in range(len(arr)):
                arr[j].pop(i)
        else:
            i += 1

    for i in range(len(arr)):
        print(arr[i])
    return

def getStatesForMoore(arr):
    currState = 0
    d = dict()

    for i in range(1, len(arr[1])):
        if d.get(arr[1][i]) == None:
            arr[0][i] = "A" + str(currState)
            d[arr[1][i]] = "A" + str(currState)
            currState += 1
        else:
            arr[0][i] = d.get(arr[1][i])

    return

def minimizeMoore(original, arr):
    start = set()
    end = set()

    for i in range(1, len(arr[0])):
        start.add(arr[0][i])

    for i in range(1, len(original[0])):
        for j in range(2, len(original)):
            id = arr[2].index(original[j][i])
            arr[j + 1][i] = arr[0][id]

    while len(start) != len(end):
        start.clear()
        end.clear()

        for i in range(1, len(arr[0])):
            start.add(arr[0][i])

        currNum = 0
        currCh = re.sub(r'[^a-zA-Z]', '', arr[0][1])
        nextCh = chr(ord(currCh) + 1)

        for i in range(1, len(original[0])):
            for j in range(2, len(original)):
                id = arr[2].index(original[j][i])
                arr[j + 1][i] = arr[0][id]

        s = dict()

        for i in range(1, len(arr[0])):
            curr = []
            for j in range(0, len(arr) - 1):
                if j != 2:
                    curr.append(arr[j][i])

            if tuple(curr) in s:
                arr[-1][i] = s[tuple(curr)]
            else:
                arr[-1][i] = nextCh + str(currNum)
                s[tuple(curr)] = nextCh + str(currNum)
                end.add(nextCh + str(currNum))
                currNum += 1

        arr[0] = arr[-1][:]

    return

def groupMoore(original, arr):
    states = []
    out = dict()
    s = set()
    for i in range(1, len(arr[0])):
        if arr[0][i] not in s:
            states.append([arr[0][i], arr[1][i], arr[2][i]])
            s.add(arr[0][i])

    for i in range(1, len(arr[1])):
        out[arr[2][i]] = arr[0][i]

    result = [['' for _ in range(len(states) + 1)] for _ in range(len(arr) - 2)]

    for i in range(1, len(states) + 1):
        result[0][i] = states[i-1][1]
        result[1][i] = states[i - 1][0]

    for i in range(1, len(arr) - 2):
        result[i][0] = arr[i + 1][0]

    for i in range(len(states)):
        curr = [states[i][1], states[i][2]]
        for j in range(1, len(original[0])):
            if original[0][j] == curr[0] and original[1][j] == curr[1]:
                for k in range(2, len(original)):
                    result[k][i+1] = out.get(original[k][j])

    return result
def moore(inFile, outFile):
    original = getOriginalMoore(inFile)

    removeUnreachebleMoore(original)

    minimization = [['' for _ in range(len(original[0]))] for _ in range(len(original) + 2)]

    for i in range(len(original)):
        for j in range(len(original[i])):
            minimization[i + 1][j] = original[i][j]

    getStatesForMoore(minimization)

    minimizeMoore(original, minimization)

    result = groupMoore(original, minimization)

    print("Result")
    for i in range(len(result)):
        print(result[i])
    print()
    writeToFile(outFile, result)

if __name__ == "__main__":
    algorithm = sys.argv[1]
    inFile = sys.argv[2]
    outFile = sys.argv[3]
    if algorithm == "mealy":
        mealy(inFile, outFile)
    elif algorithm == "moore":
        moore(inFile, outFile)
    else:
        print("Invalid algorithm")

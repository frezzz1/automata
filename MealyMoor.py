import re
import sys
import csv

# Функция записи результата в CSV-файл
def writeToFile(outFile, result):
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(result)

# Функция поиска и добавления нового состояния
def findAndAddState(stateMatrix, curr, statesArr, statesDict, statesCount):
    found = False
    for j in range(1, len(stateMatrix)):
        for k in range(1, len(stateMatrix[j])):
            if curr == stateMatrix[j][k][0]:
                statesArr.append([stateMatrix[j][k][0], stateMatrix[j][k][1], "S" + str(statesCount)])
                c = statesArr[-1][:2].copy()
                statesDict[tuple(c)] = "S" + str(statesCount)
                statesCount += 1
                found = True
    return statesArr, statesDict, statesCount, found

# Функция преобразования автомата Mealy в Moore
def mealyToMoore(inFile, outFile):
    f = open(inFile, 'r')

    lineCount = 0
    stateMatrix = []
    statesArr = []
    statesCount = 0
    statesDict = {}

    # Чтение входного файла и построение матрицы состояний
    for line in f:
        splited = line.split(';')
        stateMatrix.append([0]*len(splited))
        for i in range(len(splited)):
            item = splited[i].strip('\n').strip('\t')
            if lineCount == 0 or (i == 0 and lineCount != 0):
                stateMatrix[lineCount][i] = item
            else:
                a = splited[i].split('/')
                a[1] = a[1].strip('\n').strip('\t')
                curr = [a[0], a[1]]
                stateMatrix[lineCount][i] = curr
                if a[0] == stateMatrix[0][1] and [a[0], a[1]] not in statesArr:
                    statesArr.append(curr)
                elif curr in statesArr:
                    stateMatrix[lineCount][i] = statesArr[statesArr.index(curr)]
        lineCount += 1

    # Обработка пустых состояний
    if len(statesArr) == 0:
        statesArr.append(["-", "S" + str(statesCount)])
        statesDict["-"] = "S" + str(statesCount)
        statesCount += 1
        found = False
        for i in range(1, len(stateMatrix[0])):
            curr = stateMatrix[0][i]
            if not found:
                statesArr, statesDict, statesCount, found = findAndAddState(stateMatrix, curr, statesArr, statesDict, statesCount)
    else:
        statesArr = sorted(statesArr, key=lambda x: (x[0], x[1]))
        for i in range(len(statesArr)):
            curr = statesArr[i].copy()
            statesArr[i].append("S" + str(statesCount))
            statesDict[tuple(curr)] = "S" + str(statesCount)
            statesCount += 1

    # Заполнение матрицы состояний новыми именами состояний
    for i in range(1, len(stateMatrix)):
        for j in range(1, len(stateMatrix[i])):
            curr = tuple(stateMatrix[i][j][:2])
            if curr not in statesDict.keys():
                currState = "S" + str(statesCount)
                statesDict[curr] = currState
                stateMatrix[i][j].append(currState)
                statesCount += 1
            elif len(stateMatrix[i][j]) != 3:
                stateMatrix[i][j].append(statesDict[curr])

    result = [["" for _ in range(len(statesDict) + 1)] for _ in range(len(stateMatrix) + 1)]

    # Формирование выходного файла
    for i in range(1, len(stateMatrix)):
        result[i+1][0] = stateMatrix[i][0]
    for i in range(len(list(statesDict))):
        result[0][i + 1] = list(statesDict)[i][-1]
        result[1][i + 1] = list(statesDict.values())[i]
    for i in range(len(list(statesDict.values()))):
        j, state = list(statesDict.keys())[i][0], list(statesDict.values())[i]
        if j != "-":
            col = stateMatrix[0].index(j)
            for j in range(1, len(stateMatrix)):
                result[j+1][i+1] = stateMatrix[j][col][2]
        if j == "-":
            for j in range(1, len(stateMatrix)):
                result[j + 1][1] = stateMatrix[j][1][2]

    writeToFile(outFile, result)

# Функция преобразования автомата Moore в Mealy
def mooreToMealy(inFile, outFile):
    f = open(inFile, 'r')

    matrix = []

    for line in f:
        splited = line.split(';')
        splited[-1] = splited[-1].strip('\n').strip('\t')
        matrix.append(splited)

    for i in range(2, len(matrix)):
        for j in range(1, len(matrix[i])):
            currState = matrix[i][j]
            stateNum = re.sub(r'\D', '', currState)
            exit = matrix[0][matrix[1].index(currState)]
            matrix[i][j] = currState + "/" + exit

    matrix.pop(0)
    writeToFile(outFile, matrix)

# Основной метод программы
if __name__ == "__main__":
    algorithm = sys.argv[1]
    inFile = sys.argv[2]
    outFile = sys.argv[3]
    if algorithm == "mealy-to-moore":
        mealyToMoore(inFile, outFile)
    elif algorithm == "moore-to-mealy":
        mooreToMealy(inFile, outFile)
    else:
        print("Invalid algorithm")

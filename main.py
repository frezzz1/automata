import re
import sys
import csv
from collections import deque

# Функция форматирования результата для корректной записи в CSV-файл
def format_result(result):
    formatted_result = []
    for row in result:
        formatted_row = []
        for element in row:
            if isinstance(element, list) and len(element) == 2:
                formatted_element = f"{element[0]}/{element[1]}"  # Форматирование переходов автомата
            else:
                formatted_element = element
            formatted_row.append(formatted_element)
        formatted_result.append(formatted_row)
    return formatted_result

# Функция записи результата в CSV-файл
def writeToFile(outFile, result):
    formatted_result = format_result(result)
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(formatted_result)

# Функция чтения исходного автомата Мили из CSV-файла
def getOriginalMealy(infile):
    f = open(inFile, 'r')  # Открытие файла на чтение
    original = []
    lineCount = 0
    for line in f:
        splited = line.split(';')
        original.append([0] * len(splited))
        for i in range(len(splited)):
            item = splited[i].strip('\n').strip('\t')  # Удаление лишних символов
            if lineCount == 0 or (i == 0 and lineCount != 0):
                original[lineCount][i] = item  # Запись заголовков и состояний
            else:
                a = splited[i].split('/')  # Разделение состояния и выходного символа
                a[1] = a[1].strip('\n').strip('\t')
                original[lineCount][i] = a
        lineCount += 1
    print("Original")
    for i in range(len(original)):
        print(original[i])  # Вывод исходного автомата для отладки
    print()
    return original

# Функция удаления недостижимых состояний в автомате Мили
def removeUnreachebleMealy(arr):
    reachable_states = set()
    queue = deque([arr[0][1]])  # Очередь для обработки достижимых состояний
    reachable_states.add(arr[0][1])
    while queue:
        current_state = queue.popleft()
        try:
            index = arr[0].index(current_state)  # Поиск индекса состояния в заголовке
        except ValueError:
            continue
        for i in range(1, len(arr)):
            next_state = arr[i][index][0]  # Получение следующего состояния
            if next_state not in reachable_states:
                reachable_states.add(next_state)
                queue.append(next_state)
    i = 1
    while i < len(arr[0]):
        if arr[0][i] not in reachable_states:
            for j in range(len(arr)):
                arr[j].pop(i)  # Удаление недостижимых состояний
        else:
            i += 1
    print("remove unreachble")
    for i in range(len(arr)):
        print(arr[i])  # Вывод автомата после удаления состояний
    print()
    return

# Основной блок кода, который принимает аргументы командной строки
if __name__ == "__main__":
    algorithm = sys.argv[1]
    inFile = sys.argv[2]
    outFile = sys.argv[3]
    if algorithm == "mealy":
        mealy(inFile, outFile)  # Запуск обработки автомата Мили
    elif algorithm == "moore":
        moore(inFile, outFile)  # Запуск обработки автомата Мура
    else:
        print("Invalid algorithm")  # Ошибка при неверном вводе

import re
import sys
import csv

leftRegex = r'^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$'
rightRegex = r'^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$'

findNonTerminal = r'<(.*?)>'
findTerminal = r'\b(?!<)(\w+)(?!>)\b'

def WriteToFile(outFile, result):
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(result)


def GetType(inFile):
    leftCount = 0
    rightCount = 0
    with open(inFile, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if re.match(leftRegex, line):
                leftCount += 1
            if re.match(rightRegex, line):
                rightCount += 1

    if leftCount > rightCount:
        return 'left'

    return 'right'

def GetRules(inFile):
    rules = {}
    lastRule = ""

    with open(inFile, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            parts = line.split("->")
            if len(parts) != 2 and lastRule != "":
                rightSide = parts[0].strip()
                productions = [prod.strip() for prod in rightSide.split("|")]
                productions = [prod for prod in productions if prod]
                rules[lastRule].extend(productions)
                continue

            leftSide = parts[0].strip()
            lastRule = leftSide
            rightSide = parts[1].strip()

            productions = [prod.strip() for prod in rightSide.split("|")]
            productions = [prod for prod in productions if prod]

            if not productions:
                continue

            if leftSide in rules:
                rules[leftSide].extend(productions)
            else:
                rules[leftSide] = productions

    return rules

def GetTerminals(rules):
    terminals = []

    for v in rules.values():
        for val in v:
            val = val.split()
            for i in val:
                if '<' not in i and '>' not in i and i not in terminals:
                    terminals.append(i)

    return terminals

def GetStateMapping(rules, type):
    rulesStatesMap = dict()

    if type == 'left':
        rulesStatesMap["H"] = "q0"
        state_counter = 1

        for left, right in reversed(rules.items()):
            left_state = f"q{state_counter}"
            rulesStatesMap[left] = left_state
            state_counter += 1

    elif type == 'right':
        state_counter = 0
        for left, right in rules.items():
            left_state = f"q{state_counter}"
            rulesStatesMap[left] = left_state
            state_counter += 1
        rulesStatesMap["F"] = f"q{len(rules)}"

    return rulesStatesMap

def ToStates(rules, type):
    terminals = sorted(GetTerminals(rules))
    statesMap = GetStateMapping(rules, type)

    print(terminals)
    print(statesMap)

    result = [["" for _ in range(len(rules) + 2)] for _ in range(len(terminals) + 2)]

    for i in range(2, len(result)):
        result[i][0] = terminals[i - 2]

    result[0][len(result[0]) - 1] = "F"
    for i in range(1, len(result[1])):
        result[1][i] = list(statesMap.values())[i - 1]


    for rule in rules.items():
        currState = rule[0]
        for i in range(1, len(rule)):
            for val in rule[i]:
                if type == "right":
                    if '<' in val and '>' in val:
                        nextState = statesMap[f'<{re.search(findNonTerminal, val).group(1)}>']
                    else:
                        nextState = result[1][result[0].index('F')]
                    terminalIdx = terminals.index(re.search(findTerminal, val).group(1))

                    if result[terminalIdx+2][result[1].index(statesMap[f'<{re.search(findNonTerminal, currState).group(1)}>'])] == "":
                        result[terminalIdx+2][result[1].index(statesMap[f'<{re.search(findNonTerminal, currState).group(1)}>'])] = nextState
                    else:
                        nextState = result[1][result[1].index(nextState)]
                        result[terminalIdx+2][result[1].index(statesMap[f'<{re.search(findNonTerminal, currState).group(1)}>'])] += f',{nextState}'
                else:
                    if '<' in val or '>' in val:
                        nextState = result[1].index(statesMap[f'<{re.search(findNonTerminal, val).group(1)}>'])
                        terminalIdx = terminals.index(re.search(findTerminal, val).group(1))
                        if result[terminalIdx + 2][nextState] == "":
                            result[terminalIdx + 2][nextState] = statesMap[currState]
                        else:
                            result[terminalIdx + 2][nextState] += f',{statesMap[currState]}'
                    else:
                        terminalIdx = terminals.index(val)
                        if result[terminalIdx + 2][1] == "":
                            result[terminalIdx + 2][1] = statesMap[currState]
                        else:
                            result[terminalIdx + 2][1] += f',{statesMap[currState]}'

    return result

def GrammarToNKA(inFile, outFile):
    type = GetType(inFile)
    if not type:
        return
    print(type)

    rules = GetRules(inFile)
    print(rules)
    states = ToStates(rules, type)
    print("States")
    for i in states:
        print(i)

    WriteToFile(outFile, states)


if __name__ == '__main__':
    inFile = sys.argv[1]
    outFile = sys.argv[2]
    GrammarToNKA(inFile, outFile)

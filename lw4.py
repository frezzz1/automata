import sys
import csv
from collections import deque
from collections import defaultdict


def WriteToFile(outFile, result):
    with open(outFile, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerows(result)


def GetOriginalMealy(infile):
    f = open(inFile, 'r')
    original = []
    lineCount = 0

    for line in f:
        if not line.strip():
            continue
        splited = line.split(';')
        original.append([0] * len(splited))
        for i in range(len(splited)):
            item = splited[i].strip('\n').strip('\t')
            if i == 0 or lineCount <= 1:
                original[lineCount][i] = item
            else:
                original[lineCount][i] = item

        lineCount += 1

    print("Original")
    for i in range(len(original)):
        print(original[i])
    print()

    return original


def ReadNFA(original):
    states = []
    terminals = []
    transitions = dict()

    for i in range(1, len(original[1])):
        states.append(original[1][i])

    for i in range(2, len(original)):
        terminals.append(original[i][0])

    for stateIdx in range(len(states)):
        transitions[original[1][stateIdx + 1]] = dict()
        for i in range(2, len(original)):
            if stateIdx + 1 < len(original[i]) and original[i][stateIdx + 1] != '':
                if ',' in original[i][stateIdx + 1]:
                    nextState = original[i][stateIdx + 1].split(',')
                else:
                    nextState = [original[i][stateIdx + 1]]
                transitions[original[1][stateIdx + 1]][original[i][0]] = nextState

    return states, terminals, transitions


def eTransitions(state, transitions):
    eTransitions = set()
    queue = deque([state])

    while queue:
        current = queue.popleft()
        eTransitions.add(current)
        if 'ε' in transitions.get(current, {}):
            for nextState in transitions[current]['ε']:
                if nextState not in eTransitions:
                    queue.append(nextState)

    return list(eTransitions)


def MakeDFA(original, states, terminals, transitions):
    dfaTerminals = []

    dfaTerminals = [t for t in terminals if t != 'ε' and t not in dfaTerminals]

    start_closure = eTransitions(states[0], transitions)
    queue = deque([frozenset(start_closure)])
    dfaStates = {frozenset(start_closure): f"S0"}
    dfaTransitions = defaultdict(dict)
    count = 1

    while queue:
        current = queue.pop()
        currentState = dfaStates[frozenset(current)]

        for terminal in dfaTerminals:
            transitionsSet = set()
            for prev in current:
                if terminal in transitions.get(prev, {}):
                    for nextState in transitions[prev][terminal]:
                        transitionsSet.update(eTransitions(nextState, transitions))

            if transitionsSet:
                if frozenset(transitionsSet) not in dfaStates:
                    newState = f"S{count}"
                    dfaStates[frozenset(transitionsSet)] = newState
                    queue.appendleft(transitionsSet)
                    count += 1

                dfaTransitions[currentState][terminal] = dfaStates[frozenset(transitionsSet)]
            else:
                dfaTransitions[currentState][terminal] = ""

    if len(dfaTerminals) != 0:
        result = [['' for _ in range(len(dfaTransitions) + 1)] for _ in range(len(dfaTerminals) + 2)]
    else:
        result = [['' for _ in range(len(dfaTransitions) + 2)] for _ in range(len(dfaTerminals) + 2)]

    print("Dfa terminals ", dfaTerminals)
    print("Dfa states ", dfaStates)
    print("Dfa transitions ", dfaTransitions)

    for i in range(0, len(dfaTerminals)):
        result[i + 2][0] = dfaTerminals[i]

    for i, v in enumerate(dfaStates.items()):
        #print(i, v)
        result[1][i + 1] = v[1]
        for state in v[0]:
            if original[0][original[1].index(state)] == 'F':
                result[0][i + 1] = 'F'

    for k, v in dfaTransitions.items():
        for next in v.items():
            #print(k, next, dfaTerminals.index(next[0]))
            result[dfaTerminals.index(next[0]) + 2][result[1].index(k)] = next[1]

    return result


if __name__ == '__main__':
    inFile = sys.argv[1]
    outFile = sys.argv[2]

    original = GetOriginalMealy(inFile)
    states, terminals, transitions = ReadNFA(original)
    print("States\n", states)
    print("Terminals\n", terminals)
    print("Transitions\n", transitions)
    result = MakeDFA(original, states, terminals, transitions)

    for i in result:
        print(i)

    WriteToFile(outFile, result)

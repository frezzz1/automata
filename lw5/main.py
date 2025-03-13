import csv
import sys


class RegexTreeNode:
    def __init__(self, val, l_child=None, r_child=None):
        self.val = val
        self.l_child = l_child
        self.r_child = r_child

    def __repr__(self):
        return f"RegexTreeNode({self.val})"


class AutomatonState:
    def __init__(self):
        self.symbol_transitions = {}
        self.epsilon_transitions = []

    def add_symbol_transition(self, symbol, target_state):
        if symbol not in self.symbol_transitions:
            self.symbol_transitions[symbol] = []
        self.symbol_transitions[symbol].append(target_state)

    def add_epsilon_transition(self, target_state):
        self.epsilon_transitions.append(target_state)


class FiniteAutomaton:
    def __init__(self, initial_state, final_state):
        self.initial_state = initial_state
        self.final_state = final_state


def is_regular_char(char):
    return char not in "+*()|"


def regex_to_tree(expression):
    def parse(tokens):
        def next_token():
            return tokens.pop(0) if tokens else None

        def parse_simple():
            token = next_token()
            if token == "\\":
                escaped = next_token()
                if is_regular_char(escaped):
                    tokens.insert(0, escaped)
                else:
                    return RegexTreeNode(escaped)
            if is_regular_char(token):
                return RegexTreeNode(token)
            elif token == "(":
                node = parse_expr()
                if next_token() != ")":
                    raise ValueError("Mismatched parentheses")
                return node
            raise ValueError(f"Unexpected token: {token}")

        def parse_element():
            node = parse_simple()
            while tokens and tokens[0] in ("*", "+"):
                op = "repeat" if next_token() == "*" else "plus"
                node = RegexTreeNode(op, l_child=node)
            return node

        def parse_sequence():
            node = parse_element()
            while tokens and tokens[0] and (is_regular_char(tokens[0]) or tokens[0] == "("):
                right = parse_element()
                node = RegexTreeNode("sequence", l_child=node, r_child=right)
            return node

        def parse_expr():
            node = parse_sequence()
            while tokens and tokens[0] == "|":
                next_token()
                right = parse_sequence()
                node = RegexTreeNode("choice", l_child=node, r_child=right)
            return node

        return parse_expr()

    tokens = []
    for char in expression:
        tokens.append(char)

    return parse(tokens)


def display_tree(node, level=0):
    if node is not None:
        display_tree(node.r_child, level + 1)
        print(" " * 4 * level + "->", node.val)
        display_tree(node.l_child, level + 1)


def construct_automaton(node):
    if node is None:
        return None

    if node.val not in ("sequence", "choice", "plus", "repeat"):
        start = AutomatonState()
        accept = AutomatonState()
        start.add_symbol_transition(node.val, accept)
        return FiniteAutomaton(start, accept)
    elif node.val == "sequence":
        left_automaton = construct_automaton(node.l_child)
        right_automaton = construct_automaton(node.r_child)
        left_automaton.final_state.add_epsilon_transition(right_automaton.initial_state)
        return FiniteAutomaton(left_automaton.initial_state, right_automaton.final_state)
    elif node.val == "choice":
        start = AutomatonState()
        accept = AutomatonState()
        left_automaton = construct_automaton(node.l_child)
        right_automaton = construct_automaton(node.r_child)
        start.add_epsilon_transition(left_automaton.initial_state)
        start.add_epsilon_transition(right_automaton.initial_state)
        left_automaton.final_state.add_epsilon_transition(accept)
        right_automaton.final_state.add_epsilon_transition(accept)
        return FiniteAutomaton(start, accept)
    elif node.val == "repeat":
        start = AutomatonState()
        accept = AutomatonState()
        sub_automaton = construct_automaton(node.l_child)
        start.add_epsilon_transition(sub_automaton.initial_state)
        start.add_epsilon_transition(accept)
        sub_automaton.final_state.add_epsilon_transition(sub_automaton.initial_state)
        sub_automaton.final_state.add_epsilon_transition(accept)
        return FiniteAutomaton(start, accept)
    elif node.val == "plus":
        start = AutomatonState()
        accept = AutomatonState()
        sub_automaton = construct_automaton(node.l_child)
        start.add_epsilon_transition(sub_automaton.initial_state)
        sub_automaton.final_state.add_epsilon_transition(sub_automaton.initial_state)
        sub_automaton.final_state.add_epsilon_transition(accept)
        return FiniteAutomaton(start, accept)

    raise ValueError(f"Unexpected node value: {node.val}")


def display_automaton(automaton):
    def display_state(state, visited, state_map):
        if state in visited:
            return
        visited.add(state)
        for symbol, states in state.symbol_transitions.items():
            for s in states:
                print(f"    S{state_map[state]}-- {symbol} -->S{state_map[s]}")
                display_state(s, visited, state_map)
        for s in state.epsilon_transitions:
            print(f"    S{state_map[state]}-- ε -->S{state_map[s]}")
            display_state(s, visited, state_map)

    state_map = {}
    index = 0

    def assign_state_indices(state):
        nonlocal index
        if state not in state_map:
            state_map[state] = index
            index += 1
            for symbol, states in state.symbol_transitions.items():
                for s in states:
                    assign_state_indices(s)
            for s in state.epsilon_transitions:
                assign_state_indices(s)

    assign_state_indices(automaton.initial_state)

    print("Finite Automaton:")
    print("flowchart LR")
    display_state(automaton.initial_state, set(), state_map)


def assign_state_indices(start_state):
    state_map = {}
    index = 0
    stack = [start_state]

    while stack:
        state = stack.pop()
        if state not in state_map:
            state_map[state] = f"S{index}"
            index += 1
            for symbol, states in state.symbol_transitions.items():
                for s in states:
                    if s not in state_map:
                        stack.append(s)
            for s in state.epsilon_transitions:
                if s not in state_map:
                    stack.append(s)

    return state_map


def save_automaton(automaton, output_file):
    state_map = assign_state_indices(automaton.initial_state)
    final_state = state_map[automaton.final_state]

    transitions = {state_map[s]: {} for s in state_map}

    for state, name in state_map.items():
        for symbol, states in state.symbol_transitions.items():
            transitions[name].setdefault(symbol, set()).update(state_map[s] for s in states)
        for s in state.epsilon_transitions:
            transitions[name].setdefault("ε", set()).add(state_map[s])

    symbols = set()
    for state in transitions:
        trans = transitions[state]
        for symbol in trans:
            symbols.add(symbol)

    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow([""] + ["F" if state == final_state else "" for state in state_map.values()])
        writer.writerow([""] + [state for state in state_map.values()])

        for symbol in symbols:
            row = [symbol]
            for state in state_map.values():
                row.append(",".join(transitions.get(state, {}).get(symbol, {})))
            writer.writerow(row)


def process_regex_pattern(regex, output_file):
    tree = regex_to_tree(regex)
    # display_tree(tree)
    automaton = construct_automaton(tree)
    # display_automaton(automaton)
    save_automaton(automaton, output_file)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <output-file> <regex pattern>")
        return 1

    output_file = sys.argv[1]
    regex_pattern = sys.argv[2]

    try:
        process_regex_pattern(regex_pattern, output_file)
    except RuntimeError as e:
        print(e)
        return 1
 
    return 0


if __name__ == "__main__":
    sys.exit(main())
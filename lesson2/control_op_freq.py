import json
import sys

# Count the frequency of control operations in bril 'prog'
def count_control_ops(prog):
    ops = ['jmp', 'br', 'call', 'ret']
    counter = dict.fromkeys(ops, 0)

    for func in prog['functions']:
        for instr in func['instrs']:
            if 'op' in instr and instr['op'] in ops:
                counter[instr['op']] += 1

    return counter

if __name__ == "__main__":
    prog = json.load(sys.stdin)

    op_counts = count_control_ops(prog)

    for op, count in op_counts.items():
        print(f"{op}: {count}")

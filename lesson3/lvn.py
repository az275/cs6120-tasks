import json
import sys

from collections import defaultdict
from tdce import form_basic_blocks

COMMUTATIVE_OPS = ['add', 'mul', 'eq', 'and', 'or']
EFFECT_OPS = ['call', 'print', 'ret', 'br', 'jmp', 'store']

def track_overwritten(instrs):
    res = [1] * len(instrs)
    seen = set()

    for i in range(len(instrs) - 1, -1, -1):
        dest = instrs[i].get('dest')
        if dest and dest not in seen:
            res[i] = 0
            seen.add(dest)

    return res

def lvn(block):
    table = {}       # value tuple -> value number
    var2num = {}     # variable name -> value number
    num2var = {}     # value number -> canonical variable name
    value_number = 0
    new_block = []
    overwritten=track_overwritten(block)
    fresh_var = 0

    for i, instr in enumerate(block):
        args = instr.get('args', [])
        canonized_args = [num2var.get(var2num.get(arg, arg), arg) for arg in args]

        if 'label' in instr or instr['op'] in EFFECT_OPS:
            instr['args'] = canonized_args
            new_block.append(instr)
            continue

        op = instr['op']
        dest = instr.get('dest')

        if op == 'const':
            value = ('const', instr['type'], instr['value'])
        elif op in COMMUTATIVE_OPS:
            value = (op,) + tuple(sorted(canonized_args))
        else:
            value = (op,) + tuple(canonized_args)

        if value in table:
            value_num = table[value]
            canonical_name = num2var[value_num]
            if op != 'call' and dest:
                var2num[dest] = value_num
                if dest != canonical_name:
                    new_instr = {
                        'op': 'id',
                        'dest': dest,
                        'type': instr['type'],
                        'args': [canonical_name]
                    }
                    new_block.append(new_instr)
        else:
            table[value] = value_number
            new_instr = {'op': op}

            if op == 'const':
                new_instr['value'] = instr['value']
            else:
                new_instr['args'] = canonized_args

            if dest:
                if overwritten[i]:
                    var = f"{dest}.lvn{fresh_var}"
                    fresh_var += 1
                else:
                    var = dest

            new_instr['dest'] = var
            new_instr['type'] = instr['type']
            var2num[dest] = value_number
            num2var[value_number] = var

            new_block.append(new_instr)
            value_number += 1

    block[:] = new_block

if __name__ == "__main__":
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        blocks = form_basic_blocks(func['instrs'])
        for block in blocks:
            lvn(block)
        func['instrs'] = [instr for block in blocks for instr in block]

    json.dump(prog, sys.stdout, indent=2, sort_keys=True)

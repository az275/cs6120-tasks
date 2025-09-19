import json
import sys

CONTROL_OPS = ['jmp', 'br', 'ret']
EFFECT_OPS = ['call', 'print', 'ret', 'br', 'jmp', 'store']

def form_basic_blocks(instrs):
    blocks = []
    curr_block = []

    for instr in instrs:
        if 'op' in instr and instr['op'] in CONTROL_OPS:
            curr_block.append(instr)
            blocks.append(curr_block)
            curr_block = []
        elif 'label' in instr:
            if len(curr_block) > 0:
                blocks.append(curr_block)
            curr_block = [instr]
        else:
            curr_block.append(instr)

    if len(curr_block) > 0:
        blocks.append(curr_block)
    
    return blocks

def tdce_pass(func):
    blocks = form_basic_blocks(func['instrs'])

    used = set()
    for block in blocks:
        for instr in block:
            used.update(instr.get('args', []))

    changed = False
    for block in blocks:
        to_delete = set()
        last_def = {} # var -> index
        for i, instr in enumerate(block):
            dest = instr.get('dest')
            if dest and dest not in used and instr.get('op') not in EFFECT_OPS:
                to_delete.add(i)
                changed = True

            for arg in instr.get('args', []):
                if arg in last_def:
                    del last_def[arg]

            if dest:
                if dest in last_def:
                    to_delete.add(last_def[dest])
                    changed = True
                last_def[dest] = i

        new_block = [instr for i, instr in enumerate(block) if i not in to_delete]
        block[:] = new_block

    func['instrs'] = [instr for block in blocks for instr in block]
    return changed

def tdce(func):
    while tdce_pass(func):
        pass

if __name__ == "__main__":
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        tdce(func)

    json.dump(prog, sys.stdout, indent=2, sort_keys=True)

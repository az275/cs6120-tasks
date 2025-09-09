import json
import sys

def form_basic_blocks(instrs):
    blocks = []
    curr_block = []

    for instr in instrs:
        if 'op' in instr and instr['op'] in ['jmp', 'br', 'ret']:
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

def get_label(block):
    if 'label' in block[0]:
        return block[0]['label']
    else:
        return json.dumps(block[0])

def form_cfg(blocks):
    cfg = {}
    for i in range(len(blocks)):
        last = blocks[i][-1]
        if 'op' in last and last['op'] in ['jmp', 'br']:
            cfg[get_label(blocks[i])] = last['labels']
        elif 'op' in last and last['op'] == 'ret':
            cfg[get_label(blocks[i])] = []
        elif i+1 < len(blocks):
            cfg[get_label(blocks[i])] = [get_label(blocks[i+1])]
        else:
            cfg[get_label(blocks[i])] = []
    return cfg

if __name__ == "__main__":
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        blocks = form_basic_blocks(func['instrs'])
        func_cfg = form_cfg(blocks)
        print("Cfg for function:", func['name'])
        for src, dest in func_cfg.items():
            print(f"{src} -> {dest}")

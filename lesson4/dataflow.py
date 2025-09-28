import json
import sys

from build_cfg import form_basic_blocks, form_cfg, label2block

def worklist(cfg, block_map, merge, transfer):
    worklist = list(cfg.keys())
    in_map = {block: set() for block in cfg} # label -> (var, label)
    out_map = {block: set() for block in cfg} # label -> (var, label)

    pred = {block: [] for block in cfg}
    for block, successors in cfg.items():
        for succ in successors:
            pred[succ].append(block)

    while worklist:
        block = worklist.pop(0)

        preds = pred[block]
        if preds:
            merged = merge([out_map[p] for p in preds])
        else:
            merged = set()

        in_map[block] = merged
        new_out = transfer(block, block_map[block], in_map[block])

        if new_out != out_map[block]:
            out_map[block] = new_out
            worklist.extend(cfg[block])

    return in_map, out_map

def reaching_def_merge(pred_outs):
    return set().union(*pred_outs)

def reaching_def_transfer(block_label, instrs, input_defs):
    defs = set()
    kill = set()

    for instr in instrs:
        if 'dest' in instr:
            for defn in input_defs:
                if defn[0] == instr['dest']:
                    kill.add(defn)
            defs.add((instr['dest'], block_label))

    return defs.union(input_defs - kill)

if __name__ == "__main__":
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        print("Function:", func['name'])
        blocks = form_basic_blocks(func['instrs'])
        block_map = label2block(blocks)
        func_cfg = form_cfg(blocks)
        in_map, out_map = worklist(func_cfg, block_map, reaching_def_merge, reaching_def_transfer)
        for label, defn in in_map.items():
            print(f"In map: {label} -> {defn}")
        for label, defn in out_map.items():
            print(f"Out map: {label} -> {defn}")

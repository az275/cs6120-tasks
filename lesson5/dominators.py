import json
import sys

from build_cfg import form_basic_blocks, form_cfg, get_preds, get_label, add_entry, remove_unreachable

def get_dominators(cfg, entry):
    preds = get_preds(cfg)
    dom = {} # block -> set of blocks

    for block in cfg:
        if block == entry:
            dom[block] = {block}
        else:
            dom[block] = set(cfg.keys())

    changed = True
    while changed:
        changed = False
        for block in cfg:
            if block == entry:
                continue
            new_dom = set.intersection(*(dom[pred] for pred in preds[block]))
            new_dom.add(block)
            if new_dom != dom[block]:
                dom[block] = new_dom
                changed = True
    return dom


def get_immediate_dominators(dominators, entry):
    idoms = {} # block -> immediate dominator
    for block in dominators:
        if block == entry:
            continue
        strict_doms = dominators[block] - {block}
        for dom in strict_doms:
            if all(dom == other or dom not in dominators[other] for other in strict_doms):
                idoms[block] = dom
                break
    return idoms


def build_dominator_tree(dominators, entry):
    idoms = get_immediate_dominators(dominators, entry)
    tree = {block: [] for block in dominators} # parent -> list of children
    for block, parent in idoms.items():
        tree[parent].append(block)
    return tree


def find_dominance_frontier(cfg, entry):
    dominators = get_dominators(cfg, entry)
    idoms = get_immediate_dominators(dominators, entry)
    preds = get_preds(cfg)
    df = {block: set() for block in cfg} # block -> set of blocks

    for block in cfg:
        if block == entry:
            continue
        for pred in preds[block]:
            current = pred
            while current and current != block and current != idoms.get(block):
                df[current].add(block)
                current = idoms.get(current)

    return df


def print_tree(tree, root, indent='', last=True):
    connector = '└── ' if last else '├── '
    print(indent + connector + str(root))

    indent += '    ' if last else '│   '

    children = tree.get(root, [])
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        print_tree(tree, child, indent, is_last)


def get_all_paths(cfg, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]

    paths = []
    for succ in cfg.get(start, []):
        if succ not in path:
            paths.extend(get_all_paths(cfg, succ, end, path))
    return paths


def verify_dominators(cfg, dominators, entry):
    for block in cfg:
        paths = get_all_paths(cfg, entry, block)
        for dom in dominators[block]:
            if any(dom not in path for path in paths):
                return False
    return True


if __name__ == "__main__":
    prog = json.load(sys.stdin)

    for func in prog['functions']:
        print("Function:", func['name'])
        print()

        blocks = form_basic_blocks(func['instrs'])
        add_entry(blocks)
        func_cfg = form_cfg(blocks)
        entry = get_label(blocks[0])
        remove_unreachable(func_cfg, entry)
        dominators = get_dominators(func_cfg, entry)

        print("Dominators [block -> set of blocks]:")
        print("Passed correctness check" if verify_dominators(func_cfg, dominators, entry) else "Failed correctness check")
        for block, dom in dominators.items():
            print(f"{block} -> {dom}")
        print()

        print("Dominator tree:")
        dominator_tree = build_dominator_tree(dominators, entry)
        print_tree(dominator_tree, entry)
        print()

        print("Dominance frontier [block -> set of blocks]:")
        dominance_frontier = find_dominance_frontier(func_cfg, entry)
        for block, frontier in dominance_frontier.items():
            print(f"{block} -> {frontier}")
        print()

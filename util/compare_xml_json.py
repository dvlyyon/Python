import sys
import xml.etree.ElementTree as ET
import json

ET.register_namespace("ne","https://docs.python.org/3/library/json.html")
tree = ET.parse(sys.argv[1])
net_node = tree.getroot()
initstack = [net_node.tag.split("}")[1]]
json_node = json.load(open(sys.argv[2], "r"))
net_obj = []
json_obj = []

"""
  print netconf tree
"""
def print_netconf_tree(node,  stack):
    i = 0
    for child in node:
        i=i+1
        stack.append(child.tag.split("}")[1])
        print_netconf_tree(child, stack)
    if i == 0:
        print(".".join(stack), end="\n")
        net_obj.append(".".join(stack))
    stack.pop()

def print_json_list(node, stack):
    if len(node) == 0:
        print(".".join(stack))
        json_obj.append(".".join(stack))
        return

    for child in node:
        if isinstance (child, dict):
            print_json_dict(child,stack)
        elif isinstance (child,list):
            print("ERRRRRRRRRRRRRRRRRRRROR")
            sys.exit(1)
        else:
            print(".".join(stack))
            json_obj.append(".".join(stack))


def print_json_dict(node, stack):
    if len(node) == 0:
        print(".".join(stack))
        json_obj.append(".".join(stack))
        return

    for child in node:
        stack.append(child)
        if isinstance(node[child], dict):
            print_json_dict(node[child],stack)
        elif isinstance(node[child], list):
            print_json_list(node[child], stack)
        else:
            print(".".join(stack))
            json_obj.append(".".join(stack))
        stack.pop()


print_netconf_tree(net_node,initstack)
net_obj_set = set(net_obj)
initstack = [net_node.tag.split("}")[1]]
print_json_dict(json_node,initstack)
json_obj_set = set(json_obj)
print(f"set ==  net:{len(net_obj_set)}, json: {len(json_obj_set)}")
print(f"list ==  net:{len(net_obj)}, json: {len(json_obj)}")
n_s = net_obj_set - json_obj_set
s_n = json_obj_set - net_obj_set
print("============================net-json==================")
for o in n_s:
    print(o)
print("============================json-net==================")
for o in s_n:
    print(o)



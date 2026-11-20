import numpy as np
import matplotlib.pyplot as plt

def read_gmsh(fname):
    """Read GMSH mesh file and return nodes, elements and edge elements"""
    if not fname.endswith('.msh'):
        raise RuntimeError('Unexpected mesh file extension')
    nodes = []
    elems = []
    edge_elems = []
    parse_nodes = False
    parse_elems = False

    with open(fname) as msh:
        for line in msh:
            sp = line.split()
            if '$Nodes' in line:
                parse_nodes = True
            elif '$Elements' in line:
                parse_nodes = False
                parse_elems = True
            elif parse_nodes and len(sp) > 1:
                if len(sp[1:]) != 3:
                    raise SyntaxError('read_gmsh: Three coordinates per node are expected')
                coords = np.array(sp[1:], dtype=np.float64)
                nodes.append(coords)
            elif parse_elems and len(sp) > 1:
                eltype = int(sp[1])
                inodes = np.array(sp[3 + int(sp[2]):], dtype=np.int32) - 1
                if eltype == 1:
                    edge_elems.append(inodes)
                elif eltype == 2:
                    elems.append(inodes)
                else:
                    print(f"Unknown element type {eltype}")
    return np.array(nodes), np.array(elems), np.array(edge_elems)

def plot_mesh(nodes, connectivity):
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.triplot(nodes[:,0], nodes[:,1], connectivity, 'k-', lw=0.2)
    plt.axis('equal')
    plt.axis('off')




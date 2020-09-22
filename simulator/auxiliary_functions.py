import networkx as nx

def generate_default_gameboard_graph():
    G = nx.Graph()
    nodes = set()
    edges = set()
    for k in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J']:
        for i in range(1,11):
            for j in range(1,11):

                location_name = _convert_ijk_to_string(i,j,k)
                nodes.add(location_name)

                if (i>=2 and i<=9) and (j>=2 and j<=9): # the normal case
                    if j%2==0:
                        if i%2 == 0:
                            edges.add((location_name,_convert_ijk_to_string(i,j+1,k)))
                            edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i-1, j, k)))
                            edges.add((location_name, _convert_ijk_to_string(i+1, j, k)))
                            edges.add((location_name, _convert_ijk_to_string(i - 1, j + 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i + 1, j + 1, k)))
                        else:
                            edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i - 1, j, k)))
                            edges.add((location_name, _convert_ijk_to_string(i + 1, j, k)))
                            edges.add((location_name, _convert_ijk_to_string(i - 1, j - 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i + 1, j - 1, k)))
                    else:
                        if i % 2 == 0:
                            edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i - 1, j, k)))
                            edges.add((location_name, _convert_ijk_to_string(i + 1, j, k)))
                            edges.add((location_name, _convert_ijk_to_string(i - 1, j + 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i + 1, j + 1, k)))
                        else:
                            edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i - 1, j, k)))
                            edges.add((location_name, _convert_ijk_to_string(i + 1, j, k)))
                            edges.add((location_name, _convert_ijk_to_string(i - 1, j - 1, k)))
                            edges.add((location_name, _convert_ijk_to_string(i + 1, j - 1, k)))


                elif i == 1 and (j>=2 and j<=9) and k in ['B','C','E', 'F','H', 'J']: # left edges of zones
                    mapping = dict()
                    mapping['C'] = 'B'
                    mapping['B'] = 'A'
                    mapping['F'] = 'E'
                    mapping['E'] = 'D'
                    mapping['J'] = 'H'
                    mapping['H'] = 'G'
                    edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i + 1, j - 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i + 1, j, k)))
                    edges.add((location_name, _convert_ijk_to_string(10, j, mapping[k])))
                    edges.add((location_name, _convert_ijk_to_string(10, j-1, mapping[k])))

                elif i == 10 and (j>=2 and j<=9) and k in ['B','A','E', 'D','H', 'G']: # right edges of zones
                    mapping = dict()
                    mapping['A'] = 'B'
                    mapping['B'] = 'C'
                    mapping['D'] = 'E'
                    mapping['E'] = 'F'
                    mapping['G'] = 'H'
                    mapping['H'] = 'J'
                    edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i - 1, j + 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i - 1, j, k)))
                    edges.add((location_name, _convert_ijk_to_string(1, j, mapping[k])))
                    edges.add((location_name, _convert_ijk_to_string(1, j+1, mapping[k])))

                elif j == 1 and (i!=1 and i%2!=0) and k in ['D', 'E', 'F', 'G', 'H', 'J']: # top edges of zones
                    mapping = dict()
                    mapping['D'] = 'A'
                    mapping['E'] = 'B'
                    mapping['F'] = 'C'
                    mapping['G'] = 'D'
                    mapping['H'] = 'E'
                    mapping['J'] = 'F'
                    edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i+1, j, k)))
                    edges.add((location_name, _convert_ijk_to_string(i - 1, j, k)))
                    edges.add((location_name, _convert_ijk_to_string(i - 1, 10, mapping[k])))
                    edges.add((location_name, _convert_ijk_to_string(i, 10, mapping[k])))
                    edges.add((location_name, _convert_ijk_to_string(i+1, 10, mapping[k])))

                elif j == 10 and (i!=10 and i !=1) and k in ['D', 'E', 'F', 'A', 'B', 'C']: # bottom edges of zones
                    mapping = dict()
                    mapping['D'] = 'G'
                    mapping['E'] = 'H'
                    mapping['F'] = 'J'
                    mapping['A'] = 'D'
                    mapping['B'] = 'E'
                    mapping['C'] = 'F'
                    if i%2 == 0:
                        edges.add((location_name, _convert_ijk_to_string(i, 9, k)))
                        edges.add((location_name, _convert_ijk_to_string(i+1, 10, k)))
                        edges.add((location_name, _convert_ijk_to_string(i - 1, 10, k)))
                        edges.add((location_name, _convert_ijk_to_string(i - 1, 1, mapping[k])))
                        edges.add((location_name, _convert_ijk_to_string(i, 1, mapping[k])))
                        edges.add((location_name, _convert_ijk_to_string(i+1, 1, mapping[k])))
                    else:
                        edges.add((location_name, _convert_ijk_to_string(i, 9, k)))
                        edges.add((location_name, _convert_ijk_to_string(i + 1, 9, k)))
                        edges.add((location_name, _convert_ijk_to_string(i - 1, 9, k)))
                        edges.add((location_name, _convert_ijk_to_string(i - 1, 10, k)))
                        edges.add((location_name, _convert_ijk_to_string(i, 1, mapping[k])))
                        edges.add((location_name, _convert_ijk_to_string(i + 1, 10, k)))

                elif i == 1 and (j>=2 and j<=9) and k in ['A','D', 'G']: # left border of board

                    edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i + 1, j - 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i + 1, j, k)))

                elif i == 10 and (j >= 2 and j <= 9) and k in ['C', 'F', 'J']:  # right border of board

                    edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i - 1, j + 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i - 1, j, k)))

                elif j == 1 and (i!=1 and i%2!=0) and k in ['C', 'A', 'B']:  # top border of board

                    edges.add((location_name, _convert_ijk_to_string(i, j + 1, k)))
                    edges.add((location_name, _convert_ijk_to_string(i+1, j, k)))
                    edges.add((location_name, _convert_ijk_to_string(i - 1, j, k)))

                elif j == 10 and (i!=1 and i!=10) and k in ['G', 'H', 'J']:  # bottom border of board
                    if i%2 == 0:
                        edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                        edges.add((location_name, _convert_ijk_to_string(i+1, 10, k)))
                        edges.add((location_name, _convert_ijk_to_string(i - 1, 10, k)))
                    else:
                        edges.add((location_name, _convert_ijk_to_string(i, j - 1, k)))
                        edges.add((location_name, _convert_ijk_to_string(i + 1, 9, k)))
                        edges.add((location_name, _convert_ijk_to_string(i - 1, 9, k)))
                        edges.add((location_name, _convert_ijk_to_string(i + 1, 10, k)))
                        edges.add((location_name, _convert_ijk_to_string(i - 1, 10, k)))

    # now we come to corners: an ultra special case. We'll have to hardcode these
    edges.add((_convert_ijk_to_string(1, 1, 'A'), _convert_ijk_to_string(2, 1, 'A')))

    # we don't need to code some of the board corners, since their neighbors are covered already by the cases in the loop.
    edges.add((_convert_ijk_to_string(1, 1, 'G'),_convert_ijk_to_string(1, 10, 'D')))
    edges.add((_convert_ijk_to_string(1, 1, 'G'), _convert_ijk_to_string(2, 1, 'G')))
    edges.add((_convert_ijk_to_string(1, 1, 'D'), _convert_ijk_to_string(1, 10, 'A')))
    edges.add((_convert_ijk_to_string(1, 1, 'D'), _convert_ijk_to_string(2, 1, 'D')))
    edges.add((_convert_ijk_to_string(10, 10, 'F'), _convert_ijk_to_string(10, 1, 'J')))
    edges.add((_convert_ijk_to_string(10, 10, 'C'), _convert_ijk_to_string(10, 1, 'F')))

    # corner of DEGH
    edges.add((_convert_ijk_to_string(10, 10, 'D'), _convert_ijk_to_string(10, 9, 'D')))
    edges.add((_convert_ijk_to_string(10, 10, 'D'), _convert_ijk_to_string(9, 10, 'D')))
    edges.add((_convert_ijk_to_string(10, 10, 'D'), _convert_ijk_to_string(9, 1, 'G')))
    edges.add((_convert_ijk_to_string(10, 10, 'D'), _convert_ijk_to_string(10, 1, 'G')))
    edges.add((_convert_ijk_to_string(10, 10, 'D'), _convert_ijk_to_string(1, 1, 'H')))
    edges.add((_convert_ijk_to_string(10, 10, 'D'), _convert_ijk_to_string(1, 10, 'E')))
    edges.add((_convert_ijk_to_string(1, 10, 'E'), _convert_ijk_to_string(1, 1, 'H')))

    # corner of EFHJ
    edges.add((_convert_ijk_to_string(10, 10, 'E'), _convert_ijk_to_string(10, 9, 'E')))
    edges.add((_convert_ijk_to_string(10, 10, 'E'), _convert_ijk_to_string(9, 10, 'E')))
    edges.add((_convert_ijk_to_string(10, 10, 'E'), _convert_ijk_to_string(9, 1, 'H')))
    edges.add((_convert_ijk_to_string(10, 10, 'E'), _convert_ijk_to_string(10, 1, 'H')))
    edges.add((_convert_ijk_to_string(10, 10, 'E'), _convert_ijk_to_string(1, 1, 'J')))
    edges.add((_convert_ijk_to_string(10, 10, 'E'), _convert_ijk_to_string(1, 10, 'F')))
    edges.add((_convert_ijk_to_string(1, 10, 'F'), _convert_ijk_to_string(1, 1, 'J')))

    # corner of BCEF
    edges.add((_convert_ijk_to_string(10, 10, 'B'), _convert_ijk_to_string(10, 9, 'B')))
    edges.add((_convert_ijk_to_string(10, 10, 'B'), _convert_ijk_to_string(9, 10, 'B')))
    edges.add((_convert_ijk_to_string(10, 10, 'B'), _convert_ijk_to_string(9, 1, 'E')))
    edges.add((_convert_ijk_to_string(10, 10, 'B'), _convert_ijk_to_string(10, 1, 'E')))
    edges.add((_convert_ijk_to_string(10, 10, 'B'), _convert_ijk_to_string(1, 1, 'F')))
    edges.add((_convert_ijk_to_string(10, 10, 'B'), _convert_ijk_to_string(1, 10, 'C')))
    edges.add((_convert_ijk_to_string(1, 1, 'F'), _convert_ijk_to_string(1, 10, 'C')))

    # corner of ABDE
    edges.add((_convert_ijk_to_string(10, 10, 'A'), _convert_ijk_to_string(10, 9, 'A')))
    edges.add((_convert_ijk_to_string(10, 10, 'A'), _convert_ijk_to_string(9, 10, 'A')))
    edges.add((_convert_ijk_to_string(10, 10, 'A'), _convert_ijk_to_string(9, 1, 'D')))
    edges.add((_convert_ijk_to_string(10, 10, 'A'), _convert_ijk_to_string(10, 1, 'D')))
    edges.add((_convert_ijk_to_string(10, 10, 'A'), _convert_ijk_to_string(1, 1, 'E')))
    edges.add((_convert_ijk_to_string(10, 10, 'A'), _convert_ijk_to_string(1, 10, 'B')))
    edges.add((_convert_ijk_to_string(1, 1, 'E'), _convert_ijk_to_string(1, 10, 'B')))

    for e in edges:
        G.add_edge(e[0],e[1])

    #testing
    # print(nx.algorithms.diameter(G))
    # print(nx.algorithms.shortest_paths.generic.shortest_path(G, source='0101A',target='1010J'))
    print('returning gameboard graph...')
    return G



def _convert_ijk_to_string(i,j,k):
    location_name = ""
    if i >= 10:
        location_name += str(i)
    else:
        location_name += ('0' + str(i))

    if j >= 10:
        location_name += str(j)
    else:
        location_name += ('0' + str(j))
    location_name += k

    return location_name

# generate_default_gameboard_graph()





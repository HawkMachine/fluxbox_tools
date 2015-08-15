class Error(Exception):
  pass


def GetGridNodeLabelMaker(width, height, depth):
  """Creates default grid graph node label maker."""
  def _edge_label_maker(x, y, z):
    return (x, y, z)
  return _edge_label_maker


def GetGridEdgeLabelMaker(width, height, depth, up='up', down='down',
    left='left', right='right', z_up='z_up', z_down='z_down', wrap_x=False,
    wrap_y=False, wrap_z=False):
  """Creates edge label maker for grid graph."""
  def _edge_label_maker(x1, y1, z1, x2, y2, z2):
    directions = {
        ( 1,  0,  0): [right],
        (-1,  0,  0): [left],
        ( 0,  1,  0): [up],
        ( 0, -1,  0): [down],
        ( 0,  0,  1): [z_up],
        ( 0,  0, -1): [z_down],
    }
    def _add_or_append(dct, key, value):
      if key in dct:
        dct[key].append(value)
      else:
        dct[key] = [value]
    if wrap_x:
      _add_or_append(directions, (width-1, 0, 0) , left)
      _add_or_append(directions, (1-width, 0, 0) , right)
    if wrap_y:
      _add_or_append(directions, (0, height-1, 0) , down)
      _add_or_append(directions, (0, 1-height, 0) , up)
    if wrap_z:
      _add_or_append(directions, (0, 0, depth-1) , z_down)
      _add_or_append(directions, (0, 0, 1-depth) , z_up)
    key = (x2 - x1, y2 - y1, z2 - z1)
    return directions.get(key, None)
  return _edge_label_maker


class Node(object):

  def __init__(self, label):
    self._label = label
    self._edges = {}

  def Label(self):
    return self._label

  def GetEdge(self, label):
    return self._edges[label]

  def Edges(self):
    return list(self._edges.values())


class Edge(object):

  def __init__(self, begin, label, end):
    self._begin = begin
    self._label = label
    self._end = end

  def GetBegin(self):
    return self._begin

  def GetEnd(self):
    return self._end

  def Label(self):
    return self._label


class Graph(object):

  def __init__(self):
    self._nodes = {}
    self._edges = []

  def Nodes(self):
    return list(self._nodes.values())

  def Edges(self):
    return list(self._edges)

  def AddNode(self, label):
    # print 'Adding node', label
    if label in self._nodes:
      raise Error('Node %s already exists' % label)
    node = Node(label)
    self._nodes[label] = node
    return node

  def GetNode(self, label):
    return self._nodes[label]

  def AddEdge(self, begin_label, label, end_label):
    # print 'Adding Edge', begin_label, label, end_label
    """Adds new edge with given label. Label has to be unique in begin node."""
    begin = self.GetNode(begin_label)
    end = self.GetNode(end_label)

    if label in begin._edges:
      raise Error('Edge %s already exists in node %s' % (label, begin_label))
    edge = Edge(begin.Label(), label, end.Label())
    begin._edges[label] = edge
    self._edges.append(edge)
    return edge


class GridGraph(Graph):

  def __init__(self, width, height, depth):
    super(GridGraph, self).__init__()
    self._width = width
    self._height = height
    self._depth = depth

  def Width(self):
    return self._width

  def Height(self):
    return self._height

  def Depth(self):
    return self._depth


def GetGridGraph(width, height, depth=1, wrap_x=None, wrap_y=None, wrap_z=None,
    node_label_maker=None, edge_label_maker=None):
  """Creates a grid graph with with given dimensions.

  A node is created for each natural coefficient within points (0, 0, 0) and
  (width, height, depth).

    y   z
    ^  /
    | /
    |/
    +----> x

  By default label for each node will be a tuple (x, y, z) - its coordinates.
  You can provide your own node label maker with node_label_maker parameter,
  which has to be a function that takes the location of the node in the grid as
  parameters: x, y, z.

  By default for each two nodes (a, b, c) and (x, y, z) an edge will be created
  if |a - x| + |b - y| + |c - z| == 1 (nodes are neighbours). Edges in the plane
  defined by x and y axes (xy plane) will be given 'up', 'down', 'left', 'up',
  labels. Edges in the yz plane (that are not in the xy plane) will be given
  'z_down' and 'z_up' labels.

  You can customize the names (or even the whole graph) by providing a custom
  edge label maker with edge_label_maker parameter. It should be a function that
  takes coordinates of two points A (x1, y1, z3) and B (x2, y2, z2) and returns
  a list of labels - for each an edge will be created from A to B.

  To glue sides of the cubicle set wrap_{x,y,z} to True. These paramets are
  ignored if you provide a custom edge label maker.
  """
  if width < 1 or height < 1 or depth < 1:
    raise Error("Cannot create %dx%dx%d grid graph" % (width, height, depth))
  
  # label makers defaults.
  if node_label_maker is None:
    node_label_maker = GetGridNodeLabelMaker(
        width, height, depth)
  if not edge_label_maker:
    edge_label_maker = GetGridEdgeLabelMaker(
        width, height, depth, wrap_x=wrap_x, wrap_y=wrap_y, wrap_z=wrap_z)

  graph = GridGraph(width, height, depth)

  def node_position_range(width, height, depth):
    for x in xrange(width):
      for y in xrange(height):
        for z in xrange(depth):
          yield x, y, z

  # nodes
  for x, y, z in node_position_range(width, height, depth):
    graph.AddNode(node_label_maker(x, y, z))

  # edges
  for x1, y1, z1 in node_position_range(width, height, depth):
    for x2, y2, z2 in node_position_range(width, height, depth):
      labels = edge_label_maker(x1, y1, z1, x2, y2, z2)
      if labels:
        for label in labels:
          graph.AddEdge(
              node_label_maker(x1, y1, z1),
              label,
              node_label_maker(x2, y2, z2))
  return graph

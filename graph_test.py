import unittest
import graph

class GridGraphTest(unittest.TestCase):

  # 4x3x2 grid graph used in tests:
  #  z == 0
  #  8  9 10 11
  #  4  5  6  7
  #  0  1  2  3
  #
  #  z == 1
  #  20 21 22 23
  #  16 17 18 19
  #  12 13 14 15

  def test_SimpleGrid(self):
    def _node_label_maker(x, y, z):
      return x + 4*y + 12*z

    g = graph.GetGridGraph(4,3,2, node_label_maker=_node_label_maker)
    self.assertEqual(set([n.Label() for n in g.Nodes()]), set(range(4*3*2)))

    n0 = g.GetNode(0)
    self.assertEqual(set([e.Label() for e in n0.Edges()]),
        set(['up', 'right', 'z_up']))
    self.assertEqual(n0.GetEdge('up').GetEnd(), 4)
    self.assertEqual(n0.GetEdge('right').GetEnd(), 1)
    self.assertEqual(n0.GetEdge('z_up').GetEnd(), 12)

    n0 = g.GetNode(17)
    self.assertEqual(set([e.Label() for e in n0.Edges()]),
        set(['up', 'down', 'right', 'left', 'z_down']))
    self.assertEqual(n0.GetEdge('up').GetEnd(), 21)
    self.assertEqual(n0.GetEdge('down').GetEnd(), 13)
    self.assertEqual(n0.GetEdge('right').GetEnd(), 18)
    self.assertEqual(n0.GetEdge('left').GetEnd(), 16)
    self.assertEqual(n0.GetEdge('z_down').GetEnd(), 5)

  def test_WrapX(self):
    def _node_label_maker(x, y, z):
      return x + 4*y + 12*z
    g = graph.GetGridGraph(4,3,2, wrap_x=True, node_label_maker=_node_label_maker)

    n0 = g.GetNode(0)
    self.assertEqual(set([e.Label() for e in n0.Edges()]),
        set(['up', 'right', 'z_up', 'left']))
    self.assertEqual(n0.GetEdge('up').GetEnd(), 4)
    self.assertEqual(n0.GetEdge('right').GetEnd(), 1)
    self.assertEqual(n0.GetEdge('left').GetEnd(), 3)
    self.assertEqual(n0.GetEdge('z_up').GetEnd(), 12)

  def test_WrapY(self):
    def _node_label_maker(x, y, z):
      return x + 4*y + 12*z
    g = graph.GetGridGraph(4,3,2, wrap_y=True, node_label_maker=_node_label_maker)

    n0 = g.GetNode(0)
    self.assertEqual(set([e.Label() for e in n0.Edges()]),
        set(['up', 'right', 'z_up', 'down']))
    self.assertEqual(n0.GetEdge('up').GetEnd(), 4)
    self.assertEqual(n0.GetEdge('down').GetEnd(), 8)
    self.assertEqual(n0.GetEdge('right').GetEnd(), 1)
    self.assertEqual(n0.GetEdge('z_up').GetEnd(), 12)

  def test_WrapZ(self):
    def _node_label_maker(x, y, z):
      return x + 4*y + 12*z
    g = graph.GetGridGraph(4,3,2, wrap_z=True, node_label_maker=_node_label_maker)

    n0 = g.GetNode(0)
    self.assertEqual(set([e.Label() for e in n0.Edges()]),
        set(['up', 'right', 'z_up', 'z_down']))
    self.assertEqual(n0.GetEdge('up').GetEnd(), 4)
    self.assertEqual(n0.GetEdge('right').GetEnd(), 1)
    self.assertEqual(n0.GetEdge('z_up').GetEnd(), 12)
    self.assertEqual(n0.GetEdge('z_down').GetEnd(), 12)

  def test_DefaultNodeLabelMaker(self):
    g = graph.GetGridGraph(4,3,2)

    n0 = g.GetNode((0,0,0))
    self.assertEqual(set([e.Label() for e in n0.Edges()]),
        set(['up', 'right', 'z_up']))
    self.assertEqual(n0.GetEdge('up').GetEnd(), (0, 1, 0))
    self.assertEqual(n0.GetEdge('right').GetEnd(), (1, 0, 0))
    self.assertEqual(n0.GetEdge('z_up').GetEnd(), (0, 0, 1))

    n0 = g.GetNode((1,1, 1))
    self.assertEqual(set([e.Label() for e in n0.Edges()]),
        set(['up', 'down', 'right', 'left', 'z_down']))
    self.assertEqual(n0.GetEdge('up').GetEnd(), (1, 2, 1))
    self.assertEqual(n0.GetEdge('down').GetEnd(), (1, 0, 1))
    self.assertEqual(n0.GetEdge('right').GetEnd(), (2, 1, 1))
    self.assertEqual(n0.GetEdge('left').GetEnd(), (0, 1, 1))
    self.assertEqual(n0.GetEdge('z_down').GetEnd(), (1, 1, 0))

  def test_NegativeWidth(self):
    with self.assertRaises(graph.Error):
      graph.GetGridGraph(-1, 2, 2)


if __name__ == '__main__':
    unittest.main()

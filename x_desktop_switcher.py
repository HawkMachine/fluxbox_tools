import sys
import json
import pynotify
import argparse
import subprocess

import graph


class XDesktopsControler(object):
  """Implementation of desktop controller with xdotool."""

  def GetCurrentDesktop(self):
    return int(subprocess.check_output(['xdotool', 'get_desktop']))

  def SetDesktop(self, desktop):
    return subprocess.call(['xdotool', 'set_desktop', str(desktop)])

  def GetNumDesktops(self):
    return int(subprocess.check_output(['xdotool', 'get_num_desktops']))

  def SetNumDesktops(self, num):
    return subprocess.call(['xdotool', 'set_num_desktops', str(num)])


class FluxboxWorkspaceGridConf(object):

  def __init__(self, graph_, workspace_name=None):
    self.graph_ = graph_
    self.workspace_name = workspace_name  or ""
    if not self.workspace_name:
      if self.graph_.Width() > 1:
        self.workspace_name += "X%(x)s "
      if self.graph_.Height() > 1:
        self.workspace_name += "Y%(y)s "
      if self.graph_.Depth() > 1:
        self.workspace_name += "Z%(z)s"

  def Label2Id(self, label):
    x, y, z = label
    return x + y*self.graph_.Width() + z*self.graph_.Width()*self.graph_.Height()

  def Id2Label(self, id_):
    return (
        id_ % self.graph_.Width(),
        (id_ / self.graph_.Width()) % self.graph_.Height(),
        id_ / (self.graph_.Width()*self.graph_.Height()))

  def WorkspaceName(self, label):
    x, y, z = label
    return self.workspace_name % {'x': x, 'y': y, 'z': z}


class FluxboxWorkspaceCustomConf(object):

  def Label2Id(self, id_):
    return id_

  def Id2Label(self, label):
    return label

  def WorkspaceName(self, label):
    return str(label)



class DesktopSwitcher(object):

  def __init__(self, desktops_graph, desktops_controller):
    self.desktops_graph = desktops_graph
    self.desktops_controller = desktops_controller

  def Command(self, command):
    cur = self.desktops_controller.GetCurrentDesktop()
    node = self.desktops_graph.GetDesktop(cur)
    target = node.GetEdge(command).GetEnd()
    self.desktops_controller.SetDesktop(target)


def GetGridNodeLabelMaker(width, height, depth):
  """Grid node label maker for Fluxbox."""
  def _node_label_maker(x, y, z):
    return x + y*width + z*width*height
  return _node_label_maker


def MoveInGraph(graph_, label, cmds):
  node = graph_.GetNode(label)
  for cmd in cmds:
    node = graph_.GetNode(node.GetEdge(cmd).GetEnd())
  return node


def ShowNitification(msg):
  n = pynotify.Notification("X-Desktop Switcher Error", "Error: %s" % msg)
  n.show()

def GetGraphFromConfig(conf):
  """Loads graph from config and returns graph and translation func.
  
  Returns:
    graph, fluxbox_conf
    where:
      graph - the topology of workspaces.
      fluxbox_conf - an object that helps using graph with fluxbox.
  """
  graph_conf = conf['graph']
  if graph_conf['type'] == 'grid':
    width = graph_conf['width']
    height = graph_conf.get('height', 1)
    depth = graph_conf.get('depth', 1)
    wrap_x = graph_conf.get('wrap_x', False)
    wrap_y = graph_conf.get('wrap_y', False)
    wrap_z = graph_conf.get('wrap_z', False)

    graph_ = graph.GetGridGraph(
        width, height, depth, wrap_x=wrap_x, wrap_y=wrap_y, wrap_z=wrap_z)

    return graph_, FluxboxWorkspaceGridConf(graph_)

  elif graph_conf['type'] == 'custom':
    graph_ = graph.Graph()
    for x in xrange(graph_conf['nodes']):
      graph_.AddNode(x)
    for e in xrange(graph_conf['edges']):
      graph_.AddEdge(*e)
    return graph_, FluxboxWorkspaceCustomConf()
  raise ValueError('Unsupported graph type: %s' % graph_conf['type'])


def LoadConfig(config_path):
  with open(config_path, 'r') as fh:
    content = fh.read()
  conf = json.loads(content)
  return conf


def ValidateGraph(graph_, x_desk_ctrl, fluxboxConf):
  node_labels = [n.Label() for n in graph_.Nodes()]
  if len(node_labels) != x_desk_ctrl.GetNumDesktops():
    raise ValueError('Graph nodes is %d != %d workspaces' % (
      len(graph_.Nodes()), x_desk_ctrl.GetNumDesktops()))
  node_ids = [fluxboxConf.Label2Id(label) for label in node_labels]
  if sorted(node_ids) != range(len(node_ids)):
    raise ValueError('Node\'s labels are not consecutive natural numbers')


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--config', '-c', dest='config')
  parser.add_argument('--validate', dest='validate', action='store_const',
      const=True)
  parser.add_argument('--go', dest='go', type=str, nargs='+')
  parser.add_argument('--print_workspaces_names', dest='print_workspaces_names',
      action='store_const', const=True)
  parser.add_argument('--print_fluxbox_conf', dest='print_fluxbox_conf',
      action='store_const', const=True)

  args = parser.parse_args()

  x_desk_ctrl = XDesktopsControler()

  if not args.config:
    parser.print_help()
    return

  pynotify.init("Basic")
  conf = LoadConfig(args.config)
  if not conf:
    conf = {
        'graph': {
          'type': 'grid',
          'width': x_desk_ctrl.GetNumDesktops(),
          'height': 1,
          'depth': 1,
        },
    }
  graph_, fluxboxConf = GetGraphFromConfig(conf)

  if args.validate:
    ValidateGraph(graph_, x_desk_ctrl, fluxboxConf)
    return
  elif args.print_fluxbox_conf:
    desktopsNum = x_desk_ctrl.GetNumDesktops()
    nodesInOrder = [graph_.GetNode(fluxboxConf.Id2Label(i)) for i in xrange(desktopsNum)]
    s = [fluxboxConf.WorkspaceName(n.Label()) for n in nodesInOrder]
    print '\n'.join([
        'session.screen0.workspaces: %d' % len(graph_.Nodes()),
        'session.screen0.workspaceNames: ' + ','.join(s),
       ])
    return
  elif args.go:
    try:
      cur = x_desk_ctrl.GetCurrentDesktop()
      label = fluxboxConf.Id2Label(cur)
      print 'Current desktop =', cur
      print 'Graph node      =', label

      node = MoveInGraph(graph_, label, args.go)

      target = fluxboxConf.Label2Id(node.Label())
      print 'Target desktop  =', target
      print 'Graph node      =', node.Label()

      x_desk_ctrl.SetDesktop(target)
    except KeyError as e:
      ShowNitification("%s" % e)
      return 1
  else:
    parser.print_help()

if __name__ == '__main__':
  sys.exit(main() or 0)

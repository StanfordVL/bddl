from abc import abstractmethod, ABCMeta
import hashlib
import numpy as np

import networkx as nx
from future.utils import with_metaclass
from bddl.utils import UncontrolledCategoryError
from bddl.enum_obj_states import UnaryStatesEnum, BinaryStatesEnum, NodeTypeEnum, EdgeTypeEnum, JunctionTypeEnum, get_feature

class Expression(with_metaclass(ABCMeta)):
    def __init__(self, scope, backend, body, object_map):
        self.children = []
        self.child_values = []
        self.kwargs = {}
        self.body = body
        self.scope = scope
        self.backend = backend
        self.object_map = object_map
        self.unique = hashlib.md5(str(id(self)).encode("ascii")).hexdigest()[:6]

    def __str__(self):
        return type(self).__name__ + "-" + self.unique

    @abstractmethod
    def evaluate(self):
        pass

    def to_graph(self, G: nx.DiGraph):
        if len(self.children) == 1:
            return self.children[0].to_graph(G)

        nodename = str(self)
        assert nodename not in G.nodes

        G.add_node(nodename, node_type=NodeTypeEnum.Junction.value, node_feature=get_feature(JunctionTypeEnum[type(self).__name__]))
        for child in self.children:
            childnodename = child.to_graph(G)
            G.add_edge(nodename, childnodename, edge_type=EdgeTypeEnum.Child.value)

        return nodename


class AtomicFormula(Expression):
    def __init__(self, scope, backend, body, object_map):
        super().__init__(scope, backend, body, object_map)


class BinaryAtomicFormula(AtomicFormula):
    STATE_NAME = None

    def __init__(self, scope, backend, body, object_map):
        super().__init__(scope, backend, body, object_map)
        assert len(body) == 2, 'Param list should have 2 args'
        self.input1, self.input2 = [inp.strip('?') for inp in body]
        self.scope = scope
        try:
            if isinstance(self.scope[self.input1], str):
                self.input1 = self.scope[self.input1]
        except KeyError:
            raise UncontrolledCategoryError
        try:
            if isinstance(self.scope[self.input2], str):
                self.input2 = self.scope[self.input2]
        except KeyError:
            raise UncontrolledCategoryError

        self.get_ground_options()

    @abstractmethod
    def _evaluate(self, obj1, obj2):
        pass

    def evaluate(self):
        if (self.scope[self.input1] is not None) and (self.scope[self.input2] is not None):
            return self._evaluate(self.scope[self.input1], self.scope[self.input2], **self.kwargs)
        else:
            print('%s and/or %s are not mapped to simulator objects in scope' %
                  (self.input1, self.input2))

    @abstractmethod
    def _sample(self, obj1, obj2, binary_state):
        pass

    def sample(self, binary_state):
        if (self.scope[self.input1] is not None) and (self.scope[self.input2] is not None):
            return self._sample(self.scope[self.input1], self.scope[self.input2], binary_state, **self.kwargs)
        else:
            print('%s and/or %s are not mapped to simulator objects in scope' %
                  (self.input1, self.input2))

    def get_ground_options(self):
        self.flattened_condition_options = [
            [[self.STATE_NAME, self.input1, self.input2]]]

    def to_graph(self, G: nx.DiGraph):
        nodename = str(self)
        assert nodename not in G.nodes, "%s already in nodes" % nodename

        feature = get_feature(BinaryStatesEnum[self.STATE_CLASS.__name__])

        G.add_node(nodename, node_type=NodeTypeEnum.BinaryAtomicFormula.value, node_feature=feature)
        G.add_edge(nodename, self.input1, edge_type=EdgeTypeEnum.Argument1.value)
        G.add_edge(nodename, self.input2, edge_type=EdgeTypeEnum.Argument2.value)

        return nodename


class UnaryAtomicFormula(AtomicFormula):
    STATE_NAME = None

    def __init__(self, scope, backend, body, object_map):
        super().__init__(scope, backend, body, object_map)
        assert len(body) == 1, 'Param list should have 1 arg'
        self.input = body[0].strip('?')
        self.scope = scope
        try:
            if isinstance(self.scope[self.input], str):
                self.input = self.scope[self.input]
        except KeyError:
            raise UncontrolledCategoryError

        self.get_ground_options()

    @abstractmethod
    def _evaluate(self, obj):
        pass

    def evaluate(self):
        if self.scope[self.input] is not None:
            return self._evaluate(self.scope[self.input], **self.kwargs)
        else:
            print('%s is not mapped to a simulator object in scope' % self.input)
            return False

    @abstractmethod
    def _sample(self, obj, binary_state):
        pass

    def sample(self, binary_state):
        if self.scope[self.input] is not None:
            return self._sample(self.scope[self.input], binary_state, **self.kwargs)
        else:
            print('%s is not mapped to a simulator object in scope' % self.input)
            return False

    def get_ground_options(self):
        self.flattened_condition_options = [
            [[self.STATE_NAME, self.input]]]

    def to_graph(self, G: nx.DiGraph):
        nodename = str(self)
        assert nodename not in G.nodes, "%s already in nodes" % nodename

        feature = get_feature(UnaryStatesEnum[self.STATE_CLASS.__name__])

        G.add_node(nodename, node_type=NodeTypeEnum.UnaryAtomicFormula.value, node_feature=feature)
        G.add_edge(nodename, self.input, edge_type=EdgeTypeEnum.Argument1.value)

        return nodename
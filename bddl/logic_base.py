from abc import abstractmethod, ABCMeta

from future.utils import with_metaclass
from bddl.utils import UncontrolledCategoryError


class Expression(with_metaclass(ABCMeta)):
    def __init__(self, scope, backend, body, object_map):
        self.children = []
        self.child_values = []
        self.kwargs = {}
        self.body = body
        self.scope = scope
        self.backend = backend
        self.object_map = object_map

    @abstractmethod
    def evaluate(self):
        pass


class AtomicFormula(Expression):
    def __init__(self, scope, backend, body, object_map):
        super().__init__(scope, backend, body, object_map)
        self.inputs = [input.strip("?") for input in self.body]
        for i, input in enumerate(self.inputs): 
            try: 
                if isinstance(self.scope[input], str):
                    self.inputs[i] = self.scope[input]
            except: 
                raise UncontrolledCategoryError
        self.get_ground_options()
    
    @abstractmethod 
    def _evalute(self, *args):         # TODO figure out how to handle variable-arities
        pass 

    def evaluate(self):
        if all([self.scope[input] is not None for input in self.inputs]):
            return self._evaluate(*self.inputs, **self.kwargs)     # TODO figure out how to handle variable-arities 
        else: 
            print("One of the inputs is not mapped to simulator objects in scope")
    
    @abstractmethod 
    def _sample(self, *args):      # TODO figure out how to handle variable-arities 
        pass 

    def sample(self):
        if all([self.scope[input] is not None for input in self.inputs]):
            return self._sample(*self.inputs, **self.kwargs)     # TODO figure out how to handle variable-arities 
        else: 
            print("One of the inputs is not mapped to simulator objects in scope")    
    
    def get_ground_options(self):
        self.flattened_condition_options = [[self.STATE_NAME] + self.inputs]

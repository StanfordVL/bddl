from abc import abstractmethod, ABCMeta

from future.utils import with_metaclass


class BEHAVIORBackend(with_metaclass(ABCMeta)):
    @abstractmethod
    def get_predicate_class(self, predicate_name):
        """Given predicate_name, return an implementation of behavior.logic_base.AtomicFormula or subclasses."""
        pass
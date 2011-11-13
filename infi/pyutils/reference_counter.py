from contextlib import contextmanager

class InvalidReferenceCount(Exception):
    pass

class ReferenceCounter(object):
    def __init__(self):
        super(ReferenceCounter, self).__init__()
        self._reference = 0
        self._depends_on = []
    def add_reference(self):
        self._reference += 1
        try:
            if self._reference == 1:
                self._increase_dependents()
                try:
                    self._on_reference_first_added()
                except:
                    self._decrease_dependents()
                    raise
        except:
            self._reference -= 1
            raise
    def depend_on_counter(self, counter):
        if self._reference > 0:
            counter.add_reference()
        self._depends_on.append(counter)
    def _increase_dependents(self):
        self._for_each_dependent(_ADDREF, rollback=_DECREF)
    def _decrease_dependents(self):
        self._for_each_dependent(_DECREF, rollback=_ADDREF)
    def _for_each_dependent(self, action, rollback):
        done = []
        for c in self._depends_on:
            try:
                action(c)
            except:
                for d in done:
                    rollback(d)
                raise
            else:
                done.append(c)
    def _decrease_dependents(self):
        for c in self._depends_on:
            c.remove_reference()
    def remove_reference(self):
        if self._reference <= 0:
            raise InvalidReferenceCount()
        self._reference -= 1
        if self._reference == 0:
            try:
                self._on_reference_last_dropped()
            except:
                self._reference += 1
                raise
            self._decrease_dependents()
    @contextmanager
    def get_reference_context(self):
        self.add_reference()
        try:
            yield self
        finally:
            self.remove_reference()
    def get_reference_count(self):
        return self._reference
    def _on_reference_first_added(self):
        pass
    def _on_reference_last_dropped(self):
        pass

_ADDREF = lambda c: c.add_reference()
_DECREF = lambda c: c.remove_reference()

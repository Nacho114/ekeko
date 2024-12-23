import multiprocessing

class EkekoConfig:
    def __init__(self):
        self._num_processors = 2

    @property
    def num_processors(self):
        return self._num_processors

    @num_processors.setter
    def num_processors(self, value: int):
        assert value > 0
        self._num_processors = value


# Create a global instance
config = EkekoConfig()


multiprocessing.set_start_method("spawn", force=True)

def set_num_processors(value: int):
    config.num_processors = value


def get_num_processors() -> int:
    return config.num_processors


import hou
import os
from pathlib import Path

from mvl_make_dailies.common_utils import logger

from mvl_make_dailies.houdini import RenderStrategy

class HoudiniRenderManager:
    def __init__(self, strategy: RenderStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: RenderStrategy):
        self.strategy = strategy

    def render(self, **kwargs):
        return self.strategy.render(**kwargs)


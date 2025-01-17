from typing import Tuple, Optional, Union
from contextlib import contextmanager

from pygame import Surface

from dungeon import pre_screen
from dungeon.components import TileComponent
from dungeon.entity import Entity
from utils.surface import get_scaled_surface


class ViewPort:
    def __init__(self,
                 size: Tuple[int, int],
                 render_pos: Tuple[int, int],
                 inner_size: Tuple[int, int],
                 output_size: Tuple[int, int],
                 target: Optional[Union[Entity, Tuple[int, int]]] = (0, 0)):
        self.width, self.height = size
        self.inner_width, self.inner_height = inner_size
        self.border_width, self.border_height = (self.width - self.inner_width) // 2, (
                self.height - self.inner_height) // 2
        self._x, self._y = 0, 0
        # for render.
        self.render_pos = render_pos
        self.surface = Surface(size).convert_alpha()
        self.followed = True if isinstance(target, Entity) else False
        self.target = target
        if isinstance(target, Entity):
            target.followed = self
        self.screen = pre_screen
        self.child: 'Optional[TileComponent]' = None
        # self.fix_init()
        self.output_size = output_size
        self.follow_sprite = True
        self.update_pos()

    @property
    def target_x(self):
        if isinstance(self.target, Entity):
            if self.follow_sprite:
                return self.target.sprite.pos_x
            else:
                return 16*self.target.x
        else:
            return self.target[0]

    @property
    def target_y(self):
        if isinstance(self.target, Entity):
            if self.follow_sprite:
                return self.target.sprite.pos_y
            else:
                return 16*self.target.y
        else:
            return self.target[1]

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if value < 0:
            self._x = 0
        elif value > self.screen.get_width() - self.width:
            self._x = self.screen.get_width() - self.width
        else:
            self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if value < 0:
            self._y = 0
        elif value > self.screen.get_height() - self.height:
            self._y = self.screen.get_height() - self.height
        else:
            self._y = value

    @property
    def center_x(self):
        return self.x + self.width // 2

    @property
    def center_y(self):
        return self.y + self.height // 2

    @contextmanager
    def suspend_follow(self):
        self.follow_sprite = False
        yield self
        self.follow_sprite = True

    def fix_init(self):
        """主要是防止动态属性在init中不生效."""
        self.x = self.target_x - (self.width // 2)
        self.y = self.target_y - (self.height // 2)

    def update_x(self):
        if abs(self.target_x - self.center_x) <= self.inner_width // 2:
            return
        if self.target_x < self.center_x:
            self.x = self.target_x - self.border_width
        else:
            self.x = self.target_x - self.border_width - self.inner_width

    def update_y(self):
        if abs(self.target_y - self.center_y) <= self.inner_height // 2:
            return
        if self.target_y < self.center_y:
            self.y = self.target_y - self.border_height
        else:
            self.y = self.target_y - self.border_height - self.inner_height

    def update_pos(self):
        self.update_x()
        self.update_y()

    def render_view(self):
        self.update_pos()
        render_surface = get_scaled_surface(self.screen.subsurface(self.x, self.y, self.width, self.height).copy(),
                                            self.output_size)
        self.screen.fill((0, 0, 0, 0))
        self.screen.blit(render_surface, self.render_pos)

    def render_gui(self, source: 'Surface', pos: Tuple[int, int]):
        pass

    def render_components(self):
        if self.child:
            self.child.render_all()

    def add_components(self, components_tree: 'TileComponent'):
        self.child = components_tree

    def render(self):
        self.render_view()
        self.render_components()

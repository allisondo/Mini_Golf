from math import sqrt, cos, sin, pi
import pygame
import sys


__all__ = ('Task', 'Animation', 'remove_animations_of')



PY2 = sys.version_info[0] == 2
string_types = None
text_type = None
if PY2:
    string_types = basestring
    text_type = unicode
else:
    string_types = text_type = str


def remove_animations_of(group, target):
    animations = [ani for ani in group.sprites() if isinstance(ani, Animation)]
    to_remove = [ani for ani in animations if target in ani.targets]
    group.remove(*to_remove)


class Task(pygame.sprite.Sprite):
    def __init__(self, callback, interval=0, loops=1, args=None, kwargs=None):
        assert (callable(callback))
        assert (loops >= -1)
        super(Task, self).__init__()
        self.interval = interval
        self.loops = loops
        self.callback = callback
        self._timer = 0
        self._args = args if args else list()
        self._kwargs = kwargs if kwargs else dict()
        self._loops = loops
        self._chain = list()

    def chain(self, *others):
        if self._loops == -1:
            raise ValueError
        for task in others:
            assert isinstance(task, Task)
            self._chain.append(task)

    def update(self, dt):
        self._timer += dt
        if self._timer >= self.interval:
            self._timer -= self.interval
            self.callback(*self._args, **self._kwargs)
            if not self._loops == -1:
                self._loops -= 1
                if self._loops <= 0:
                    self._execute_chain()
                    self._chain = None
                    self.kill()

    def _execute_chain(self):
        groups = self.groups()
        for task in self._chain:
            task.add(*groups)


class Animation(pygame.sprite.Sprite):
    def __init__(self, **kwargs):
        super(Animation, self).__init__()
        self.targets = None
        self.delay = kwargs.get('delay', 0)
        self._started = False
        self._round_values = kwargs.get('round_values', False)
        self._duration = float(kwargs.get('duration', 1000.))
        self._transition = kwargs.get('transition', 'linear')
        self._initial = kwargs.get('initial', None)
        if isinstance(self._transition, string_types):
            self._transition = getattr(AnimationTransition, self._transition)
        self._elapsed = 0.
        for key in ('duration', 'transition', 'round_values', 'delay',
                    'initial'):
            kwargs.pop(key, None)
        self.props = kwargs

    def _get_value(self, target, name):
        if self._initial is None:
            attr = getattr(target, name)
            if callable(attr):
                value = attr()
                if value is None:
                    return 0
            else:
                return getattr(target, name)
        else:
            if callable(self._initial):
                return self._initial()
            else:
                return self._initial

    @staticmethod
    def _set_value(target, name, value):
        attr = getattr(target, name)
        if callable(attr):
            attr(value)
        else:
            setattr(target, name, value)

    def update(self, dt):
        self._elapsed += dt
        if self.delay > 0:
            if self._elapsed < self.delay:
                return
            else:
                self._elapsed -= self.delay
                self.delay = 0

        p = min(1., self._elapsed / self._duration)
        t = self._transition(p)
        for target, props in self.targets:
            for name, values in props.items():
                a, b = values
                value = (a * (1. - t)) + (b * t)

                if self._round_values:
                    value = int(round(value, 0))

                self._set_value(target, name, value)

        if hasattr(self, 'update_callback'):
            self.update_callback()

        if p >= 1:
            self.finish()

    def finish(self):
        if self.targets is not None:
            for target, props in self.targets:
                for name, values in props.items():
                    a, b = values
                    self._set_value(target, name, b)

        if hasattr(self, 'update_callback'):
            self.update_callback()

        self.targets = None
        self.kill()
        if hasattr(self, 'callback'):
            self.callback()

    def start(self, sprite):
        self.targets = [(sprite, dict())]
        for target, props in self.targets:
            for name, value in self.props.items():
                initial = self._get_value(target, name)
                props[name] = initial, value


class AnimationTransition(object):
    @staticmethod
    def linear(progress):
        """.. image:: images/anim_linear.png"""
        return progress

    @staticmethod
    def in_quad(progress):
        """.. image:: images/anim_in_quad.png
        """
        return progress * progress

    @staticmethod
    def out_quad(progress):
        """.. image:: images/anim_out_quad.png
        """
        return -1.0 * progress * (progress - 2.0)

    @staticmethod
    def in_out_quad(progress):
        """.. image:: images/anim_in_out_quad.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p
        p -= 1.0
        return -0.5 * (p * (p - 2.0) - 1.0)

    @staticmethod
    def in_cubic(progress):
        """.. image:: images/anim_in_cubic.png
        """
        return progress * progress * progress

    @staticmethod
    def out_cubic(progress):
        """.. image:: images/anim_out_cubic.png
        """
        p = progress - 1.0
        return p * p * p + 1.0

    @staticmethod
    def in_out_cubic(progress):
        """.. image:: images/anim_in_out_cubic.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p
        p -= 2
        return 0.5 * (p * p * p + 2.0)

    @staticmethod
    def in_quart(progress):
        """.. image:: images/anim_in_quart.png
        """
        return progress * progress * progress * progress

    @staticmethod
    def out_quart(progress):
        """.. image:: images/anim_out_quart.png
        """
        p = progress - 1.0
        return -1.0 * (p * p * p * p - 1.0)

    @staticmethod
    def in_out_quart(progress):
        """.. image:: images/anim_in_out_quart.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p * p
        p -= 2
        return -0.5 * (p * p * p * p - 2.0)

    @staticmethod
    def in_quint(progress):
        """.. image:: images/anim_in_quint.png
        """
        return progress * progress * progress * progress * progress

    @staticmethod
    def out_quint(progress):
        """.. image:: images/anim_out_quint.png
        """
        p = progress - 1.0
        return p * p * p * p * p + 1.0

    @staticmethod
    def in_out_quint(progress):
        """.. image:: images/anim_in_out_quint.png
        """
        p = progress * 2
        if p < 1:
            return 0.5 * p * p * p * p * p
        p -= 2.0
        return 0.5 * (p * p * p * p * p + 2.0)

    @staticmethod
    def in_sine(progress):
        """.. image:: images/anim_in_sine.png
        """
        return -1.0 * cos(progress * (pi / 2.0)) + 1.0

    @staticmethod
    def out_sine(progress):
        """.. image:: images/anim_out_sine.png
        """
        return sin(progress * (pi / 2.0))

    @staticmethod
    def in_out_sine(progress):
        """.. image:: images/anim_in_out_sine.png
        """
        return -0.5 * (cos(pi * progress) - 1.0)

    @staticmethod
    def in_expo(progress):
        """.. image:: images/anim_in_expo.png
        """
        if progress == 0:
            return 0.0
        return pow(2, 10 * (progress - 1.0))

    @staticmethod
    def out_expo(progress):
        """.. image:: images/anim_out_expo.png
        """
        if progress == 1.0:
            return 1.0
        return -pow(2, -10 * progress) + 1.0

    @staticmethod
    def in_out_expo(progress):
        """.. image:: images/anim_in_out_expo.png
        """
        if progress == 0:
            return 0.0
        if progress == 1.:
            return 1.0
        p = progress * 2
        if p < 1:
            return 0.5 * pow(2, 10 * (p - 1.0))
        p -= 1.0
        return 0.5 * (-pow(2, -10 * p) + 2.0)

    @staticmethod
    def in_circ(progress):
        """.. image:: images/anim_in_circ.png
        """
        return -1.0 * (sqrt(1.0 - progress * progress) - 1.0)

    @staticmethod
    def out_circ(progress):
        """.. image:: images/anim_out_circ.png
        """
        p = progress - 1.0
        return sqrt(1.0 - p * p)

    @staticmethod
    def in_out_circ(progress):
        """.. image:: images/anim_in_out_circ.png
        """
        p = progress * 2
        if p < 1:
            return -0.5 * (sqrt(1.0 - p * p) - 1.0)
        p -= 2.0
        return 0.5 * (sqrt(1.0 - p * p) + 1.0)

    @staticmethod
    def in_elastic(progress):
        """.. image:: images/anim_in_elastic.png
        """
        p = .3
        s = p / 4.0
        q = progress
        if q == 1:
            return 1.0
        q -= 1.0
        return -(pow(2, 10 * q) * sin((q - s) * (2 * pi) / p))

    @staticmethod
    def out_elastic(progress):
        """.. image:: images/anim_out_elastic.png
        """
        p = .3
        s = p / 4.0
        q = progress
        if q == 1:
            return 1.0
        return pow(2, -10 * q) * sin((q - s) * (2 * pi) / p) + 1.0

    @staticmethod
    def in_out_elastic(progress):
        """.. image:: images/anim_in_out_elastic.png
        """
        p = .3 * 1.5
        s = p / 4.0
        q = progress * 2
        if q == 2:
            return 1.0
        if q < 1:
            q -= 1.0
            return -.5 * (pow(2, 10 * q) * sin((q - s) * (2.0 * pi) / p))
        else:
            q -= 1.0
            return pow(2, -10 * q) * sin((q - s) * (2.0 * pi) / p) * .5 + 1.0

    @staticmethod
    def in_back(progress):
        """.. image:: images/anim_in_back.png
        """
        return progress * progress * ((1.70158 + 1.0) * progress - 1.70158)

    @staticmethod
    def out_back(progress):
        """.. image:: images/anim_out_back.png
        """
        p = progress - 1.0
        return p * p * ((1.70158 + 1) * p + 1.70158) + 1.0

    @staticmethod
    def in_out_back(progress):
        """.. image:: images/anim_in_out_back.png
        """
        p = progress * 2.
        s = 1.70158 * 1.525
        if p < 1:
            return 0.5 * (p * p * ((s + 1.0) * p - s))
        p -= 2.0
        return 0.5 * (p * p * ((s + 1.0) * p + s) + 2.0)

    @staticmethod
    def _out_bounce_internal(t, d):
        p = t / d
        if p < (1.0 / 2.75):
            return 7.5625 * p * p
        elif p < (2.0 / 2.75):
            p -= (1.5 / 2.75)
            return 7.5625 * p * p + .75
        elif p < (2.5 / 2.75):
            p -= (2.25 / 2.75)
            return 7.5625 * p * p + .9375
        else:
            p -= (2.625 / 2.75)
            return 7.5625 * p * p + .984375

    @staticmethod
    def _in_bounce_internal(t, d):
        return 1.0 - AnimationTransition._out_bounce_internal(d - t, d)

    @staticmethod
    def in_bounce(progress):
        """.. image:: images/anim_in_bounce.png
        """
        return AnimationTransition._in_bounce_internal(progress, 1.)

    @staticmethod
    def out_bounce(progress):
        """.. image:: images/anim_out_bounce.png
        """
        return AnimationTransition._out_bounce_internal(progress, 1.)

    @staticmethod
    def in_out_bounce(progress):
        """.. image:: images/anim_in_out_bounce.png
        """
        p = progress * 2.
        if p < 1.:
            return AnimationTransition._in_bounce_internal(p, 1.) * .5
        return AnimationTransition._out_bounce_internal(p - 1., 1.) * .5 + .5


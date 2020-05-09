"""
What if 1 hour was 100 minutes and 1 minute was 100 seconds?
Let's visualize that in python! (p5 js would have been nice too)

Note: small timing issues but i don't really care. This program is not intended to run for a long time anyway.
"""
from typing import Union, List, Tuple, Optional, Dict

import time
import pygame as pg
from enum import Enum

COLOR_T = Tuple[int, int, int, int]

NEW_MIN_IN_HOUR = 100
NEW_SEC_IN_MIN = 100
SEC_IN_HOUR = 60*60
NEW_SEC_DURATION = SEC_IN_HOUR / (NEW_MIN_IN_HOUR * NEW_SEC_IN_MIN)

pg.init()
pg.font.init()

class SecondState(Enum):
    BLINK: int = 1
    IDLE: int = 2

class Second(pg.Rect):
    MIN_BLIT_TIME = 0.25
    MILESTONE_COLOR = pg.color.THECOLORS['green']
    TEXT_COLOR = pg.color.THECOLORS['white']
    INFOS_FONT = pg.font.Font('freesansbold.ttf', 26)

    __slots__ = ('state', 'blink_color', 'idle_color', 'last_blink', 'interval', 'blinks', 'blinks_in_milestone',
                 'reached_milestones')

    def __init__(self, *args, blink_color: COLOR_T, idle_color: COLOR_T, interval: float, milestone: int,
                 **kwargs):
        super(Second, self).__init__(*args, **kwargs)
        self.state: int = SecondState.IDLE
        self.blink_color = blink_color
        self.idle_color = idle_color
        self.last_blink: float = 0
        self.interval: float = interval
        self.blinks: int = 0
        self.blinks_in_milestone: int = milestone
        self.reached_milestones: int = 0  # replaceable with int(blinks/blinks_in_milestone) but the less OPs the better

    def draw_infos(self):
        text = self.INFOS_FONT.render(f'{self.reached_milestones}min'
                                      f' {self.blinks - self.reached_milestones * self.blinks_in_milestone}sec',
                                      antialias=True, color=self.TEXT_COLOR)
        text_rect: pg.Rect = text.get_rect()
        text_rect.center = (self.left + self.width // 2, self.top + self.height // 2)
        screen.blit(text, text_rect)

    def draw_blink(self):
        self.blinks += 1
        if self.blinks % self.blinks_in_milestone == 0:
            self.reached_milestones += 1
            pg.draw.rect(screen, self.MILESTONE_COLOR, self)
        else:
            pg.draw.rect(screen, self.blink_color, self)
        self.draw_infos()

    def draw_idle(self):
        pg.draw.rect(screen, self.idle_color, self)
        self.draw_infos()

    def update(self):
        if self.state == SecondState.IDLE:
            self.draw_blink()
            self.state = SecondState.BLINK
        else:
            self.draw_idle()
            self.state = SecondState.IDLE

    def time_controlled_update(self, now: float) -> bool:
        if self.state == SecondState.IDLE:
            if now - self.last_blink >= self.interval:
                self.draw_blink()
                self.state = SecondState.BLINK
                self.last_blink = now  # will introduce time slip
                return True
            return False
        else:
            if now - self.last_blink >= self.MIN_BLIT_TIME:
                self.draw_idle()
                self.state = SecondState.IDLE
                return True
            return False


def is_exit_key_press(pressed, mods) -> bool:
    return (mods & pg.KMOD_CTRL) and (pressed[pg.K_w] or pressed[pg.K_c])


def handle_quit_event():
    print('Good luck on your current run.')
    exit()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('Time flow is not that objective', add_help=False)
    parser.add_argument('--help', '-h', action='store_true')
    args = parser.parse_args()
    if args.help:
        print("Usage:\n"
              "\tJust run the program without any options\n"
              "\tShortcuts:     s - start\n"
              "\t               ctrl+w terminate\n"
              "\t               ctrl+c terminate\n")
        exit(0)

    HEIGHT, WIDTH = 512, 512
    screen: pg.Surface = pg.display.set_mode((WIDTH, HEIGHT))
    new_seconds = Second(0, 0, WIDTH / 2, HEIGHT,
                         blink_color=pg.color.THECOLORS['red'],
                         idle_color=pg.color.THECOLORS['black'],
                         interval=NEW_SEC_DURATION, milestone=100)
    old_seconds = Second(WIDTH/2, 0, WIDTH/2, HEIGHT,
                         blink_color=pg.color.THECOLORS['blue'],
                         idle_color=pg.color.THECOLORS['black'],
                         interval=1.0, milestone=60)
    pg.display.flip()

    clock = pg.time.Clock()
    started: bool = False
    while True:
        if pg.event.get(pg.QUIT):
            handle_quit_event()

        pressed = pg.key.get_pressed()
        mods = pg.key.get_mods()
        if is_exit_key_press(pressed, mods):
            handle_quit_event()

        if pressed[pg.K_s] and not started:
            print('Lets go')
            started = True

        if started:
            now = time.time()
            if new_seconds.time_controlled_update(now) or old_seconds.time_controlled_update(now):
                pg.display.flip()
        _ = pg.event.get()  # otherwise ubuntu thinks the prorgam is not responding
        clock.tick(120)

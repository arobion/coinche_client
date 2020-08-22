# -*- coding: utf-8 -*-

from functools import wraps

class CoincheMsgFormatter():

    END = '#ENDCRN'

    def _add_end(self, string):
        string += self.END
        return string

    def action_method(string):
        string += 'ACTION+'
        return string

    def info_method(string):
        string += 'INFO+'
        return string
    
    def format(method_type):
        def decorate(f):
            @wraps(f)
            def wrapper(self, *args, **kwargs):
                res = f(self, *args, **kwargs)
                res = method_type('') + res
                res = self._add_end(res)
                return res
            return wrapper
        return decorate

    @format(action_method)
    def send_annonce(self, val, color):
        msg = 'annonce {} {}'.format(val, color)
        return msg

    @format(action_method)
    def send_passe(self):
        msg = 'annonce passe'
        return msg

    @format(action_method)
    def send_play(self, card):
        msg = 'play {}'.format(card)
        return msg

    @format(info_method)
    def send_name(self, name):
        msg = name
        return msg

    def received_msg(self, queue):
        if not self.END in queue[0]:
            return None, 'ACTION', ['None']

        msg = queue[0].split(self.END, 1)
        res = msg.pop(0).split('+')
        if msg[0]:
            queue[0] = ''.join(msg)
        else:
            queue.pop(0)
        return queue, res[0], res[1].split(' ')

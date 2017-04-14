"""
AUTHOR: Nikolas Papaioannou (Neonoleta)
"""

import json
import socket
from time import sleep
from map import MapManager


class Controller:
    def __init__(self, target='localhost'):
        print("Init controller")
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = target
        self.port = 54321
        self.s.connect((self.host, self.port))
        sleep(1)
        self.mm = MapManager()
        self.plan = None

    def parse_next_tile(self, current, next_tile):
        """
        Takes the current and the next tile. Checks if they are next to each other. Then send the correct movement command
        :param current: current tile
        :param next_tile: next tile
        :return: void
        """

        x1, y1 = current.point
        x2, y2 = next_tile.point

        deltax = x2 - x1
        deltay = y2 - y1

        # assert abs(deltax) < 2
        # assert abs(deltay) < 2

        if deltax == 0:  # Not left or right:
            if deltay < 0:  # Negative -> UP
                self.send_command('UP')
            elif deltay > 0:  # Pos
                self.send_command('DOWN')
            else:
                raise ValueError("BOTH deltas zero")
        elif deltay == 0:
            if deltax < 0:
                self.send_command('LEFT')
            elif deltax > 0:
                self.send_command('RIGHT')
            else:
                raise ValueError("BOTH deltas zero")

    def send_command(self, command):
        print("COMMAND: {}".format(command))
        try:
            if command == 'UP':
                self.s.send(b'UP\n')
            elif command == 'DOWN':
                self.s.send(b'DOWN\n')
            elif command == 'RIGHT':
                self.s.send(b'RIGHT\n')
            elif command == 'LEFT':
                self.s.send(b'LEFT\n')

        except Exception as e:
            print(e)

    def run(self):
        extra_buffer = ''
        while True:
            print("Loop start")
            data = self.s.recv(1500)
            print(data)

            jsons = []
            messages = data.splitlines()

            # print(messages)
            for msg in messages:
                try:
                    state = json.loads(extra_buffer + msg.decode('utf-8'))
                    jsons.append(state)
                    extra_buffer = ''
                except json.JSONDecodeError as error:
                    print(error.msg)
                    extra_buffer += msg.decode('utf-8')
                    pass
                    break

            for json_str in jsons:
                self.decide(json_str)

    def decide(self, state_object):

        messagetype = state_object.get('messagetype', None)
        print("Messagetype: {}".format(messagetype))
        if messagetype == 'welcome':
            print("Welcome to new a new match!")
            self.welcome()
        elif messagetype == 'stateupdate':
            self.state_update(state_object)
        elif messagetype == 'dead':
            print("You have died... rip")
            self.dead()
            self.plan = None
        elif messagetype == 'endofround':
            print("Round done")
            self.plan = None
        elif messagetype == 'startofround':
            print("Start of round")
            self.plan = None

    def state_update(self, state_object):
        print("Updating state...")
        """
        TODO:
        1. Set map
        2. Calculate heatmap
        3. Pick plan
        4. Do plan

        :param state_object:
        :return:
        """
        if self.plan:
            self.use_plan()
            return

        self.mm.set_map(state_object)
        self.mm.print_map()
        self.mm.set_players(state_object)
        clusters = self.mm.generate_heat_map()
        self.plan = self.mm.create_plan(clusters)

    def welcome(self):
        print("Sending Bot Name")
        self.s.send(b"NAME UiO :^)\n")

    def dead(self):
        print("Implement something to fiddle with your death data.")

    def use_plan(self):
        path, ticks = self.plan
        print("Using plan for the next {} ticks".format(ticks))
        print("Len of plan: {}".format(str(len(path))))
        self.parse_next_tile(path[0], path[1])

        if len(path) <= 2:
            self.plan = None
        elif ticks == 0:
            self.plan = None
        else:
            self.plan = (path[1:], ticks - 1)


if __name__ == '__main__':
    c = Controller()
    c.run()

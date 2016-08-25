# /usr/bin/python3

# MELNIKOV ILYA

import time
import random
from math import pow


class Unit:

    def __init__(self, health, recharge):
        self.health = health
        self.recharge = recharge
        self.alive = True
        self.last_attack_time = 0

    def take_damage(self, value):
        self.health -= value
        self.alive = self.health > 0

    def get_recharge(self):
        millisec = (time.time() - self.last_attack_time)*1000
        return self.recharge - millisec

    def get_health(self):
        return self.health


class Soldier(Unit):

    def __init__(self, health, recharge):
        super().__init__(health, recharge)
        self.experience = 0

    def increase_exp(self):
        if self.experience <= 50:
            self.experience += 1

    def get_success_attack(self):
        return (0.5 * (1 + self.health / 100) * random.randint(50 + self.experience, 100) / 100)

    def attack_damage(self):
        return 0.05 + self.experience / 100


class Vehicle(Unit):

    def __init__(self, health, operators, recharge, veh_health):
        super().__init__(health, recharge)
        self.operators = operators
        self.veh_health = veh_health

    def get_success_attack(self):
        gavg = 1

        for operator in self.operators:
            gavg *= operator.get_success_attack()
        return 0.5 * (1 + self.health / 100) * pow(gavg, 1 / len(self.operators))

    def attack_damage(self):
        tot_exp = 0

        for operator in self.operators:
            tot_exp += operator.experience
        return 0.1 + tot_exp / 100

    def get_alive_operators(self):
        return [operator for operator in self.operators if operator.alive]

    def take_damage(self, value):
        self.veh_health -= value * 0.6
        self.alive = self.veh_health > 0

        for operator in self.operators:
            operator.take_damage(value * 0.1)

        if self.get_alive_operators():
            random.choice(self.get_alive_operators()).take_damage(value * 0.2)

        self.alive = bool(self.get_alive_operators())


class Squad:

    def __init__(self, units):
        self.units = units
        self.alive = True

    def get_success_attack(self):
        gavg = 1

        for unit in self.get_alive_units():
            gavg *= unit.get_success_attack()
        return pow(gavg, 1 / len(self.units))

    def take_damage(self, damage):
        alive_units = self.get_alive_units()
        hit_damage = damage/len(alive_units)

        for unit in alive_units:
            unit.take_damage(hit_damage)

        self.alive = bool(self.get_alive_units())

    def attack_damage(self):
        damage = 0

        for unit in self.units:
            if unit.get_recharge() <= 0:
                unit.last_attack_time = time.time()
                damage += unit.attack_damage()
        return damage * 100000

    def get_alive_units(self):
        return [unit for unit in self.units if unit.alive]

    def attack(self, enemy_army, strategy):
        enemy_squad = strategy.chose_enemy_squad(enemy_army)

        if enemy_squad and self.get_success_attack() > enemy_squad.get_success_attack():
            enemy_squad.take_damage(self.attack_damage())


class Army:

    def __init__(self, squads, strategy, name):
        self.squads = squads
        self.strategy = strategy
        self.name = name

    def get_alive_squads(self):
        return [squad for squad in self.squads if squad.alive]

    def is_alive(self):
        return bool(self.get_alive_squads())

    def attack(self, enemy_army, strategy):
        for squad in self.get_alive_squads():
            squad.attack(enemy_army, strategy)
            print("\n\tAttacker's army has {} squads left".format(len(self.get_alive_squads())))
            print("\tDefender's army has {} squads left\n".format(len(enemy_army.get_alive_squads())))

    def __str__(self):
        return self.name


class Battlefield:

    def __init__(self, armies):
        self.armies = armies
        self.rounds = 0

    def get_alive_armies(self):
        return [army for army in self.armies if army.is_alive()]

    def is_won(self):
        return len(self.get_alive_armies()) == 1

    def start(self):
        print('FIGHT!!!')
        self.rounds = 0

        while not self.is_won():
            self.rounds += 1
            for army in self.armies:
                if not army.is_alive():
                    continue
                alive_armies = self.get_alive_armies()
                alive_armies.remove(army)
                enemy_army = random.choice(alive_armies)
                print('\tArmy {} attacks army {}.'.format(army.name, enemy_army.name))
                army.attack(enemy_army, army.strategy)

        winner = self.get_alive_armies()[0]
        return '{} won in {} rounds with {} strategy'.format(winner.name, self.rounds, winner.strategy.__name__)

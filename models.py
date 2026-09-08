from random import random, randint, choice, choices

TOOL = "professional-looking value"
ITEM = "even more proffessional-looking value"

HEAL = 'models0'
RECHARGE = 'models1'
HEALOVERTIME = 'models2'
RECHARGEOVERTIME = 'models3'
DAMAGE = 'models4'
ELECDAMAGE = 'models5'
POISON = 'models6'
FLEE = 'models7'
SUMMON = 'models8'
DEFEND = 'models9'

SELF = 'models20'
FIELD = 'models21'
ENEMIES = 'models22'
DELAY1 = 'models23'
ONDEATH = 'models24'
AFTERBATTLE = 'models25'

class Item():
    def __init__(self, Name, effects, useText = None, desc = None):
        '''effects are a list, where each effect in the list is in the format (string of attribute to change, True if multiplier or False if adder, intensity, cap stat if any)'''
        self.Name = Name
        self.type = ITEM
        self.effects = effects
        self.useText = ("used " + Name) if useText == None else useText
        self.desc = "" if desc == None else desc

    def UseItem(self, entity):
        '''Returns string of use text'''
        output = f"{entity.Name} {self.useText}.\n"
        for effect in self.effects:
            if 'models' in effect[0]:
                if type(effect[1]) == type(1):
                    pass
                elif effect[1].isnumeric():
                    effect[1] = int(effect[1])
                else:
                    effect[1] = getattr(entity, effect[1])
                if effect[0] == HEAL:
                    if entity.hp + effect[1] > entity.hp_max:
                        entity.hp = entity.hp_max
                        output += f"{entity.Name} healed to full!\n"
                    else:
                        entity.hp += effect[1]
                        output += f"{entity.Name} healed for {int(effect[1])}hp.\n"
                elif effect[0] == RECHARGE:
                    if entity.ep + effect[1] > entity.ep_max:
                        entity.ep = entity.ep_max
                        output += f"{entity.Name} recharged to full!\n"
                    else:
                        entity.ep += effect[1]
                        output += f"{entity.Name} recharged for {int(effect[1])}ep.\n"
                elif effect[0] == HEALOVERTIME:
                    entity.effects.append(effect)
                    output += f"{entity.Name} gained {int(effect[2])} turns of healing.\n"
                elif effect[0] == RECHARGEOVERTIME:
                    entity.effects.append(effect)
                    output += f"{entity.Name}'s ep started recovering.\n"
                elif effect[0] == POISON:
                    entity.effects.append(effect)
                    output += f"{entity.Name} was poisoned for {int(effect[1])} turns!\n"
                elif effect[0] == DAMAGE:
                    recv_damage = entity.RecvDamage(effect[1])
                    if recv_damage == False:
                        output += (f"{entity.Name} took!\n")
                    else:
                        output += (f"{entity.Name} took {recv_damage} damage.\n")
                elif effect[0] == ELECDAMAGE:
                    output += (f"{entity.Name} took {entity.RecvElecDamage(effect[1])} electrical damage.\n")
                elif effect[0] == FLEE:
                    pass
                elif effect[0] == SUMMON:
                    pass

                    
            else:
                if type(effect[1]) == type(1):
                    pass
                elif effect[1].isnumeric():
                    effect[1] = int(effect[1])
                else:
                    effect[1] = getattr(entity, effect[1])
                prev = getattr(entity, effect[0])
                new = prev+effect[1]
                output += f"{entity.Name}'s {effect[0]} was increased by {effect[1]}.\n"
                setattr(entity, effect[0], new)
        return output

class Tool():
    def __init__(self, Name, cost = 0, cooldown = 1, effects = [], useText = None, desc = None):
        '''effects are a list, where each effect in the list is in the format (string of attribute to change, True if multiplier or False if adder, intensity, cap stat if any)'''
        self.Name = Name
        self.type = TOOL
        self.cost = cost
        self.effects = effects
        self.useText = ("used " + Name) if useText == None else useText
        self.desc = "" if desc == None else desc
        self.cooldown = cooldown

        self.isUsed = False

    def UseTool(self, user, target, enemies):
        '''Returns string of use text'''
        output = f"{user.Name} {self.useText} on {target.Name if user != target else 'themself'}.\n"
        #pick a random effect
        for effect in self.effects:
            if type(effect[2]) == type(1):
                pass
            elif effect[2].isnumeric():
                effect[2] = int(effect[2].strip())
            else:
                effect[2] = getattr(user, effect[2])
        effect = choices(self.effects, [x[2] for x in self.effects])[0]

        if effect[0] == "None":
            output += "...but nothing happens!\n"
            return output

        #if self targetting, adject targets
        if len(effect) == 4 and effect[3] == SELF:
            target = user

        #if magnifier uses stats, adjust value
        if type(effect[1]) == type(1):
            pass
        elif effect[1].strip('-').isnumeric():
            effect[1] = int(effect[1])
        elif '*' in effect[1]:
            attr, mult = effect[1].split('*')
            effect[1] = getattr(user, attr) * int(mult)
        elif '/' in effect[1]:
            attr, mult = effect[1].split('*')
            effect[1] = getattr(user, attr) * int(mult)
        else:
            effect[1] = getattr(user, effect[1])

        #if effect is a special value, manipulate it accordingly
        if 'models' in effect[0]:
            if effect[0] == HEAL:
                if target.hp + effect[1] > target.hp_max:
                    target.hp = target.hp_max
                    output += f"{target.Name} healed to full!\n"
                else:
                    target.hp += effect[1]
                    output += f"{target.Name} healed for {int(effect[1])}hp.\n"
            elif effect[0] == RECHARGE:
                if target.ep + effect[1] > target.ep_max:
                    target.ep = target.ep_max
                    output += f"{target.Name} recharged to full!\n"
                else:
                    target.ep += effect[1]
                    output += f"{target.Name} recharged for {int(effect[1])}ep.\n"
            elif effect[0] == HEALOVERTIME:
                target.effects.append(effect)
                output += f"{target.Name} gained {int(effect[2])} turns of healing.\n"
            elif effect[0] == RECHARGEOVERTIME:
                target.effects.append(effect)
                output += f"{target.Name}'s ep started recovering.\n"
            elif effect[0] == POISON:
                target.effects.append(effect)
                output += f"{target.Name} was poisoned for {int(effect[1])} turns!\n"
            elif effect[0] == DAMAGE:
                recv_damage = target.RecvDamage(effect[1])
                if recv_damage == False:
                    output += (f"{target.Name} dodged the attack!\n")
                else:
                    output += (f"{target.Name} took {recv_damage} damage.\n")
            elif effect[0] == ELECDAMAGE:
                output += (f"{target.Name} took {target.RecvElecDamage(effect[1])} electrical damage.\n")
            elif effect[0] == FLEE:
                pass
            elif effect[0] == SUMMON:
                pass
            
        #if its a stat, update the stat accordingly
        else:
            if type(effect[1]) == type(1):
                pass
            elif effect[1].isnumeric() or '-' in effect[1]:
                effect[1] = int(effect[1])
            else:
                effect[1] = getattr(user, effect[1])
            #check for effect modifiers
            if len(effect) == 4 and effect[3] == ENEMIES:
                for enemy in enemies:
                    prev = getattr(enemy[2], effect[0])
                    new = prev+effect[1]
                    output += f"{enemy[2].Name}'s {effect[0]} was increased by {effect[1]}.\n"
                    setattr(enemy[2], effect[0], new)
            else:
                prev = getattr(target, effect[0])
                new = prev+effect[1]
                output += f"{target.Name}'s {effect[0]} was increased by {effect[1]}.\n"
                setattr(target, effect[0], new)
        return output

class Entity():
    def __init__(self, Name = "Entity", hp = 20, hp_max = None, ep = 10, ep_max = None, df = 2, atk = 5, lk = 5, cc = None, cf = None, dc = None, df_pw = None):
        ###MAIN STATS###
        self.Name = Name
        self.hp = hp #HEALTH
        self.hp_max = hp if hp_max == None else hp_max #MAX HP
        self.ep = ep #ENERGY
        self.ep_max = ep if ep_max == None else ep_max #MAX EP
        self.df = df #DEFENCE
        self.atk = atk #ATTACK FORCE
        self.lk = lk #LUCK
        self.cc = 0.03*lk if cc == None else cc #CRIT CHANCE
        self.dc = 0.02*lk if dc == None else dc #DODGE CHANCE
        self.cf = 2.5*atk if cf == None else cf #CRIT FORCE

        self.df_pw = df*2 if df_pw == None else df_pw #DEFENCE POWER: how much extra defence the player gets if they defended

        ###ITEMS###
        self.inv = {}

        ###TOOLS###
        self.tools = {}

        ###BATTLE STATS###
        self.effects = []
        self.atk_tmp = 0
        self.df_tmp = 0

    def GetStats(self):
        '''Returns HP, MaxHP, EP, MaxEP, DF, TempDF, ATK and TempATK'''
        return self.hp, self.hp_max, self.ep, self.ep_max, self.df, self.df_tmp + self.df_pw if DEFEND in self.effects else self.df_tmp, self.atk, self.atk_tmp

    def GameTick(self):
        '''Progresses the battle one turn forward. Lose one stack of effects and recharge all tools.'''
        for effect in self.effects:
            if effect == DEFEND:
                self.effects.remove(DEFEND)
            elif effect[0] == HEALOVERTIME:
                effect[1], effect[2] = int(effect[1]), int(effect[2])
                self.hp = min(self.hp_max, self.hp + effect[1])
                effect[2] -= 1
                if effect[2] == 0:
                    self.effects.remove(effect)
            elif effect[0] == RECHARGEOVERTIME:
                self.ep = min(self.ep_max, self.ep + effect[1])
            elif effect[0] == POISON:
                effect[1] = int(effect[1])
                if effect[1] <= 0:
                    self.effects.remove(effect)
                else:
                    self.hp -= effect[1]
                    effect[1] -= 1
                    if effect[1] <= 0:
                        self.effects.remove(effect)
        for tool in self.tools.keys():
            self.tools[tool] = True

    def DealDamage(self):
        '''Returns if a crit occurred, followed by raw damage dealt'''
        if random() <= self.cc:
            return True, self.cf
        return False, self.atk

    def Defend(self):
        '''Gains df_pw in defence, returns extra df gained'''
        self.effects.append(DEFEND)
        return self.df_pw

    def RecvDamage(self, damage=0):
        '''Change entity's hp by damage, affected by defence and dodge chance
        Returns False if dodged, else true damage dealt'''
        if random() < self.dc:
            return False
        if DEFEND in self.effects:
            true_damage = max(damage-self.df-self.df_tmp-self.df_pw, 0)
        else:
            true_damage = max(damage-self.df-self.df_tmp, 0)
        self.hp -= true_damage
        return true_damage

    def RecvElecDamage(self, damage=0):
        '''Change entity's hp by damage, affected by defence, but not dodge chance
        Returns true damage dealt'''
        if DEFEND in self.effects:
            true_damage = max(damage-self.df-self.df_tmp-self.df_pw, 0)
        else:
            true_damage = max(damage-self.df-self.df_tmp, 0)
        self.hp -= true_damage
        return true_damage

    def GainItem(self, item, count = 1):
        '''Adds an item to player's inventory'''
        for inv_item in self.inv.keys():
            if item.Name == inv_item.Name:
                self.inv[inv_item] += count
                return
        self.inv[item] = count

    def GetInventory(self):
        '''Returns list of items and amounts'''
        output = []
        for item, count in self.inv.items():
            output.append([item.Name, count, item.desc])
        return output

    def RemoveItem(self, itemName):
        '''Removes 1 item from inventory, returns Item'''
        for item in self.inv.keys():
            if item.Name == itemName:
                self.inv[item] -= 1
                if self.inv[item] == 0:
                    self.inv.pop(item)
                return item

    def GainTool(self, tool):
        "Returns False if tool is already in inventory"
        for tools_tool in self.tools.keys():
            if tool.Name == tools_tool.Name:
                return False
        self.tools[tool] = True

    def GetTools(self):
        '''Returns list of tools, cost, charge, max charge, availability and description'''
        output = []
        for tool, isAvailable in self.tools.items():
            output.append([tool.Name, tool.cost, isAvailable, tool.desc])
        return output

    def UseTool(self, toolName):
        '''Makes a tool no longer available and consumes its cost, returns False if tool cannot be used or cost cannot be paid'''
        for tool in self.tools.keys():
            if tool.Name == toolName:
                if self.tools[tool] == True and self.ep >= tool.cost:
                    self.tools[tool] = False
                    self.ep -= tool.cost
                    return tool
                else:
                    return False

    def IsDead(self):
        '''Returns if entity is dead'''
        return self.hp <= 0

class Enemy(Entity):
    def __init__(self, Name = "Enemy", hp = 20, hp_max = None, ep = 10, ep_max = None, df = 2, atk = 5, lk = 5, cc = None, cf = None, dc = None, df_pw = None,desc = "", xp = 5, loot = [], species = 'H', img = None):
        super().__init__(Name, hp, hp_max, ep, ep_max, df, atk, lk, cc, cf, dc, df_pw)
        self.desc = desc
        self.xp = xp
        self.loot = loot
        self.img = img

        ###BATTLE LOGIC###
        self.species = species
        
    def GetInfoText(self):
        '''Returns info window text about the enemy'''
        return f"HP:{self.hp}/{self.hp_max}\nEP:{self.ep}/{self.ep_max}\nATK:{self.atk}, DEF:{self.df}\nLCK:{self.lk}"

    def GainTool(self, tool):
        "can gain multiple of the same tool"
        self.tools[tool] = True

    def DoTurn(self, player, enemies):
        '''Based on its species, does something
           Returns just damage if it chooses to attack, else strings if it uses stuff'''
        output = ""
        if self.Name == "B4RT3ND3R":
            for tool in self.tools.keys():
                self.UseTool(tool.Name)
                if tool.Name == "Green Bottle":
                    enemy = choice([x[2] for x in enemies])
                    output += tool.UseTool(self, enemy, enemies)
                else:
                    output += tool.UseTool(self, player, enemies)
            return [output]
        elif self.Name == 'Riverboat Gambler':
            for tool in self.tools.keys():
                self.UseTool(tool.Name)
                output += tool.UseTool(self, self, enemies)
            return [self.DealDamage(), output]
        elif self.Name == "R1V3RB04T_CR1TT3R":
            for tool in self.tools.keys():
                self.UseTool(tool.Name)
                output += tool.UseTool(self, self, enemies)
            return [output]
        elif self.species == 'H' and len(self.tools.keys()) == 0:
            return [self.DealDamage()]
        elif self.species == 'Z':
            for tool in self.tools.keys():
                self.UseTool(tool.Name)
                output += tool.UseTool(self, player, enemies)
            return [output]
        elif self.species == 'R':
            for tool in self.tools.keys():
                self.UseTool(tool.Name)
                output += tool.UseTool(self, player, enemies)
            return [output]
        else:
            for tool in self.tools.keys():
                self.UseTool(tool.Name)
                output += tool.UseTool(self, player, enemies)
            return [self.DealDamage(), output]
        
    
    def dropLoot(self):
        '''Returns dropped XP and loot'''
        return self.xp, self.loot if self.loot else None

class Player(Entity):
    def __init__(self, Name = "Player", hp = 20, hp_max = None, ep = 10, ep_max = None, df = 2, atk = 5, lk = 5, cc = None, cf = None, dc = None, df_pw = None):
        super().__init__(Name, hp, hp_max, ep, ep_max, df, atk, lk, cc, cf, dc, df_pw)
        self.lvl = 1
        self.xp = 0

    def GetStats(self):
        '''Returns HP, MaxHP, EP, MaxEP, DF, TempDF, ATK, TempATK, lvl, xp, required xp and effects, if any'''
        effect_output = []
        for effect in self.effects:
            if effect == DEFEND:
                effect_output.append(f"DEFEND")
            elif effect[0] == POISON:
                effect_output.append(f"POISON[{effect[1]}]")
            elif effect[0] == HEALOVERTIME:
                effect_output.append(f"HEAL[{effect[2]}]")
            elif effect[0] == RECHARGEOVERTIME:
                effect_output.append(f"RECHARGE")
        return self.hp, self.hp_max, self.ep, self.ep_max, self.df, self.df_tmp, self.atk, self.atk_tmp, self.lvl, self.xp, 10*self.lvl, effect_output

    def gainXP(self, xp):
        '''Returns True if player leveled up'''
        self.xp += xp
        if self.xp > 10*self.lvl:
            self.xp -= 10*self.lvl
            self.lvl += 1
            self.hp_max += 5
            self.hp += 5
            self.atk += 1
            self.df += 1
            self.lk == 1
            return True
    

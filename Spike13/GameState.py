from Goal import Goal
from Action import Action

class GameState(object):
    def __init__(self):
        goal1 = Goal("Eat", 4)
        goal2 = Goal("Sleep", 3)
        self.goals = [goal1, goal2]
        self.action_index = -1

        game_state = self

        # actions
        action1 = Action("Get raw food", [{"goal": goal1, "insistance_change": -4}],-3)
        action2 = Action("Sleep in bed",  [{"goal": goal2, "insistance_change": -2}], -3)
        action3 = Action("Get snack",  [{"goal": goal1, "insistance_change": -2}],-2)
        self.base_action = Action("No action",[],0)

        self.actions = [action1, action2, action3]
        self.strength = 5

    def Exhausted(self):
        if self.strength == 0:
            return True
        else:
            return  False

    def GetCurrentStateDiscontent(self):
        discontent = 0
        for goal in self.goals:
            discontent += goal.GetGoalInsistance() * goal.GetGoalInsistance()

        return discontent


    def reset(self):
        self.action_index = -1

    def next_action(self):
        for i in range(self.action_index + 1,len(self.actions)):
            #print("index {}".format(i))
            if self.actions[i].cost + self.strength >= 0:
                self.action_index = i
                return self.actions[i]

        return None

    def apply_action(self,action_to_apply):
        for effect in action_to_apply.effects:
            for goal in self.goals:
                if effect["goal"].goal_name == goal.goal_name:
                    goal.UpdateGoalInsistance(effect["insistance_change"])

        self.strength += action_to_apply.cost

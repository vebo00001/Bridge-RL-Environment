import environment as rlenv
import gym
import numpy as np
from gym import spaces
import pygame
import time


#pygame.init()
#clock = pygame.time.Clock()

env = rlenv.CustomGridworldEnv()

# 6 actions: 0 - move left, 1 - move right, 2 - move down, 3 - move  up, 4 - save, 5 - no-op

observations = env.reset()
done = False
total_reward = 0
steps = 0


env.render()

while not done and steps != 2:
    #actions = [env.action_space.sample() for _ in range(env.num_agents)]
    actions = [4, 5, 1, 5]
    #actions = [1, 2, 3, 0]
    next_observations, rewards, done, _ = env.step(actions)

    total_reward += sum(rewards)
    print("Actions: ", actions)
    print("Observations:", next_observations)
    print("Rewards:", rewards)
    print("Done:", done)

    steps = steps + 1

    env.render()


# run = True

# while run:
#     clock.tick(1) # set game speed to 30 fps

#     it = 0

#     while it != 3:
#         env.render() # make pygame render calls to window
#         time.sleep(1)
#         #actions = [env.action_space.sample() for _ in range(env.num_agents)]
#         actions = [4, 5, 1, 5]
#         next_observations, rewards, done, _ = env.step(actions)

#         total_reward += sum(rewards)
#         print("Actions: ", actions)
#         print("Observations:", next_observations)
#         print("Rewards:", rewards)
#         print("Done:", done)

#         it = it + 1

#         pygame.display.update() # update window

#     run = False
#     pygame.quit()

#     done = True


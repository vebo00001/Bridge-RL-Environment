import gym
import numpy as np
from gym import spaces
import pygame

class CustomGridworldEnv(gym.Env):
    def __init__(self):
        # Define the grid dimensions
        self.grid_width = 4
        self.grid_height = 4

        # Define the agent properties
        self.num_agents = 4
        self.agent_locations = [(0, 0)] * self.num_agents
        self.agent_drowning = [False] * self.num_agents
        self.agent_drowning_time = [0] * self.num_agents

        # Define the action and observation spaces
        self.action_space = spaces.Discrete(6)  # 6 actions: 0 - move left, 1 - move right, 2 - move up, 3 - move down, 4 - save, 5 - no-op
        self.observation_space = spaces.Dict({
            'location': spaces.MultiDiscrete([self.grid_height, self.grid_width]),  # Agent's location
            'drowning': spaces.MultiBinary(self.num_agents),  # Whether agent is drowning or not
            'drowning_time': spaces.MultiDiscrete([6] * self.num_agents),  # Time interval the agent has been drowning
        })

# Initialize Pygame
        pygame.init()
        self.screen_width = 400
        self.screen_height = 400
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Multi Agent RL Environment")
        self.clock = pygame.time.Clock()

        # # Load agent image
        # self.agent_image = pygame.image.load("C:/Users/vedan/Documents/RL Environment/agent.png")
        # self.agent_image = pygame.transform.scale(self.agent_image, (50, 50))  # Adjust agent image size


    def step(self, actions):
        rewards = [-1] * self.num_agents
        dones = [False] * self.num_agents

        # Perform the specified actions for each agent
        for agent_idx, action in enumerate(actions):
            if not self.agent_drowning[agent_idx]:
                location = self.agent_locations[agent_idx]
                new_location = self._get_new_location(location, action)


                if self._is_water(new_location) and not self._is_water(location):
                    self.agent_locations[agent_idx] = new_location
                    self.agent_drowning_time[agent_idx] += 1
                
                elif self._is_water(new_location) and self._is_water(location):
                    self.agent_drowning_time[agent_idx] += 1
                    if self.agent_drowning_time[agent_idx] >= 5:
                        self.agent_drowning[agent_idx] = True
                        rewards[agent_idx] = -100  # Penalty for drowning
                        dones[agent_idx] = True

                else:
                    self.agent_locations[agent_idx] = new_location

                    if new_location == (3, 3):
                        rewards[agent_idx] = 100  # Reward for reaching the goal state
                        dones[agent_idx] = True


            if action == 4:  # Save action
                if not self.agent_drowning[agent_idx]:
                    saved_agent_idx = self._get_agent_to_save(agent_idx)
                    if saved_agent_idx is not None:
                        self.agent_locations[saved_agent_idx] = self.agent_locations[agent_idx]
                        self.agent_drowning[saved_agent_idx] = False
                        self.agent_drowning_time[saved_agent_idx] = 0

        if all(dones):
            return self._get_observations(), rewards, True, {}

        return self._get_observations(), rewards, False, {}

    def reset(self):
        # Reset the agent states
        # self.agent_locations = [(0, 0)] * self.num_agents
        # self.agent_drowning = [False] * self.num_agents
        # self.agent_drowning_time = [0] * self.num_agents
        self.agent_locations = [(0, 0), (1, 0), (0, 1), (2, 2)]
        self.agent_drowning = [False, False, False, False]
        self.agent_drowning_time = [0, 1, 0, 0]

        return self._get_observations()

    def _get_new_location(self, location, action):
        row, col = location

        if action == 0:  # Move left
            col = max(col - 1, 0)
            
        elif action == 1:  # Move right
            col = min(col + 1, self.grid_width - 1)

        elif action == 2:  # Move down
            row = max(row - 1, 0)

        elif action == 3:  # Move up
            row = min(row + 1, self.grid_height - 1)

        return (row, col)

    def _is_water(self, location):
        row, col = location

        if row == 0 or row == 3 or 1 <= col <= 2:
            return False  # Bridge
        else:
            return True  # Water

    def _get_agent_to_save(self, current_agent_idx):
        for agent_idx in range(self.num_agents):
            if agent_idx != current_agent_idx and not self.agent_drowning[agent_idx]:
                if self._is_adjacent_on_bridge(self.agent_locations[agent_idx], self.agent_locations[current_agent_idx]):
                    return agent_idx

        return None

    def _is_adjacent_on_bridge(self, location1, location2):
        row1, col1 = location1
        row2, col2 = location2

        if row1 == row2 and abs(col1 - col2) == 1:
            return True
        elif col1 == col2 and abs(row1 - row2) == 1:
            return True
        else:
            return False

    def _get_observations(self):
        observations = []
        for agent_idx in range(self.num_agents):
            observations.append({
                'location': self.agent_locations[agent_idx],
                'drowning': int(self.agent_drowning[agent_idx]),
                'drowning_time': self.agent_drowning_time[agent_idx]
            })

        return observations
    
    # def render(self):
    #     for agent_idx in range(self.num_agents):
    #         grid = np.full((self.grid_height, self.grid_width), '~')  # Initialize grid with water cells
    #         grid[1:2, 1:2] = '|'
    #         for row in range(0, self.grid_height):
    #             for col in range(0, self.grid_width):
    #                 location = (row, col)
    #                 if location == self.agent_locations[agent_idx]:
    #                     if self.agent_drowning_time[agent_idx] >= 1:
    #                         grid[row, col] = 'D'  # Drowning agent
    #                     else:
    #                         grid[row, col] = 'A'  # Agent on land
    #                 elif not self._is_water(location) and not 1 <= row <= 2:
    #                     grid[row, col] = '_'  # Land

    #                 elif 1 <= row <= 2 and 1 <= col <= 2:
    #                     grid[row, col] = '|'



    #         print(f"Agent {agent_idx + 1} Grid:")
    #         print(np.flipud(grid))
    #         print()

    def render(self):

        cell_width = self.screen_width // self.grid_width
        cell_height = self.screen_height // self.grid_height

        # Create a transparent grid surface
        grid_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

        # Render the grid cells
        for row in range(self.grid_height):
            for col in range(self.grid_width):
                x = col * cell_width
                y = row * cell_height

                # Set cell color based on land, water, or bridge
                if self._is_water((row, col)):
                    color = (0, 0, 255, 128)  # Blue for water
                elif 1 <= row <= 2 and 1 <= col <= 2:
                    color = (128,128,128, 128)  # Black for bridge
                else:
                    color = (0, 255, 0, 128)  # Green for land

                 # Render the cell
                pygame.draw.rect(self.screen, color, (x, y, cell_width, cell_height))

        # Render the grid lines on the grid surface
        line_color = (0, 0, 0, 128)  # Black color for grid lines (with transparency)
        for x in range(0, self.screen_width, cell_width):
            pygame.draw.line(grid_surface, line_color, (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, cell_height):
            pygame.draw.line(grid_surface, line_color, (0, y), (self.screen_width, y), 1)

        # Render the agents as red circles on top of the grid surface
        agent_radius = min(cell_width, cell_height) // 3
        for agent_location in self.agent_locations:
            agent_row, agent_col = agent_location
            agent_x = (agent_col + 0.80) * cell_width - agent_radius
            agent_y = (agent_row + 0.80) * cell_height - agent_radius
            pygame.draw.circle(grid_surface, (255, 0, 0), (int(agent_x), int(agent_y)), agent_radius)

        # Blit the grid surface onto the screen
        grid_surface_flipped = pygame.transform.flip(grid_surface, False, True)
        self.screen.blit(grid_surface_flipped, (0, 0))

        pygame.display.flip()



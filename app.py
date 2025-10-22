import pygame
import random
import math
import sys
from enum import Enum, auto
import sys; print(sys.version)

# Tile Types
class Tile(Enum):
    GRASS = auto()
    DIRT = auto()
    STONE = auto()
    WATER = auto()
    TREE = auto()
    FLOWER = auto()
    TREASURE = auto()
    KEY_ITEM = 11
    BRICK = 12
    QUESTION_BLOCK = 13
    ICE = 14
    SNOW = 15
    SAND = 16
    CACTUS = 17
    LAVA = 18
    OBSIDIAN = 19
    PORTAL = 20
    CRYSTAL = 22
    MUSHROOM_BLOCK = 23
    LILY_PAD = 24
    VINE = 25
    DARK_STONE = 26
    CORAL = 27
    NPC = 28
    MUSHROOM_RED = 29
    MUSHROOM_BLUE = 30
    BUSH = 31
    CRATE = 32
    SIGN = 33
    STONE_BLOCK = 34
    TREE_PINE = 35
    TREE_OAK = 36
    TREE_MUSHROOM = 37

# Initialize Pygame
pygame.init()

# Screen setup - must be done before any asset loading
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Exploration Game")

# Initialize fonts
pixel_font = pygame.font.Font(None, 16)  # Pixel-style font
pygame.font.init()
clock = pygame.time.Clock()

# Asset Loading
def load_image(path, scale=1, colorkey=None):
    """Load an image with optional scaling and colorkey transparency."""
    try:
        image = pygame.image.load(path).convert_alpha()
        if scale != 1:
            new_size = (int(image.get_width() * scale), int(image.get_height() * scale))
            image = pygame.transform.scale(image, new_size)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    except pygame.error as e:
        print(f'Cannot load image: {path}')
        print(f'Error: {e}')
        # Return a placeholder surface if image fails to load
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 128))  # Semi-transparent magenta as error color
        return surf

def load_animation_frames(folder_path, scale=1, colorkey=None):
    """Load all images from a folder as an animation sequence."""
    import os
    try:
        frames = []
        # Sort files to ensure correct order (e.g., frame1.png, frame2.png, ...)
        files = sorted(os.listdir(folder_path))
        for filename in files:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                frame = load_image(os.path.join(folder_path, filename), scale, colorkey)
                frames.append(frame)
        return frames
    except Exception as e:
        print(f'Error loading animation from {folder_path}: {e}')
        return []

# Load player animations (Jack the Knight)
class PlayerAnimations:
    def __init__(self):
        base_path = 'assets/sprites/characters/player/knight'
        self.idle = load_animation_frames(f'{base_path}/idle', scale=2)
        self.walk = load_animation_frames(f'{base_path}/walk', scale=2)
        self.run = load_animation_frames(f'{base_path}/run', scale=2)
        self.jump = load_animation_frames(f'{base_path}/jump', scale=2)
        self.attack = load_animation_frames(f'{base_path}/attack', scale=2)
        self.dead = load_animation_frames(f'{base_path}/dead', scale=2)
        self.current_animation = self.idle
        self.animation_frame = 0
        self.animation_speed = 0.15  # Slightly slower for knight animations
        self.current_time = 0
        self.facing_right = True  # Track which way Jack is facing

    def update(self, dt):
        if not self.current_animation:
            return
        self.current_time += dt
        frame_duration = 1.0 / len(self.current_animation) * 1000  # ms per frame
        self.animation_frame = int((self.current_time * self.animation_speed * 1000) / frame_duration) % len(self.current_animation)
    
    def get_current_frame(self):
        if not self.current_animation:
            return None
        return self.current_animation[self.animation_frame]

# NPC Types
NPC_TYPES = {
    'MERCHANT': {'name': 'Merchant', 'icon': '🧙', 'color': (245, 158, 11), 'dialogue': [
        "Welcome! Rare items for sale.", "Health potion: 20 coins?", "Treasures from all dimensions!", "Deal?"
    ]},
    'EXPLORER': {'name': 'Explorer', 'icon': '🧭', 'color': (139, 69, 19), 'dialogue': [
        "I've traveled far and wide.", "The world is full of wonders!", "Be careful in the caves!"
    ]},
    'WIZARD': {'name': 'Wizard', 'icon': '🧙', 'color': (138, 43, 226), 'dialogue': [
        "I sense great magic in you.", "The crystals hold great power.", "Beware the dark caves!"
    ]},
    'FARMER': {'name': 'Farmer', 'icon': '👨‍🌾', 'color': (34, 139, 34), 'dialogue': [
        "My crops grow well here.", "The soil is rich in this valley.", "Need any supplies?"
    ]},
    'CUTE_GIRL': {'name': 'Cute Girl', 'icon': '👧', 'color': (255, 182, 193), 'dialogue': [
        "Hello there, traveler!", "The forest is beautiful today.", "Watch out for the dark caves!"
    ]},
    'SANTA': {'name': 'Santa', 'icon': '🎅', 'color': (255, 0, 0), 'dialogue': [
        "Ho ho ho! Merry Christmas!", "Have you been good this year?", "Would you like a present?"
    ]},
    'DINO': {'name': 'Dino', 'icon': '🦖', 'color': (0, 128, 0), 'dialogue': [
        "Rawr! I mean... hello!", "I'm not like other dinosaurs.", "Do you like my tiny arms?"
    ]},
    'ZOMBIE_MALE': {'name': 'Zombie', 'icon': '🧟', 'color': (100, 200, 100), 'dialogue': [
        "Brains... I mean, hello!", "I'm not feeling so good...", "Got any... snacks?"
    ]},
    'ZOMBIE_FEMALE': {'name': 'Zombie Girl', 'icon': '🧟‍♀️', 'color': (150, 200, 150), 'dialogue': [
        "Ugh... what day is it?", "I used to be alive once...", "Don't mind the smell..."
    ]},
    'NINJA': {'name': 'Ninja Girl', 'icon': '🥷', 'color': (100, 100, 100), 'dialogue': [
        "...", "The shadows protect me.", "I was never here."
    ]},
    'RED_HAT': {'name': 'Red Hat', 'icon': '🎩', 'color': (200, 0, 0), 'dialogue': [
        "I like my hat. It's red.", "Have you seen my hat? Oh, I'm wearing it.", "Red is the best color!"
    ]},
    'ROBOT': {'name': 'Robot', 'icon': '🤖', 'color': (150, 150, 150), 'dialogue': [
        "BEEP BOOP. GREETINGS, FLESHY HUMAN.", "DO NOT WORRY, I AM NOT PLANNING WORLD DOMINATION.", "YET."
    ]},
    'SCIENTIST': {'name': 'Mad Scientist', 'icon': '👨‍🔬', 'color': (0, 0, 255), 'dialogue': [
        "The results are... inconclusive.", "Fascinating! Let me take notes.", "It's alive! IT'S ALIVE!"
    ]}
}

# Load NPC sprites
class NPCSprites:
    def __init__(self):
        self.sprites = {}
        self.animations = {}
        # Create a placeholder surface for NPCs without assets
        self.placeholder = self.create_placeholder_sprite()
        self.load_npcs()
        
    def create_placeholder_sprite(self, size=32):
        """Create a simple colored square with a question mark as a placeholder."""
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        # Draw a colored rectangle
        pygame.draw.rect(surface, (200, 200, 200), (0, 0, size, size))
        pygame.draw.rect(surface, (100, 100, 100), (0, 0, size, size), 2)
        # Add a question mark
        font = pygame.font.Font(None, 24)
        text = font.render('?', True, (0, 0, 0))
        text_rect = text.get_rect(center=(size//2, size//2))
        surface.blit(text, text_rect)
        return surface
        
    def load_npcs(self):
        # Define NPC types and their corresponding sprite folders
        npc_data = {
            # Cute Girl (already had this one)
            'CUTE_GIRL': {
                'name': 'Cute Girl',
                'folder': 'Cute Girl',
                'color': (255, 182, 193),  # Light pink
                'dialogue': [
                    "Hello there, traveler!",
                    "The forest is beautiful today.",
                    "Watch out for the dark caves!"
                ]
            },
            # Merchant
            'MERCHANT': {
                'name': 'Merchant',
                'folder': 'merchant',
                'color': (245, 158, 11),  # Orange
                'dialogue': [
                    "Welcome to my shop!",
                    "I have the best prices in town.",
                    "Special deal just for you!"
                ]
            },
            # Santa
            'SANTA': {
                'name': 'Santa',
                'folder': 'santasprites',
                'color': (255, 0, 0),  # Red
                'dialogue': [
                    "Ho ho ho! Merry Christmas!",
                    "Have you been good this year?",
                    "Would you like a present?"
                ]
            },
            # Dino
            'DINO': {
                'name': 'Dino',
                'folder': 'dino',
                'color': (0, 128, 0),  # Green
                'dialogue': [
                    "Rawr! I mean... hello!",
                    "I'm not like other dinosaurs.",
                    "Do you like my tiny arms?"
                ]
            },
            # Zombie (Male)
            'ZOMBIE_MALE': {
                'name': 'Zombie',
                'folder': 'Zombies/male',
                'color': (100, 200, 100),  # Zombie green
                'dialogue': [
                    "Brains... I mean, hello!",
                    "I'm not feeling so good...",
                    "Got any... snacks?"
                ]
            },
            # Zombie (Female)
            'ZOMBIE_FEMALE': {
                'name': 'Zombie Girl',
                'folder': 'Zombies/female',
                'color': (150, 200, 150),  # Lighter zombie green
                'dialogue': [
                    "Ugh... what day is it?",
                    "I used to be alive once...",
                    "Don't mind the smell..."
                ]
            },
            # Ninja Girl
            'NINJA': {
                'name': 'Ninja Girl',
                'folder': 'Ninja Girl',
                'color': (100, 100, 100),  # Gray
                'dialogue': [
                    "...",  # Ninjas are quiet
                    "The shadows protect me.",
                    "I was never here."
                ]
            },
            # Red Hat
            'RED_HAT': {
                'name': 'Red Hat',
                'folder': 'Red Hat',
                'color': (200, 0, 0),  # Red
                'dialogue': [
                    "I like my hat. It's red.",
                    "Have you seen my hat? Oh, I'm wearing it.",
                    "Red is the best color!"
                ]
            },
            # Robot
            'ROBOT': {
                'name': 'Robot',
                'folder': 'Robot',
                'color': (150, 150, 150),  # Metal gray
                'dialogue': [
                    "BEEP BOOP. GREETINGS, FLESHY HUMAN.",
                    "DO NOT WORRY, I AM NOT PLANNING WORLD DOMINATION.",
                    "YET."
                ]
            },
            # Explorer
            'EXPLORER': {
                'name': 'Explorer',
                'folder': 'explorer',
                'color': (139, 69, 19),  # Brown
                'dialogue': [
                    "I've been to the highest peaks!",
                    "The world is full of wonders.",
                    "Care to join me on an adventure?"
                ]
            },
            # Farmer
            'FARMER': {
                'name': 'Farmer',
                'folder': 'farmer',
                'color': (34, 139, 34),  # Forest green
                'dialogue': [
                    "These crops won't grow themselves!",
                    "Best harvest in years, I tell ya.",
                    "City folk don't understand farming..."
                ]
            },
            # Knight
            'KNIGHT': {
                'name': 'Knight',
                'folder': 'knight',
                'color': (192, 192, 192),  # Silver
                'dialogue': [
                    "Halt! Who goes there?",
                    "I protect these lands.",
                    "My sword is at your service."
                ]
            },
            # Scientist
            'SCIENTIST': {
                'name': 'Mad Scientist',
                'folder': 'scientist',
                'color': (0, 0, 255),  # Blue
                'dialogue': [
                    "The results are... inconclusive.",
                    "Fascinating! Let me take notes.",
                    "It's alive! IT'S ALIVE!"
                ]
            },
            # Wizard
            'WIZARD': {
                'name': 'Wizard',
                'folder': 'wizard',
                'color': (138, 43, 226),  # Purple
                'dialogue': [
                    "I sense great magic within you.",
                    "The arcane arts are not to be trifled with.",
                    "Abracadabra! ...Did that work?"
                ]
            }
        }

        for npc_type, data in npc_data.items():
            # Initialize with placeholder sprite
            self.sprites[npc_type] = self.placeholder
            
            # Create a simple animation with just the placeholder
            self.animations[npc_type] = {
                'idle': [self.placeholder],
                'current_frame': 0,
                'animation_speed': 0.1,
                'current_time': 0
            }
            
            # Update NPC_TYPES with the loaded data
            if npc_type in NPC_TYPES:
                NPC_TYPES[npc_type].update({
                    'name': data['name'],
                    'color': data['color']
                })
            else:
                NPC_TYPES[npc_type] = {
                    'name': data['name'],
                    'color': data['color'],
                    'dialogue': data['dialogue']
                }
                
            # Try to load actual assets if available
            folder = data.get('folder')
            if folder:
                try:
                    # First try loading from the NPC's direct folder
                    try:
                        idle_frames = load_animation_frames(
                            f'assets/sprites/characters/npcs/{folder}',
                            scale=2,
                            colorkey=-1
                        )
                    except:
                        # If that fails, try loading from an Idle subfolder
                        idle_frames = load_animation_frames(
                            f'assets/sprites/characters/npcs/{folder}/Idle',
                            scale=2,
                            colorkey=-1
                        )
                    
                    # If we successfully loaded frames, use them
                    if idle_frames:
                        self.sprites[npc_type] = idle_frames[0]
                        self.animations[npc_type] = {
                            'idle': idle_frames,
                            'current_frame': 0,
                            'animation_speed': 0.1,
                            'current_time': 0
                        }
                except Exception as e:
                    # Silently handle missing assets, we already have placeholders
                    pass
        
    def update(self, dt):
        # Update animation frames for all NPCs
        for npc_type, anim in self.animations.items():
            anim['current_time'] += dt
            if anim['current_time'] >= anim['animation_speed']:
                anim['current_time'] = 0
                anim['current_frame'] = (anim['current_frame'] + 1) % len(anim['idle'])
                # Update the main sprite with the current frame
                self.sprites[npc_type] = anim['idle'][anim['current_frame']]
        
    def get(self, npc_type):
        return self.sprites.get(npc_type.upper())


class TileSprites:
    def __init__(self):
        self.sprites = {}
        self.load_tiles()
    
    def load_tiles(self):
        # Load mushroom forest tiles
        mushroom_forest_path = 'assets/sprites/tiles/mushroom_forest'
        try:
            print(f"Loading tiles from: {mushroom_forest_path}")
            
            # Load bush variants
            bush_frames = []
            for i in range(1, 5):
                bush_path = f'{mushroom_forest_path}/Bush ({i}).png'
                print(f"Loading: {bush_path}")
                bush_img = load_image(bush_path)
                if bush_img:
                    bush_frames.append(bush_img)
            if bush_frames:
                self.sprites[Tile.BUSH] = bush_frames
                print(f"Loaded {len(bush_frames)} bush frames")
            
            # Load crate
            crate_path = f'{mushroom_forest_path}/Crate.png'
            print(f"Loading: {crate_path}")
            self.sprites[Tile.CRATE] = load_image(crate_path)
            
            # Load mushrooms
            mushroom_red_path = f'{mushroom_forest_path}/Mushroom_1.png'
            print(f"Loading: {mushroom_red_path}")
            self.sprites[Tile.MUSHROOM_RED] = load_image(mushroom_red_path)
            
            mushroom_blue_path = f'{mushroom_forest_path}/Mushroom_2.png'
            print(f"Loading: {mushroom_blue_path}")
            self.sprites[Tile.MUSHROOM_BLUE] = load_image(mushroom_blue_path)
            
            # Load signs
            sign_frames = []
            for i in range(1, 3):
                sign_path = f'{mushroom_forest_path}/Sign_{i}.png'
                print(f"Loading: {sign_path}")
                sign_img = load_image(sign_path)
                if sign_img:
                    sign_frames.append(sign_img)
            if sign_frames:
                self.sprites[Tile.SIGN] = sign_frames
                print(f"Loaded {len(sign_frames)} sign frames")
            
            # Load stone block
            stone_path = f'{mushroom_forest_path}/Stone.png'
            print(f"Loading: {stone_path}")
            self.sprites[Tile.STONE_BLOCK] = load_image(stone_path)
            
            # Load tree variants
            tree_frames = []
            for i in range(1, 4):
                tree_path = f'{mushroom_forest_path}/Tree_{i}.png'
                print(f"Loading: {tree_path}")
                tree_img = load_image(tree_path)
                if tree_img:
                    tree_frames.append(tree_img)
            if tree_frames:
                self.sprites[Tile.TREE_MUSHROOM] = tree_frames
                print(f"Loaded {len(tree_frames)} tree frames")
                
            print("Finished loading tile images")
            
        except Exception as e:
            import traceback
            print(f"Error loading tile images: {e}")
            traceback.print_exc()
    
    def get_tile_image(self, tile_type, variant=0):
        """Get a tile image, with optional variant for tiles with multiple sprites"""
        if tile_type in self.sprites:
            tile = self.sprites[tile_type]
            if isinstance(tile, list):
                return tile[variant % len(tile)]
            return tile
        return None

# Initialize sprites
player_animations = PlayerAnimations()
npc_sprites = NPCSprites()
tile_sprites = TileSprites()

# For backward compatibility
PLAYER_SPRITE = player_animations.get_current_frame() or pygame.Surface((32, 32), pygame.SRCALPHA)
NPC_SPRITES = npc_sprites.sprites

# Constants
TILE_SIZE = 40
VIEWPORT_WIDTH = 16
VIEWPORT_HEIGHT = 12
SCREEN_WIDTH = VIEWPORT_WIDTH * TILE_SIZE
SCREEN_HEIGHT = VIEWPORT_HEIGHT * TILE_SIZE + 150  # Extra for HUD

# Creature Types and Stats
CREATURE_TYPES = {
    'FIRE': {'name': 'Fire', 'color': (255, 100, 0), 'strong_against': 'GRASS', 'weak_against': 'WATER'},
    'WATER': {'name': 'Water', 'color': (0, 150, 255), 'strong_against': 'FIRE', 'weak_against': 'GRASS'},
    'GRASS': {'name': 'Grass', 'color': (0, 200, 0), 'strong_against': 'WATER', 'weak_against': 'FIRE'},
    'ELECTRIC': {'name': 'Electric', 'color': (255, 215, 0), 'strong_against': 'WATER', 'weak_against': 'GROUND'},
    'GROUND': {'name': 'Ground', 'color': (160, 82, 45), 'strong_against': 'ELECTRIC', 'weak_against': 'WATER'}
}

CREATURE_NAMES = {
    'FIRE': ['Charmander', 'Vulpix', 'Growlithe', 'Ponyta', 'Magmar'],
    'WATER': ['Squirtle', 'Psyduck', 'Tentacool', 'Magikarp', 'Staryu'],
    'GRASS': ['Bulbasaur', 'Oddish', 'Bellsprout', 'Exeggcute', 'Tangela'],
    'ELECTRIC': ['Pikachu', 'Voltorb', 'Magnemite', 'Electabuzz', 'Jolteon'],
    'GROUND': ['Sandshrew', 'Diglett', 'Geodude', 'Cubone', 'Rhyhorn']
}

class Creature:
    def __init__(self, ctype=None):
        if ctype is None:
            ctype = random.choice(list(CREATURE_TYPES.keys()))
        
        self.type = ctype
        self.name = random.choice(CREATURE_NAMES[ctype])
        self.level = random.randint(1, 10)
        self.health = 20 + (self.level * 5)
        self.max_health = self.health
        self.attack = 5 + self.level
        self.defense = 5 + self.level
        self.speed = random.randint(1, 10)
        self.experience = 0
        self.experience_to_level = self.level * 10
        self.moves = [
            {'name': 'Tackle', 'power': 10, 'type': 'NORMAL', 'pp': 30},
            {'name': 'Elemental Blast', 'power': 15, 'type': self.type, 'pp': 15}
        ]
        
        # Random chance for a special move
        if random.random() < 0.3:
            special_moves = [
                {'name': 'Quick Attack', 'power': 8, 'type': 'NORMAL', 'pp': 20, 'priority': 1},
                {'name': 'Defense Curl', 'power': 0, 'type': 'NORMAL', 'pp': 20, 'effect': 'defense_up'},
                {'name': 'Growl', 'power': 0, 'type': 'NORMAL', 'pp': 20, 'effect': 'attack_down'}
            ]
            self.moves.append(random.choice(special_moves))
    
    def attack_move(self, move_index, target):
        if move_index >= len(self.moves):
            return "Invalid move!"
            
        move = self.moves[move_index]
        if move['pp'] <= 0:
            return f"No PP left for {move['name']}!"
            
        move['pp'] -= 1
        damage = 0
        message = f"{self.name} used {move['name']}! "
        
        # Handle status moves
        if 'effect' in move:
            if move['effect'] == 'defense_up':
                self.defense += 2
                return message + f"{self.name}'s defense rose!"
            elif move['effect'] == 'attack_down':
                target.attack = max(1, target.attack - 2)
                return message + f"{target.name}'s attack fell!"
            return message + "But it failed!"
        
        # Calculate damage for attacking moves
        effectiveness = 1.0
        if move['type'] in CREATURE_TYPES:
            if CREATURE_TYPES[move['type']]['strong_against'] == target.type:
                effectiveness = 2.0
                message += "It's super effective! "
            elif CREATURE_TYPES[move['type']]['weak_against'] == target.type:
                effectiveness = 0.5
                message += "It's not very effective... "
        
        damage = int((((2 * self.level / 5 + 2) * move['power'] * (self.attack / target.defense)) / 50 + 2) * effectiveness)
        damage = max(1, damage)  # Minimum 1 damage
        
        # Add some randomness to damage (85-100% of calculated damage)
        damage = int(damage * (0.85 + 0.15 * random.random()))
        
        target.health = max(0, target.health - damage)
        message += f"Dealt {damage} damage!"
        
        return message
    
    def gain_experience(self, exp):
        self.experience += exp
        message = f"{self.name} gained {exp} EXP!"
        
        if self.experience >= self.experience_to_level:
            self.level_up()
            message += f"\n{self.name} grew to level {self.level}!"
        
        return message
    
    def level_up(self):
        self.level += 1
        self.max_health += 5
        self.health = self.max_health
        self.attack += 2
        self.defense += 2
        self.experience = 0
        self.experience_to_level = self.level * 10
        
        # Learn new moves at certain levels
        if self.level == 10 and len(self.moves) < 4:
            new_moves = {
                'FIRE': {'name': 'Flamethrower', 'power': 30, 'type': 'FIRE', 'pp': 10},
                'WATER': {'name': 'Hydro Pump', 'power': 30, 'type': 'WATER', 'pp': 10},
                'GRASS': {'name': 'Solar Beam', 'power': 35, 'type': 'GRASS', 'pp': 10},
                'ELECTRIC': {'name': 'Thunderbolt', 'power': 30, 'type': 'ELECTRIC', 'pp': 10},
                'GROUND': {'name': 'Earthquake', 'power': 35, 'type': 'GROUND', 'pp': 10}
            }
            self.moves.append(new_moves[self.type])
    
    def is_fainted(self):
        return self.health <= 0

# Font setup
font = pygame.font.SysFont('Arial', 20)
small_font = pygame.font.SysFont('Arial', 16)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Biome Definitions
BIOMES = {
    'GRASSLAND': {'name': 'Grassland', 'color': (34, 197, 94), 'icon': '🌱', 'bg': (100, 150, 255)},
    'DESERT':    {'name': 'Desert',    'color': (245, 158, 11), 'icon': '🏜️', 'bg': (255, 200, 100)},
    'SNOW':      {'name': 'Tundra',    'color': (147, 197, 253), 'icon': '❄️', 'bg': (200, 230, 255)},
    'FOREST':    {'name': 'Forest',    'color': (22, 163, 74), 'icon': '🌲', 'bg': (50, 150, 50)},
    'LAVA':      {'name': 'Volcanic',  'color': (234, 88, 12), 'icon': '🌋', 'bg': (180, 50, 50)},
    'OCEAN':     {'name': 'Ocean',     'color': (59, 130, 246), 'icon': '🌊', 'bg': (50, 100, 200)},
    'SWAMP':     {'name': 'Swamp',     'color': (101, 163, 13), 'icon': '🐸', 'bg': (80, 120, 80)},
    'MOUNTAIN':  {'name': 'Mountain',  'color': (107, 114, 128), 'icon': '⛰️', 'bg': (100, 100, 100)},
    'JUNGLE':    {'name': 'Jungle',     'color': (21, 128, 61), 'icon': '🦜', 'bg': (30, 100, 30)},
    'MUSHROOM':  {'name': 'Mushroom',  'color': (168, 85, 247), 'icon': '🍄', 'bg': (150, 50, 150)},
    'CRYSTAL':   {'name': 'Crystal Cave','color': (139, 92, 246), 'icon': '💎', 'bg': (80, 50, 120)},
    'WASTELAND': {'name': 'Wasteland', 'color': (120, 113, 108), 'icon': '💀', 'bg': (90, 80, 70)}
}

# Tile enum has been moved to the top of the file

WALKABLE = [
    Tile.GRASS, Tile.DIRT, Tile.FLOWER, Tile.TREASURE, Tile.KEY_ITEM,
    Tile.QUESTION_BLOCK, Tile.SNOW, Tile.SAND, Tile.PORTAL, Tile.CRYSTAL,
    Tile.ICE, Tile.MUSHROOM_BLOCK, Tile.LILY_PAD, Tile.DARK_STONE, Tile.NPC,
    Tile.BRICK, Tile.OBSIDIAN, Tile.MUSHROOM_RED, Tile.MUSHROOM_BLUE, 
    Tile.BUSH, Tile.CRATE, Tile.SIGN, Tile.STONE_BLOCK
]

# NPC Types
NPC_TYPES = {
    'MERCHANT': {'name': 'Merchant', 'icon': '🧙', 'color': (245, 158, 11), 'dialogue': [
        "Welcome! Rare items for sale.", "Health potion: 20 coins?", "Treasures from all dimensions!", "Deal?"
    ]},
    'EXPLORER': {'name': 'Explorer', 'icon': '🧑‍🚀', 'color': (59, 130, 246), 'dialogue': [
        "I've mapped these lands!", "Hidden portals everywhere.", "Crystal Cave has rare loot.", "Map knowledge: 15 coins."
    ]},
    'WIZARD': {'name': 'Wizard', 'icon': '🧙‍♂️', 'color': (139, 92, 246), 'dialogue': [
        "Magic flows here...", "I sense power in you.", "Teleport spell: 30 coins.", "Portals need courage."
    ]},
    'FARMER': {'name': 'Farmer', 'icon': '👨‍🌾', 'color': (22, 163, 74), 'dialogue': [
        "Good crops in grasslands!", "Trade supplies: 10 coins.", "Perfect weather.", "Hard work pays!"
    ]},
    'KNIGHT': {'name': 'Knight', 'icon': '⚔️', 'color': (220, 38, 38), 'dialogue': [
        "Stay alert at night!", "I guard these lands.", "You're brave.", "Protection charm: 25 coins."
    ]},
    'SCIENTIST': {'name': 'Scientist', 'icon': '🔬', 'color': (6, 182, 212), 'dialogue': [
        "Fascinating physics!", "Studying portals.", "Crystals hold energy!", "Upgrade: 40 coins."
    ]}
}

# Game State
class Game:
    def __init__(self):
        self.player_x = 0
        self.player_y = 0
        self.coins = 50
        self.health = 3
        self.score = 0
        self.has_key = False
        self.current_dimension = 'overworld'
        self.biomes_discovered = ['GRASSLAND']
        self.npcs_met = set()
        self.messages = []
        self.show_map = False
        self.active_npc = None
        self.show_npc_buttons = False
        self.dialogue_index = 0
        self.anim_frame = 0
        self.world_cache = {}
        self.npc_cache = {}
        self.game_time = 0  # 0-2400 minutes (0:00-24:00)
        self.time_speed = 0.5  # Game minutes per frame
        
        # Creature collection system
        self.creatures = []  # Player's collected creatures
        self.current_creature = None  # Currently selected creature
        self.wild_creature = None  # Current wild creature in battle
        self.in_battle = False  # Whether the player is in a battle
        self.battle_messages = []  # Messages to display during battle
        self.battle_turn = 'player'  # 'player' or 'enemy'
        self.battle_won = False  # Track if player won the battle

    def add_message(self, msg):
        self.messages = self.messages[-1:] + [msg]
        pygame.time.set_timer(pygame.USEREVENT + 1, 2500, loops=1)

    def seeded_random(self, x, y, seed=0):
        n = math.sin(x * 12.9898 + y * 78.233 + seed) * 43758.5453
        return n - math.floor(n)
        
    def is_valid_position(self, x, y):
        """Check if the given coordinates are within the valid world bounds."""
        # Define your world bounds here
        min_x, max_x = -1000, 1000  # Adjust these values based on your game's world size
        min_y, max_y = -1000, 1000  # Adjust these values based on your game's world size
        
        return min_x <= x <= max_x and min_y <= y <= max_y

    def get_time_of_day(self):
        """Convert game time (in minutes) to hours and minutes."""
        hours = int(self.game_time // 60) % 24
        minutes = int(self.game_time % 60)
        return hours, minutes
        
    def get_light_level(self):
        """Calculate the current light level based on time of day."""
        hour = self.game_time / 60  # Convert to hours
        # Smooth transitions for dawn and dusk
        if 5 <= hour < 7:  # Dawn
            return 0.3 + 0.7 * ((hour - 5) / 2)
        elif 7 <= hour < 18:  # Day
            return 1.0
        elif 18 <= hour < 20:  # Dusk
            return 1.0 - 0.7 * ((hour - 18) / 2)
        else:  # Night
            return 0.3
            
    def get_biome(self, x, y):
        if self.current_dimension != 'overworld':
            if self.current_dimension == 'crystal_cave': return 'CRYSTAL'
            if self.current_dimension == 'nether': return 'LAVA'
            if self.current_dimension == 'mushroom': return 'MUSHROOM'

        bx = x // 30
        by = y // 30
        r = self.seeded_random(bx, by, 12345)
        if r < 0.10: return 'DESERT'
        if r < 0.20: return 'SNOW'
        if r < 0.35: return 'FOREST'
        if r < 0.40: return 'LAVA'
        if r < 0.50: return 'OCEAN'
        if r < 0.60: return 'SWAMP'
        if r < 0.70: return 'MOUNTAIN'
        if r < 0.80: return 'JUNGLE'
        if r < 0.85: return 'MUSHROOM'
        if r < 0.90: return 'WASTELAND'
        return 'GRASSLAND'

    def get_npc_type(self, x, y):
        r = self.seeded_random(x, y, 7777)
        if r < 0.17: return 'MERCHANT'
        if r < 0.34: return 'EXPLORER'
        if r < 0.51: return 'WIZARD'
        if r < 0.68: return 'FARMER'
        if r < 0.85: return 'KNIGHT'
        return 'SCIENTIST'

    def generate_tile(self, x, y, biome):
        r = self.seeded_random(x, y)
        if r < 0.008:
            return Tile.NPC

        match biome:
            case 'GRASSLAND':
                if r < 0.05: return Tile.WATER
                if r < 0.15: return Tile.TREE
                # Check for nearby paths to connect to
                nearby_dirt = any([
                    self.get_tile(x+dx, y+dy) == Tile.DIRT 
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
                    if self.get_biome(x+dx, y+dy) == 'GRASSLAND'
                ])
                
                # Higher chance for dirt if near existing dirt (creates paths)
                if nearby_dirt and r < 0.5: return Tile.DIRT
                
                # Base chances for tiles
                if r < 0.20: return Tile.FLOWER
                if r < 0.40: return Tile.DIRT  # Increased chance for dirt
                if r < 0.42: return Tile.TREASURE
                if r < 0.27: return Tile.QUESTION_BLOCK
                if r < 0.285: return Tile.PORTAL
                if r < 0.295: return Tile.KEY_ITEM
                return Tile.GRASS
            case 'DESERT':
                if r < 0.15: return Tile.CACTUS
                if r < 0.20: return Tile.STONE
                if r < 0.22: return Tile.TREASURE
                if r < 0.24: return Tile.QUESTION_BLOCK
                if r < 0.255: return Tile.PORTAL
                return Tile.SAND
            case 'SNOW':
                if r < 0.10: return Tile.WATER
                if r < 0.20: return Tile.ICE
                if r < 0.30: return Tile.STONE
                if r < 0.32: return Tile.TREASURE
                if r < 0.34: return Tile.QUESTION_BLOCK
                if r < 0.355: return Tile.PORTAL
                return Tile.SNOW
            case 'FOREST':
                if r < 0.35: return Tile.TREE
                if r < 0.40: return Tile.FLOWER
                if r < 0.43: return Tile.TREASURE
                if r < 0.45: return Tile.QUESTION_BLOCK
                if r < 0.465: return Tile.PORTAL
                return Tile.GRASS
            case 'LAVA':
                if r < 0.25: return Tile.LAVA
                if r < 0.40: return Tile.OBSIDIAN
                if r < 0.45: return Tile.STONE
                if r < 0.47: return Tile.TREASURE
                if r < 0.49: return Tile.CRYSTAL
                if r < 0.505: return Tile.PORTAL
                return Tile.BRICK
            case 'OCEAN':
                if r < 0.70: return Tile.WATER
                if r < 0.75: return Tile.LILY_PAD
                if r < 0.78: return Tile.CORAL
                if r < 0.80: return Tile.TREASURE
                if r < 0.815: return Tile.PORTAL
                return Tile.SAND
            case 'MUSHROOM_FOREST':
                if r < 0.20: return Tile.MUSHROOM_RED
                if r < 0.30: return Tile.MUSHROOM_BLUE
                if r < 0.50: return Tile.TREE_MUSHROOM
                if r < 0.60: return Tile.BUSH
                if r < 0.65: return Tile.TREE_PINE
                if r < 0.70: return Tile.TREE_OAK
                if r < 0.72: return Tile.CRATE
                if r < 0.74: return Tile.SIGN
                if r < 0.76: return Tile.STONE_BLOCK
                if r < 0.77: return Tile.TREASURE
                if r < 0.785: return Tile.PORTAL
                return Tile.GRASS
            case 'CRYSTAL':
                if r < 0.30: return Tile.DARK_STONE
                if r < 0.40: return Tile.CRYSTAL
                if r < 0.43: return Tile.TREASURE
                if r < 0.445: return Tile.PORTAL
                return Tile.STONE
            case _:
                return Tile.GRASS

    def get_tile(self, x, y):
        key = (x, y)
        if key in self.world_cache:
            return self.world_cache[key]
        
        # Get the biome without triggering tile generation
        biome = self.get_biome(x, y)
    
        # Generate the tile
        tile = self.generate_tile(x, y, biome)
        self.world_cache[key] = tile
        return tile
    
    def generate_tile(self, x, y, biome):
        # First check if we're in a valid position
        if not self.is_valid_position(x, y):
            return Tile.WATER  # or whatever default tile for out of bounds
            
        # Check for nearby dirt tiles without causing recursion
        nearby_dirt = False
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in self.world_cache and self.world_cache[(nx, ny)] == Tile.DIRT:
                nearby_dirt = True
                break
        
        # Rest of your tile generation logic...
        if biome == 'GRASSLAND':
            if random.random() < 0.2 or (nearby_dirt and random.random() < 0.5):
                return Tile.DIRT
            # Rest of your grassland generation...
        
        # Default fallback
        return Tile.GRASS

    def set_tile(self, x, y, tile):
        key = (x, y, self.current_dimension)
        self.world_cache[key] = tile

    def get_npc(self, x, y):
        key = (x, y, self.current_dimension)
        if key not in self.npc_cache and self.get_tile(x, y) == Tile.NPC:
            npc_type = self.get_npc_type(x, y)
            self.npc_cache[key] = {**NPC_TYPES[npc_type], 'type': npc_type}
        return self.npc_cache.get(key)

    def move_player(self, dx, dy):
        if self.active_npc: return
        nx, ny = self.player_x + dx, self.player_y + dy
        tile = self.get_tile(nx, ny)
        biome = self.get_biome(nx, ny)

        if biome not in self.biomes_discovered:
            self.biomes_discovered.append(biome)
            self.add_message(f"Discovered {BIOMES[biome]['name']}!")
            self.score += 500

        if tile == Tile.PORTAL:
            r = self.seeded_random(nx, ny, 9999)
            if r < 0.33:
                self.travel_dimension('crystal_cave', 'Crystal Cave')
            elif r < 0.66:
                self.travel_dimension('nether', 'The Nether')
            else:
                self.travel_dimension('mushroom', 'Mushroom Realm')
            return

        if tile == Tile.NPC:
            npc = self.get_npc(nx, ny)
            if npc:
                npc_key = f"{npc['type']}-{nx}-{ny}"
                if npc_key not in self.npcs_met:
                    self.npcs_met.add(npc_key)
                    self.score += 150
                self.active_npc = {'npc': npc, 'x': nx, 'y': ny}
            return

        if tile in WALKABLE:
            self.player_x, self.player_y = nx, ny
            if tile == Tile.TREASURE:
                self.coins += 10
                self.score += 100
                self.set_tile(nx, ny, self.generate_tile(nx, ny, biome))
                self.add_message("+10 Coins!")
            elif tile == Tile.CRYSTAL:
                self.coins += 25
                self.score += 250
                self.set_tile(nx, ny, self.generate_tile(nx, ny, biome))
                self.add_message("+25 Coins!")
            elif tile == Tile.QUESTION_BLOCK:
                r = self.seeded_random(nx, ny, 777)
                if r < 0.5:
                    self.coins += 5
                    self.score += 50
                    self.add_message("+5 Coins!")
                else:
                    self.health = min(3, self.health + 1)
                    self.add_message("+1 Life!")
                self.set_tile(nx, ny, Tile.BRICK)
            elif tile == Tile.KEY_ITEM:
                self.has_key = True
                self.score += 200
                self.set_tile(nx, ny, self.generate_tile(nx, ny, biome))
                self.add_message("Got Key!")
        elif tile in [Tile.WATER, Tile.LAVA]:
            self.health = max(0, self.health - 1)
            self.add_message("Burning!" if tile == Tile.LAVA else "Ouch!")

    def travel_dimension(self, dim, name):
        self.current_dimension = dim
        self.player_x = self.player_y = 0
        self.score += 3000
        self.add_message(f"Entered {name}!")

    def handle_trade(self, cost, reward):
        if self.coins >= cost:
            self.coins -= cost
            if reward == 'health':
                self.health = min(3, self.health + 1)
                self.add_message("+1 Health!")
            elif reward == 'map':
                new_biomes = [b for b in BIOMES.keys() if b not in self.biomes_discovered]
                if new_biomes:
                    revealed = random.sample(new_biomes, min(3, len(new_biomes)))
                    self.biomes_discovered.extend(revealed)
                    self.add_message(f"Revealed {len(revealed)} biomes!")
            elif reward == 'teleport':
                self.add_message("Teleport unlocked!")
            elif reward == 'coins':
                self.coins += 15
                self.add_message("+15 Coins!")
            elif reward == 'protection':
                self.add_message("Protection charm!")
                self.score += 500
            elif reward == 'upgrade':
                self.add_message("Equipment upgraded!")
                self.score += 1000
            self.active_npc = None
        else:
            self.add_message("Not enough coins!")

    def draw_tile(self, surface, tile, x, y, is_player):
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        center = rect.center

        if is_player:
            jump = -2 if self.anim_frame % 4 < 2 else 0
            pygame.draw.rect(surface, (220, 50, 50), rect.inflate(-4, -4))
            pygame.draw.rect(surface, (180, 0, 0), rect.inflate(-4, -4), 3)
            text = font.render('M', True, WHITE)
            text_rect = text.get_rect(center=(center[0], center[1] + jump))
            surface.blit(text, text_rect)
            return

        if tile == Tile.NPC:
            npc = self.get_npc(x, y)
            if npc:
                pygame.draw.rect(surface, (34, 197, 94), rect)
                pygame.draw.rect(surface, (22, 163, 74), rect, 2)
                icon = font.render(npc['icon'], True, WHITE)
                surface.blit(icon, icon.get_rect(center=center))
            return

        # Try to get tile image first, fall back to colors
        tile_image = tile_sprites.get_tile_image(tile, x + y)  # Use position for variant
        if tile_image:
            # Scale image to fit the tile
            scaled_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))
            surface.blit(scaled_image, rect)
            return
            
        # Default tile drawing (fallback if no image found)
        colors = {
            Tile.GRASS: (34, 197, 94),
            Tile.DIRT: (146, 64, 14),
            Tile.STONE: (156, 163, 175),
            Tile.WATER: (59, 130, 246),
            Tile.TREE: (34, 197, 94),
            Tile.FLOWER: (34, 197, 94),
            Tile.TREASURE: (34, 197, 94),
            Tile.KEY_ITEM: (34, 197, 94),
            Tile.BRICK: (217, 119, 6),
            Tile.QUESTION_BLOCK: (251, 191, 36),
            Tile.ICE: (219, 234, 254),
            Tile.SNOW: (240, 249, 255),
            Tile.SAND: (254, 243, 199),
            Tile.CACTUS: (254, 243, 199),
            Tile.LAVA: (249, 115, 22),
            Tile.OBSIDIAN: (31, 41, 55),
            Tile.PORTAL: (139, 92, 246),
            Tile.CRYSTAL: (34, 197, 94),
            Tile.MUSHROOM_BLOCK: (220, 38, 38),  # Red mushroom block
            Tile.LILY_PAD: (59, 130, 246),
            # Mushroom Forest Tiles - Colors are fallbacks if images fail to load
            Tile.MUSHROOM_RED: (220, 38, 38),      # Red
            Tile.MUSHROOM_BLUE: (59, 130, 246),    # Blue
            Tile.BUSH: (22, 101, 52),              # Dark green
            Tile.CRATE: (146, 64, 14),             # Brown
            Tile.SIGN: (253, 230, 138),            # Light yellow
            Tile.STONE_BLOCK: (107, 114, 128),     # Gray
            Tile.TREE_PINE: (22, 101, 52),         # Dark green
            Tile.TREE_OAK: (34, 197, 94),          # Green
            Tile.TREE_MUSHROOM: (147, 51, 234),    # Purple
            Tile.VINE: (34, 197, 94),
            Tile.DARK_STONE: (55, 65, 81),
            Tile.CORAL: (59, 130, 246),
            Tile.TREE_PINE: (22, 101, 52),  # Dark green
            Tile.TREE_OAK: (22, 101, 52),  # Dark green
            Tile.TREE_MUSHROOM: (147, 51, 234),  # Purple
        }

        color = colors.get(tile, (100, 100, 100))
        pygame.draw.rect(surface, color, rect)
        if tile in [Tile.BRICK, Tile.OBSIDIAN, Tile.STONE, Tile.DARK_STONE]:
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

        # Icons
        icons = {
            Tile.TREE: '🌲', 
            Tile.FLOWER: '🌸', 
            Tile.TREASURE: '$', 
            Tile.KEY_ITEM: '🔑',
            Tile.QUESTION_BLOCK: '?', 
            Tile.CACTUS: '🌵', 
            Tile.LAVA: '🔥', 
            Tile.PORTAL: '🌀',
            Tile.CRYSTAL: '💎', 
            Tile.MUSHROOM_BLOCK: '🍄', 
            Tile.LILY_PAD: '🪷',
            Tile.VINE: '🌿', 
            Tile.CORAL: '🪸',
            # Mushroom Forest icons
            Tile.MUSHROOM_RED: '🍄',
            Tile.MUSHROOM_BLUE: '🍄',
            Tile.BUSH: '🌿',
            Tile.CRATE: '📦',
            Tile.SIGN: '📜',
            Tile.STONE_BLOCK: '🪨',
            Tile.TREE_PINE: '🌲',
            Tile.TREE_OAK: '🌳',
            Tile.TREE_MUSHROOM: '🍄'
        }
        if tile in icons:
            text = font.render(icons[tile], True, WHITE if tile not in [Tile.TREASURE, Tile.QUESTION_BLOCK] else BLACK)
            surface.blit(text, text.get_rect(center=center))

        if tile == Tile.QUESTION_BLOCK:
            pygame.draw.rect(surface, (217, 119, 6), rect, 3)

    def draw_battle_screen(self):
        # Draw battle background
        screen.fill((200, 230, 250))  # Light blue background
        
        # Draw player creature (right side)
        player_creature = self.creatures[self.current_creature]
        pygame.draw.rect(screen, (150, 200, 150), (SCREEN_WIDTH - 200, 200, 150, 100))
        self.draw_text(player_creature.name, SCREEN_WIDTH - 180, 210, (0, 0, 0))
        self.draw_text(f"Lv{player_creature.level}", SCREEN_WIDTH - 100, 210, (0, 0, 0))
        
        # Draw health bar
        health_ratio = player_creature.health / player_creature.max_health
        health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 200, 0) if health_ratio > 0.2 else (255, 0, 0)
        pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH - 180, 230, 120, 15))
        pygame.draw.rect(screen, health_color, (SCREEN_WIDTH - 180, 230, int(120 * health_ratio), 15))
        self.draw_text(f"HP: {player_creature.health}/{player_creature.max_health}", SCREEN_WIDTH - 175, 230, (255, 255, 255))
        
        # Draw wild creature (left side)
        pygame.draw.rect(screen, (200, 150, 150), (50, 50, 150, 100))
        self.draw_text(f"Wild {self.wild_creature.name}", 70, 60, (0, 0, 0))
        self.draw_text(f"Lv{self.wild_creature.level}", 150, 60, (0, 0, 0))
        
        # Draw health bar for wild creature
        wild_health_ratio = self.wild_creature.health / self.wild_creature.max_health
        wild_health_color = (0, 255, 0) if wild_health_ratio > 0.5 else (255, 200, 0) if wild_health_ratio > 0.2 else (255, 0, 0)
        pygame.draw.rect(screen, (100, 100, 100), (70, 80, 120, 10))
        pygame.draw.rect(screen, wild_health_color, (70, 80, int(120 * wild_health_ratio), 10))
        
        # Draw HUD
        pygame.draw.rect(screen, (50, 50, 50), (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
        screen.blit(font.render(f'Coins: {self.coins}', True, YELLOW), (10, SCREEN_HEIGHT - 35))
        screen.blit(font.render(f'Health: {self.health}', True, RED), (150, SCREEN_HEIGHT - 35))
        screen.blit(font.render(f'Score: {self.score}', True, WHITE), (300, SCREEN_HEIGHT - 35))
        
        # Show active creature if any
        if self.creatures and not self.in_battle:
            active = self.creatures[0]  # Show first creature in party
            health_ratio = active.health / active.max_health
            health_color = (0, 255, 0) if health_ratio > 0.5 else (255, 200, 0) if health_ratio > 0.2 else (255, 0, 0)
            
            # Draw creature info
            pygame.draw.rect(screen, (80, 80, 80), (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 60, 180, 50))
            self.draw_text(f"{active.name} Lv{active.level}", SCREEN_WIDTH - 190, SCREEN_HEIGHT - 55, (255, 255, 255))
            
            # Health bar
            pygame.draw.rect(screen, (50, 50, 50), (SCREEN_WIDTH - 190, SCREEN_HEIGHT - 35, 160, 10))
            pygame.draw.rect(screen, health_color, (SCREEN_WIDTH - 190, SCREEN_HEIGHT - 35, int(160 * health_ratio), 10))
            self.draw_text(f"HP: {active.health}/{active.max_health}", SCREEN_WIDTH - 185, SCREEN_HEIGHT - 35, (255, 255, 255))

        # Draw move options
        for i, move in enumerate(player_creature.moves[:2]):  # Show first 2 moves
            move_text = f"{i+1}. {move['name']} ({move['pp']}/{move['pp']})"
            self.draw_text(move_text, 20 + (i % 2) * 200, SCREEN_HEIGHT - 60 + (i // 2) * 30, (0, 0, 0))
        
        # Add more options (Run, Bag, etc.)
        self.draw_text("R. Run", SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60, (0, 0, 0))

    def start_battle(self, wild_creature=None):
        if not self.creatures:
            self.add_message("You don't have any creatures to battle with!")
            return False
            
        if wild_creature is None:
            # Random wild creature based on biome
            biome = self.get_biome(self.player_x, self.player_y)
            creature_types = {
                'GRASSLAND': 'GRASS',
                'DESERT': 'GROUND',
                'SNOW': 'WATER',
                'FOREST': 'GRASS',
                'LAVA': 'FIRE',
                'OCEAN': 'WATER',
                'SWAMP': 'GRASS',
                'MOUNTAIN': 'GROUND',
                'JUNGLE': 'GRASS',
                'MUSHROOM': 'GRASS',
                'CRYSTAL': 'ELECTRIC',
                'WASTELAND': 'GROUND'
            }
            ctype = creature_types.get(biome, random.choice(list(CREATURE_TYPES.keys())))
            self.wild_creature = Creature(ctype)
        else:
            self.wild_creature = wild_creature
            
        self.in_battle = True
        self.battle_turn = 'player'
        self.battle_messages = [f"A wild {self.wild_creature.name} appeared!"]
        
        # If no creature is selected, use the first one
        if self.current_creature is None:
            self.current_creature = 0
        
        return True
    
    def end_battle(self, player_won):
        if player_won:
            exp_gain = self.wild_creature.level * 5
            message = self.creatures[self.current_creature].gain_experience(exp_gain)
            self.battle_messages.append(f"{self.creatures[self.current_creature].name} gained {exp_gain} EXP!")
            
            # Chance to catch the wild creature if player has less than 6
            if len(self.creatures) < 6 and random.random() < 0.3:  # 30% catch rate
                self.creatures.append(self.wild_creature)
                self.battle_messages.append(f"You caught {self.wild_creature.name}!")
                
        self.in_battle = False
        self.wild_creature = None
        self.battle_won = player_won
        return message
    
    def handle_battle_input(self, key):
        if not self.in_battle:
            return False
            
        if key == pygame.K_ESCAPE:
            self.in_battle = False
            self.wild_creature = None
            return True
            
        if key == pygame.K_1 and len(self.creatures[self.current_creature].moves) > 0:
            # Use first move
            message = self.creatures[self.current_creature].attack_move(0, self.wild_creature)
            self.battle_messages.append(message)
            
            if self.wild_creature.is_fainted():
                self.battle_messages.append(f"Wild {self.wild_creature.name} fainted!")
                self.end_battle(True)
                return True
                
            # Enemy's turn
            enemy_move = random.randint(0, len(self.wild_creature.moves) - 1)
            message = self.wild_creature.attack_move(enemy_move, self.creatures[self.current_creature])
            self.battle_messages.append(f"Wild {self.wild_creature.name} {message}")
            
            if self.creatures[self.current_creature].is_fainted():
                self.battle_messages.append(f"{self.creatures[self.current_creature].name} fainted!")
                # Find another creature that's not fainted
                for i, creature in enumerate(self.creatures):
                    if not creature.is_fainted():
                        self.current_creature = i
                        self.battle_messages.append(f"Go! {creature.name}!")
                        return True
                # If no creatures left
                self.battle_messages.append("All your creatures fainted!")
                self.end_battle(False)
                return True
                
        # Add more battle options here (items, switch, run, etc.)
        
        return True
    
    def add_message(self, text):
        """Add a message to the message log"""
        self.messages.append(text)
        if len(self.messages) > 5:  # Keep only the last 5 messages
            self.messages.pop(0)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.in_battle:
                self.handle_battle_input(event)
            elif event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_m:
                self.show_map = not self.show_map
            elif event.key == pygame.K_SPACE and self.active_npc:
                # If buttons are showing, don't advance dialogue
                if hasattr(self, 'show_npc_buttons') and self.show_npc_buttons:
                    return True
                    
                # Handle NPC interaction
                if self.active_npc not in self.npcs_met:
                    self.npcs_met.add(self.active_npc)
                    self.dialogue_index = 0
                else:
                    self.dialogue_index += 1
                
                # If we've gone through all dialogue, show buttons
                npc = NPC_TYPES[self.active_npc]
                if self.dialogue_index >= len(npc['dialogue']):
                    self.show_npc_buttons = True
                return True
            elif not self.active_npc:  # Only allow movement when not in dialogue
                if event.key in (pygame.K_w, pygame.K_UP):
                    self.move_player(0, -1)
                if event.key in (pygame.K_s, pygame.K_DOWN):
                    self.move_player(0, 1)
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    self.move_player(-1, 0)
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.move_player(1, 0)
                if event.key == pygame.K_e and self.current_dimension != 'overworld':
                    self.current_dimension = 'overworld'
                    self.add_message("Returned to Overworld!")
                if event.key == pygame.K_b:
                    self.start_battle()
                if event.key == pygame.K_h:
                    self.handle_battle_input(event.key)

    def draw(self):
        # Update time
        self.game_time = (self.game_time + self.time_speed) % 1440  # 1440 minutes in a day
        
        # Get time of day
        hours, minutes = self.get_time_of_day()
        light_level = self.get_light_level()
        
        # Clear screen with sky color
        current_biome = self.get_biome(self.player_x, self.player_y)
        bg_color = list(BIOMES[current_biome]['bg'])
        # Darken the background based on time of day
        bg_color = [int(c * light_level) for c in bg_color]
        screen.fill(tuple(bg_color))
        
        # If in battle, draw battle screen instead of the world
        if self.in_battle:
            self.draw_battle_screen()
            return

        # Viewport
        start_x = self.player_x - VIEWPORT_WIDTH // 2
        start_y = self.player_y - VIEWPORT_HEIGHT // 2
        viewport_surface = pygame.Surface((SCREEN_WIDTH, VIEWPORT_HEIGHT * TILE_SIZE))
        viewport_surface.fill((50, 50, 50))

        for row in range(VIEWPORT_HEIGHT):
            for col in range(VIEWPORT_WIDTH):
                wx = start_x + col
                wy = start_y + row
                tile = self.get_tile(wx, wy)
                is_player = (wx == self.player_x and wy == self.player_y)
                self.draw_tile(viewport_surface, tile, col, row, is_player)

        screen.blit(viewport_surface, (0, 80))

        # HUD
        hud_y = 10
        pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, 70), border_radius=10)
        self.draw_text(f"SCORE: {self.score:06d}", 20, hud_y, YELLOW)
        self.draw_text(f"×{self.coins}", 200, hud_y, YELLOW)
        self.draw_text(f"{len(self.npcs_met)}", 300, hud_y, GREEN)

        # Health
        for i in range(3):
            color = RED if i < self.health else (100, 100, 100)
            pygame.draw.rect(screen, color, (400 + i*30, hud_y, 25, 25))

        if self.has_key:
            pygame.draw.rect(screen, YELLOW, (520, hud_y, 30, 30), border_radius=5)

        # NPC Dialogue
        if self.active_npc:
            self.draw_npc_dialogue()

        # Map
        if self.show_map:
            self.draw_map()

    def draw_text(self, text, x, y, color):
        rendered = font.render(text, True, color)
        screen.blit(rendered, (x, y))

    def draw_npc_dialogue(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Dialog box with modern design
        dialog_height = 180 if not hasattr(self, 'show_npc_buttons') or not self.show_npc_buttons else 250
        dialog_rect = pygame.Rect(50, SCREEN_HEIGHT - dialog_height - 20, SCREEN_WIDTH - 100, dialog_height)
        
        # Shadow effect
        shadow_rect = dialog_rect.move(5, 5)
        pygame.draw.rect(screen, (0, 0, 0, 100), shadow_rect, border_radius=12)
        
        # Main dialog box
        pygame.draw.rect(screen, (40, 40, 60), dialog_rect, border_radius=10)
        pygame.draw.rect(screen, (80, 80, 120), dialog_rect, 2, border_radius=10)

        # NPC info
        npc_type = self.active_npc
        npc = None
        
        # Find NPC data from NPC_TYPES
        for npc_key, npc_data in NPC_TYPES.items():
            if npc_key == npc_type or (isinstance(npc_data, dict) and npc_data.get('name', '').upper() == npc_type):
                npc = npc_data if isinstance(npc_data, dict) else {'name': str(npc_type), 'color': (200, 200, 200)}
                break
        
        if npc is None:
            # Default NPC data if not found
            npc = {'name': str(npc_type), 'color': (200, 200, 200), 'icon': '?'}
        
        # Portrait area
        portrait_rect = pygame.Rect(dialog_rect.x + 15, dialog_rect.y + 15, 80, 80)
        pygame.draw.rect(screen, (30, 30, 40), portrait_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 150), portrait_rect, 2, border_radius=8)
        
        # Get NPC sprite - use the 'type' key from the npc dictionary
        npc_sprite = npc_sprites.get(npc_type['type'] if isinstance(npc_type, dict) and 'type' in npc_type else str(npc_type))
        
        # Draw NPC sprite if available, otherwise use icon
        if npc_sprite:
            # Scale the sprite to fit the portrait
            npc_sprite = pygame.transform.scale(npc_sprite, (70, 70))
            screen.blit(npc_sprite, (portrait_rect.x + 5, portrait_rect.y + 5))
        else:
            # Fallback to text icon
            icon = font.render(npc.get('icon', '?'), True, npc.get('color', (255, 255, 255)))
            screen.blit(icon, (portrait_rect.x + 25, portrait_rect.y + 20))
        
        # Name plate
        name_bg = pygame.Rect(portrait_rect.right + 10, portrait_rect.y, 200, 25)
        pygame.draw.rect(screen, npc.get('color', (200, 200, 200)), name_bg, border_radius=4)
        name_surf = pixel_font.render(npc.get('name', 'Unknown'), True, (240, 240, 240))
        screen.blit(name_surf, (name_bg.x + 10, name_bg.y + 5))
        
        # Dialog text with word wrapping
        dialogue = npc.get('dialogue', ["..."])
        if not dialogue:  # In case dialogue is empty
            dialogue = ["..."]
            
        text = dialogue[self.dialogue_index % len(dialogue)]
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if small_font.size(test_line)[0] < dialog_rect.width - 150:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line of text
        for i, line in enumerate(lines):
            text_surf = small_font.render(line, True, (240, 240, 240))
            screen.blit(text_surf, (portrait_rect.right + 15, dialog_rect.y + 50 + i * 20))
        
        # Draw buttons if in interaction mode
        if hasattr(self, 'show_npc_buttons') and self.show_npc_buttons:
            btn_y = dialog_rect.y + 120
            
            # Different buttons based on NPC type
            if npc_type == 'MERCHANT':
                self.draw_button("Buy Health (20 coins)", dialog_rect.x + 20, btn_y, GREEN, self.buy_health)
                self.draw_button("Buy Potion (30 coins)", dialog_rect.x + 20, btn_y + 50, (0, 200, 200), self.buy_potion)
            elif npc_type == 'EXPLORER':
                self.draw_button("Buy Map (15 coins)", dialog_rect.x + 20, btn_y, BLUE, self.buy_map)
                self.draw_button("Get Hint (10 coins)", dialog_rect.x + 20, btn_y + 50, (200, 200, 0), self.get_hint)
            
            # Common close button
            self.draw_button("Goodbye", dialog_rect.right - 220, btn_y + 50, (100, 100, 100), self.close_dialogue)
        else:
            # Animated continue prompt
            prompt_alpha = 128 + int(127 * (math.sin(pygame.time.get_ticks() * 0.003) + 1) / 2)
            prompt_surf = small_font.render('Press SPACE to continue...', True, (200, 200, 200, prompt_alpha))
            prompt_rect = prompt_surf.get_rect(bottomright=(dialog_rect.right - 15, dialog_rect.bottom - 15))
            screen.blit(prompt_surf, prompt_rect)
    
    def buy_health(self):
        if self.coins >= 20:
            self.coins -= 20
            self.health = min(3, self.health + 1)
            self.add_message("Health restored!")
        else:
            self.add_message("Not enough coins!")
    
    def buy_potion(self):
        if self.coins >= 30:
            self.coins -= 30
            # Add potion to inventory or use immediately
            self.health = 3
            self.add_message("Potion used! Health fully restored!")
        else:
            self.add_message("Not enough coins!")
    
    def buy_map(self):
        if self.coins >= 15:
            self.coins -= 15
            self.show_map = True
            self.add_message("Map revealed! Press M to toggle.")
        else:
            self.add_message("Not enough coins!")
    
    def get_hint(self):
        if self.coins >= 10:
            self.coins -= 10
            hints = [
                "Look for hidden paths in the mountains.",
                "Some NPCs have special items for sale.",
                "Different biomes have different creatures.",
                "Collect coins to buy useful items."
            ]
            self.add_message(random.choice(hints))
        else:
            self.add_message("Not enough coins!")
    
    def close_dialogue(self):
        self.active_npc = None
        self.show_npc_buttons = False

    def draw_button(self, text, x, y, color, action):
        btn = pygame.Rect(x, y, 400, 40)
        pygame.draw.rect(screen, color, btn, border_radius=8)
        self.draw_text(text, x + 20, y + 10, WHITE)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if btn.collidepoint(mouse) and click[0]:
            action()

    def draw_map(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        box = pygame.Rect(50, 100, SCREEN_WIDTH - 100, 400)
        pygame.draw.rect(screen, (30, 30, 30), box, border_radius=15)

        self.draw_text(f"Discovered Biomes ({len(self.biomes_discovered)}/{len(BIOMES)})", 80, 120, WHITE)

        y = 160
        for key, biome in BIOMES.items():
            color = biome['color'] if key in self.biomes_discovered else (100, 100, 100)
            name = biome['name'] if key in self.biomes_discovered else '???'
            self.draw_text(f"{biome['icon']} {name}", 80, y, color)
            y += 30

# Main Game
game = Game()

# Animation timer
anim_timer = 0

running = True
while running:
    dt = clock.tick(60)
    dt_seconds = dt / 1000.0  # Convert to seconds for consistent timing
    anim_timer += dt
    
    # Update NPC animations
    npc_sprites.update(dt_seconds)
    
    if anim_timer > 200:
        game.anim_frame = (game.anim_frame + 1) % 4
        anim_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT + 1:
            game.messages.pop(0)
        if event.type == pygame.KEYDOWN:
            if game.active_npc:
                if event.key == pygame.K_ESCAPE:
                    game.active_npc = None
            else:
                if event.key in (pygame.K_w, pygame.K_UP):
                    game.move_player(0, -1)
                if event.key in (pygame.K_s, pygame.K_DOWN):
                    game.move_player(0, 1)
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    game.move_player(-1, 0)
                if event.key in (pygame.K_d, pygame.K_RIGHT):
                    game.move_player(1, 0)
                if event.key == pygame.K_m:
                    game.show_map = not game.show_map
                if event.key == pygame.K_e and game.current_dimension != 'overworld':
                    game.current_dimension = 'overworld'
                    game.add_message("Returned to Overworld!")

    # Close map with click outside
    if game.show_map and pygame.mouse.get_pressed()[0]:
        game.show_map = False

    game.draw()
    pygame.display.flip()

pygame.quit()
sys.exit()
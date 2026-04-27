WIDTH  = 600
HEIGHT = 600
CELL   = 30

COLS = WIDTH  // CELL   
ROWS = HEIGHT // CELL   

FOOD_LIFETIME_MS  = 5000
POISON_CHANCE     = 0.25   


POWERUP_FIELD_MS  = 8000   
POWERUP_EFFECT_MS = 5000   
POWERUP_SPAWN_INTERVAL_MS = 7000   


FOOD_PER_LEVEL    = 3    
BASE_FPS          = 5
OBSTACLES_FROM_LVL = 3     
OBSTACLES_PER_LVL  = 3     


FOOD_TYPES = {
    1: {"score": 1, "color": (50,  200, 50)},
    3: {"score": 3, "color": (230, 140, 0)},
    5: {"score": 5, "color": (160, 50,  220)},
}
FOOD_WEIGHT_POOL = [1, 1, 1, 1, 3, 3, 5]


import os

WIDTH = 800
HEIGHT = 400
FPS = 60
GROUND_Y = 360

PLAYER_W = 70
PLAYER_H = 70
JUMP_STRENGTH = 20
GRAVITY = 1
DUCK_MS = 400

SCORE_FILE = "scores7.json"
TOP_SCORES = 5


DEFAULT_KEYWORDS = ["porcupine", "bumblebee"]

PV_ACCESS_KEY = "L/Cc3RGVz8+Z4jpXZwwhtqzL21UBiSVDqS1H4htNxk2GRkPcrf103g=="

# Voice / gameplay tuning
# Minimum milliseconds between voice-triggered jumps
JUMP_COOLDOWN = 250

# How much to shrink the cactus collision box (width_shrink, height_shrink)
# Used to reduce false collisions caused by transparent sprite padding
CACTUS_HITBOX_SHRINK = (20, 10)

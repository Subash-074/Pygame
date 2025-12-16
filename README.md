

Project Name: Anime Battle

Course: Programming 1

---

Description

Anime Battle is a original 2D action-platformer game created using Python and Pygame.
The player begins in a mysterious ancient chamber containing two magical paths.
Each paths leads to a unique 1-on-1 anime-style boss fight (Naruto or Luffy).

Your goal is simple:
At first you need to enter the room, after that you can defeat all enemies, and win the game.

The game includes:

* Player and enemy sprites
* AI behavior
* Background music
* Sound effects
* Animated transitions
* State-based game structure

---

How to Run the Game

1. Install Python (version 3.8+ recommended)
2. Install Pygame: pip3 install pygame
3. Ensure your project folder contains:

* main.py
* img folder
* sound folder

4. Run the game: python main.py

---

Controls

Rooms (Door Selection / Empthy paths)

* Enter Key – Play the game
* LEFT / RIGHT Key – Move
* UP Key – Jump 
* SPACE Key – Enter door

Battle

* LEFT / RIGHT Key – Move
* UP Key – Jump
* SPACE Key – Attack
* ESC Key – Exit battle and return to room

Game Over Screen

* R Key – Restart game

---

Custom Classes Implemented (Required for Project)

1. Character (Base Class)

Handles:

* Gravity + jumping physics
* Movement
* Health system
* Collision rectangle
* Knockback mechanics

This is the foundation used by Player and Enemy.

---

2. Player (Inherits from Character)

Adds:

* Keyboard input movement
* Player-specific jump handling
* Player sprite display

---

3. Enemy (Inherits from Character)

Adds:

* Simple AI that moves toward player
* Enemy sprite image
* Enemy name property

---

4. Door (Empthy Paths)

Manages:

* Door position + hitbox
* Checking if player is standing in front of a door
* Determining which battle starts

---

Features

Physics System

* Gravity
* Jumping
* Ground collision

Combat System

* Attack cooldowns
* Rect collision detection
* Knockback movement
* Enemy AI follows player

Multiple Game States

1. Menu
2. Room (hub area)
3. Battle
4. Game Over

Uses a state machine inside the Game class.

Audio System

* Background music changes depending on location
* Punch sound effect
* “FIGHT!” intro sound

Custom Artwork

* Player sprite (AI generated based on written prompt)
* Enemy sprites (Naruto, Luffy)
* Multiple battle backgrounds
* Room background

---

Sources & References Used 
Python Crash Course By Eric Mathews 
Youtube Videos 
Datacamp 

Pygame Documentation

* Game loop
* Sprites
* Surfaces
* Event handling
* Music + sound playback


Author: Subash Sapkota 
Matriculation number: 100006899 

---


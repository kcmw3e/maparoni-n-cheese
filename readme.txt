# maparoni-n-cheese
## Description
A map maker, random or custom or combined.
maparoni-n-cheese is a basic 2D map maker (think treasure map but not treasure just map). Maps can be made manually throug the placement of map objects using the mouse (or possibly touchscreen if available) or they can be randomly generated using a Voronoi diagram. Combinations of both are allowed!

## How to run it
Simply open up the main file called (you guessed it!) maparoni-n-cheese. Run it in your favorite text editor, or straight with Python3
(note: the pyglet module MUST be installed for it to work). Two sample files ("30 seed map save.txt" and "70 seed map save.txt") are included and can be opened for an example of 2 randomly-generated maps (one with, well, 30 seeds, and the other with 70 :P). These files can be edited manually via changing text (but be sure to follow the same format inside them) and then re-loaded to move things around 
(not recommended --> pretty tedious tbh and it's way easier just using the program).

## Required libraries
pyglet is a MUST, and tkinter is needed for file saving/loading, but tkinter can be ignored if file io isn't desired (may need to edit the imports if this is the path you desire).

## Shortcut commands
Notable shortcuts are:
- s --> switch between visualizing the random map generation (looks really cool when it's enabled) and just going for it quick as ya can (less recommended because it doesn't look cool, but is probably more efficient/less recourse intesive)
- delete --> IF a map object is selected, delete will delete it.
- escape --> quickly switch back to the select tool instead of having to move that pesky mouse to the gui and back <>{
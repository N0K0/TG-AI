#UiO-Bot

## How to run

To run the script simply do the following:

> python bot.py

This should set up everything needed to run the script :)



## Layout of program

We got a module based bot with an controller so that it is easy to swap out single pieces when needed.

Currently we got the following:

* MapManager 
* MapObject
    * Tile
    * Enemy
* Controller
* Parser
* Decicion_maker


### map_manager 
This is mainly a abstraction of the map system where we hide all the pathing functions and a inner container with the actual map and its layout
This is where we generate the current value of each tile on the map.
### map_object
Just a helper class defining an series of objects for valuing the map

### Controller
Just a simple controller class for starting up and running the main loop

### Parser
Nothing really, just dumps a string to JSON atm

### Decicion_maker
The actual decicion maker. For example if we figure we want to stick to a plan for a couple of ticks this is the brain that would make the desicion


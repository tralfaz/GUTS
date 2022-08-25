# GUTS

A gravitation simulator using Python 3.10, VisPy and PyQt6

This PyQt6 application displays two windows.  An Action/Option window that
provides controls to create, start, and stop a simulation run.  It also
provides controls to change various parameters used in generating random
starting conditions.

The other window is used excusiovely to display simulation scene.  This window
provides the user the ability to rotate, zoom, and shift the scene.  This can
be done with the following actions:

   Zoom - Mouse scroll wheel.

   Rotate - Mouse button-1 drag rotates scene

   Shift - Mouse shift-button-1 drag to shift scene origin

Actions:
---------------------------------
  New Simulation
     Creates a new set of gravity bodies, with random masses, positions and
     velocities.  Once pressed the simulation can then be started and stopped.

  Start
     After a new simulation, this will start the timer, and the gravity
     simulation starts animating at the current frame rate.  It can also
     continue a stopped simulation that has been stopped.

  Stop
     Stops the animation timer halting the animation.  It can be restarted by
     pressing Start.

  Jump One Second
     Advance one frame second in the animations time frame simulation.

  Add
     Add a random mass body to the scene.

  Delete
     Remove the oldest mass body added to the scene.

  Quit
     Exit the application.


Options
----------------------------------
  Bodies:
     The number of random mass bodies to create in a new simulation.

  Gravity:
     Gravitational constant to use.  Hugely increased to induce mass body
     interaction. 

  Mass Range:
     The range of random mass, in Kilograms, assigned to each random body.

  Position Range:
     The range of random X,Y,Z axis  coordinates, used to assign a 3D position
     to each random body.

  Velocity Range:
     The random range of X,Y,Z velocity vectors, in meters per second, to
     assign to each random body.  Keep small to ensure bodies stay in view.

  Frame Modes:
  
     Add - Adds new markers with each frame step.  Produces something like Anime
           tentacle porn.  Who doesn't like anime tentacle porn.

     Move - Each body marker is moved with each frame step.  Produces speres 
            zooming around in space.

     Radii - Like Move but with lines from each body to the scene origin.

     Trails - Like Move, but adds body path trails, up to a maximum length, for
              each body.  Produces multicolored sperghetti.

  Frame Rate:
     Change the animation speed.  Choose the number of animation frames to try
     to produce each realtime second.  The "auto" value will attempt to create
     as many frames a second that is reasonable.

  Trail Length:
     Set maximum trail length when in Add or Trails mode.  The value of Trail
     Length can be much larger in Trails mode then in Add mode.


Required Runtime Environment
-----------------------------------------
Python:
   Begin by installing Python 3.10.  Download the appropriate release for your
   O/S from https://www.python.org/downloads/

Using the pip3 utility provided with your python installation, install
the following:

  vispy:
     pip3 install numpy

  PyQt6:
     pip3 install PyQt6

  vispy:
     pip3 intstall vispy


  Run the guts app:
     python3 guts.py

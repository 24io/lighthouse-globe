# lighthouse-globe

## History

### Idea

A simple animation of a rotating planet (e.g. Earth) on a background with stars. 

Plan to use Mollweide-Projection images als base for the animation, mainly to have very few sample points at the poles, 
to reduce rendering artifacts there.

Extended goal is to have either the rotation or some outside effect like the position of the day-night terminator be
controlled by keyboard (arrow keys).

A further option would be swapping between different planets (earth, mars, moon) with keyboard input.

### Initial prototype

After a short sprint of roughly twelve hours of coding a first prototype that could render map content to a circle on
the screen was ready. The most glaring initial bug was a lack of curvature on the sphere, since it was actually just a
mask scrolling ver the map. Introducing the missing acos() computation fixed that.

Considering the problematic code quality and the already unwieldy size of the single code file, it was time for a little
refactoring.

### Refactoring the prototype

Pulling the map out of the main file as a first step already hinted at some bugs in the rendering (inverted latitude).
Also refactoring the screen and image as a wrapper for how Pyghthouse handles its frames made refactoring the renderer
a quite easy task. However, this required a geometry class. As an exercise, this was also added as a module providing
(initially) points, vectors, and a sphere for 3d space.

As a convenient side effect, refactoring the renderer originally provided a polar view of the example earth map. This
led to the decision to also implement different views, initially as fixed-angle rotations. For this, however, the
geometry modules needed expansion to handle rotation. Quaternions were initially chosen for this. After reading up on
quaternions, the idea was dropped and Euler resp. Tait-Bryan angles were implemented in the x-y-z configuration.

Implementing the new geometry in the renderer resulted in an initial (un-rotated) view from below onto the South Pole.
This was consistent with the chosen right-handed reference frame where x- and y-axes corresponded to the same axes of
the screen while the z-axis was oriented towards the view direction through the rotation axis of the sphere.

Next plan was to implement a camera which would reside in the screen class and thus be accessible from within the
renderer and also from outside the renderer via getters and setters to later implement a camera control.

Now wiring all classes together and implementing a camera control was a trivial task resulting in v0.2.0 being finished.

## Functionality

### Mathematics

The mathematical principles used are neatly summarized in 
[this article about the spherical coordinate system](https://en.wikipedia.org/wiki/Spherical_coordinate_system) and
[this article about Euler angles](https://en.wikipedia.org/wiki/Euler_angles).

In short, each pixel given in its screen coordinates ranging from (0, 0) in the top left corner to the
(width - 1, height - 1) in the bottom left corner. From these screen coordinates it is transformed into the renderers
world coordinates, a right-handed coordinate system with an offset and rotation stored in the camera and screen objects.

from each point a line is cast in parallel to an imaginary line going from the center of the screen towards the origin.
Initially, this is along the z-axis, which results in a view onto the South Pole of the sphere. Each intersecting point
is then transformed into spherical coordinates. These coordinates can then fetch an interpolated rgb-color from a
previously loaded rgb-map, where the spherical coordinates are transformed into map-pixel coordinates.

Any pixel that does not intersect the sphere is left black. This might be changed in a later version.

### Key Map

| key              | function                                        |
|------------------|-------------------------------------------------|
| <kbd>ESC</kbd>   | Terminates the program                          |
| <kbd>Space</kbd> | Pauses the animation                            |
| <kbd>+</kbd>     | Increases rotation rate up to 90 deg/sec        |
| <kbd>-</kbd>     | Decreases rotation rate down to -90 deg/sec     |
| <kbd>w</kbd>     | Rotates the view up by 2.5 degrees              |
| <kbd>s</kbd>     | Rotates the view down by 2.5 degrees            |
| <kbd>a</kbd>     | Rotates the view left by 2.5 degrees            |
| <kbd>d</kbd>     | Rotates the view right by 2.5 degrees           |
| <kbd>q</kbd>     | Rolls the view counter-clockwise by 2.5 degrees |
| <kbd>e</kbd>     | Rolls the view clockwise by 2.5 degrees         |
| <kbd>p</kbd>     | Flips between polar views                       |
| <kbd>r</kbd>     | Resets view to default equatorial view          |

## Conclusion

While working on the refactoring, the most striking lesson learned is how much development time was reduced with each
refactoring. In the end, adding new features became an easy task for most new features that were not included in the
initial prototype.

The most helpful refactoring was definitely the creation of the geometry class.

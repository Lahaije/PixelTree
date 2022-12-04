# PixelTree
3D Neopixel Christmas Tree. Pixels can be mapped using webcam images from different sides.

This library is not yet finished. The latest status is available at https://gathering.tweakers.net/forum/list_messages/2153702

Within the code references to phi and theta are made.
This project assumes a Spherical coordinate system https://en.wikipedia.org/wiki/Spherical_coordinate_system and the angles match the wikipedia definition.
Angle phi is positive in a clockwise manner.

For image processing X and Y are used.

X is vertical, Y is horizontal.

For snapped images the camera is originally placed in a the sperical coordinate system on the positive x axes. 
This lead to the following definitions for the axes

Image X corresponds Spherical Z

Image Y corresponds Spherical Y

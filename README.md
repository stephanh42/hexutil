# hexutil
Classes and functions to deal with hexagonal grids.

![Screenshot of example.py](img/screenshot.png)

## Introduction

This module provies the following functionality.

1. Manipulation of grid coordinates in a hexagonal grid.
2. Converting between hexagonal grid coordinates and screen coordinates.
3. Field-of-view calculation on a hegagonal grid.
4. A\* path-finding on a hexagonal grid.

All this is provided by the module `hexutil`.
The file [example.py](example.py) contains example coding using this functionality.
The above image is a screenshot from this example.

## Manipulation of grid coordinates in a hexagonal grid.

The class `hexagon.Hex` represents a particular hexagon in a grid.
Class `Hex` takes two integer arguments, `x` and `y`. 
These need to satisfy the proeprty that their sum is even.

The following (x,y) coordinate system is used to address hexagons in the grid.

![Hexgrid coordinate system](img/hexcoords.png)

At first, it may seem weird that this coordinate system leaves "holes" in the representation, 
i.e. there is no hexagon corresponding to, say,  (0, 1). However, that turns out to ne not a real problem in practise.
The advantage is that relationship to the actual center points of the hexagons becaomes very simple, namely, just
multiply `y` with √3. This also simplifies screen coordinate calculations.

The only time the "holes" are an issue is if you want to pack grid data densely into a 2D (numpy) array or a list-of-lists. In that case, just use 
`ar[hexagon.x//2][hexagon.y]` to index into array `ar`.

The constructor of `Hex` checks the "x+y is even" property. If it is not satisfied, an `InvalidHex` exception is thrown.

## Converting between hexagonal grid coordinates and screen coordinates.

Todo.

## Field-of-view calculation on a hegagonal grid.

Todo.

## A\* path-finding on a hexagonal grid.

Todo.


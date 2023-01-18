#pragma once

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <SFML/Graphics.hpp>

using namespace std;
using namespace sf;

class Object
{
protected:

    float x, y;
    Color color;

    Object()
    {

    }

public:

    float getX()
    {
        return x;
    }

    float getY()
    {
        return y;
    }
};

class Point : public Object
{
public:

    CircleShape point;

    Point()
    {

    }

    Point(float valueX, float valueY, Color valueColor)
    {
        x = valueX;
        y = valueY;
        color = valueColor;

        point.setRadius(1);
        point.setFillColor(color);
        point.setPosition(x, y);
    }
};

class Rectangle : public Object
{
protected:

    float x2, y2, w, h;

public:

    RectangleShape rect;

    Rectangle()
    {

    }

    Rectangle(float valueX1, float valueY1, float valueX2, float valueY2, Color valueColor)
    {
        x = valueX1;
        y = valueY1;
        x2 = valueX2;
        y2 = valueY2;
        w = x2 - x;
        h = y2 - y;
        color = valueColor;

        rect.setSize(Vector2f(w, h));
        rect.setFillColor(color);
        rect.setPosition(x, y);
    }

    float getX2()
    {
        return x2;
    }

    float getY2()
    {
        return y2;
    }
};

class HLine : public Rectangle
{
public:

    HLine()
    {

    }

    HLine(float valueX, float valueY, float valueX2, Color valueColor)
    {
        x = valueX;
        y = valueY;
        x2 = valueX2;
        color = valueColor;

        if (x2 - x >= 0)
            w = x2 - x;
        else
            w = x - x2;

        if (w == 0)
            w = 1;

        rect.setSize(Vector2f(w, 1));
        rect.setFillColor(color);
        rect.setPosition(x, y);
    }
};

class VLine : public Rectangle
{
public:

    VLine()
    {

    }

    VLine(float valueX, float valueY, float valueY2, Color valueColor)
    {
        x = valueX;
        y = valueY;
        y2 = valueY2;
        color = valueColor;

        if (y2 - y >= 0)
            h = y2 - y;
        else
            h = y - y2;

        if (h == 0)
            h = 1;

        rect.setSize(Vector2f(1, h));
        rect.setFillColor(color);
        rect.setPosition(x, y);
    }
};

vector <string> params;



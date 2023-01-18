#include "Header.h"

int main()
{
    string line;
    ifstream input("input.txt");

    if (!input.is_open())
    {
        cout << "No file 'input.txt' found!\n";
    }
    else
    {
        while (!input.eof())
        {
            input >> line;
            params.push_back(line);
        }
    }

    input.close();

    float sceneX1 = stof(params.at(0));
    float sceneX2 = stof(params.at(2));
    float sceneY1 = stof(params.at(1));
    float sceneY2 = stof(params.at(3));

    RenderWindow window(VideoMode(sceneX2 - sceneX1, sceneY2 - sceneY1), "window");

    RenderTexture rt{};
    rt.create(sceneX2 - sceneX1, sceneY2 - sceneY1);
    rt.clear(Color::White);

    Point p(stof(params.at(5)), stof(params.at(6)), Color::Blue);
    Rectangle r(stof(params.at(8)), stof(params.at(10)), stof(params.at(9)), stof(params.at(11)), Color::Green);
    HLine h(stof(params.at(13)), stof(params.at(15)), stof(params.at(14)), Color::Yellow);
    VLine v(stof(params.at(19)), stof(params.at(17)), stof(params.at(18)), Color::Red);

    if (p.getX() >= sceneX1 && p.getX() <= sceneX2 && p.getY() >= sceneY1 && p.getY() <= sceneY2)
    {
        p.point.setPosition(stof(params.at(5)) - sceneX1, stof(params.at(6)) - sceneY1);
    }

    if (r.getX() <= sceneX2 && r.getX2() >= sceneX1 && r.getY() <= sceneY2 && r.getY2() >= sceneY1)
    {
        r.rect.setPosition(r.getX()-sceneX1,r.getY2()-sceneY1);
    }

    if (h.getX() <= sceneX2 && h.getX2() >= sceneX1 && h.getY() >= sceneY1 && h.getY() <= sceneY2)
    {
        h.rect.setPosition(h.getX() - sceneX1, h.getY() - sceneY1);
    }

    if (v.getX() >= sceneX1 && v.getX() <= sceneX2 && v.getY() <= sceneY2 && v.getY2() >= sceneY1)
    {
        v.rect.setPosition(v.getX() - sceneX1, v.getY() - sceneY1);
    }

    rt.draw(p.point);
    rt.draw(r.rect);
    rt.draw(h.rect);
    rt.draw(v.rect);
    rt.display();

    Image im{ rt.getTexture().copyToImage() };
    im.saveToFile("res.bmp");

    while (window.isOpen())
    {
        Event event;
        while (window.pollEvent(event))
        {
            if (event.type == Event::Closed)
                window.close();
        }

        window.clear();
        window.draw(p.point);
        window.draw(r.rect);
        window.draw(h.rect);
        window.draw(v.rect);
        window.display();

    }

}
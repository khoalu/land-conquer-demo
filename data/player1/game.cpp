#include <iostream>
#include <fstream>
#include <algorithm>
#include <vector>

const int MAXN = 50;
const int MAX_ZONE = 10;

struct Zone {
    int r,c,w,h,m;
    Zone() {}
    Zone(int r, int c, int w, int h, int m): r(r), c(c), w(w), h(h), m(m) {}
};

struct Action {
    int r, c;
    Action() {}
    Action(int r, int c): r(r), c(c) {}
};

int turn, pColor, size, moves, drills;
int color[MAXN][MAXN], obstacle[MAXN][MAXN], point[MAXN][MAXN];

int nZone;
Zone zones[MAX_ZONE];

std::vector<Action> globalActions;

void readInput()
{
    // read content from file GAME.INP
    std::ifstream ifs("GAME.INP");
    ifs >> turn >> pColor >> size >> moves >> drills;

    for(int i = 0; i < size; i++)
    {
        for(int j = 0; j < size; j++)
        {
            ifs >> color[i][j];
        }
    }

    for(int i = 0; i < size; i++)
    {
        for(int j = 0; j < size; j++)
        {
            ifs >> obstacle[i][j];
        }
    }

    for(int i = 0; i < size; i++)
    {
        for(int j = 0; j < size; j++)
        {
            ifs >> point[i][j];
        }
    }

    ifs >> nZone;
    for(int i = 0; i < nZone; i++)
    {
        ifs >> zones[i].r >> zones[i].c >> zones[i].w >> zones[i].h >> zones[i].m;
    }
    ifs.close();
}

void writeOutput()
{
    // write content from vector globalActions to file GAME.OUT
    std::ofstream ofs("GAME.OUT");
    for(auto& action: globalActions) ofs << action.r << " " << action.c << '\n';
    ofs.close();
}


bool inside(int r, int c)
{
    return 0 <= r && r < size && 0 <= c && c < size;
}
const int td[] = {0, -1, 0, 1};
const int tc[] = {1, 0, -1, 0};
void process()
{
    // calculate action and push it to globalActions vector
    for(int i = 0; i < size; i++)
    {
        for(int j = 0; j < size; j++)
        {
            if (color[i][j] == 2)
            {
                for(int k = 0; k < 4; k++)
                {
                    int nr = i + td[k];
                    int nc = j + tc[k];
                    if (inside(nr, nc) &&  color[nr][nc] == pColor)
                    {
                        if (obstacle[i][j] == 0 || 
                            obstacle[i][j] == 1 || 
                            (obstacle[i][j] == 2 && drills > 0))
                        globalActions.push_back(Action(i, j));
                    }
                }
            }
        }
    }
    std::random_shuffle(globalActions.begin(), globalActions.end());
    if (globalActions.size() > moves)
        globalActions.resize(moves);
}

int main()
{
    // while (true) {}
    readInput();
    process();
    writeOutput();
    return 0;
}
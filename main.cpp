#include <iostream>
#include <vector>
#include <set>
#include <algorithm>
using namespace std;

class Game {
private:
    int const N = 10, WS = 5;

    vector<vector<int>> board;
    vector<int> hs; // lowest position per col we can't use

    // update as desired
    void rotate_policy(int move_number) {
        if( move_number % 6 == 5 ) rotate_board();
    }

    void apply_gravity() {
        hs.assign(N, N);

        for(int r=N-1; r>=0; --r) {
            for(int c=0; c<N; ++c) {
                if( !board[r][c] || r == --hs[c] ) continue;
                swap(board[hs[c]][c], board[r][c]);
            }
        }
    }

    // does one 90 degree clockwise rotation
    void rotate_board() {
        for(int r=0; r<(N+1)/2; ++r) {
            for(int c=0; c<N/2; ++c) {

                int cr=r, cc=c;
                for(int i=0; i<3; ++i) {
                    int nr = N-1-cc, nc = cr;
                    swap(board[cr][cc], board[nr][nc]);
                    cr = nr, cc = nc;
                }

            }
        }

        apply_gravity();
    }

    // cant naievely do this quickly because the rotate kind of messes with stuff
    set<int> get_winners() {
        set<int> winners;

        for(int r=0; r<N; ++r) for(int c=0; c<N; ++c) {
            if( !board[r][c] ) continue;

            int cr, cc, cnt;

            cr = r, cc = c, cnt = 0;
            while( cc < N && board[cr][cc] == board[r][c] ) ++cc, ++cnt;
            if( cnt >= WS ) winners.insert( board[r][c] );

            int dr = 1;
            for(int dc=-1; dc<=1; ++dc) {
                cr = r, cc = c, cnt = 0;
                while( 0 <= cc && cc < N && cr < N && board[cr][cc] == board[r][c] ) {
                    cr += dr, cc += dc, ++cnt;
                }

                if( cnt >= WS ) winners.insert( board[r][c] );
            }
        }

        return winners;
    }

    bool make_move(int c, int v) {
        if( v == 0 || c < 0 || c >= N || hs[c] <= 0 ) return false;
        board[--hs[c]][c] = v;
        return true;
    }

    void print_board() {
        for(auto &row : board) {
            for(auto &v : row) {
                cout << v << ' ';
            }

            cout << '\n';
        }
    }

public:
    Game() { }

    void start_game() {
        board.assign(N, vector<int>(N, 0)), hs.assign(N, N);

        int next_player = 1, move_number = 0;

        set<int> winners;
        while( !( winners = get_winners() ).size() ) {

            {   // Print Prompt
                cout << "Current Board:" << "\n\n";
                print_board();
                cout << "\n\n";

                cout << "Player " << next_player << "s turn" << "\n\n";
            }

            {   // read in next move to make and make move
                int chosen_col, cnt=0;

                do {
                    cout << "Choose a valid column";
                    for(int _=0; _<cnt; ++_) cout << '!';
                    cout << '\n';
                    ++cnt;

                    cin >> chosen_col;
                    cout << '\n';

                } while( !make_move(chosen_col, next_player) );
            }

            rotate_policy( move_number++ );

            next_player = (next_player&1) + 1;
        }

        {   // Final Board State
            cout << "Final Board:" << "\n\n";
            print_board();
            cout << "\n\n";
        }

        if( winners.size() ) {
            cout << "Winners: ";
            for(auto v : winners) cout << v << ' ';
            cout << "\n\n";
        } else {
            cout << "DRAW :(" << "\n\n";
        }
    }

    vector<vector<int>> get_board() {
        return board;
    }
};


int main() {
    Game my_game = Game();
    my_game.start_game();
    return 0;
}

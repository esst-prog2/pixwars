"""Start PixWars: one human on the keyboard against one bot.

    uv run python main.py

Controls
    A / D or arrows   move          SPACE / W   jump
    J                 attack        K           place a block
    L                 break         1-4         buy in your shop zone,
                                                otherwise select a slot
    ESC               quit
"""

from pixwars_client import run

if __name__ == "__main__":
    run()

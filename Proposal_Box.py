from tkinter import *

class Proposal_Box:
    def __init__(self, canvas, text, pos, color="white") -> None:
        tag = f"movable{id(self)}"
        self.rect = canvas.create_rectangle(
            pos[0], pos[2], pos[1], pos[3],
            outline="#fb0",
            fill=color,
            tag=(tag, )
        )
        self.text = canvas.create_text((pos[0]+pos[1])//2 ,(pos[2]+pos[3])//2, text=text, tag=(tag,))
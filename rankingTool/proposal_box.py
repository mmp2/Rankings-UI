from tkinter import *

class Proposal_Box:
    def __init__(self, canvas, reviewer, pos, prop=None, color="white", dash=(), outl="white", width=3) -> None:
        self.reviewer = reviewer
        self.prop = prop
        self.pos = pos
        self.canvas = canvas
        if prop == None:
            text = reviewer
            self.rectag = (f"{reviewer}", )
            self.textag = (f"{reviewer}text", )
        else:
            self.rectag = (f"{reviewer}", f"{prop}")
            self.textag = (f"{reviewer}text", f"{prop}text")
            text = prop
        self.rect = self.canvas.create_rectangle(
            pos[0], pos[2], pos[1], pos[3],
            fill=color,
            dash=dash,
            #dashoff = 3,
            #stipple='gray25',
            outline=outl,
            width=width,
            tag=self.rectag
        )
        self.text = self.canvas.create_text((pos[0]+pos[1])//2 ,(pos[2]+pos[3])//2, text=text, tag=self.textag)
    
    def get_reviewer_prop(self):
        return (self.reviewer, self.prop)

    def get_pos(self):
        return self.pos[0], self.pos[2], self.pos[1], self.pos[3],

    def update_rect(self, color=None, dash=None, outl=None, width=None, state=None):
        self.canvas.itemconfig(self.rect, fill=color, dash=dash, outline=outl, width=width, state=state)
        self.canvas.update()
    
    def update_text(self,  state=None):
        self.canvas.itemconfig(self.text, state=state)
        self.canvas.update()
import tkinter as tk
import tkinter.font as tkFont

class App:
    def __init__(self, root):
        #setting title
        root.title("undefined")
        #setting window size
        width=600
        height=500
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        time_text=tk.Label(root)
        ft = tkFont.Font(family='Times',size=18)
        time_text["font"] = ft
        time_text["fg"] = "#333333"
        time_text["justify"] = "center"
        time_text["text"] = "Time:"
        time_text.place(x=20,y=20,width=70,height=25)

        Temperature_text=tk.Label(root)
        ft = tkFont.Font(family='Times',size=18)
        Temperature_text["font"] = ft
        Temperature_text["fg"] = "#333333"
        Temperature_text["justify"] = "center"
        Temperature_text["text"] = "Temp="
        Temperature_text.place(x=310,y=20,width=70,height=25)

        Temperature_value=tk.Label(root)
        ft = tkFont.Font(family='Times',size=18)
        Temperature_value["font"] = ft
        Temperature_value["fg"] = "#333333"
        Temperature_value["justify"] = "center"
        Temperature_value["text"] = "40 C"
        Temperature_value.place(x=380,y=20,width=70,height=25)

        time_value=tk.Label(root)
        ft = tkFont.Font(family='Times',size=18)
        time_value["font"] = ft
        time_value["fg"] = "#333333"
        time_value["justify"] = "center"
        time_value["text"] = "2021-01-29 19:45:35"
        time_value.place(x=80,y=20,width=216,height=30)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

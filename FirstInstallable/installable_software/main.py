import tkinter as tk

def main():
    window = tk.Tk()
    window.title("My First Installable Software")
    window.geometry("400x200")

    label = tk.Label(window, text="This is my first installable software", font=("Arial", 16))
    label.pack(expand=True)

    window.mainloop()

if __name__ == "__main__":
    main()

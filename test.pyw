import tkinter as tk

def show_custom_messagebox():
    custom_messagebox = tk.Toplevel()
    custom_messagebox.title("Custom Messagebox")

    text_content = "This is a custom messagebox with non-editable text."
    text_widget = tk.Text(custom_messagebox, wrap=tk.WORD, width=40)
    text_widget.insert(tk.END, text_content)
    
    # Set the state of the Text widget to "disabled"
    text_widget.configure(state="disabled")
    text_widget.pack()

    ok_button = tk.Button(custom_messagebox, text="OK", command=custom_messagebox.destroy)
    ok_button.pack()

    # Calculate the number of lines in the text
    num_lines = text_widget.get("1.0", "end-1c").count("\n") + 1

    # Calculate the required width based on the text content
    text_widget.update_idletasks()
    text_widget_width = text_widget.winfo_reqwidth()

    # Calculate the required height based on the number of lines and text content
    text_widget_height = text_widget.winfo_reqheight()

    # Get the screen width and height
    screen_width = custom_messagebox.winfo_screenwidth()
    screen_height = custom_messagebox.winfo_screenheight()

    # Calculate the x and y positions to center the window
    x = (screen_width - text_widget_width) // 2
    y = (screen_height - text_widget_height) // 2

    # Set the window size and position in the center
    custom_messagebox.geometry(f"{text_widget_width}x{text_widget_height}+{x}+{y}")

# Create the main tkinter window
root = tk.Tk()

# Create a button to trigger the custom messagebox
button = tk.Button(root, text="Show Custom Messagebox", command=show_custom_messagebox)
button.pack()

root.mainloop()

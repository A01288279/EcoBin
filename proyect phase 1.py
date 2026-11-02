import os
import pandas as pd
import tkinter as tk
from datetime import datetime

#Folder where this .py file is located (so it can find the CSV files from anywhere).
base_folder = os.path.dirname(os.path.abspath(__file__))
questions_file = os.path.join(base_folder, "preguntas_en.csv")
results_file = os.path.join(base_folder, "resultados.csv")

def load_questions(file_path):
    table = pd.read_csv(file_path, dtype=str)
    questions = {}
    for index, row in table.iterrows():
        #pd.isna is used to ignore missing values if the answer is neither "Yes" nor "No".
        if pd.isna(row["si"]) or pd.isna(row["no"]):
            continue
        questions[row["id"]] = {
            "question": row["pregunta"],
            "yes": row["si"],
            "no": row["no"]
        }
    return questions


def save_results(results):
    new_results = pd.DataFrame([{"date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                  "result": results
                                    }])
    # mode="a" is used to append to the end of the file without deleting the existing content.
    new_results.to_csv(results_file, mode="a", index=False, header=not os.path.exists(results_file))

def get_bin(text):
    # Returns only the bin name, ignoring the explanation
    for bin_name in ["GREEN", "BLUE", "YELLOW", "GRAY"]:
        if bin_name in text:
            return bin_name
    return "SPECIAL"

def calculate_percentage(result):
    if not os.path.exists(results_file):
        return 100.0

    data = pd.read_csv(results_file)
    total_tests = len(data)
    if total_tests == 0:
        return 100.0
    bins = data["result"].apply(get_bin)
    recycling_count = (bins == get_bin(result)).sum()
    percentage = (recycling_count / total_tests) * 100
    return percentage

# The class is responsible for displaying/drawing the window and handling how the program works.
class EcoBin:
    def __init__(self, window, questions):
        self.window = window
        self.questions = questions
        self.current_question_id = "1" #To start with the first question.

        window.title("EcoBin ♻")
        window_width = 600
        window_height = 400
        window.geometry(f"{window_width}x{window_height}")
        window.configure(bg="#e8f5e9") #To set a background color for the window

        #For the font of the window
        tk.Label(window, text="EcoBin ♻", font=("Arial", 26, "bold"), bg="#e8f5e9", fg="#2e7d32").pack(pady=20)

        self.question_label = tk.Label(window, text="", font=("Arial", 16), wraplength=480, bg="#e8f5e9")
        self.question_label.pack(pady=20)

        self.frame_buttons = tk.Frame(window, bg="#e8f5e9")
        self.frame_buttons.pack()

        self.button_yes = tk.Button(self.frame_buttons, text="Yes", 
                                    font=("Arial", 14), bg="#81c784", 
                                    command=lambda: self.respond("yes"))
        
        self.button_no = tk.Button(self.frame_buttons, text="No", 
                                   font=("Arial", 14), bg="#e57373", 
                                   command=lambda: self.respond("no"))

        self.button_other = tk.Button(self.frame_buttons, text="Do another test",
                                      font=("Arial", 14), bg="#64b5f6",
                                        command=self.restart_test)
        self.restart_test()


    def restart_test(self):
        self.current_question_id = "1"
        self.button_other.grid_remove()  # Hide the "Do another test" button.
        self.button_yes.grid(row=0, column=0, padx=10)
        self.button_no.grid(row=0, column=1, padx=10) #to tell where in the window the button will be placed
        self.show_question()

    def show_question(self):
        self.question_label.config(text=self.questions[self.current_question_id]["question"], 
                                   font=("Arial", 16), wraplength=480, bg="#e8f5e9")

    def respond(self, answer):
        nextq = self.questions[self.current_question_id][answer]
        #If it starts with "R", it means it's a final answer; otherwise, it's another question.
        if nextq.startswith("R") and len(nextq) > 2:
            self.show_result(nextq[2:])  # Show the result without the "R:"
        else:
            self.current_question_id = nextq #go to the next question
            self.show_question()

    
    def show_result(self, result):
        # Saves the results in the CSV file.
        save_results(result)

        # Calculates the percentage of times this result has been obtained
        percentage = calculate_percentage(result)

        # Displays the result in the window and hides the answer buttons
        self.question_label.config(
            text=f"Throw it in:\n\n{result}\n\n"
                 f"This bin represents {percentage:.1f}% of your results.",
            fg="#1b5e20"
        )

        self.button_yes.grid_remove()
        self.button_no.grid_remove()
        self.button_other.grid(row=0, column=0)



    
def main():
    #Loads the questions and opens the window.
    #If the questions file doesn't exist, the program closes.
    if not os.path.exists(questions_file):
        print(f"Error: The file '{questions_file}' does not exist.")
        return

    questions = load_questions(questions_file)

    window = tk.Tk()
    EcoBin(window, questions)
    window.mainloop() #Keeps the window open until the user closes it.

if __name__ == "__main__":
    main()
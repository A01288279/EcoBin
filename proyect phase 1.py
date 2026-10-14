import os
import pandas as pd
import tkinter as tk
from datetime import datetime

# Carpeta donde está este archivo .py (así encuentra los CSV desde cualquier lugar)
base_folder = os.path.dirname(os.path.abspath(__file__))
questions_file = os.path.join(base_folder, "preguntas_en.csv")
results_file = os.path.join(base_folder, "resultados.csv")

def load_questions(file_path):
    table = pd.read_csv(file_path, dtype=str)
    questions = {}
    for index, row in table.iterrows():
        #pd.isna es por si le falta el "si" o el "no" se ignora
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
    # mode="a" es para agregar al final del archivo sin borrar lo que ya estaba
    new_results.to_csv(results_file, mode="a", index=False, header=not os.path.exists(results_file))

def calculate_percentage(result):
    if not os.path.exists(results_file):
        return 100.0

    data = pd.read_csv(results_file)
    total_tests = len(data)
    if total_tests == 0:
        return 100.0
    recycling_count = (data["result"] == result).sum()
    percentage = (recycling_count / total_tests) * 100
    return percentage

# La class se encarga demostrar/dibujar la ventana y manejar el funcionamiento del programa.
class EcoBin:
    def __init__(self, window, questions):
        self.window = window
        self.questions = questions
        self.current_question_id = "1" # para empezar con la primera pregunta

        window.title("EcoBin ♻")
        window_width = 600
        window_height = 400
        window.geometry(f"{window_width}x{window_height}")
        window.configure(bg="#e8f5e9") #para ponerle un color de fondo a la ventana

        #para la tipografía de la ventana
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
        self.button_other.grid_remove()  # Ocultar el botón "Do another test"
        self.button_yes.grid(row=0, column=0, padx=10)
        self.button_no.grid(row=0, column=1, padx=10) #para decirle donde en la window se va a poner el boton
        self.show_question()

    def show_question(self):
        self.question_label.config(text=self.questions[self.current_question_id]["question"], 
                                   font=("Arial", 16), wraplength=480, bg="#e8f5e9")

    def respond(self, answer):
        nextq = self.questions[self.current_question_id][answer]
        #si empieza con R es porque es una respuesta final, si no es otra pregunta
        if nextq.startswith("R") and len(nextq) > 2:
            self.show_result(nextq[2:])  # Mostrar el resultado sin la "R:"
        else:
            self.current_question_id = nextq #pasa a la siguiente pregunta
            self.show_question()

    
    def show_result(self, result):
        # Guarda los resultadoes en el archivo CSV
        save_results(result)

        # Calcula el porcentaje de veces que se ha obtenido este resultado
        percentage = calculate_percentage(result)

        # muestra el resultado en la ventana y oculta los botones de respuesta
        self.question_label.config(
            text=f"Throw it in:\n\n{result}\n\n"
                 f"This bin represents {percentage:.1f}% of your results.",
            fg="#1b5e20"
        )

        self.button_yes.grid_remove()
        self.button_no.grid_remove()
        self.button_other.grid(row=0, column=0)



    
def main():
    #carga las preguntas y abre la window
    #si el archivo de las preguntas no existe, se cierra el programa
    if not os.path.exists(questions_file):
        print(f"Error: The file '{questions_file}' does not exist.")
        return

    questions = load_questions(questions_file)

    window = tk.Tk()
    EcoBin(window, questions)
    window.mainloop() #mantiene la ventana abierta hasta que el usuario la cierre

if __name__ == "__main__":
    main()
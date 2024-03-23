import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk

import random
import logging

from .communication import CANDY1, CANDY2, request_candy, RESPONSE_SUCCESS, RESPONSE_TIMEOUT
from .question_bank import next_question, categories

COUNTDOWN_STEP = 1500

def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    
def view_incorrect_answer(frame, redirect_func):
    clear_frame(frame)

    incorrect_label = tk.Label(frame, text="Atsakymas neteisingas. Bandykite dar kartą.", font=("Rando", 30))
    incorrect_label.pack(pady=20)

    frame.after(2000, lambda: redirect_func(frame))

def view_answer_question(frame, category):
    clear_frame(frame)

    question_data = next_question(category)

    question_label = tk.Label(frame, text=question_data["question"], font=("Rando", 20))
    question_label.pack(pady=20)

    answers = [question_data["correct_answer"]] + question_data["incorrect_answers"]
    random.shuffle(answers)

    def process_answer(answer):
        if answer == question_data["correct_answer"]:
            view_pick_candy(frame)
        else:
            view_incorrect_answer(frame, redirect_func=view_pick_quiz_category)

    for answer in answers:
        answer_button = tk.Button(frame, command=lambda answer=answer: process_answer(answer),
                                  text=answer, font=("Rando", 25), width=100, height=2, borderwidth=0, relief="solid")
        answer_button.pack(pady=5)

def view_take_candy(frame, candy):
    clear_frame(frame)

    text_label = tk.Label(frame, text="Gaudykite saldainį!", font=("Rando", 25))
    text_label.pack(pady=20)

    countdown_label = tk.Label(frame, font=("Rando", 25))
    countdown_label.pack()

    counting_task = None

    def after_given_candy(response):
        nonlocal counting_task

        # Cancel counting task
        if counting_task is not None:
            frame.after_cancel(counting_task)
            counting_task = None

        if response == RESPONSE_SUCCESS:
            view_pick_quiz_category(frame)
        elif response == RESPONSE_TIMEOUT:
            timeout_message(frame)

    def countdown(count):
        nonlocal counting_task
        countdown_label['text'] = count

        if count > 1:
            counting_task = frame.after(COUNTDOWN_STEP, countdown, count-1)
        else:
            counting_task = None
            timeout_message(frame)

    request_candy(candy, after_given_candy)
    countdown(20)


def view_pick_candy(frame):
    clear_frame(frame)

    answer_label = tk.Label(frame, text="Sveikiname! Atsakėte teisingai.", font=("Rando", 30))
    answer_label.pack(pady=20)

    question_label = tk.Label(frame, text="Kokio saldainio norite?", font=("Rando", 30))
    question_label.pack(pady=20)

    candy1_button = tk.Button(frame, command=lambda: view_take_candy(frame, CANDY1), 
                               width=250, height=250, image=candy1_img, borderwidth=0, relief="solid")
    candy1_button.pack(side=tk.LEFT, padx=10)

    candy2_button = tk.Button(frame, command=lambda: view_take_candy(frame, CANDY2), 
                               width=250, height=250, image=candy2_img, borderwidth=0, relief="solid")
    candy2_button.pack(side=tk.RIGHT, padx=10)

def view_pick_quiz_category(frame):
    clear_frame(frame)

    category_label = tk.Label(frame, text="Pasirinkite kategoriją", font=("Rando", 35))
    category_label.pack(pady=20)

    for category in categories.keys():
        category_button = tk.Button(frame, command=lambda category=category: view_answer_question(frame, category), 
                                    text=category, font=("Rando", 25), width=15, height=2, borderwidth=0, relief="solid")
        category_button.pack(pady=10)

# Loads used images and set up their sizes
def load_logos():
    global ku_img, conexus_img, fondas_img, candy1_img, candy2_img

    # University logos
    ku_img = Image.open("img/ku.png")
    ku_img = ku_img.resize((250, 80))
    ku_img = ImageTk.PhotoImage(ku_img)

    conexus_img = Image.open("img/conexus.png")
    conexus_img = conexus_img.resize((120, 50))
    conexus_img = ImageTk.PhotoImage(conexus_img)

    fondas_img = Image.open("img/fondas.png")
    fondas_img = fondas_img.resize((140, 45))
    fondas_img = ImageTk.PhotoImage(fondas_img)

    # Candy logos
    candy1_img = Image.open("img/candy1.png")
    candy1_img = candy1_img.resize((250, 250))
    candy1_img = ImageTk.PhotoImage(candy1_img)

    candy2_img = Image.open("img/candy2.png")
    candy2_img = candy2_img.resize((250, 250))
    candy2_img = ImageTk.PhotoImage(candy2_img)

def timeout_message(frame):
    clear_frame(frame)
    
    timeout_label = tk.Label(frame, text="Laikas baigėsi! Bandykite dar kartą.", font=("Rando", 30))
    timeout_label.pack(pady=20)

    frame.after(5000, lambda: view_pick_quiz_category(frame))


def setup_window():
    logging.info("Creating window...")

    # Setup window
    root = tk.Tk()
    root.title("Saldainiai")

    root.attributes('-fullscreen', True)

    # For raspberry
    root.attributes('-type', 'splash')

    # Load logos used in the application
    load_logos()

    # Setup header of the window
    frame_header = tk.Frame(root)
    frame_header.pack(expand=True)

    # Display logos in the header
    conexus_logo = tk.Label(frame_header, height=120, image=conexus_img, borderwidth=0, relief="solid")
    conexus_logo.grid(row = 0, column = 0, padx=10)

    ku_logo = tk.Label(frame_header, height=120, image=ku_img, borderwidth=0, relief="solid")
    ku_logo.grid(row = 0, column = 1, padx=10)

    fondas_logo = tk.Label(frame_header, height=120, image=fondas_img, borderwidth=0, relief="solid")
    fondas_logo.grid(row = 0, column = 2, padx=10)

    def on_exit():
        result = messagebox.askquestion("Exit", "Ar tikrai norite išeiti?")
        if result == "yes":
            logging.info('Destroying window...')
            root.destroy()

    # Display exit button
    exit_button = tk.Button(root, text="X", font=("Rando", 20), command=on_exit)
    exit_button.place(relx=1.0, x=-10, y=10, anchor="ne")

    # Setup main content of window
    frame_content = tk.Frame(root)
    frame_content.pack(expand=True)

    # Display question frame first
    view_pick_quiz_category(frame_content)

    # Main loop
    root.mainloop()


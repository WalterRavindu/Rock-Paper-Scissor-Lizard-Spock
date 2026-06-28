import pyfirmata
import time  #import inbuilt time module
import numpy as np
import tkinter as tk #import GUI module 

from threading import Thread

# Setting the port Arduino is connected to
board = pyfirmata.Arduino('COM5')

# Start an iterator thread so that serial buffer does not overflow
it = pyfirmata.util.Iterator(board)
it.start()

# Configure the analog pin
analog_pin1 = board.get_pin('a:0:i') #Rock - button1
analog_pin2 = board.get_pin('a:1:i') #Paper - button2
analog_pin3 = board.get_pin('a:2:i') #Scissor - button3
analog_pin4 = board.get_pin('a:3:i') #Lizard - button4
analog_pin5 = board.get_pin('a:4:i') #Spock - button5
reset_pin   = board.get_pin('a:5:i') #Reset - button_reset

#Configuring digital pins
led_player_marks_1 = board.get_pin('d:2:o')
led_player_marks_2 = board.get_pin('d:3:o')
led_player_marks_3 = board.get_pin('d:4:o')

led_computer_marks_1 = board.get_pin('d:5:o')
led_computer_marks_2 = board.get_pin('d:6:o')
led_computer_marks_3 = board.get_pin('d:7:o')

led_computer_choice_1 = board.get_pin('d:8:o')
led_computer_choice_2 = board.get_pin('d:9:o')
led_computer_choice_3 = board.get_pin('d:10:o')

led_indicator = board.get_pin('d:11:o')

buzzer = board.get_pin('d:12:o')

# Allow time for the analog pin to initialize
time.sleep(1)

# Initializing player choice
player_choice = 0
computer_choice = 0

# Initializing marks
player_marks = 0
computer_marks = 0

# Create GUI
root = tk.Tk()
root.title("Rock Paper Scissor Lizard Spock")

# Heading label
heading_label = tk.Label(root, text="Rock Paper Scissor Lizard Spock", font=("Helvetica", 50, "bold"))
heading_labe2 = tk.Label(root, text="Group D8", font=("Helvetica", 45, "bold"),fg="red")
heading_label.pack(pady=10)
heading_labe2.pack(pady=10)

#Labels in GUI
player_label = tk.Label(root, text="Player Marks: 0",font=("Helvetica", 32))
player_label.pack()

computer_label = tk.Label(root, text="Computer Marks: 0",font=("Helvetica", 32))
computer_label.pack()

status_label = tk.Label(root, text="",font=("Helvetica", 32))
status_label.pack()

def show_marks(player_marks, computer_marks):
    '''
    This is a function to show marks of player and computer by LEDs as binary
    '''
    
    player_label.config(text=f"Player Marks: {player_marks}")#updating labels
    computer_label.config(text=f"Computer Marks: {computer_marks}")
    
    decimal_player_marks = player_marks
    binary_player_marks = format(decimal_player_marks, 'b').zfill(3)#converting to binary

    decimal_computer_marks = computer_marks
    binary_computer_marks = format(decimal_computer_marks, 'b').zfill(3)

    led_player_marks_1.write(int(binary_player_marks[0]))
    led_player_marks_2.write(int(binary_player_marks[1]))
    led_player_marks_3.write(int(binary_player_marks[2]))

    led_computer_marks_1.write(int(binary_computer_marks[0]))
    led_computer_marks_2.write(int(binary_computer_marks[1]))
    led_computer_marks_3.write(int(binary_computer_marks[2]))

def update_status(text):
    '''
    This function is to update information in labels
    '''
    status_label.config(text=text)

def choice_leds():
    binary_computer_choice = format(computer_choice, 'b').zfill(3)
    led_computer_choice_1.write(int(binary_computer_choice[0]))
    led_computer_choice_2.write(int(binary_computer_choice[1]))
    led_computer_choice_3.write(int(binary_computer_choice[2]))
    '''
    Choices-
    1. Rock - 001
    2. Paper - 010
    3. Scissor - 011
    4. Lizard - 100
    5. Spock - 101
    '''

def off_leds():
    '''
    This is a function to turn off all LEDs
    '''    
    led_player_marks_1.write(0)
    led_player_marks_2.write(0)
    led_player_marks_3.write(0)

    led_computer_marks_1.write(0)
    led_computer_marks_2.write(0)
    led_computer_marks_3.write(0)

    led_computer_choice_1.write(0)
    led_computer_choice_2.write(0)
    led_computer_choice_3.write(0)

    led_indicator.write(0)

def show_end():
    '''
    To show end of game by blinking computer choice LEDs
    '''
    for i in range(5):
        off_leds()         

        time.sleep(0.5)

        led_computer_choice_1.write(1)
        led_computer_choice_2.write(1)
        led_computer_choice_3.write(1)

        time.sleep(0.5)

def player_blink():
    '''
    If player wins, player marks LEDs blink
    '''
    for i in range(5):
        led_player_marks_1.write(0)
        led_player_marks_2.write(0)
        led_player_marks_3.write(0)
        time.sleep(0.5)
        led_player_marks_1.write(1)
        led_player_marks_2.write(1)
        led_player_marks_3.write(1)
        time.sleep(0.5)

def computer_blink():
    '''
    If computer wins, computer marks LEDs blink
    '''
    for i in range(5):
        led_computer_marks_1.write(0)
        led_computer_marks_2.write(0)
        led_computer_marks_3.write(0)
        time.sleep(0.5)
        led_computer_marks_1.write(1)
        led_computer_marks_2.write(1)
        led_computer_marks_3.write(1)
        time.sleep(0.5)

def read_button_state(pin):
    '''
    This function is to read analog inputs and convert to digital
    '''
    value = pin.read()
    if value is None:
        return None
    else:
        return round(value)  # Converting the reading to 0 or 1

def beep(pin, duration, volume):
    buzzer.write(1)  # Turn the buzzer on
    buzzer.write(volume)  # Adjust the volume using PWM
    time.sleep(duration)  # Wait for the specified duration
    buzzer.write(0)  # Turn the buzzer off

def game():
    global player_marks, computer_marks, computer_choice

    player_marks = 0
    computer_marks = 0

    '''
    This break_outer is used to break the for loop(handling rounds)
    when reset button is pressed in while loop.
    '''


    break_outer = False

    beep(12,0.2,1)
    time.sleep(0.3)
    beep(12,0.1,1)
    time.sleep(0.3)
    beep(12,0.1,1)

    for round_number in range(1, 8):
        
        button_reset_pressed = False
        player_choice = 0

        time.sleep(2)

        button1_pressed = False
        button2_pressed = False
        button3_pressed = False
        button4_pressed = False
        button5_pressed = False

        update_status(f"---- Round {round_number} ----")
        beep(12, 0.1, 1)
        start_time = time.time()

        while True:
            current_time = time.time()
            elapsed_time = current_time - start_time
            led_indicator.write(1)

            if elapsed_time > 5:
                led_indicator.write(0)
                update_status("Your time is over")
                
                beep(12,0.1,1)
                time.sleep(0.1)
                beep(12,0.1,1)         
                
                computer_marks += 1
                break

            if not button_reset_pressed:
                button_reset_state = read_button_state(reset_pin)
                if button_reset_state == 1:
                    button_reset_pressed = True
                    update_status("Game reset! Press reset button to play again")
                    off_leds()
                    break_outer = True
                    break

            if not button1_pressed:
                button1_state = read_button_state(analog_pin1)
                if button1_state == 1:
                    button1_pressed = True
                    update_status("Your choice : Rock")
                    player_choice = 1

            if not button2_pressed:
                button2_state = read_button_state(analog_pin2)
                if button2_state == 1:
                    button2_pressed = True
                    update_status("Your choice : Paper")
                    player_choice = 2

            if not button3_pressed:
                button3_state = read_button_state(analog_pin3)
                if button3_state == 1:
                    button3_pressed = True
                    update_status("Your choice : Scissor")
                    player_choice = 3

            if not button4_pressed:
                button4_state = read_button_state(analog_pin4)
                if button4_state == 1:
                    button4_pressed = True
                    update_status("Your choice : Lizard")
                    player_choice = 4

            if not button5_pressed:
                button5_state = read_button_state(analog_pin5)
                if button5_state == 1:
                    button5_pressed = True
                    update_status("Your choice : Spock")
                    player_choice = 5

            if button1_pressed or button2_pressed or button3_pressed or button4_pressed or button5_pressed:
                led_indicator.write(0)
                break

            time.sleep(0.1)

        if break_outer:
            break
        '''
        For loop is broken when the while loop is broken by pressing reset button
        '''

        #Generate computer choice
        computer_choice = np.random.randint(1, 6)

        time.sleep(0.5)

        #Displaying computer choice
        computer_choice_list = ['(1) Rock', '(2) Paper', '(3) Scissor', '(4) Lizard', '(5) Spock']
        update_status(f'Computer choice : {computer_choice_list[computer_choice-1]}')
        choice_leds()
        time.sleep(2)

        #Comparing choices

        if computer_choice == 1:
            if player_choice == 1:
                update_status('Tie - no marks for anybody')
                    
            elif player_choice == 2:
                player_marks+=1

            elif player_choice == 3:
                computer_marks+=1

            elif player_choice == 4:
                computer_marks+=1

            elif player_choice == 5:
                player_marks+=1

        elif computer_choice == 2:
            if player_choice == 2:
                update_status('Tie - no marks for anybody')
                    
            elif player_choice == 1:
                computer_marks+=1

            elif player_choice == 3:
                player_marks+=1

            elif player_choice == 4:
                player_marks+=1

            elif player_choice == 5:
                computer_marks+=1
                

        elif computer_choice == 3:
            if player_choice == 3:
                update_status('Tie - no marks for anybody')
                    
            elif player_choice == 1:
                player_marks+=1

            elif player_choice == 2:
                computer_marks+=1

            elif player_choice == 4:
                computer_marks+=1

            elif player_choice == 5:
                player_marks+=1
                

        elif computer_choice == 4:
            if player_choice == 4:
                update_status('Tie - no marks for anybody')
                    
            elif player_choice == 1:
                player_marks+=1

            elif player_choice == 2:
                computer_marks+=1

            elif player_choice == 3:
                player_marks+=1

            elif player_choice == 5:
                computer_marks+=1
                

        elif computer_choice == 5:
            if player_choice == 5:
                update_status('Tie - no marks for anybody')
                    
            elif player_choice == 1:
                computer_marks+=1

            elif player_choice == 2:
                player_marks+=1

            elif player_choice == 3:
                computer_marks+=1

            elif player_choice == 4:
                player_marks+=1
                
            

        time.sleep(0.3)
        show_marks(player_marks, computer_marks)

    else:
    #Handles what to happen when all 7 rounds are over
        
        update_status('---- Game Over ----')
        off_leds()
        show_marks(player_marks, computer_marks)
        off_leds()

        if player_marks > computer_marks:
            update_status('Congratulations! You win!')
            player_blink()
        elif player_marks < computer_marks:
            update_status('Computer wins. Try again!')
            computer_blink()
        else:
            update_status('No winner')

        off_leds()
        show_end()
        off_leds()
        
        beep(12,0.1,1)
        time.sleep(0.3)
        beep(12,0.1,1)
        time.sleep(0.3)
        beep(12,0.2,1)
        
        update_status('Press reset button to start the game again')

    button_reset_pressed = False

def run_game():
    while True:
        game()
        time.sleep(0.5)
        while True:
            '''
            These codes run when game is stoped by pressing
            reset button or game is over when all rounds are completed.
            '''

            #Waiting for reset button to press to start again
            button_reset_pressed = False
            if not button_reset_pressed:
                button_reset_state = read_button_state(reset_pin)
                if button_reset_state == 1:
                    button_reset_pressed = True
                    update_status('Game starting...')
                    break
                    #Inner while loop breaks. Outer while loop starts to
                    #restart game
            time.sleep(0.2)

game_thread = Thread(target=run_game)
game_thread.start()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("Exiting...")
finally:
    board.exit()

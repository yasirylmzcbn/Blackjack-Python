# Ferdinando, Yasir, Cameron
import json
import urllib.request
import tkinter as tk
from tkinter import *
from tkinter import simpledialog, messagebox
from PIL import ImageTk, Image
import os

cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in %r: %s" % (cwd, files))

# Window
root = tk.Tk()
root.title('Blackjack')
root.geometry("600x800+400+0")
root.config(bg='#090')


# Helper Method
def retrieve_json(url):
    req = urllib.request.Request(
        url,
        headers = { 'User-Agent': 'python-blackjack' }
    )
    response = urllib.request.urlopen(req)
    return json.loads(response.read())


# Game Variables
current_player = 1 # 0 is dealer
player_hands = []
deck_id = None
bust_players = []
stay_players = []
win_players = []
show_dealer = False
player_wins = [0, 0, 0]
player_losses = [0, 0, 0]
player_ties = [0, 0, 0]

# Helper Methods
def is_game_over():
    players = []
    for i in range(1, len(player_hands)):
        players.append(stay_players[i] or bust_players[i])
    for x in players:
        if x is False:
            return False
    return True

def next_player():
    global current_player
    current_player += 1
    if current_player >= len(player_hands):
        current_player = 1
    if is_game_over():
        check_winner()
    elif stay_players[current_player] or bust_players[current_player]:
        next_player()

def card_value(card):
    face = card['value']
    if face.isdigit():
        return int(face)
    elif face == 'KING' or face == 'QUEEN' or face == 'JACK':
        return 10
    elif face == 'ACE':
        return 'A'

def hand_value(player):
    hard_sum = 0
    soft_sum = 0
    for card in player_hands[player]:
        card_val = card_value(card)
        if card_val=='A':
            soft_sum+=1
            hard_sum+=11
        else:
            soft_sum+=card_val
            hard_sum+=card_val
    return (soft_sum, hard_sum)

def current_player_hand_value():
    return hand_value(current_player)

def dealer_hand_value():
    return hand_value(0)


# Graphics
ui_heading = Label(root, text='BLACKJACK', font=('Helvetica', 50), fg='black', bg='#090')
ui_dealer = Label(root, font=('Helvetica', 30), fg='black', bg='#090')
ui_dealer_hand_value = Label(root, font=('Helvetica', 25), fg='black', bg='#090')
ui_dealer_cards=Frame(root)
ui_player = Label(root, font=('Helvetica', 30), fg='black', bg='#090')
ui_current_player_hand_value = Label(root, font=('Helvetica', 25), fg='black', bg='#090')
ui_buttons = Frame(root)
ui_hit_button = Button(ui_buttons, text='Hit', font=('Helvetica', 30), padx=20, pady=10, fg='black', bg=
'SystemButtonFace')
ui_stay_button = Button(ui_buttons, text='Stay', font=('Helvetica', 30), padx=20, pady=10, fg='black', bg=
'SystemButtonFace')
ui_cards = Frame(root)
ui_scoreboard = Label(root, text=' ', font=('Helvetica', 15), fg='black', bg='#090', justify=LEFT)

images = []
def refresh_ui():
    global images
    ui_player['text'] = 'Player ' + str(current_player) + "'s Turn"
    ui_dealer['text'] = "Dealer's Hand"
    soft_sum, hard_sum = current_player_hand_value()
    ui_current_player_hand_value['text'] = 'Hand Value: ' + str(soft_sum) + ' (' + str(hard_sum) + 'h)'
    if show_dealer == True:
        ui_dealer_hand_value['text'] = 'Dealer Hand Value: ' + str(dealer_hand_value()[0]) + ' (' + str(dealer_hand_value()[1]) + 'h)'
    else:
        ui_dealer_hand_value['text'] = ''
    for widget in ui_cards.winfo_children():
       widget.destroy()
    for widget in ui_dealer_cards.winfo_children():
       widget.destroy()
    if show_dealer:
        for dcard in player_hands[0]:
            canvas = Canvas(ui_dealer_cards, width=125, height=175, bd='0', highlightthickness=0, bg='#090')
            canvas.pack(side=RIGHT)
            image = Image.open(urllib.request.urlopen(urllib.request.Request(
                dcard['image'],
                headers = { 'User-Agent': 'python-blackjack' }
            )))
            image = image.resize((125, 175), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(image)
            canvas.create_image(0, 0, anchor=NW, image=img)
            images.append(img)
    else:
        canvas = Canvas(ui_dealer_cards, width=125, height=175, bd='0', highlightthickness=0, bg='#090')
        canvas.pack(side=RIGHT)
        image = Image.open(urllib.request.urlopen(urllib.request.Request(
            player_hands[0][0]['image'],
            headers = { 'User-Agent': 'python-blackjack' }
        )))
        image = image.resize((125, 175), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor=NW, image=img)
        images.append(img)
        canvas = Canvas(ui_dealer_cards, width=125, height=175, bd='0', highlightthickness=0, bg='#090')
        canvas.pack(side=RIGHT)
        image = Image.open("card_back.png")
        image = image.resize((125, 175), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor=NW, image=img)
        images.append(img)
    for card in player_hands[current_player]:
        canvas = Canvas(ui_cards, width=125, height=175, bd='0', highlightthickness=0, bg='#090')
        canvas.pack(side=RIGHT)
        image = Image.open(urllib.request.urlopen(urllib.request.Request(
            card['image'],
            headers = { 'User-Agent': 'python-blackjack' }
        )))
        image = image.resize((125, 175), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(image)
        canvas.create_image(0, 0, anchor=NW, image=img)
        images.append(img)


# Play a Turn
def has_blackjack(player):
    ace = False
    ten = False
    for x in player_hands[player]:
        if card_value(x) == 10:
            ten = True
        elif card_value(x) == 'A':
            ace = True
    return ten and ace

def check_winner():
    global player_wins, player_losses, player_ties, show_dealer
    dealer_soft, dealer_hard = dealer_hand_value()
    win_players.append('N/A') # index 0 is for dealer
    for i in range(1, len(player_hands)):
        soft_sum, hard_sum = hand_value(i)
        if bust_players[i] == True:
            win_players.append(False)
            player_losses[i]+=1
        elif dealer_soft > 21 and dealer_hard > 21:
            win_players.append(True)
            player_wins[i] += 1
        elif len(player_hands[i]) == 2 and has_blackjack(i):
            if len(player_hands[0]) == 2 and has_blackjack(0):
                win_players.append(False)
                player_ties[i]+=1
            else:
                win_players.append(True)
                player_wins[i]+=1
        else:
            if (soft_sum <= 21 and soft_sum > dealer_soft) or (hard_sum <= 21 and hard_sum > dealer_hard) or (hard_sum <= 21 and hard_sum > dealer_soft) or (soft_sum <= 21 and soft_sum > dealer_hard):
                win_players.append(True)
                player_wins[i] += 1
            else:
                win_players.append(False)
                player_losses[i] += 1
    msg = ''
    for i in range(1, len(win_players)):
        win = 'Wins' if win_players[i] else 'Loses'
        msg += '(Player ' + str(i) + ' ' + win + ') '
    show_dealer = True
    refresh_ui()
    messagebox.showinfo('Blackjack', msg)
    reset()

def is_bust():
    soft_sum, hard_sum = current_player_hand_value()
    return soft_sum > 21 and hard_sum > 21

def is_tied():
    player_soft_sum, player_hard_sum = current_player_hand_value()
    dealer_soft_sum, dealer_hard_sum = dealer_hand_value()
    if player_hard_sum > 21:
        if dealer_hard_sum >21:
            return dealer_soft_sum == player_soft_sum
        else:
            return dealer_hard_sum == player_soft_sum
    else:
        if dealer_hard_sum >21:
            return dealer_soft_sum == player_hard_sum
        else:
            return dealer_hard_sum == player_hard_sum

def hit():
    global current_player
    cards = retrieve_json('https://deckofcardsapi.com/api/deck/' + deck_id + '/draw/?count=1')['cards']
    player_hands[current_player].extend(cards)
    if is_bust():
        bust_players[current_player] = True
        messagebox.showinfo('Blackjack', 'Player ' + str(current_player) + ' is now bust')
        next_player()
    elif has_blackjack(current_player):
        next_player()
    refresh_ui()

def stay():
    global current_player
    stay_players[current_player] = True
    next_player()
    refresh_ui()

def dealer_play():
    while dealer_hand_value()[0]<17 and dealer_hand_value()[1]<17:
        cards = retrieve_json('https://deckofcardsapi.com/api/deck/' + deck_id + '/draw/?count=1')['cards']
        player_hands[0].extend(cards)

ui_hit_button.config(command=lambda:hit())
ui_stay_button.config(command=lambda:stay())


# Initialization
numPlayers = simpledialog.askinteger('Blackjack', 'How many players?', parent=root, minvalue=1, maxvalue=4)
root.attributes('-fullscreen', True)
def reset():
    global current_player, player_hands, deck_id, bust_players, stay_players, win_players, show_dealer
    current_player = 1 # 0 is dealer
    player_hands = []
    deck_id = retrieve_json('https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1')['deck_id']
    bust_players = []
    stay_players = []
    win_players = []
    show_dealer = False
    ui_scoreboard['text'] = 'Wins:Losses:Ties\n'
    if isinstance(numPlayers, int):
        for i in range(numPlayers + 1):
            cards = retrieve_json('https://deckofcardsapi.com/api/deck/' + deck_id + '/draw/?count=2')['cards']
            player_hands.append([])
            player_hands[i].extend(cards)
            bust_players.append(False)
            stay_players.append(False)
            player_wins.append(0)
            player_losses.append(0)
            player_ties.append(0)
            pl = 'Player ' + str(i) if i != 0 else 'Dealer'
            ui_scoreboard['text'] += '(' + pl + ' ' + str(player_wins[i]) + ':' + str(player_losses[i]) + ':' + str(player_ties[i]) + ') '
        dealer_play()
        refresh_ui()

reset()
ui_heading.place(relx=0.5, y=50, anchor=CENTER)
ui_dealer.place(relx=0.5, y=100, anchor=CENTER)
ui_dealer_cards.place(relx=0.5,y=210,anchor=CENTER)
ui_dealer_hand_value.place(relx=0.5, y=315, anchor=CENTER)
ui_player.place(relx=0.5, y=357, anchor=CENTER)
ui_cards.place(relx=0.5, y=475, anchor=CENTER)
ui_current_player_hand_value.place(relx=0.5, y=580, anchor=CENTER)
ui_hit_button.pack(side=LEFT)
ui_stay_button.pack(side=RIGHT)
ui_buttons.place(relx=0.5, y=655, anchor=CENTER)
ui_scoreboard.place(relx=0, rely=1, anchor=SW)
refresh_ui()
root.mainloop()



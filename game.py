import player
import constant
import region
import dice

import random
from tkinter import messagebox
import tkinter as tk

colorset = ["red", "blue"]


format_time = lambda seconds : "Elapsed time -> %02d:%02d"%(seconds//60, seconds % 60)

format_currency = lambda money: "${:,}".format(money)


class Game:
    def __init__(self, region_info=None, players_name=None):
        main_view = MainView()
        self.__main_view = main_view
        self.__canvas = main_view.map_canvas
        assert len(region_info) == constant.TOTAL_REGIONS
        self.__region_list = [region.Region(region_info[i][0], region_info[i][1], root_view=self.__canvas, _x=constant.REGION_OF_X_POS[i], _y=constant.REGION_OF_Y_POS[i]) for i in range(constant.TOTAL_REGIONS)]

        assert len(players_name) == constant.PLAYER_NO
        self.__player_list = [player.Player(players_name[i],self.__canvas, colorset[i]) for i in range(constant.PLAYER_NO)]

        self.__region_list[14].set_desert()
        self.__region_list[0].set_cannot_buy()

        self.__current_turn = 1  # current turn number
        self.__current_player_no = 0

        self.__dices_list = [dice.Dice(), dice.Dice()]
        self.__canvas.create_image(275, 350, anchor=tk.NW, image=self.__dices_list[0])
        self.__canvas.create_image(375, 350, anchor=tk.NW, image=self.__dices_list[1])

        self.dice_button = tk.Button(main_view.footer, text='roll dices', command=self.play)
        self.dice_button.pack(side=tk.LEFT, padx=20)

        self.reset_button = tk.Button(main_view.footer, text='reset', command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=20)

        self.__elapsed_time = 0
        self.__timer_on = False
        self.__timer_label = tk.Label(self.__main_view.header, text=format_time(0))
        self.__timer_label.pack()
        self.__turn_label = tk.Label(self.__main_view.header, text="Turn #%2d" % self.__current_turn)
        self.__turn_label.pack()

        self.__players_name_label = [tk.Label(self.__main_view.frame_info,
                                              text=self.__player_list[i].get_player_name(),
                                              fg=self.__player_list[i].get_color(),
                                              font=("Helvetica", 16),
                                              width=10)
                                     for i in range(constant.PLAYER_NO)]
        self.__players_money_label = [tk.Label(self.__main_view.frame_info,
                                              text=format_currency(self.__player_list[i].get_current_money()),
                                               font=("Helvetica", 16))
                                     for i in range(constant.PLAYER_NO)]
        self.__display_current_player = self.__main_view.map_canvas.create_text(
            350, 300,
            text="%s turn" % self.__player_list[0].get_player_name(),
            font=("Helvetica", 16),
            fill=self.__player_list[0].get_color()
        )

        for i in range(constant.PLAYER_NO):
            self.__players_name_label[i].grid(row=2*i, column=1)
            self.__players_money_label[i].grid(row=2*i+1, column=1)

    # update timer text.
    def update_timer(self):
        if not self.__timer_on:
            return
        self.__elapsed_time += 1
        self.__timer_label.config(text=format_time(self.__elapsed_time))
        self.__main_view.after(1000, self.update_timer)

    # reset game
    def reset(self):
        # reset player information
        for _player in self.__player_list:
            assert isinstance(_player, player.Player)
            _player.reset()

        # reset region information
        for _region in self.__region_list:
            assert isinstance(_region, region.Region)
            _region.reset()
        self.__elapsed_time = 0
        self.__current_turn = 1
        self.__current_player_no = 0
        self.__timer_on = False

        self.dice_button.config(state=tk.NORMAL)
        self.__timer_label.config(text=format_time(self.__elapsed_time))
        self.__turn_label.config(text="Turn #%2d" % self.__current_turn)
        for i in range(constant.PLAYER_NO):
            self.__players_money_label[i].config(text=format_currency(self.__player_list[i].get_current_money()))

        self.__main_view.map_canvas.itemconfig(self.__display_current_player, text="%s turn" % self.__player_list[0].get_player_name())
        self.__main_view.map_canvas.itemconfig(self.__display_current_player, fill=self.__player_list[0].get_color())

    # get dice numbers with random. and return dice numbers with tuple. 
    # Here updates dice image
    def roll_dice(self):
        (dice1, dice2) = (random.randint(1, 6), random.randint(1, 6))
        self.__dices_list[0].update_dice_num(dice1)
        self.__dices_list[1].update_dice_num(dice2)
        return dice1, dice2

    # player's work in one turn. include rolling the dice, moving and buying region
    def player_move(self, _player: player.Player):
        dice1, dice2 = self.roll_dice() # roll the dice
        print(dice1, dice2)
        current_region = self.__region_list[_player.move(dice1, dice2)]  # player's current position
        assert isinstance(current_region, region.Region)  # check if current_region is Region class
        _type = current_region.get_buy_type(_player.get_id())  # with values in constant.py, set purchase type
        if current_region.is_desert() and not _player.check_desert():
            _player.set_stop()
            messagebox.showerror("Desert", "You are in desert!")
        # pay toll when the region is owned by other player.
        if _player.get_id() != current_region.get_owner_id() and current_region.get_owner_id() is not None:
            _toll = current_region.get_toll()
            _player.pay_money(_toll, current_region.get_owner())
            print("%s gave $%d money to %s"
                  % (_player.get_player_name(), _toll, current_region.get_owner().get_player_name()))
        # ask whether buy the region or not
        current_region_price = current_region.get_sales_price(_player.get_id())
        if _player.get_current_money() >= current_region_price and current_region.can_buy():
            want_to_buy = messagebox.askyesno("Buy", constant.ASK_BUY_MESSAGE[_type] % current_region_price)
            if want_to_buy:
                    current_region.buy(_player)
        if dice1 != dice2:
            self.__current_player_no = (self.__current_player_no + 1) % constant.PLAYER_NO
        else:
            messagebox.showinfo("Double", "Your dices ar Double!")
        return dice1, dice2

    # every works in one turn
     # if game is not over, return none. when someone is bankrupt, return bankrupt player id
    def one_turn(self):
        _player = self.__player_list[self.__current_player_no]
        self.player_move(_player)

        for i in range(constant.PLAYER_NO):
            self.__players_money_label[i].config(text=format_currency(self.__player_list[i].get_current_money()))

        if _player.is_bankrupt():
            return _player

        if self.__current_player_no == 0:
            self.__current_turn += 1  # 한 턴을 증가시킨다.
            self.__turn_label.config(text="Turn #%2d" % self.__current_turn)
        _player = self.__player_list[(self.__current_player_no) % constant.PLAYER_NO]
        self.__main_view.map_canvas.itemconfig(self.__display_current_player, text="%s turn" % _player.get_player_name())
        self.__main_view.map_canvas.itemconfig(self.__display_current_player, fill=_player.get_color())

        return None

    # process a game
    def play(self):
        if not self.__timer_on:
            self.__timer_on = True
            self.update_timer()
        if self.__current_turn == constant.MAXIMUM_TURN:
            self.show_winner()
            return
        self.dice_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)
        result = self.one_turn()
        self.dice_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        # when game is over, initialize all previous game information
        if result is not None:
            assert isinstance(result, player.Player)
            print("%s is bankrupt!" % result.get_player_name())
            self.show_winner()

    def show_winner(self):
        self.__timer_on = False
        scores = self.get_score()
        print(scores)
        if scores[0] == scores[1]:
            message = "Draw"
        elif scores[0] > scores[1]:
            message = "%s Win!" % self.__player_list[0].get_player_name()
        else:
            message = "%s Win!" % self.__player_list[1].get_player_name()
        self.dice_button.config(state=tk.DISABLED)
        messagebox.showinfo("Winner", message)

    def get_score(self):
        scores = [self.__player_list[i].get_current_money() for i in range(constant.PLAYER_NO)]
        for _region in self.__region_list:
            _id = _region.get_owner_id()
            if _id is not None:
                scores[_id-1] += _region.get_current_price()
        return scores


class MainView(tk.Tk):
    def __init__(self, title="Game 1.0"):
        super().__init__()
        self.title(title)
        self.resizable(0, 0)
        self.wm_attributes("-topmost", 1)
        self.header = tk.Frame(self)
        self.header.grid(row=0, column=0)
        self.map_canvas = tk.Canvas(self, width=950, heigh=700)
        self.map_canvas.grid(row=1, column=0)
        self.footer = tk.Frame(self)
        self.footer.grid(row=2, column=0)
        self.frame_info = tk.Frame(self)
        self.frame_info.grid(row=1, column=1)
        self.update()


class AskMessageBox(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Config")
        self.texts = []
        for i in range(constant.PLAYER_NO):
            tk.Label(self, text="Input Player%d name" % (i+1)).grid(row=i, column=0)
            self.texts.append(tk.Entry())
            self.texts[i].grid(row=i, column=1)
        tk.Button(self, text="Submit", command=self.submit).grid(row=2, column=0, columnspan=2)
        self.mainloop()

    # call when click submit button.
    def submit(self):
        players_name = []
        for _text in self.texts:
            players_name.append(_text.get())
        self.destroy()
        start_game(players_name)


# start game
def start_game(players_name):
    region_name_list = ['정문', '법대', '규장각', '사회대', '문화관', '잔디밭', '학생회관', '자연대',
                    '농생대', '농식', '해동', '아랫공대', '공깡', '중도', '관정', '인문대', '인문신양',
                    '자하연', '음미대', '경영대', '체육관', 'MOA', '대운동장', '기숙사', '감골식당',
                    '사범대', '롯데리아', '느티나무']

    region_price_list = [0, 500, 1600, 2100, 1500, 800, 1800, 1000, 2000, 1400, 1200, 2500, 1200, 1500, 800, 1500, 2200,
                     1300, 1800, 800, 2000, 1200, 900, 1100, 2100, 1300, 1600, 2700]
    # make list with region name and price
    main_view = MainView()

    regions_info = [(region_name_list[i], region_price_list[i]) for i in range(constant.TOTAL_REGIONS)]

    Game(regions_info, players_name)

    main_view.mainloop()


if __name__ == "__main__":
    s = AskMessageBox()

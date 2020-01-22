 # * author : Philippe Vo 
 # * date : 2019-December-22 16:21:57
 
# * Imports
# 3rd Party Imports
from trello import TrelloClient
from datetime import date
# User Imports

# * Code
class TrelloController():
    def __init__(self):
        # Authentication
        self.client = TrelloClient(
        api_key='12cd68c66b5178fb06a2a96e0df9f436',
        api_secret='414fbec6d5e25fd777b9d06d7b42143be3ce4e0b04cb38c40c5063ad0b541ad1',
        token='75a3501253afbac5d09f6931aa3274d776d1eb2d22c91a5d730dcfa1380d802d'
        )

        self.allBoards = self.client.list_boards()

    def get_board(self, boardName):
        """ returns the board based on the name """
        for board in self.allBoards:
            if board.name == "SCHOOL WINTER":
                break

        return board

    def get_cards(self, board):
        """ get all the cards we have so we can know their titles, list name and due dates """
        cardDataList = []
        lists = board.list_lists()
        for list_ in lists:
            if list_.name == "Completed": # REVIEW : We ingore the Completed list
                continue
            data = {}
            data["groupName"] = list_.name
            for card in list_.list_cards():
                if card.due_date != "": # REVIEW : For now, we dont add cards with no due dates by default
                    data = {}
                    data["groupName"] = list_.name
                    data["cardName"] = card.name
                    data["dueDate"] = card.due_date # REVIEW : Ignore the due dates that are more than 2 weeks ?
                    today = date.today()
                    daysLeft = (card.due_date.date() - today)
                    daysLeft = int(daysLeft.days)
                    if  daysLeft < 14:
                        cardDataList.append(data)

        return cardDataList

# obj = TrelloController()
# board = obj.get_board("SCHOOL WINTER")
# cards = obj.get_cards(board)

# for card in cards:
#     print(card)

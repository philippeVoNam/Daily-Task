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
        board = self.get_board("SCHOOL WINTER")
        self.listIds = self.get_list_ids(board)
        self.cardDataList = self.get_cards(board)

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
                    data["card"] = card
                    today = date.today()
                    daysLeft = (card.due_date.date() - today)
                    daysLeft = int(daysLeft.days)
                    if  daysLeft < 14:
                        cardDataList.append(data)

        return cardDataList

    def get_list_ids(self, board):
        """[returns a Dictionary that contains the lists name and its id]
        
        Arguments:
            board {[trello.Board]} -- [description]
        
        Returns:
            [Dictionary of String and Strings ?] -- [{list name, list_id}}]
        """
        listIds = {}
        lists = board.list_lists()
        for list_ in lists:
            listIds[list_.name] = list_.id

        return listIds

    def move_to_complete(self, groupName, title):
        """[move the card to completed section of trello]
        
        Arguments:
            groupName {[String]} -- [card list name]
            title {[String]} -- [card name]
        """
        card = self.get_card(groupName, title)
        try:
            card.change_list(self.listIds["Completed"])
            print("Card moved to Completed")
        except Exception as e:
            print("Card not found")
    
    def get_card(self, groupName, title):
        """[return the card depending on card groupName and title]
        
        Arguments:
            groupName {[String]} -- [card list name]
            title {[String]} -- [card title]
        
        Returns:
            [trello.card] -- [description]
        """
        for card in self.cardDataList:
            if card["groupName"] == groupName and card["cardName"] == title:
                return card["card"]
        
        return None

# obj = TrelloController()
# board = obj.get_board("SCHOOL WINTER")
# cards = obj.get_cards(board)

# for card in cards:
#     print(card)

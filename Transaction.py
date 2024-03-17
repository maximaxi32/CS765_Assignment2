# importing libraries
import uuid


# class to describe a transaction type object
class Transaction:
    def __init__(self, sender, receiver, timestamp, ListOfPeers, type, amount):
        self.ID = str(uuid.uuid4()) # unique ID of the transaction
        self.sender = sender    # sender of the amount/coins in the transaction
        self.receiver = receiver    # receiver of the amount/coins in the transaction
        self.timestamp = timestamp  # timestamp of the creation of the transaction
        self.type = type  # type can be "coinbase" or "transfer"
        self.amount = amount    # amount of coins transferred in the transaction

    # function to write the transaction details to a TxnLog.txt file
    def printTransaction(self, type):
        # if the transaction is a coinbase transaction, then the sender and receiver are same
        if type == "coinbase":
            with open("TxnLog.txt", "a") as myfile:
                myfile.write(
                    "TxnID: " + self.ID + " " + str(self.sender) + " mines 50 coins\n"
                )
            return

        # for transfer transactions
        with open("TxnLog.txt", "a") as myfile:
            myfile.write(
                "TxnID: "
                + self.ID
                + " "
                + str(self.sender)
                + " pays "
                + str(self.receiver)
                + " "
                + str(self.amount)
                + " coins\n"
            )
        return

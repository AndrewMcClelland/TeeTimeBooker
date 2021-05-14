from GolfHandler import GolfHandler

class GolfNowGolfHandler(GolfHandler):
    def __init__(self, username: str, password: str, numberHoles: str, numberPlayers: str, preferredTeeTimeRanges: str, baseUrl: str, bookTimeEnabled: bool, twilioHandler: TwilioHandler, logger):
        super().__init__(numberHoles=numberHoles, numberPlayers=numberPlayers, preferredTeeTimeRanges=preferredTeeTimeRanges, baseUrl=baseUrl, bookTimeEnabled=bookTimeEnabled, twilioHandler=twilioHandler, logger=logger)

        self.username = username
        self.password = password
    
    def BookTeeTimes(self):
        print("Book GolfNow")
class Player():
    def __init__(self, id, firstName, lastName, team):
        self.firstName = firstName
        self.lastName = lastName
        self.team = team
        self.id = id

    def get_fullname(self):
        return f"{self.firstName} {self.lastName}"
    
    def get_firstname(self):
        return self.firstName

    def get_id(self):
        return self.id

    def get_team(self):
        return self.team

    
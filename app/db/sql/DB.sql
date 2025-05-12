CREATE TABLE Participants (
    UserID UUID PRIMARY KEY,
    Name TEXT NOT NULL,
    LastName TEXT NOT NULL,
    BirthDate DATE NOT NULL
);

CREATE TABLE Lotteries (
    LotteryID UUID PRIMARY KEY,
    Date DATE NOT NULL UNIQUE,
    Closed BOOLEAN DEFAULT FALSE
);

CREATE TABLE Lotteries (
    LotteryID UUID PRIMARY KEY,
    Date DATE NOT NULL UNIQUE,
    Closed BOOLEAN DEFAULT FALSE
);

CREATE TABLE WinningBallots (
    LotteryID UUID PRIMARY KEY,
    BallotID UUID NOT NULL,
    WinningDate DATE NOT NULL,
    WinningAmount DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_lottery_win FOREIGN KEY (LotteryID) REFERENCES Lotteries(LotteryID),
    CONSTRAINT fk_ballot_win FOREIGN KEY (BallotID) REFERENCES Ballots(BallotID)
);

-- Make DB go brrr

CREATE INDEX idx_ballots_user ON Ballots(UserID);
CREATE INDEX idx_ballots_lottery ON Ballots(LotteryID);
CREATE INDEX idx_winning_date ON WinningBallots(WinningDate);

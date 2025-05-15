CREATE TABLE Participants (
    user_id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date DATE NOT NULL
);

CREATE TABLE Lotteries (
    lottery_id SERIAL PRIMARY KEY,
    lottery_date DATE NOT NULL UNIQUE,
    closed BOOLEAN DEFAULT FALSE
);

CREATE TABLE Ballots (
    ballot_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES Participants(user_id),
    lottery_id INTEGER NOT NULL REFERENCES Lotteries(lottery_id),
    ballot_number VARCHAR(255) UNIQUE,
    expiry_date DATE,
    CONSTRAINT fk_participant FOREIGN KEY (user_id) REFERENCES Participants(user_id)
);

CREATE TABLE WinningBallots (
    lottery_id INTEGER PRIMARY KEY, 
    ballot_id INTEGER NOT NULL UNIQUE, 
    winning_date DATE NOT NULL,
    winning_amount INTEGER NOT NULL,
    CONSTRAINT fk_lottery_win FOREIGN KEY (lottery_id) REFERENCES Lotteries(lottery_id),
    CONSTRAINT fk_ballot_win FOREIGN KEY (ballot_id) REFERENCES Ballots(ballot_id),
    CONSTRAINT chk_winning_amount_range CHECK (winning_amount > 0 AND winning_amount <= 100)
);

-- Indexes remain conceptually the same, referencing integer columns now
CREATE INDEX idx_ballots_user ON Ballots(user_id);
CREATE INDEX idx_ballots_lottery ON Ballots(lottery_id);
CREATE INDEX idx_winning_date ON WinningBallots(winning_date);
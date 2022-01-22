
CREATE TABLE PersonInBook (personID INTEGER NOT NULL, bookID INTEGER NOT NULL);

.import bruce.csv TmpBruceInComic
.import dick.csv TmpDickInComic

INSERT INTO PersonInBook (personID, bookID) SELECT 'Bruce', comicID FROM TmpBruceInComic;
INSERT INTO PersonInBook (personID, bookID) SELECT 'Dick', comicID FROM TmpDickInComic;

CREATE TABLE Book (id INTEGER, name TEXT NOT NULL, year smallint(4) NOT NULL, month tinyint(2) DEFAULT NULL, day tinyint(2) DEFAULT NULL);

CREATE TABLE BookNames (id INTEGER, name TEXT NOT NULL);

INSERT INTO BookNames (id, name) SELECT DISTINCT bookID, bookID FROM PersonInBook;

CREATE TABLE Person (id INTEGER, name TEXT NOT NULL);

INSERT INTO Person (id, name) SELECT DISTINCT personID, personID FROM PersonInBook;

CREATE TABLE Author (id INTEGER, name TEXT NOT NULL);

CREATE TABLE BookHasAuthor (bookID INTEGER, authorID INTEGER, FOREIGN KEY(bookID) REFERENCES Book(id), FOREIGN KEY(authorID) REFERENCES Author(id));

CREATE TEMPORARY TABLE PersonPairs (firstPersonID INTEGER, secondPersonID INTEGER, FOREIGN KEY(firstPersonID) REFERENCES Person(id), FOREIGN KEY(secondPersonID) REFERENCES Person(id));

INSERT INTO PersonPairs (firstPersonID, secondPersonID) SELECT firstPerson.id, secondPerson.id FROM Person AS firstPerson CROSS JOIN Person AS secondPerson WHERE firstPerson.id != secondPerson.id;

CREATE TABLE AppearancesTogether (firstPersonID INTEGER NOT NULL, secondPersonID INTEGER NOT NULL, bookID INTEGER NOT NULL);

INSERT INTO AppearancesTogether (firstPersonID, secondPersonID, bookID) SELECT firstPersonID, secondPersonID, secondPersonInBook.bookID FROM PersonPairs INNER JOIN PersonInBook AS firstPersonInBook ON firstPersonInBook.personID=firstPersonID INNER JOIN PersonInBook AS secondPersonInBook ON (secondPersonInBook.personID=secondPersonID AND secondPersonInBook.bookID=firstPersonInBook.bookID);

CREATE TABLE NumberOfAppearancesTogether (firstPersonID INTEGER, secondPersonID INTEGER, numberAppearances INTEGER);

INSERT INTO NumberOfAppearancesTogether (firstPersonID, secondPersonID, numberAppearances) SELECT firstPersonID, secondPersonID, COUNT(DISTINCT(bookID)) FROM AppearancesTogether GROUP BY firstPersonID, secondPersonID;

CREATE TEMPORARY TABLE PersonWithTotalAppearances (personID INTEGER, totalAppearances INTEGER);

INSERT INTO PersonWithTotalAppearances (personID, totalAppearances) SELECT personID, COUNT(DISTINCT(bookID)) FROM PersonInBook GROUP BY personID;

CREATE TABLE FractionOfAppearancesTogether (firstPersonID INTEGER, secondPersonID INTEGER, numberAppearances INTEGER, fractionOfFirstPersonsAppearances REAL);

INSERT INTO FractionOfAppearancesTogether (firstPersonID, secondPersonID, numberAppearances, fractionOfFirstPersonsAppearances) SELECT firstPersonID, secondPersonID, numberAppearances, 1.0*numberAppearances/totalAppearances FROM NumberOfAppearancesTogether INNER JOIN PersonWithTotalAppearances ON PersonWithTotalAppearances.personID=firstPersonID;


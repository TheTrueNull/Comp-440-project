/*USE THESE TO CREATE THE SERVER THAN ADD A USER IN THE ADMINISTRATION TAB WITH ONLY INSERT AND SELECT PRIVALEGES*/


CREATE TABLE Users (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255),
    firstName VARCHAR(255),
    lastName VARCHAR(255),
    email VARCHAR(255) UNIQUE
);


CREATE TABLE Items (
    itemID INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    title VARCHAR(255),
    description TEXT,
    datePosted DATE,
    price DECIMAL(10,2),
    categories VARCHAR(255),
    FOREIGN KEY (username) REFERENCES Users(username)
);


CREATE TABLE Reviews (
    reviewID INT AUTO_INCREMENT PRIMARY KEY,
    itemID INT,
    username VARCHAR(255),
    reviewDate DATE,
    score ENUM('Excellent', 'Good', 'Fair', 'Poor'),
    remark TEXT,
    FOREIGN KEY (itemID) REFERENCES Items(itemID),
    FOREIGN KEY (username) REFERENCES Users(username)
); 
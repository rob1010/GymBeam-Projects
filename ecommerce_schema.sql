-- Operačná databáza
CREATE TABLE Category (
    CategoryID INT PRIMARY KEY,
    Name VARCHAR(100),
    ParentCategoryID INT,
    FOREIGN KEY (ParentCategoryID) REFERENCES Category(CategoryID)
);

CREATE TABLE Product (
    ProductID INT PRIMARY KEY,
    Name VARCHAR(100),
    Price DECIMAL(10, 2),
    Description TEXT,
    Availability BOOLEAN,
    CategoryID INT,
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
);

CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(100),
    Address VARCHAR(255),
    Region VARCHAR(50),
    RegistrationDate DATE
);

CREATE TABLE "Order" (
    OrderID INT PRIMARY KEY,
    CustomerID INT,
    OrderDate DATE,
    Status VARCHAR(50),
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
);

CREATE TABLE OrderItem (
    OrderItemID INT PRIMARY KEY,
    OrderID INT,
    ProductID INT,
    Quantity INT,
    UnitPrice DECIMAL(10, 2),
    FOREIGN KEY (OrderID) REFERENCES "Order"(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

CREATE TABLE Transaction (
    TransactionID INT PRIMARY KEY,
    OrderID INT,
    TransactionDate DATE,
    PaymentMethod VARCHAR(50),
    Amount DECIMAL(10, 2),
    FOREIGN KEY (OrderID) REFERENCES "Order"(OrderID)
);

-- Analytická databáza (Star Schema)
CREATE TABLE TimeDim (
    TimeID INT PRIMARY KEY,
    OrderDate DATE,
    Year INT,
    Quarter INT,
    Month INT,
    Day INT
);

CREATE TABLE ProductDim (
    ProductID INT PRIMARY KEY,
    Name VARCHAR(100),
    Price DECIMAL(10, 2),
    Description TEXT,
    Availability BOOLEAN,
    CategoryID INT
);

CREATE TABLE CategoryDim (
    CategoryID INT PRIMARY KEY,
    Name VARCHAR(100),
    ParentCategoryID INT
);

CREATE TABLE CustomerDim (
    CustomerID INT PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(100),
    Address VARCHAR(255),
    Region VARCHAR(50),
    RegistrationDate DATE
);

CREATE TABLE TransactionDim (
    TransactionID INT PRIMARY KEY,
    TransactionDate DATE,
    PaymentMethod VARCHAR(50),
    Amount DECIMAL(10, 2)
);

CREATE TABLE SalesFact (
    OrderItemID INT,
    OrderID INT,
    ProductID INT,
    CustomerID INT,
    TransactionID INT,
    TimeID INT,
    Quantity INT,
    UnitPrice DECIMAL(10, 2),
    TotalAmount DECIMAL(10, 2),
    PRIMARY KEY (OrderItemID),
    FOREIGN KEY (ProductID) REFERENCES ProductDim(ProductID),
    FOREIGN KEY (CustomerID) REFERENCES CustomerDim(CustomerID),
    FOREIGN KEY (TransactionID) REFERENCES TransactionDim(TransactionID),
    FOREIGN KEY (TimeID) REFERENCES TimeDim(TimeID)
);
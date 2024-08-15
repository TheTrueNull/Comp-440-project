/* These are the queries for Phase 3
#1)

SET SESSION sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY',''));

SELECT categories, MAX(price) AS MaxPrice, title, description
FROM Items
GROUP BY categories;


#2)

SELECT DISTINCT i1.username
FROM Items i1, Items i2
WHERE i1.username = i2.username 
AND i1.datePosted = i2.datePosted
  AND i1.categories = 'X' 
  AND i2.categories = 'Y'
  AND i1.itemID != i2.itemID;

#3)

SELECT DISTINCT i.itemID, i.title
FROM Items i
JOIN Reviews r ON i.itemID = r.itemID
WHERE i.username = 'User X'
  AND EXISTS (
    SELECT 1
    FROM Reviews r2
    WHERE r2.itemID = i.itemID 
    AND r2.score IN ('Excellent', 'Good')
  );


#4)

SELECT username, COUNT(*) AS Countno
FROM Items
WHERE datePosted = '2024-07-04'
GROUP BY username
HAVING COUNT(*) = (
    SELECT MAX(Countno) FROM (
        SELECT COUNT(*) AS Countno
        FROM Items
        WHERE datePosted = '2024-07-04'
        GROUP BY username
    ) AS Counts
);

#5)

SELECT DISTINCT username
FROM Reviews
WHERE score = 'Poor'
AND username NOT IN (
    SELECT username FROM Reviews WHERE score <> 'Poor'
);


#6)

SELECT DISTINCT username
FROM Items i
WHERE NOT EXISTS (
    SELECT 1 FROM Reviews r WHERE r.itemID = i.itemID AND r.score = 'Poor'
);

*/
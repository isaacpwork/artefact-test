/* Create table */

CREATE TABLE [dbo].[Transactions] (
    TransactionTimestamp datetime,
    CustomerId int,
    ProductId int,
    TransactionId int IDENTITY(1, 1),
);

/* Select freq dist */

SELECT
    t1.[Count] AS [TransactionCount],
    count(*) AS [CustomerCount]
FROM (
    SELECT
        count(*) AS [Count],
        [dbo].[Transactions].[CustomerId]
    FROM
        [dbo].[Transactions]
    GROUP BY
        [dbo].[Transactions].[CustomerId]
) AS t1
GROUP BY
    t1.[Count]
ORDER BY
    [TransactionCount] ASC

/* Select cumulative dist */

SELECT 
    [TransactionCount],
	SUM([CustomerCount]) OVER (ORDER BY [TransactionCount]) AS [CumSum]
FROM (
    SELECT
        t1.[Count] AS [TransactionCount],
        count(*) AS [CustomerCount]
    FROM (
        SELECT
            count(*) AS [Count],
            [dbo].[Transactions].[CustomerId]
        FROM
            [dbo].[Transactions]
        GROUP BY
            [dbo].[Transactions].[CustomerId]
    ) AS t1
    GROUP BY
        t1.[Count]
) AS cc

/* Common friends */

CREATE TABLE [dbo].[Friends] (
    Friend1Id int,
    Friend2Id int
);

/* Two users to find mutual friends between */
DECLARE @f1 int = 1, @f2 int = 2;

SELECT 
	count(*) AS [MutualCount]
FROM (
	SELECT
		[Friend1Id] AS [F1FriendId]
	FROM
		[dbo].[Friends]
	WHERE
		[Friend2Id] = @f1
	UNION
	SELECT
		[Friend2Id] AS [F1FriendId]
	FROM
		[dbo].[Friends]
	WHERE
		[Friend1Id] = @f1
) as F1Friends
JOIN (
	SELECT
		[Friend1Id] AS [F2FriendId]
	FROM
		[dbo].[Friends]
	WHERE
		[Friend2Id] = @f2
	UNION
	SELECT
		[Friend2Id] AS [F2FriendId]
	FROM
		[dbo].[Friends]
	WHERE
		[Friend1Id] = @f2
) AS F2Friends
ON F1FriendId = F2FriendId
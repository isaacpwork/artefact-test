import psycopg2

class CommentsDb:
    cursor = None
    connection = None

    def connect(self):
        self.connection = psycopg2.connect(user="admin",
                                password="WCFHXGMFOZNENNNJ",
                                host="aws-us-east-1-portal.4.dblayer.com",
                                port="33649",
                                database="compose")
        self.connection.autocommit = True

        self.cursor = self.connection.cursor()

    # Insert into db, comment_obj must be a list of dictionary for comments
    def insert(self, comment_obj):
        for cmt in comment_obj:
            insert_comment = "insert into Comments (UserName, Content, Timestamp) values (%s, %s, %s) on conflict on constraint unique_cmt do nothing"
            self.cursor.execute(insert_comment, (cmt['nickname'], cmt['content'], cmt['creationTime']))

    # Search db for comment content containing the keyword
    def select(self, keyword):
        select_keyword = "select row_to_json(t) from (select UserName, Content, Timestamp from Comments where Content like %s) t"

        self.cursor.execute(select_keyword, ('%{}%'.format(keyword), ))

        return self.cursor.fetchall()

    def create(self):
        create_comments = "create table Comments (Id serial primary key, UserName varchar, Content varchar, Timestamp timestamp, constraint unique_cmt unique (UserName, Content, Timestamp))"

        self.cursor.execute(create_comments)

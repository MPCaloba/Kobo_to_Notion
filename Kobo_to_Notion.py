# Import the necessary modules --------------------------------------------------------------
import pandas as pd
import os
import sqlite3
from sqlite3 import Error
from notion_client import Client


# Get the folder and file directories -------------------------------------------------------
path = os.path.abspath(os.getcwd())
sqlite_file = path + "\KoboReader.sqlite"


## Setting up the connection to Notion ------------------------------------------------------
notion_token = 'secret_6LLjHhhTT1svptfOn1PKcaAPO1bWo3ozuKSmYjU9hC7'
page_id = 'c3df18b1d083451e89b61a0419422e29'   # 'Kobo to Notion' page


## Connecting to the SQLite file ------------------------------------------------------------
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


## Writing text to the specified Notion page ------------------------------------------------
def write_text(client, page_id, text, type):
    client.blocks.children.append(
        block_id = page_id,
        children = [
            {
                "object": "block",
                "type": type,
                type: {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": text
                            }
                        }
                    ]
                }
            }
        ]
    )


## Main function ----------------------------------------------------------------------------
def main():
    conn = create_connection(sqlite_file)
    
    # Nota -- tenho que fazer inner join com o Bookmark para ir buscar só os livros que têm highlights
    books_in_file = pd.read_sql("SELECT DISTINCT c.ContentId AS 'Content ID', c.Title AS 'Book Title', c.Attribution AS 'Author', c.DateLastRead AS Date " +
                                "FROM Bookmark AS b INNER JOIN content AS c " +
                                "ON b.VolumeID = c.ContentID " +
                                "ORDER BY 4 ASC", conn)
    bookmark_df = pd.read_sql("SELECT VolumeID AS 'Volume ID', Text AS 'Highlight', Annotation, DateCreated AS 'Created On', Type " + 
                            "FROM Bookmark " + 
                            "ORDER BY 4 ASC", conn)
    
    for i in range(0, len(bookmark_df)):
        bookmark_df['Highlight'][i] = bookmark_df['Highlight'][i].strip()
    
    client = Client(auth=notion_token)
    
    for i in range(0, len(books_in_file)):
        write_text(client, page_id, books_in_file['Book Title'][i] + ' - ' + books_in_file['Author'][i], 'heading_2')
        
        for x in range(0, len(bookmark_df)):
            
            if books_in_file['Book Title'][i] in bookmark_df['Volume ID'][x]:
                
                if bookmark_df['Type'][x] == 'highlight':
                    write_text(client, page_id, bookmark_df['Highlight'][x], 'paragraph')
                else:
                    write_text(client, page_id, bookmark_df['Annotation'][x], 'quote')
                    write_text(client, page_id, bookmark_df['Highlight'][x], 'paragraph')
        
        write_text(client, page_id, ' ', 'paragraph')


## Starting block ---------------------------------------------------------------------------
if __name__ == '__main__':
    main()
from pathlib import Path
import numpy as np
import os

class FileCrawler:
    wildcard=None
    def __init__(self,wildcard):
        self.wildcard=wildcard
        
    def get_file(self):
        #Look for possible paths to make things easier
        filelist = Path('../../../Maraging Steels/').rglob('*'+self.wildcard+'*.csv')
        filepath = ''
        file_list = ['']
        file_list.clear()

        counter = 1
        print('Looking for files...')
        print('')
        for file in filelist:
            pos = os.path.abspath(file).find("Maraging Steels")+(len("Maraging Steels"))+1
            print('['+str(counter)+'] '+os.path.abspath(file)[pos:])
            file_list.append(os.path.abspath(file))
            counter = counter+1

        print('')
        num_files = len(file_list)

        if num_files > 0:
            selector = input('Select file from list [1-'+str(num_files)+'] or enter a path: ')
        else:
            selector = input('Enter a path: ')

        if selector.isnumeric():
            filepath = file_list[int(selector)-1]
        else:
            filepath = selector

        print(filepath)

        if not(os.path.isfile(filepath)):
            print('Not a valid file')
            return ''
        return filepath

    def get_file_list(self):
        #Look for possible paths to make things easier
        filelist = Path('../../../Maraging Steels/').rglob('*'+self.wildcard+'*.csv')
        filepath = ''
        file_list = ['']
        file_list.clear()

        counter = 1
        print('Looking for files...')
        print('')
        for file in filelist:
            pos = os.path.abspath(file).find("Maraging Steels")+(len("Maraging Steels"))+1
            #print('['+str(counter)+'] '+os.path.abspath(file)[pos:])
            file_list.append(os.path.abspath(file))
            counter = counter+1

        return file_list

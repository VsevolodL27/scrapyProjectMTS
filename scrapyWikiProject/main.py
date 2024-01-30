# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


from scrapy import cmdline
cmdline.execute("scrapy crawl movies -o movies.csv".split())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

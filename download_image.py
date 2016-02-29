# -*- coding: utf-8 -*-
# from django.core.management.base import BaseCommand

import urllib
import os
import datetime
import time
import ConfigParser
import MySQLdb
import sys

default_config = {
    "host": "localhost",
    "port": "3306",
    "db": "image_test",
    "user": "root",
    "password": "0000",
    "charset": "utf8",
    "table": "image_tmp",
    "id_column": "id",
    "url_column": "image",
    "path": "~/tmp/item_images/",
    "path_column": "path",
    "limit_file_count": "1000",
    "interval": "0",
    "block_time": "0:00-0:00",
}


def log(msg):
    sys.stdout.write(str(msg) + "\n")
    sys.stdout.flush()


class ImageDownloader:
    def __init__(self, config="./config.ini"):
        self.inifile = ConfigParser.SafeConfigParser(default_config)
        self.inifile.read(config)

    def download_image(self, items):
        if not items:
            items = self.get_items()

        success = []
        dl_err = []
        interval = self.inifile.getfloat("fetch", "interval")

        for item in items:
            # Downloading
            try:
                item_id = item['id']
                item_image = item['image']
                # filename = be.consts.PATH_IMAGES  + str(item_id)
                filename = self.get_dir_path() + str(item_id)
                log("download start %s on %s " % (item_id, filename))
                if item_image == '':
                    dl_err.append(str(item['id']))
                    continue
                if not os.path.exists(filename):
                    urllib.urlretrieve(item_image, filename)
                # success.append(str(item['id']))
                success.append({"id": item_id, "path": filename})
            except Exception as error:
                log(error)
                dl_err.append(str(item['id']))
                continue
            time.sleep(interval)

        log(str(len(success)) + " items are downloaded.")
        if len(dl_err) > 0:
            log("Download Error: " + ', '.join(dl_err))
        return success

    def get_database_config(self):
        config = {
            "host": self.inifile.get("database", "host"),
            "port": int(self.inifile.get("database", "port")),
            "db": self.inifile.get("database", "db"),
            "user": self.inifile.get("database", "user"),
            "passwd": self.inifile.get("database", "password"),
            "charset": self.inifile.get("database", "charset"),
        }
        return config

    def get_items(self):
        items = []

        table = self.inifile.get("input", "table")
        id_column = self.inifile.get("input", "id_column")
        image_column = self.inifile.get("input", "url_column")
        path_column = self.inifile.get("output", "path_column")

        try:
            cnn = MySQLdb.connect(**self.get_database_config())
            cur = cnn.cursor()
            sql = "select %s, %s from %s where %s IS NULL" % (id_column, image_column, table, path_column)
            cur.execute(sql)
            rows = cur.fetchall()

            for row in rows:
                items.append({"id": row[0], "image": row[1]})

            cur.close()
            cnn.close()
        except MySQLdb.Error as e:
            log(e)
        return items

    def save(self, images):

        table = self.inifile.get("input", "table")
        id_column = self.inifile.get("input", "id_column")
        path_column = self.inifile.get("output", "path_column")

        values = []
        for image in images:
            values.append((image["id"], image["path"]))
        if len(values) == 0:
            return

        try:
            cnn = MySQLdb.connect(**self.get_database_config())
            cur = cnn.cursor()
            sql1 = "INSERT INTO %s (%s, %s) VALUES" % (table, id_column, path_column)
            sql2 = "ON DUPLICATE KEY UPDATE %s = VALUES(%s)" % (path_column, path_column)
            # sql = "replace into %s (%s, %s) VALUES " % (table, id_column, path_column)
            sql = sql1 + " (%s, %s) " + sql2
            # log(sql)
            cur.executemany(sql, values)
            # Make sure data is committed to the database
            cnn.commit()

            cur.close()
            cnn.close()
        except MySQLdb.Error as e:
            log(e)

    def get_dir_path(self):
        path = self.inifile.get("output", "path")
        limit = self.inifile.getint("output", "limit_file_count")
        if not os.path.exists(path):
            os.makedirs(path)
        files = os.listdir(path)
        files.sort()
        last = ""
        dire = []
        # 入れていいディレクトリを探す
        for filename in files:
            path_tmp = path + filename
            if os.path.isdir(path_tmp):
                if len(os.listdir(path_tmp)) < limit:
                    dire.append(path_tmp)
                last = self.get_int_str(filename, last)
                # log("dir: %s %d" % (file, len(os.listdir(path + file))))
        if len(dire) > 0:
            dire.sort()
            return dire[0] + "/"
        # 入れていいディレクトリが無いとき
        if last:
            try:
                last_int = int(last)
            except:
                last_int = 0
        else:
            last_int = 0
        while os.path.exists(path + str(last_int)):
            # log(last_int)
            last_int += 1
        last = path + str(last_int)
        os.makedirs(last)
        return last + "/"

    @staticmethod
    def get_int_str(filename, default):
        try:
            return str(int(filename))
        except:
            return default


class Command:  # (BaseCommand):
    def handle(self, *args, **options):
        log('Start at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        log('----')

        start = time.time()

        downloader = ImageDownloader()
        result = downloader.download_image()
        downloader.save(self, result)

        end = time.time()

        log("----")
        log("Finish at " + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        log("Spend " + str(end - start) + " seconds")


if __name__ == "__main__":
    param = sys.argv
    if len(param) > 1:
        downloader = ImageDownloader(param[1])
    else:
        downloader = ImageDownloader()

    log('Start at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
    log('----')

    start = time.time()

    items = downloader.get_items()
    result = downloader.download_image(items)
    downloader.save(result)

    end = time.time()

    log("----")
    log("Finish at " + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
    log("Spend " + str(end - start) + " seconds")

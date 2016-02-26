# python-image-downloader
image download script written by python


## Run

```bash
python download_image.py default_config.ini
```

if no config file option, script read `./config.ini` file.

## Config File

```
[database]
# host     : localhost
# port     : 3306
db       : image_test
user     : root
password : 0000
# charset  : utf8

[input]
table      : image_tmp
# id_column  : id
# url_column : image

[output]
path        : ~/tmp/item_images/
# path_column : path
# limit_file_count: 3

[fetch]
# interval   : 1
# block_time : 2:00-5:00
```

## Queueing database

if you make queue db, use MySQL compatibility database.
(like MySQL, MariaDB, Amazon Aurora)

```sql
CREATE TABLE `image_tmp` (
  `id` INT(11) NOT NULL, # if need, specify AUTO_INCREMENT option
  `image` VARCHAR(128) NOT NULL,
  `path` VARCHAR(128) NULL,
  PRIMARY KEY (`id`));
```

## License

[MIT](https://github.com/wasnot/python-image-downloader/blob/master/LICENSE)


## Author

[wasnot](https://github.com/wasnot)

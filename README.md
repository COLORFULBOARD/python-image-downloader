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

## License
https://github.com/wasnot/python-image-downloader/blob/master/LICENSE
[MIT](https://github.com/wasnot/python-image-downloader/blob/master/LICENSE)


## Author

[tcnksm](https://github.com/wasnot)

<?php

namespace App\Helper;

class File
{
    public static function save($path, $contents): int | false
    {
        if (!is_dir(dirname($path)))
            mkdir(dirname($path));

        return file_put_contents($path, $contents);
    }
}

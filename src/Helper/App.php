<?php

namespace App\Helper;

class App
{
    public static function root(): string
    {
        $dir = __DIR__;
        $pos = strrpos($dir, '/src/Helper');

        return substr($dir, 0, $pos);
    }

    public static function resources(): string
    {
        return self::root() . '/resources';
    }

    public static function docs(): string
    {
        return self::root() . '/docs';
    }

    public static function templates(): string
    {
        return self::root() . '/templates';
    }

    public static function archive(): string
    {
        return self::docs() . '/archive';
    }

    public static function getWebsites(): array
    {
        $websites = file_get_contents(self::resources() . '/websites.json');

        //return [json_decode($websites)[0]];

        return json_decode($websites);
    }

    public static function isCli(): bool
    {
        return php_sapi_name() === 'cli';
    }
}

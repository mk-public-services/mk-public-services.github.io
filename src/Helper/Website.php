<?php

namespace App\Helper;

class Website
{
    public static function parseRobotsTxt(array $content, $only = null): array | string|null
    {
        $supports = ['sitemap'];
        $data = [];

        foreach ($content as $c) {
            if (strpos($c, ':') === false)
                continue;

            list($left, $right) = explode(':', trim($c), 2);

            foreach ($supports as $s) {
                $left = strtolower(trim($left));
                if ($left === $s)
                    $data[$left] = trim($right);
            }
        }

        if ($only) {
            if (isset($data[$only]))
                return $data[$only];
            else
                return null;
        }

        return $data;
    }
}

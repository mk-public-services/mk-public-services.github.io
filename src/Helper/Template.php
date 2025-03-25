<?php

namespace App\Helper;

class Template
{
    public static function render($template, $data = []): string
    {
        $templatePath = App::templates() . '/' . $template;
        if (!file_exists($templatePath))
            throw new \Exception('Template ' . $template . ' does not exist.');

        if (!is_array($data))
            throw new \Exception('Invalid template variables.');

        foreach ($data as $k => $v) {
            ${$k} = $v;
        }

        ob_start();
        include($templatePath);
        $templateContents = ob_get_contents();
        ob_end_clean();
        return $templateContents;
    }
}

<?php

namespace App\Command;

use App\Helper\Template;
use App\Helper\App;
use App\Helper\File;

class ExportForWeb
{
    public function go()
    {
        $certs = json_decode(file_get_contents(App::docs() . '/valid-certificates.json'), true);
        $robotsAndSitemap = json_decode(file_get_contents(App::docs() . '/robots-and-sitemap.json'), true);
        $newsfeeds = json_decode(file_get_contents(App::docs() . '/newsfeeds.json'), true);

        $data = $robotsAndSitemap;
        foreach ($certs as $web => $value) {
            $data[$web]['cert'] = $value;
        }
        foreach ($newsfeeds as $web => $value) {
            $data[$web]['feed'] = $value;
        }

        foreach ($data as &$d) {
            $d['score'] = 0;
            if ($d['cert'] == 1)
                $d['score']++;
            if ($d['robots'] == 1)
                $d['score']++;
            if ($d['sitemap'] != 0)
                $d['score']++;
            if ($d['feed'] != 0)
                $d['score']++;
        }

        uasort(
            $data,
            fn($a, $b) =>
            $b['score'] - $a['score']
        );

        File::save(App::docs() . '/index.html', Template::render('index.php', ['websites' => $data]));
    }
}

<?php

namespace App\Command;

use App\Helper\App;

class SaveToArchive
{
    public function go()
    {
        $archive = App::archive() . '/' . date('d-m-Y') . '/';

        if (!is_dir($archive))
            mkdir($archive, 0755, true);

        if (!is_dir($archive . '/css'))
            mkdir($archive . '/css', 0755);

        if (!is_dir($archive . '/img'))
            mkdir($archive . '/img', 0755);

        copy(App::docs() . '/index.html', $archive . '/index.html');
        copy(App::docs() . '/css/style.css', $archive . '/css/style.css');
        copy(App::docs() . '/img/github-mark.svg', $archive . '/img/github-mark.svg');

        copy(App::docs() . '/robots-and-sitemap.json', $archive . '/robots-and-sitemap.json');
        copy(App::docs() . '/valid-certificates.json', $archive . '/valid-certificates.json');
    }
}

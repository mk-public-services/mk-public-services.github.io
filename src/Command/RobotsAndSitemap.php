<?php

namespace App\Command;

use App\Helper\App;
use App\Helper\File;
use App\Helper\Website;

class RobotsAndSitemap
{
    public function go()
    {
        $websites = App::getWebsites();

        $json = [];

        foreach ($websites as $website) {
            $robotsFile = @file($website . '/robots.txt');

            $data = [];
            if ($robotsFile === false) {
                $data['robots'] = 0;
                $data['sitemap'] = 0;
            } else {
                $data['robots'] = 1;
                $sitemap = Website::parseRobotsTxt($robotsFile, 'sitemap');

                if ($sitemap) {
                    $sitemapContents = @file_get_contents($sitemap);

                    if ($sitemapContents === false)
                        $data['sitemap'] = 0;
                    else
                        $data['sitemap'] = $sitemap;
                } else {
                    $data['sitemap'] = 0;
                }
            }

            $json[$website] = $data;
        }

        File::save(App::docs() . '/robots-and-sitemap.json', json_encode($json));
    }
}

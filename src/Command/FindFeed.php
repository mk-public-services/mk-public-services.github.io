<?php

namespace App\Command;

use App\Helper\App;
use App\Helper\File;

class FindFeed
{
    public function go()
    {
        $websites = App::getWebsites();

        $json = [];

        foreach ($websites as $w) {
            if ($this->findRssFeed($w) !== false)
                $json[$w] = 1;
            else
                $json[$w] = 0;
        }

        File::save(App::docs() . '/newsfeeds.json', json_encode($json));
    }

    private function findRssFeed($url)
    {
        $feeds = [];

        // Normalize base URL
        $parsed = parse_url($url);
        if (!isset($parsed['scheme']) || !isset($parsed['host'])) {
            return false;
        }
        $base = $parsed['scheme'] . '://' . $parsed['host'];

        // Step 1: Look in HTML <link> tags
        $html = @file_get_contents($url);
        if ($html !== false) {
            libxml_use_internal_errors(true);
            $dom = new \DOMDocument();
            $dom->loadHTML($html);
            libxml_clear_errors();

            $xpath = new \DOMXPath($dom);
            foreach ($xpath->query('//link[@rel="alternate"]') as $link) {
                $type = $link->getAttribute('type');
                if (in_array($type, ['application/rss+xml', 'application/atom+xml'])) {
                    $href = $link->getAttribute('href');
                    if (strpos($href, 'http') !== 0) {
                        $href = rtrim($base, '/') . '/' . ltrim($href, '/');
                    }
                    if ($this->isValidRss($href)) {
                        $feeds[] = $href;
                    }
                }
            }
        }

        // Step 2: Try common feed paths
        $commonPaths = ['/feed', '/rss', '/rss.xml', '/atom.xml'];
        foreach ($commonPaths as $path) {
            $testUrl = rtrim($base, '/') . $path;
            if ($this->isValidRss($testUrl)) {
                $feeds[] = $testUrl;
            }
        }

        return array_unique($feeds) ?: false;
    }

    private function isValidRss($url)
    {
        $content = @file_get_contents($url);
        if ($content === false) {
            return false;
        }

        libxml_use_internal_errors(true);
        $xml = simplexml_load_string($content);
        libxml_clear_errors();

        if (!$xml) return false;

        $root = strtolower($xml->getName());
        return in_array($root, ['rss', 'feed']);
    }
}

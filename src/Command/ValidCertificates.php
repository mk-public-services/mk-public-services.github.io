<?php

namespace App\Command;

use App\Helper\App;
use App\Helper\File;
use Spatie\SslCertificate\SslCertificate;

class ValidCertificates
{
    public function go()
    {
        $websites = App::getWebsites();

        $json = [];

        foreach ($websites as $website) {
            try {
                $certificate = @SslCertificate::createForHostName($website);
            } catch (\Exception $e) {
                $json[$website] = 0;
                continue;
            } finally {
                if ($certificate->isValid($website)) {
                    $json[$website] = 1;
                }
            }
        }

        File::save(App::docs() . '/valid-certificates.json', json_encode($json));
    }
}

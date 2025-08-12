<!doctype html>
<html>

<head>
    <link rel="stylesheet" href="./css/style.css" type="text/css" media="all" />
    <title>Македонски Јавни Услуги</title>
</head>

<body>
    <span class="refreshed">Освежено на <?php echo date('d-m-Y H:i:s'); ?></span>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Адреса</th>
                <th>Сертификат</th>
                <th>robots.txt</th>
                <th>Sitemap</th>
                <th>Feed</th>
            </tr>
        </thead>
        <tbody>
            <?php
            $count = 0;
            foreach ($websites as $web => $v) {
                $count++ ?>
                <tr>
                    <td><?= $count ?></td>
                    <td><a href="<?= $web ?>" target="_blank"><?= $web ?></a></td>
                    <td><?= $v['cert'] ? '&#x2705;' : '&#x274C;' ?></td>
                    <td><?= $v['robots'] ? '&#x2705;' : '&#x274C;' ?></td>
                    <td><?= $v['sitemap'] == 0 ? '&#x274C;' : '&#x2705;' ?></td>
                    <td><?= $v['feed'] == 0 ? '&#x274C;' : '&#x2705;' ?></td>
                </tr>
            <?php } ?>
        </tbody>
    </table>
    <footer>
        <ul>
            <li>
                <a href="https://github.com/mk-public-services/mk-public-services.github.io"><img src="./img/github-mark.svg" alt="link to github repo" /></a>
            </li>
        </ul>
    </footer>
</body>

</html>
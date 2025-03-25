<?php

$dir = __DIR__;

include $dir . '/vendor/autoload.php';

if ($argc < 2) {
    echo 'Please specify command.' . PHP_EOL;
    exit;
}

$command = $argv[1];
$commandPath = $dir . '/src/Command/' . $command . '.php';

if (!file_exists($commandPath)) {
    echo 'Command does not exist.' . PHP_EOL;
    exit;
}

$commandClass = 'App\\Command\\' . $command;
$cmd = new $commandClass;
$ret = $cmd->go($argv);

echo $ret;

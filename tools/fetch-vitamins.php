<?php
/**
 * Converts CSV files downloaded from https://companion.pokeclicker.com into
 * JSON files containing only the necessary data for the user script to
 * optimally distribute all the vitamins.
 *
 * As of now, the source files need to be placed with the script. It would be
 * nice, if they could be downloaded on-demand at some point but, because of
 * their dynamic nature, unfortunately, there is no straightforward way to get
 * a download link for them.
 */

declare(strict_types=1);

enum Region: int
{
    case Kanto = 0;
    case Johto = 1;
    case Hoenn = 2;
    case Sinnoh = 3;
    case Unova = 4;
    case Kalos = 5;
    case Alola = 6;
    case Galar = 7;
}

enum Vitamin: int
{
    case Protein = 0;
    case Calcium = 1;
    case Carbos = 2;
}

$inputFiles = [
    Region::Kanto->value => __DIR__ . '/data/01-kanto.csv',
    Region::Johto->value => __DIR__ . '/data/02-johto.csv',
    Region::Hoenn->value => __DIR__ . '/data/03-hoenn.csv',
    Region::Sinnoh->value => __DIR__ . '/data/04-sinnoh.csv',
    Region::Unova->value => __DIR__ . '/data/05-unova.csv',
    Region::Kalos->value => __DIR__ . '/data/06-kalos.csv',
    Region::Alola->value => __DIR__ . '/data/07-alola.csv',
    Region::Galar->value => __DIR__ . '/data/08-galar.csv',
];

$regions = [
    Region::Kanto->value => [],
    Region::Johto->value => [],
    Region::Hoenn->value => [],
    Region::Sinnoh->value => [],
    Region::Unova->value => [],
    Region::Kalos->value => [],
    Region::Alola->value => [],
    Region::Galar->value => [],
];

foreach ($inputFiles as $regionId => $inputFileName) {
    $currentRow = 0;
    $firstRow = [];
    $fd = fopen($inputFileName, 'r');

    while ($row = fgetcsv($fd)) {
        if ($currentRow++ === 0) {
            $firstRow = $row;

            continue;
        }

        $parsedRow = array_combine($firstRow, $row); // re-index from header values
        $regions[$regionId][$parsedRow['#']] = [
            Vitamin::Protein->value => (int)$parsedRow['Optimal Protein'],
            Vitamin::Calcium->value => (int)$parsedRow['Optimal Calcium'],
            Vitamin::Carbos->value => (int)$parsedRow['Optimal Carbos'],
        ];
    }

    fclose($fd);

    $targetFilename = dirname($inputFileName) . '/' . basename($inputFileName, '.csv') . '.json';
    file_put_contents($targetFilename, json_encode($regions[$regionId]));
}

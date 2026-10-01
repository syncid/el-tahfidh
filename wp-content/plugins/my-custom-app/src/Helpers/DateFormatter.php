<?php

declare(strict_types=1);

namespace MyCustomApp\Helpers;

use DateTimeImmutable;
use DateTimeZone;

/**
 * Format tanggal untuk tampilan, sesuai bahasa & zona waktu situs.
 */
final class DateFormatter
{
    private function __construct()
    {
    }

    /**
     * '2026-10-05' -> 'Senin, 5 Oktober 2026'. Kembalikan input apa adanya jika tidak valid.
     */
    public static function date(string $ymd): string
    {
        $date = DateTimeImmutable::createFromFormat('!Y-m-d', $ymd, wp_timezone());

        return $date === false ? $ymd : (string) wp_date('l, j F Y', $date->getTimestamp());
    }

    /**
     * Datetime UTC dari database -> waktu situs, mis. '2 Okt 2026 09:15'.
     */
    public static function utc_datetime(string $utc): string
    {
        $date = DateTimeImmutable::createFromFormat('Y-m-d H:i:s', $utc, new DateTimeZone('UTC'));

        return $date === false ? $utc : (string) wp_date('j M Y H:i', $date->getTimestamp());
    }
}

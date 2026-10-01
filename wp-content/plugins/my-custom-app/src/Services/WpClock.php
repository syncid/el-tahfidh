<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

use DateTimeImmutable;

/**
 * Jam produksi: memakai zona waktu dari Pengaturan > Umum WordPress.
 */
final class WpClock implements ClockInterface
{
    public function now(): DateTimeImmutable
    {
        return new DateTimeImmutable('now', wp_timezone());
    }
}

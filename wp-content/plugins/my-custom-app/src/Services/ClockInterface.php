<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

use DateTimeImmutable;

/**
 * Sumber waktu "sekarang". Diinjeksikan agar logika berbasis tanggal bisa diuji.
 */
interface ClockInterface
{
    /**
     * Waktu sekarang dalam zona waktu situs.
     */
    public function now(): DateTimeImmutable;
}

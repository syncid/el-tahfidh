<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

/**
 * Hasil booking. dobel = true jika anak ini sudah punya booking aktif di tanggal tsb.
 */
final class BookingResult
{
    public function __construct(
        public readonly string $kode,
        public readonly string $sesi,
        public readonly bool $dobel
    ) {
    }
}

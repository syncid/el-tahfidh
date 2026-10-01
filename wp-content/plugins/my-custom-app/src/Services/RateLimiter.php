<?php

declare(strict_types=1);

namespace MyCustomApp\Services;

/**
 * Pembatas jumlah percobaan berbasis transient (cukup untuk form publik bervolume rendah).
 */
final class RateLimiter
{
    /**
     * Catat satu percobaan. Mengembalikan false jika batas sudah tercapai.
     *
     * @param string $bucket   Nama fitur, mis. 'survey_booking'.
     * @param string $identity Identitas klien, mis. alamat IP (di-hash, tidak disimpan mentah).
     */
    public function attempt(string $bucket, string $identity, int $limit, int $window_seconds): bool
    {
        $key  = 'mca_rl_' . md5($bucket . '|' . $identity);
        $hits = (int) get_transient($key);

        if ($hits >= $limit) {
            return false;
        }

        set_transient($key, $hits + 1, $window_seconds);

        return true;
    }
}
